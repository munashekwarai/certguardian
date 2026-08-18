"""CertGuardian inventory and scan REST API."""
import os,sqlite3
from fastapi import FastAPI,HTTPException,Query
from pydantic import BaseModel,Field
from .models import DEFAULT_THRESHOLDS,Endpoint
from .repository import Repository
from .service import Guardian

class EndpointInput(BaseModel):
 name:str=Field(min_length=1,max_length=100);host:str=Field(min_length=1,max_length=253)
 port:int=Field(default=443,ge=1,le=65535);scan_interval_minutes:int=Field(default=1440,ge=1,le=10080)
 thresholds:list[int]=Field(default_factory=lambda:list(DEFAULT_THRESHOLDS),min_length=1,max_length=20)
 owner:str|None=Field(default=None,max_length=200)

repository=Repository(os.getenv('CERTGUARDIAN_DB',':memory:'));guardian=Guardian(repository)
app=FastAPI(title='CertGuardian',version='0.2.0')
@app.get('/health')
def health():return {'status':'ok','inventory_count':len(repository.list())}
@app.post('/endpoints',status_code=201)
def create(value:EndpointInput):
 try:e=repository.add(Endpoint(**{**value.model_dump(),'thresholds':tuple(value.thresholds)}))
 except sqlite3.IntegrityError:raise HTTPException(409,'an endpoint with that name already exists') from None
 except ValueError as exc:raise HTTPException(422,str(exc)) from None
 return {'id':e.id,**value.model_dump()}
@app.get('/endpoints')
def endpoints():return [{'id':e.id,'name':e.name,'host':e.host,'port':e.port,'owner':e.owner} for e in repository.list()]
@app.post('/endpoints/{endpoint_id}/scan')
def scan_endpoint(endpoint_id:int):
 try:return guardian.scan(endpoint_id).to_dict()
 except KeyError as exc:raise HTTPException(404,str(exc)) from None
@app.get('/endpoints/{endpoint_id}/history')
def history(endpoint_id:int,limit:int=Query(100,ge=1,le=1000)):
 try:e=repository.get(endpoint_id)
 except KeyError as exc:raise HTTPException(404,str(exc)) from None
 return {'endpoint_id':e.id,'latest':repository.latest(e.id),'scans':repository.history(e.id,limit)}
@app.post('/scans/due')
def scan_due():return {'results':[x.to_dict() for x in guardian.scan_due()]}
@app.get('/alerts')
def alerts():return [{'endpoint':{'id':x['endpoint'].id,'name':x['endpoint'].name},'latest':x['latest']} for x in repository.attention()]
