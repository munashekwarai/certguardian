from app.core import urgency
from app.store import Inventory
def test_thresholds(): assert urgency(31)=="HEALTHY" and urgency(4)=="DUE_5D" and urgency(-1)=="EXPIRED"
def test_history():
 i=Inventory();i.add({"host":"example.com","state":"HEALTHY"});assert i.history("example.com")[0]["state"]=="HEALTHY"
def test_due_inventory_and_scheduled_scan():
 i=Inventory();fake=lambda h,p:{"host":h,"port":p,"state":"DUE_5D"};i.scheduled_scan([("internal.example",443)],fake);assert i.due_hosts()==["internal.example"]
