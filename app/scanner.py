"""SNI-aware TLS certificate scanner with bounded failures."""
from __future__ import annotations
import hashlib,socket,ssl
from datetime import datetime,timezone
from .models import CertificateState,Endpoint,ScanResult,classify

class CertificateScanner:
    def __init__(self,timeout_seconds:float=5):
        if not .1<=timeout_seconds<=30:raise ValueError("timeout must be between 0.1 and 30 seconds")
        self.timeout=timeout_seconds

    def scan(self,endpoint:Endpoint)->ScanResult:
        try:return self._scan(endpoint)
        except (OSError,TimeoutError,ssl.SSLError,ValueError) as exc:
            return ScanResult(endpoint_id=endpoint.id,endpoint_name=endpoint.name,host=endpoint.host,port=endpoint.port,
                state=CertificateState.ERROR,hostname_valid=False,error={"type":type(exc).__name__,"message":str(exc)[:200]})

    def _scan(self,endpoint:Endpoint)->ScanResult:
        context=ssl.create_default_context()
        with socket.create_connection((endpoint.host,endpoint.port),self.timeout) as raw:
            with context.wrap_socket(raw,server_hostname=endpoint.host) as secured:
                cert=secured.getpeercert(); binary=secured.getpeercert(binary_form=True)
                protocol=secured.version();cipher=secured.cipher()
        before=datetime.strptime(cert["notBefore"],"%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        after=datetime.strptime(cert["notAfter"],"%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        days=(after-datetime.now(timezone.utc)).days;state,threshold=classify(days,endpoint.thresholds)
        return ScanResult(endpoint_id=endpoint.id,endpoint_name=endpoint.name,host=endpoint.host,port=endpoint.port,
            state=state,hostname_valid=True,issuer=dict(x[0] for x in cert.get("issuer",())),
            subject=dict(x[0] for x in cert.get("subject",())),sans=[v for k,v in cert.get("subjectAltName",()) if k=="DNS"],
            serial_number=cert.get("serialNumber"),not_before=before,not_after=after,days_remaining=days,
            matched_threshold=threshold,protocol=protocol,cipher=cipher[0] if cipher else None,
            fingerprint_sha256=hashlib.sha256(binary).hexdigest())
