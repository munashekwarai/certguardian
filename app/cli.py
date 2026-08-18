"""CertGuardian operator CLI."""
import json,typer
from .core import scan
from .models import Endpoint
from .repository import Repository
from .service import Guardian
app=typer.Typer(no_args_is_help=True)
def emit(x):typer.echo(json.dumps(x,indent=2,default=str))
@app.command('scan')
def scan_host(host:str,port:int=443):emit(scan(host,port))
@app.command('add')
def add(name:str,host:str,port:int=443,database:str='./data/certguardian.db',owner:str|None=None):
 e=Repository(database).add(Endpoint(name=name,host=host,port=port,owner=owner));emit({'id':e.id,'name':e.name})
@app.command('run')
def run(endpoint_id:int,database:str='./data/certguardian.db'):
 emit(Guardian(Repository(database)).scan(endpoint_id).to_dict())
@app.command('due')
def due(database:str='./data/certguardian.db'):
 r=Repository(database);emit([{'id':e.id,'name':e.name} for e in r.due_for_scan()])
@app.command('watch')
def watch(database:str='./data/certguardian.db',poll_seconds:int=60):Guardian(Repository(database)).run_forever(poll_seconds)
if __name__=='__main__':app()
