import json,typer
from .core import scan
app=typer.Typer()
@app.command()
def scan_host(host:str,port:int=443): print(json.dumps(scan(host,port),indent=2))
if __name__=="__main__":app()
