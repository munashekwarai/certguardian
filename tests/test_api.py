from fastapi.testclient import TestClient
from app import api
from app.models import CertificateState,ScanResult
from app.repository import Repository
from app.service import Guardian
class Scanner:
 def scan(self,e):return ScanResult(endpoint_id=e.id,endpoint_name=e.name,host=e.host,port=e.port,state=CertificateState.DUE,hostname_valid=True,days_remaining=10,matched_threshold=10)
def client(monkeypatch):
 repo=Repository();monkeypatch.setattr(api,'repository',repo);monkeypatch.setattr(api,'guardian',Guardian(repo,Scanner()));return TestClient(api.app)
def test_inventory_scan_history_and_alert_api(monkeypatch):
 http=client(monkeypatch);created=http.post('/endpoints',json={'name':'portal','host':'portal.example','owner':'platform'});assert created.status_code==201
 id=created.json()['id'];assert http.get('/endpoints').json()[0]['owner']=='platform'
 assert http.post(f'/endpoints/{id}/scan').json()['matched_threshold']==10
 assert http.get(f'/endpoints/{id}/history').json()['latest']['state']=='DUE'
 assert http.get('/alerts').json()[0]['endpoint']['name']=='portal'
def test_duplicate_and_missing_are_structured(monkeypatch):
 http=client(monkeypatch);payload={'name':'portal','host':'portal.example'}
 assert http.post('/endpoints',json=payload).status_code==201;assert http.post('/endpoints',json=payload).status_code==409
 assert http.post('/endpoints/404/scan').status_code==404
