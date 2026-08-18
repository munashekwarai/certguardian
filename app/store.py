import json,sqlite3,time
class Inventory:
 def __init__(self,path=":memory:"):
  self.db=sqlite3.connect(path);self.db.execute("create table if not exists scans(id integer primary key, host text, scanned_at integer, result text)")
 def add(self,result): self.db.execute("insert into scans(host,scanned_at,result) values(?,?,?)",(result["host"],int(time.time()),json.dumps(result)));self.db.commit()
 def history(self,host): return [json.loads(x[0]) for x in self.db.execute("select result from scans where host=? order by id desc",(host,))]
 def due_hosts(self,latest_states=("EXPIRED","DUE_30D","DUE_15D","DUE_10D","DUE_5D","DUE_3D","DUE_2D","DUE_1D")):
  hosts=[x[0] for x in self.db.execute("select distinct host from scans")]
  return [h for h in hosts if self.history(h) and self.history(h)[0].get("state") in latest_states]
 def scheduled_scan(self,targets,scanner):
  results=[]
  for host,port in targets:
   result=scanner(host,port);self.add(result);results.append(result)
  return results
