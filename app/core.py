import socket,ssl
from datetime import datetime,timezone
THRESHOLDS=(30,15,10,5,3,2,1)
def urgency(days):
 if days<0:return "EXPIRED"
 hit=next((d for d in reversed(THRESHOLDS) if days<=d),None)
 return f"DUE_{hit}D" if hit else "HEALTHY"
def scan(host,port=443,timeout=5,now=None):
 if not host or len(host)>253:raise ValueError("invalid host")
 ctx=ssl.create_default_context()
 with socket.create_connection((host,port),timeout) as raw:
  with ctx.wrap_socket(raw,server_hostname=host) as s: cert=s.getpeercert()
 expiry=datetime.strptime(cert["notAfter"],"%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc);now=now or datetime.now(timezone.utc);days=(expiry-now).days
 ssl.match_hostname(cert,host)
 return {"host":host,"port":port,"issuer":dict(x[0] for x in cert["issuer"]),"sans":[v for k,v in cert.get("subjectAltName",()) if k=="DNS"],"not_before":cert["notBefore"],"not_after":expiry.isoformat(),"days_remaining":days,"state":urgency(days),"hostname_valid":True}
