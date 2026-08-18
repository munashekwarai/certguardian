"""Inventory scan orchestration."""
import time
from .repository import Repository
from .scanner import CertificateScanner

class Guardian:
 def __init__(self,repository:Repository,scanner:CertificateScanner|None=None):self.repository=repository;self.scanner=scanner or CertificateScanner()
 def scan(self,endpoint_id:int):
  endpoint=self.repository.get(endpoint_id);result=self.scanner.scan(endpoint);self.repository.record(result);return result
 def scan_due(self):return [self.scan(endpoint.id) for endpoint in self.repository.due_for_scan()]
 def run_forever(self,poll_seconds=60,max_cycles=None,sleep=time.sleep):
  if not 1<=poll_seconds<=3600:raise ValueError('poll_seconds must be between 1 and 3600')
  cycles=0
  while max_cycles is None or cycles<max_cycles:
   self.scan_due();cycles+=1
   if max_cycles is None or cycles<max_cycles:sleep(poll_seconds)
