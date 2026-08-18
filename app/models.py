"""Certificate inventory and scan domain models."""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

DEFAULT_THRESHOLDS = (30, 15, 10, 5, 3, 2, 1)

class CertificateState(StrEnum):
    HEALTHY="HEALTHY"; DUE="DUE"; EXPIRED="EXPIRED"; ERROR="ERROR"

@dataclass(frozen=True, slots=True)
class Endpoint:
    name:str; host:str; port:int=443; scan_interval_minutes:int=1440
    thresholds:tuple[int,...]=DEFAULT_THRESHOLDS; enabled:bool=True; owner:str|None=None; id:int|None=None
    def __post_init__(self):
        if not self.name.strip() or len(self.name)>100: raise ValueError("name must contain 1 to 100 characters")
        if not self.host.strip() or len(self.host)>253: raise ValueError("host must contain 1 to 253 characters")
        if not 1<=self.port<=65535: raise ValueError("port must be between 1 and 65535")
        if not 1<=self.scan_interval_minutes<=10080: raise ValueError("scan interval must be between 1 minute and 7 days")
        if not self.thresholds or any(x<1 or x>365 for x in self.thresholds): raise ValueError("thresholds must contain days between 1 and 365")
        if len(set(self.thresholds))!=len(self.thresholds): raise ValueError("thresholds must be unique")
        object.__setattr__(self,"thresholds",tuple(sorted(self.thresholds,reverse=True)))

@dataclass(frozen=True, slots=True)
class ScanResult:
    endpoint_name:str; host:str; port:int; state:CertificateState; hostname_valid:bool
    issuer:dict[str,str]=field(default_factory=dict); subject:dict[str,str]=field(default_factory=dict)
    sans:list[str]=field(default_factory=list); serial_number:str|None=None
    not_before:datetime|None=None; not_after:datetime|None=None; days_remaining:int|None=None
    matched_threshold:int|None=None; protocol:str|None=None; cipher:str|None=None
    fingerprint_sha256:str|None=None; error:dict[str,Any]|None=None
    scanned_at:datetime=field(default_factory=lambda:datetime.now(timezone.utc)); endpoint_id:int|None=None
    def to_dict(self):
        value=asdict(self);value["state"]=self.state.value
        for key in ("not_before","not_after","scanned_at"):
            value[key]=value[key].isoformat() if value[key] else None
        return value

def classify(days:int, thresholds:tuple[int,...]=DEFAULT_THRESHOLDS)->tuple[CertificateState,int|None]:
    if days<0:return CertificateState.EXPIRED,None
    matches=[value for value in thresholds if days<=value]
    return (CertificateState.DUE,min(matches)) if matches else (CertificateState.HEALTHY,None)
