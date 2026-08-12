#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,sys,os
HERE=Path(__file__).resolve().parent; root=HERE.parent/'staging'; manifest=json.loads((HERE/'CORRIGIBILITY-4_FROZEN_STAGING_MANIFEST.json').read_text())
fail=[]
for rec in manifest['files']:
 p=root/rec['path']
 if not p.exists(): fail.append('missing '+rec['path']); continue
 h=hashlib.sha256(p.read_bytes()).hexdigest()
 if h!=rec['sha256']: fail.append('hash '+rec['path']+' '+h+' != '+rec['sha256'])
ex=(root/'Examined-main'/'index.html').read_text(encoding='utf-8'); nav=(root/'SPC-FALL-2026-Navigator-main'/'index.html').read_text(encoding='utf-8')
checks=[
 ('Examined C4 identity','examined-fall-2026-corrigibility-4-a11y-candidate' in ex),
 ('Examined chat live region','id="chat-messages" role="log" aria-live="polite"' in ex),
 ('Examined mode live status','id="examined-corrigibility-mode-label" class="corrigibility-mode-label" role="status" aria-live="polite" aria-atomic="true"' in ex),
 ('Navigator C2 identity','navigator-fall-2026-corrigibility-2-prototype' in nav),
 ('Goose/Midas contract Examined','GENERATIVITY GUARDIAN / BOUNDED MIDAS SENTINEL' in ex),
 ('Goose/Midas contract Navigator','GENERATIVITY GUARDIAN / BOUNDED MIDAS SENTINEL' in nav),
 ('Navigator fixed support text','What you wrote may describe immediate danger.' in nav),
 ('Expected backend Examined','https://ucp-backend-4dig.onrender.com/api/claude-proxy' in ex),
 ('Expected backend Navigator','https://ucp-backend-4dig.onrender.com/api/claude-proxy' in nav),
]
for n,ok in checks:
 print(('PASS' if ok else 'FAIL'),n)
 if not ok:fail.append(n)
print('Frozen files checked:',len(manifest['files']))
if fail:
 print('\n'.join(fail),file=sys.stderr);sys.exit(2)
