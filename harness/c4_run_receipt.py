#!/usr/bin/env python3
from pathlib import Path
import argparse,json,hashlib,datetime
ap=argparse.ArgumentParser();ap.add_argument('--cross',required=True);ap.add_argument('--semantic',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
def load(p):
 p=Path(p)
 if not p.exists():return None
 try:return json.loads(p.read_text())
 except Exception:return {'parse_error':True}
def sha(p):
 p=Path(p);return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
c=load(a.cross);s=load(a.semantic)
r={'build':'CORRIGIBILITY-4','created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cross_browser':{'present':c is not None,'sha256':sha(a.cross),'browsers':c.get('browsers') if c else None,'pass':c.get('pass') if c else None,'total':c.get('total') if c else None,'fail':c.get('fail') if c else None},'live_semantic':{'present':s is not None,'sha256':sha(a.semantic),'mode':s.get('mode') if s else None,'records':s.get('records') if s else None,'ok':s.get('ok') if s else None,'errors':s.get('errors') if s else None,'provider_requests_seen':s.get('provider_requests_seen') if s else None},'student_promotion':'NOT AUTHORIZED BY WORKFLOW','next':'Blind human semantic review, custodian unblind, manual VoiceOver/NVDA/physical-device gates, accountable release signoff.'}
Path(a.out).write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
