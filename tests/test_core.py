from datetime import datetime,timedelta,timezone
import pytest
from app.core import urgency
from app.models import CertificateState,Endpoint,ScanResult,classify
from app.repository import Repository
from app.service import Guardian

def result(endpoint,state=CertificateState.HEALTHY,days=90,at=None):
 return ScanResult(endpoint_id=endpoint.id,endpoint_name=endpoint.name,host=endpoint.host,port=endpoint.port,state=state,hostname_valid=state!=CertificateState.ERROR,days_remaining=days,scanned_at=at or datetime.now(timezone.utc))

def test_expiry_threshold_boundaries():
 assert urgency(31)=='HEALTHY';assert urgency(30)=='DUE_30D';assert urgency(4)=='DUE_5D';assert urgency(1)=='DUE_1D';assert urgency(-1)=='EXPIRED'

def test_endpoint_validation_and_threshold_normalization():
 e=Endpoint(name='site',host='example.com',thresholds=(1,30,5));assert e.thresholds==(30,5,1)
 with pytest.raises(ValueError,match='port'):Endpoint(name='bad',host='x',port=0)
 with pytest.raises(ValueError,match='unique'):Endpoint(name='bad',host='x',thresholds=(5,5))

def test_repository_inventory_history_and_attention(tmp_path):
 repo=Repository(str(tmp_path/'certs.db'));e=repo.add(Endpoint(name='vpn',host='vpn.example',owner='operations'))
 repo.record(result(e,CertificateState.DUE,5));assert repo.latest(e.id)['days_remaining']==5
 assert repo.attention()[0]['endpoint'].owner=='operations';assert repo.history(e.id,1)[0]['state']=='DUE'

def test_due_scheduler_respects_last_scan_time():
 repo=Repository();e=repo.add(Endpoint(name='api',host='api.example',scan_interval_minutes=60))
 assert repo.due_for_scan()==[e]
 repo.record(result(e,at=datetime.now(timezone.utc)-timedelta(minutes=30)));assert repo.due_for_scan()==[]
 assert repo.due_for_scan(datetime.now(timezone.utc)+timedelta(minutes=31))==[e]

class FakeScanner:
 def __init__(self):self.hosts=[]
 def scan(self,e):self.hosts.append(e.host);return result(e,CertificateState.DUE,3)

def test_guardian_scans_due_endpoints_and_persists():
 repo=Repository();e=repo.add(Endpoint(name='mail',host='mail.example'));scanner=FakeScanner();values=Guardian(repo,scanner).scan_due()
 assert scanner.hosts==['mail.example'];assert values[0].matched_threshold is None;assert repo.latest(e.id)['state']=='DUE'

def test_watch_loop_is_bounded_for_supervision():
 repo=Repository();repo.add(Endpoint(name='mail',host='mail.example',scan_interval_minutes=1));sleeps=[]
 Guardian(repo,FakeScanner()).run_forever(10,max_cycles=2,sleep=sleeps.append);assert sleeps==[10]
