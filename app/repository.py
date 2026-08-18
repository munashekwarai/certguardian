"""SQLite inventory and immutable historical scan storage."""
import json,sqlite3
from datetime import datetime,timezone
from pathlib import Path
from .models import CertificateState,Endpoint,ScanResult

class Repository:
 def __init__(self,path=":memory:"):
  if path!=":memory:":Path(path).parent.mkdir(parents=True,exist_ok=True)
  self.db=sqlite3.connect(path,check_same_thread=False);self.db.row_factory=sqlite3.Row
  self.db.executescript('''PRAGMA foreign_keys=ON;
  CREATE TABLE IF NOT EXISTS endpoints(id INTEGER PRIMARY KEY,name TEXT UNIQUE NOT NULL,host TEXT NOT NULL,port INTEGER NOT NULL,scan_interval_minutes INTEGER NOT NULL,thresholds_json TEXT NOT NULL,enabled INTEGER NOT NULL,owner TEXT);
  CREATE TABLE IF NOT EXISTS scans(id INTEGER PRIMARY KEY,endpoint_id INTEGER NOT NULL REFERENCES endpoints(id) ON DELETE CASCADE,state TEXT NOT NULL,hostname_valid INTEGER NOT NULL,result_json TEXT NOT NULL,scanned_at TEXT NOT NULL);
  CREATE INDEX IF NOT EXISTS scans_endpoint_time ON scans(endpoint_id,scanned_at DESC);''')
 def add(self,e:Endpoint)->Endpoint:
  cur=self.db.execute('INSERT INTO endpoints(name,host,port,scan_interval_minutes,thresholds_json,enabled,owner) VALUES(?,?,?,?,?,?,?)',(e.name,e.host,e.port,e.scan_interval_minutes,json.dumps(e.thresholds),int(e.enabled),e.owner));self.db.commit();return self.get(cur.lastrowid)
 def get(self,id:int)->Endpoint:
  row=self.db.execute('SELECT * FROM endpoints WHERE id=?',(id,)).fetchone()
  if not row:raise KeyError(f"endpoint {id} not found")
  return Endpoint(id=row['id'],name=row['name'],host=row['host'],port=row['port'],scan_interval_minutes=row['scan_interval_minutes'],thresholds=tuple(json.loads(row['thresholds_json'])),enabled=bool(row['enabled']),owner=row['owner'])
 def list(self,enabled_only=False):
  sql='SELECT id FROM endpoints'+(' WHERE enabled=1' if enabled_only else '')+' ORDER BY id';return [self.get(x[0]) for x in self.db.execute(sql)]
 def record(self,r:ScanResult):
  if r.endpoint_id is None:raise ValueError('persisted scans require endpoint_id')
  self.db.execute('INSERT INTO scans(endpoint_id,state,hostname_valid,result_json,scanned_at) VALUES(?,?,?,?,?)',(r.endpoint_id,r.state.value,int(r.hostname_valid),json.dumps(r.to_dict(),sort_keys=True),r.scanned_at.isoformat()));self.db.commit()
 def history(self,id:int,limit=100):
  limit=max(1,min(limit,1000));return [json.loads(x[0]) for x in self.db.execute('SELECT result_json FROM scans WHERE endpoint_id=? ORDER BY scanned_at DESC LIMIT ?',(id,limit))]
 def latest(self,id:int):
  values=self.history(id,1);return values[0] if values else None
 def due_for_scan(self,now=None):
  now=now or datetime.now(timezone.utc);due=[]
  for endpoint in self.list(True):
   latest=self.latest(endpoint.id)
   if latest is None:due.append(endpoint);continue
   scanned=datetime.fromisoformat(latest['scanned_at'])
   if (now-scanned).total_seconds()>=endpoint.scan_interval_minutes*60:due.append(endpoint)
  return due
 def attention(self):
  values=[]
  for endpoint in self.list(True):
   latest=self.latest(endpoint.id)
   if latest and latest['state']!=CertificateState.HEALTHY.value:values.append({"endpoint":endpoint,"latest":latest})
  return values
