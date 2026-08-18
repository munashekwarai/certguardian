from fastapi import FastAPI
from .core import scan
app=FastAPI(title="CertGuardian")
@app.get("/scan/{host}")
def run_scan(host:str,port:int=443):return scan(host,port)
