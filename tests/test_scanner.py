from unittest.mock import patch
from app.models import CertificateState,Endpoint
from app.scanner import CertificateScanner

def test_network_failure_becomes_bounded_scan_evidence():
 with patch('socket.create_connection',side_effect=TimeoutError('connection timed out')):
  value=CertificateScanner().scan(Endpoint(name='vpn',host='vpn.example'))
 assert value.state is CertificateState.ERROR;assert value.error=={'type':'TimeoutError','message':'connection timed out'}

def test_scanner_timeout_is_bounded():
 try:CertificateScanner(60)
 except ValueError as exc:assert 'timeout' in str(exc)
 else:raise AssertionError('unsafe timeout accepted')
