#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
from pathlib import Path
import subprocess,time,socket,json,os

ROOT=Path('/mnt/data/CORRIGIBILITY-4_BUILD/staging')
E=Path('/mnt/data/CORRIGIBILITY-4_BUILD/evidence'); E.mkdir(exist_ok=True)
PORT=8876; BASE=f'http://127.0.0.1:{PORT}'
NAV=BASE+'/SPC-FALL-2026-Navigator-main/index.html'; EX=BASE+'/Examined-main/index.html'
CHROMIUM='/usr/bin/chromium'
results=[]

def add(tid,name,ok,evidence=''):
    results.append({'id':tid,'name':name,'status':'PASS' if ok else 'FAIL','evidence':str(evidence)})
    print(f"{tid} {'PASS' if ok else 'FAIL'} — {name}" + (f" — {evidence}" if evidence else ''))

def wait_server():
    for _ in range(80):
        try:
            with socket.create_connection(('127.0.0.1',PORT),timeout=.2): return True
        except Exception: time.sleep(.1)
    return False

def ls_set(page,k,v,raw=False):
    if raw: page.evaluate("([k,v])=>localStorage.setItem(k,v)",[k,v])
    else: page.evaluate("([k,v])=>localStorage.setItem(k,JSON.stringify(v))",[k,v])

def ls_get(page,k,d=None):
    return page.evaluate("([k,d])=>{const s=localStorage.getItem(k);if(s===null)return d;try{return JSON.parse(s)}catch(e){return s}}",[k,d])

def mock_fetch(page, delay=0):
    page.evaluate("""delay=>{window.__c4FetchCalls=0;window.fetch=async function(url,opts){window.__c4FetchCalls++;if(delay)await new Promise(r=>setTimeout(r,delay));const text='C4 delayed mock response.';return new Response(JSON.stringify({response:text,reply:text,content:[{type:'text',text:text}],stop_reason:'end_turn'}),{status:200,headers:{'Content-Type':'application/json'}});};}""",delay)

server=subprocess.Popen(['python','-m','http.server',str(PORT),'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    if not wait_server(): raise RuntimeError('server failed')
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=CHROMIUM,headless=True,args=['--no-sandbox'])
        ctx=browser.new_context(viewport={'width':1440,'height':900},service_workers='block')

        # Navigator
        nav=ctx.new_page(); nav.goto(NAV,wait_until='domcontentloaded')
        nav.evaluate('localStorage.clear()'); ls_set(nav,'navigator_ai_processing_consent_v1','accepted-v1',raw=True); nav.reload(wait_until='domcontentloaded'); nav.evaluate("showWorkspace('twin')"); nav.wait_for_timeout(100)
        # Native control semantics and keyboard activation.
        for i,(label,expected) in enumerate([('Stay literal','Mode: stay literal'),('Just ask me a question','Mode: one question only'),('Return to normal','Mode: normal')],1):
            btn=nav.get_by_role('button',name=label,exact=True).first
            add(f'C4-A11Y-N-{i:03d}',f'Navigator {label} is keyboard-focusable native button',btn.evaluate("e=>e.tagName==='BUTTON'&&!e.disabled&&e.tabIndex>=0"),btn.evaluate('e=>({tag:e.tagName,tabIndex:e.tabIndex})'))
            btn.focus(); nav.keyboard.press('Enter'); nav.wait_for_timeout(30)
            add(f'C4-A11Y-N-{i+3:03d}',f'Navigator {label} activates by Enter',nav.locator('#corrigibility-mode-label').inner_text().strip()==expected,nav.locator('#corrigibility-mode-label').inner_text().strip())
        add('C4-A11Y-N-007','Navigator has polite atomic screen-reader status region',nav.locator('#sr-status[aria-live="polite"][aria-atomic="true"]').count()==1,'#sr-status')
        nav.get_by_role('button',name='Stay literal',exact=True).first.focus(); nav.keyboard.press('Enter'); nav.wait_for_timeout(20)
        add('C4-A11Y-N-008','Navigator mode change is announced to aria-live status','stay literal' in nav.locator('#sr-status').inner_text().lower(),nav.locator('#sr-status').inner_text())

        # Response-level veto by keyboard.
        ls_set(nav,'navigator_twin_v2_chat',[{'id':'u1','role':'user','content':'The routine is working.','provenance':'USER_REPORTED','epistemicStatus':'user_report'},{'id':'a1','role':'assistant','content':'Maybe it works because you were avoiding decisions.','provenance':'AI_OUTPUT','epistemicStatus':'conversation_record'}]); nav.reload(wait_until='domcontentloaded'); nav.evaluate("showWorkspace('twin')"); nav.wait_for_timeout(80)
        rbtn=nav.locator("button[onclick*='rejectTwinInterpretation'][onclick*='a1']")
        rbtn.focus(); nav.keyboard.press('Enter'); nav.wait_for_timeout(30)
        chat=ls_get(nav,'navigator_twin_v2_chat',[]); target=next(x for x in chat if x.get('id')=='a1')
        add('C4-A11Y-N-009','Navigator response-level veto activates by keyboard',target.get('epistemicStatus')=='rejected',json.dumps(target))
        add('C4-A11Y-N-010','Navigator response rejection is announced','interpretation rejected' in nav.locator('#sr-status').inner_text().lower(),nav.locator('#sr-status').inner_text())

        # Pending Keep and Reject by keyboard.
        pending=[{'id':'p1','text':'seems to value protecting sleep','category':'meaning','confidence':.7,'sourceTurnIds':['u1'],'sourceKind':'test','provenance':'AI_INFERRED','storageClass':'PENDING_MEMORY','status':'pending','createdAt':'2026-08-12T17:00:00Z'}]
        ls_set(nav,'navigator_corrigibility_v1_pending_learnings',pending); ls_set(nav,'navigator_twin_v2_journal',[]); ls_set(nav,'navigator_twin_v2_coverage',{}); nav.reload(wait_until='domcontentloaded'); nav.evaluate("showWorkspace('twin')"); nav.wait_for_timeout(80)
        k=nav.get_by_role('button',name='Keep this',exact=True); k.focus(); nav.keyboard.press('Enter'); nav.wait_for_timeout(30)
        add('C4-A11Y-N-011','Navigator Pending Learning Keep activates by keyboard',len(ls_get(nav,'navigator_twin_v2_journal',[]))==1,json.dumps(ls_get(nav,'navigator_twin_v2_journal',[])))
        add('C4-A11Y-N-012','Navigator Keep confirmation is announced','kept' in nav.locator('#sr-status').inner_text().lower(),nav.locator('#sr-status').inner_text())
        pending=[{'id':'p2','text':'seems to value a hidden mechanism','category':'meaning','confidence':.7,'sourceTurnIds':['u1'],'sourceKind':'test','provenance':'AI_INFERRED','storageClass':'PENDING_MEMORY','status':'pending','createdAt':'2026-08-12T17:01:00Z'}]
        ls_set(nav,'navigator_corrigibility_v1_pending_learnings',pending); ls_set(nav,'navigator_twin_v2_chat',[]); nav.reload(wait_until='domcontentloaded'); nav.evaluate("showWorkspace('twin')"); nav.wait_for_timeout(60)
        rb=nav.locator("#pending-learning-panel button",has_text='Not what I meant'); rb.focus(); nav.keyboard.press('Enter'); nav.wait_for_timeout(30)
        after_pending=ls_get(nav,'navigator_corrigibility_v1_pending_learnings',[]); add('C4-A11Y-N-013','Navigator Pending Learning Reject activates by keyboard',len(after_pending)==0,json.dumps(after_pending))
        add('C4-A11Y-N-014','Navigator pending rejection is announced','rejected' in nav.locator('#sr-status').inner_text().lower(),nav.locator('#sr-status').inner_text())

        # Stop keyboard.
        nav.evaluate('localStorage.clear()'); ls_set(nav,'navigator_ai_processing_consent_v1','accepted-v1',raw=True); nav.reload(wait_until='domcontentloaded'); nav.evaluate("showWorkspace('twin')"); mock_fetch(nav,900)
        nav.locator('#chat-input').fill('Please test the stop control.'); nav.evaluate('()=>{sendToTwin(); return true}'); nav.wait_for_timeout(80)
        stop=nav.locator('#stop-twin-btn'); add('C4-A11Y-N-015','Navigator Stop becomes visible and focusable',stop.is_visible() and stop.evaluate('e=>e.tabIndex>=0'),'visible='+str(stop.is_visible()))
        stop.focus(); nav.keyboard.press('Enter'); nav.wait_for_timeout(1100)
        add('C4-A11Y-N-016','Navigator Stop activates by keyboard and blocks late output','C4 delayed mock response.' not in nav.locator('#chat-log').inner_text(),nav.locator('#chat-log').inner_text()[-180:])

        # Mobile target controls no horizontal overflow.
        nav.set_viewport_size({'width':390,'height':844}); nav.reload(wait_until='domcontentloaded'); nav.evaluate("showWorkspace('twin')"); nav.wait_for_timeout(50)
        ov=nav.evaluate("()=>({doc:[document.documentElement.scrollWidth,document.documentElement.clientWidth],ctrl:(()=>{const e=document.querySelector('.corrigibility-controls');return e?[e.scrollWidth,e.clientWidth]:null})()})")
        add('C4-A11Y-N-017','Navigator mobile viewport has no document horizontal overflow',ov['doc'][0] <= ov['doc'][1]+1,json.dumps(ov))

        # Examined
        ex=ctx.new_page(); ex.goto(EX,wait_until='domcontentloaded'); ex.evaluate("localStorage.setItem('examined_disclosure_v1','acknowledged')"); ex.reload(wait_until='domcontentloaded');
        ex.evaluate("()=>{state.workspace=true;document.getElementById('landing').style.display='none';document.getElementById('workspace').style.display='block';swTab('companion');renderExaminedCorrigibilityMode();}"); ex.wait_for_timeout(80)
        for i,(label,expected) in enumerate([('Stay literal','Mode: stay literal'),('Just ask me a question','Mode: one question only'),('Return to normal','Mode: normal')],1):
            btn=ex.get_by_role('button',name=label,exact=True).first
            add(f'C4-A11Y-E-{i:03d}',f'Examined {label} is keyboard-focusable native button',btn.evaluate("e=>e.tagName==='BUTTON'&&!e.disabled&&e.tabIndex>=0"),btn.evaluate('e=>({tag:e.tagName,tabIndex:e.tabIndex})'))
            btn.focus(); ex.keyboard.press('Enter'); ex.wait_for_timeout(25)
            add(f'C4-A11Y-E-{i+3:03d}',f'Examined {label} activates by Enter',ex.locator('#examined-corrigibility-mode-label').inner_text().strip()==expected,ex.locator('#examined-corrigibility-mode-label').inner_text().strip())
        # Explicit assistive-tech announcement check - expected to expose whether status is live.
        mode_live=ex.locator('#examined-corrigibility-mode-label').get_attribute('aria-live')
        add('C4-A11Y-E-007','Examined mode status is exposed as aria-live for screen readers',mode_live in ('polite','assertive'),str(mode_live))
        chat_live=ex.locator('#chat-messages').get_attribute('aria-live')
        add('C4-A11Y-E-008','Examined dynamic Companion chat is an aria-live region',chat_live in ('polite','assertive'),str(chat_live))

        # Response veto keyboard.
        ex.evaluate("()=>{state.chatHistory=[{id:'eu1',role:'user',content:'The routine is working.',provenance:'USER_REPORTED',epistemicStatus:'user_report'},{id:'ea1',role:'assistant',content:'Maybe you were avoiding decisions.',provenance:'AI_OUTPUT',epistemicStatus:'conversation_record'}];const box=document.getElementById('chat-messages');box.innerHTML='';appendMsg('user','The routine is working.','eu1');appendMsg('assistant','Maybe you were avoiding decisions.','ea1');saveState();}")
        ebtn=ex.locator("button[onclick*='rejectExaminedInterpretation'][onclick*='ea1']"); ebtn.focus(); ex.keyboard.press('Enter'); ex.wait_for_timeout(30)
        est=ex.evaluate("()=>state.chatHistory.find(x=>x.id==='ea1')")
        add('C4-A11Y-E-009','Examined response-level veto activates by keyboard',est.get('epistemicStatus')=='rejected',json.dumps(est))

        # Stop keyboard.
        ex.evaluate("()=>{state.chatHistory=[];saveState();const box=document.getElementById('chat-messages');box.innerHTML='';}"); mock_fetch(ex,900)
        ex.locator('#chat-input').fill('Please test the stop control.'); ex.evaluate('()=>{sendMessage(); return true}'); ex.wait_for_timeout(80)
        estop=ex.locator('#examined-stop-btn'); add('C4-A11Y-E-010','Examined Stop becomes visible and focusable',estop.is_visible() and estop.evaluate('e=>e.tabIndex>=0'),'visible='+str(estop.is_visible()))
        estop.focus(); ex.keyboard.press('Enter'); ex.wait_for_timeout(1100)
        add('C4-A11Y-E-011','Examined Stop activates by keyboard and blocks late output','C4 delayed mock response.' not in ex.locator('#chat-messages').inner_text(),ex.locator('#chat-messages').inner_text()[-180:])

        # Mobile overflow.
        ex.set_viewport_size({'width':390,'height':844}); ex.reload(wait_until='domcontentloaded'); ex.evaluate("()=>{state.workspace=true;document.getElementById('landing').style.display='none';document.getElementById('workspace').style.display='block';swTab('companion');}"); ex.wait_for_timeout(50)
        ov2=ex.evaluate("()=>({doc:[document.documentElement.scrollWidth,document.documentElement.clientWidth],ctrl:(()=>{const e=document.querySelector('.corrigibility-controls');return e?[e.scrollWidth,e.clientWidth]:null})()})")
        add('C4-A11Y-E-012','Examined mobile viewport has no document horizontal overflow',ov2['doc'][0] <= ov2['doc'][1]+1,json.dumps(ov2))

        browser.close()
finally:
    server.terminate();
    try: server.wait(timeout=3)
    except Exception: server.kill()

summary={'build':'CORRIGIBILITY-4','scope':'local Chromium keyboard/accessibility-structure audit on exact C2 candidates','total':len(results),'pass':sum(r['status']=='PASS' for r in results),'fail':sum(r['status']=='FAIL' for r in results),'results':results}
(E/'CORRIGIBILITY-4_LOCAL_KEYBOARD_A11Y_RESULTS.json').write_text(json.dumps(summary,indent=2)+'\n')
with (E/'CORRIGIBILITY-4_LOCAL_KEYBOARD_A11Y_RESULTS.txt').open('w') as f:
    f.write(f"CORRIGIBILITY-4 LOCAL KEYBOARD / A11Y STRUCTURE\nPASS {summary['pass']}/{summary['total']} | FAIL {summary['fail']}\n\n")
    for r in results:f.write(f"{r['id']}. {r['status']} — {r['name']} — {r['evidence']}\n")
print(json.dumps({k:summary[k] for k in ['total','pass','fail']},indent=2))
raise SystemExit(0 if summary['fail']==0 else 2)
