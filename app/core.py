"""One-shot compatibility API."""
from .models import DEFAULT_THRESHOLDS,Endpoint,classify
from .scanner import CertificateScanner
THRESHOLDS=DEFAULT_THRESHOLDS

def urgency(days):
 state,threshold=classify(days)
 return 'EXPIRED' if state.value=='EXPIRED' else (f'DUE_{threshold}D' if threshold else 'HEALTHY')

def scan(host,port=443,timeout=5,now=None):
 result=CertificateScanner(timeout).scan(Endpoint(name=host,host=host,port=port))
 value=result.to_dict()
 if result.matched_threshold:value['state']=f'DUE_{result.matched_threshold}D'
 return value
