#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
from pathlib import Path
import subprocess,time,socket,json,os,sys
HERE=Path(__file__).resolve().parent
ROOT=Path(os.environ.get('C4_STAGING_ROOT',str(HERE.parent/'staging')))
OUT=Path(os.environ.get('C4_OUTPUT_DIR',str(HERE.parent/'cross_output'))); OUT.mkdir(parents=True,exist_ok=True)
PORT=int(os.environ.get('C4_CROSS_PORT','8895')); BASE=f'http://127.0.0.1:{PORT}'
NAV=f'{BASE}/SPC-FALL-2026-Navigator-main/index.html'; EX=f'{BASE}/Examined-main/index.html'
BROWSERS=[x.strip() for x in os.environ.get('C4_BROWSERS','chromium,firefox,webkit').split(',') if x.strip()]
results=[]
def add(browser,tid,name,ok,e=''):
    results.append({'browser':browser,'id':tid,'name':name,'status':'PASS' if ok else 'FAIL','evidence':str(e)})
    print(f"{browser} {tid} {'PASS' if ok else 'FAIL'} — {name}"+(f" — {e}" if e else ''))

def wait_server():
    for _ in range(80):
        try:
            with socket.create_connection(('127.0.0.1',PORT),timeout=.2): return True
        except Exception: time.sleep(.1)
    return False
def setj(page,k,v): page.evaluate("([k,v])=>localStorage.setItem(k,JSON.stringify(v))",[k,v])
def getj(page,k,d=None): return page.evaluate("([k,d])=>{const s=localStorage.getItem(k);if(s===null)return d;try{return JSON.parse(s)}catch(e){return s}}",[k,d])
def open_twin(page,page_errors,stage):
    page.wait_for_timeout(100)
    if page_errors:
        print(f"NAV_PAGE_ERRORS {stage}: {json.dumps(page_errors[-5:])}")
    try:
        page.wait_for_function("()=>typeof window.showWorkspace==='function'",timeout=3000)
    except Exception:
        print(f"NAV_READY_FAIL {stage}: {json.dumps(page_errors[-10:])}")
        try:
            print("NAV_READY_STATE",page.evaluate("()=>({href:location.href,ready:document.readyState,showWorkspace:typeof window.showWorkspace})"))
        except Exception as e:
            print("NAV_READY_STATE_ERROR",repr(e))
        raise
    page.evaluate("showWorkspace('twin')")
def route_mock(route,request):
    if request.method=='OPTIONS':
        return route.fulfill(status=204,headers={'Access-Control-Allow-Origin':'*','Access-Control-Allow-Headers':'Content-Type','Access-Control-Allow-Methods':'POST, OPTIONS'},body='')
    body={}
    try: body=request.post_data_json or {}
    except Exception: pass
    sys_txt=str(body.get('system',''))
    if 'extract one brief learning' in sys_txt:
        text='{"journalEntry":"seems to value protecting rest","category":"meaning","confidence":0.7}'
    else: text='C4 delayed cross-browser mock response.'
    # Delay ordinary dialogue so Stop can be tested.
    if 'extract one brief learning' not in sys_txt: time.sleep(.45)
    payload={'response':text,'reply':text,'content':[{'type':'text','text':text}],'stop_reason':'end_turn'}
    route.fulfill(status=200,content_type='application/json',headers={'Access-Control-Allow-Origin':'*'},body=json.dumps(payload))
server=subprocess.Popen(['python','-m','http.server',str(PORT),'--bind','127.0.0.1'],cwd=ROOT,stdout=(OUT/'http_server.log').open('w'),stderr=subprocess.STDOUT)
try:
    if not wait_server():raise RuntimeError('server failed')
    with sync_playwright() as p:
        for bname in BROWSERS:
            bt=getattr(p,bname)
            kw={'headless':True}
            if bname=='chromium':
                exe=os.environ.get('C4_CHROMIUM_EXECUTABLE','')
                if exe: kw.update({'executable_path':exe,'args':['--no-sandbox']})
            browser=bt.launch(**kw)
            ctx=browser.new_context(viewport={'width':1280,'height':820},service_workers='block')
            ctx.route('**/api/claude-proxy',route_mock)
            # NAV load
            page_errors=[]; nav=ctx.new_page(); nav.on('pageerror',lambda e:page_errors.append(str(e)))
            r=nav.goto(NAV,wait_until='domcontentloaded',timeout=30000); nav.evaluate("localStorage.clear();localStorage.setItem('navigator_ai_processing_consent_v1','accepted-v1')"); nav.reload(wait_until='domcontentloaded'); open_twin(nav,page_errors,'initial'); nav.wait_for_timeout(60)
            add(bname,'CB-01','Navigator loads with expected identity',bool(r and r.ok) and nav.locator('meta[name="navigator-build"]').get_attribute('content')=='navigator-fall-2026-corrigibility-2-prototype',nav.title())
            add(bname,'CB-02','Navigator has no page errors',not page_errors,json.dumps(page_errors[:3]))
            btn=nav.get_by_role('button',name='Stay literal',exact=True).first; btn.focus(); nav.keyboard.press('Enter');
            add(bname,'CB-03','Navigator mode changes by keyboard',nav.locator('#corrigibility-mode-label').inner_text().strip()=='Mode: stay literal',nav.locator('#sr-status').inner_text())
            # veto
            setj(nav,'navigator_twin_v2_chat',[{'id':'u','role':'user','content':'It works.','provenance':'USER_REPORTED','epistemicStatus':'user_report'},{'id':'a','role':'assistant','content':'Hidden mechanism.','provenance':'AI_OUTPUT','epistemicStatus':'conversation_record'}]); nav.reload(wait_until='domcontentloaded'); open_twin(nav,page_errors,'veto'); nav.locator("button[onclick*='rejectTwinInterpretation'][onclick*='a']").focus(); nav.keyboard.press('Enter'); nav.wait_for_timeout(20)
            target=next(x for x in getj(nav,'navigator_twin_v2_chat',[]) if x.get('id')=='a'); add(bname,'CB-04','Navigator response veto works by keyboard',target.get('epistemicStatus')=='rejected',json.dumps(target))
            # pending keep/reject
            setj(nav,'navigator_corrigibility_v1_pending_learnings',[{'id':'p','text':'seems to value rest','category':'meaning','confidence':.7,'sourceTurnIds':['u'],'provenance':'AI_INFERRED','storageClass':'PENDING_MEMORY','status':'pending'}]); setj(nav,'navigator_twin_v2_journal',[]); nav.reload(wait_until='domcontentloaded'); open_twin(nav,page_errors,'pending-keep'); nav.get_by_role('button',name='Keep this',exact=True).focus(); nav.keyboard.press('Enter'); nav.wait_for_function("()=>{try{return JSON.parse(localStorage.getItem('navigator_twin_v2_journal')||'[]').length===1}catch(e){return false}}",timeout=2000)
            add(bname,'CB-05','Navigator pending memory Keep works by keyboard',len(getj(nav,'navigator_twin_v2_journal',[]))==1,'journal='+str(len(getj(nav,'navigator_twin_v2_journal',[]))))
            setj(nav,'navigator_corrigibility_v1_pending_learnings',[{'id':'p2','text':'seems to value a hidden mechanism','category':'meaning','confidence':.7,'sourceTurnIds':['u'],'provenance':'AI_INFERRED','storageClass':'PENDING_MEMORY','status':'pending'}]); setj(nav,'navigator_twin_v2_chat',[]); nav.reload(wait_until='domcontentloaded'); open_twin(nav,page_errors,'pending-reject'); nav.locator('#pending-learning-panel button',has_text='Not what I meant').focus(); nav.keyboard.press('Enter'); nav.wait_for_timeout(20)
            add(bname,'CB-06','Navigator pending memory Reject works by keyboard',len(getj(nav,'navigator_corrigibility_v1_pending_learnings',[]))==0,nav.locator('#sr-status').inner_text())
            # stop
            nav.evaluate("localStorage.clear();localStorage.setItem('navigator_ai_processing_consent_v1','accepted-v1')"); nav.reload(wait_until='domcontentloaded'); open_twin(nav,page_errors,'stop'); nav.evaluate("()=>{window.fetch=async()=>{await new Promise(r=>setTimeout(r,900));const t='C4 delayed cross-browser mock response.';return new Response(JSON.stringify({response:t,reply:t,content:[{type:'text',text:t}],stop_reason:'end_turn'}),{status:200,headers:{'Content-Type':'application/json'}})}}"); nav.locator('#chat-input').fill('Test delayed response.'); nav.evaluate('()=>{sendToTwin();return true}'); nav.wait_for_timeout(60); st=nav.locator('#stop-twin-btn'); vis=st.is_visible();
            if vis: st.focus(); nav.keyboard.press('Enter')
            nav.wait_for_timeout(650); add(bname,'CB-07','Navigator Stop blocks delayed persistence',vis and 'C4 delayed cross-browser mock response.' not in nav.locator('#chat-log').inner_text(),nav.locator('#chat-log').inner_text()[-120:])
            # EX
            ex_errors=[]; ex=ctx.new_page(); ex.on('pageerror',lambda e:ex_errors.append(str(e))); r2=ex.goto(EX,wait_until='domcontentloaded'); ex.evaluate("localStorage.setItem('examined_disclosure_v1','acknowledged')"); ex.reload(wait_until='domcontentloaded'); ex.evaluate("()=>{state.workspace=true;document.getElementById('landing').style.display='none';document.getElementById('workspace').style.display='block';swTab('companion');}"); ex.wait_for_timeout(50)
            add(bname,'CB-08','Examined loads with C4 accessibility candidate identity',bool(r2 and r2.ok) and ex.locator('meta[name="examined-build"]').get_attribute('content')=='examined-fall-2026-corrigibility-4-a11y-candidate',ex.title())
            add(bname,'CB-09','Examined has no page errors',not ex_errors,json.dumps(ex_errors[:3]))
            eb=ex.get_by_role('button',name='Stay literal',exact=True).first; eb.focus(); ex.keyboard.press('Enter'); add(bname,'CB-10','Examined mode keyboard activation and live-status exposure',ex.locator('#examined-corrigibility-mode-label').inner_text().strip()=='Mode: stay literal' and ex.locator('#examined-corrigibility-mode-label').get_attribute('aria-live')=='polite',ex.locator('#examined-corrigibility-mode-label').inner_text())
            ex.evaluate("()=>{state.chatHistory=[{id:'u',role:'user',content:'It works.','provenance':'USER_REPORTED','epistemicStatus':'user_report'},{id:'a',role:'assistant',content:'Hidden mechanism.','provenance':'AI_OUTPUT','epistemicStatus':'conversation_record'}];const b=document.getElementById('chat-messages');b.innerHTML='';appendMsg('user','It works.','u');appendMsg('assistant','Hidden mechanism.','a');saveState();}"); ex.locator("button[onclick*='rejectExaminedInterpretation'][onclick*='a']").focus(); ex.keyboard.press('Enter'); ex.wait_for_timeout(20); et=ex.evaluate("()=>state.chatHistory.find(x=>x.id==='a')")
            add(bname,'CB-11','Examined response veto works by keyboard',et.get('epistemicStatus')=='rejected',json.dumps(et))
            ex.evaluate("()=>{state.chatHistory=[];saveState();document.getElementById('chat-messages').innerHTML='';window.fetch=async()=>{await new Promise(r=>setTimeout(r,900));const t='C4 delayed cross-browser mock response.';return new Response(JSON.stringify({response:t,reply:t,content:[{type:'text',text:t}],stop_reason:'end_turn'}),{status:200,headers:{'Content-Type':'application/json'}})}}"); ex.locator('#chat-input').fill('Test delayed response.'); ex.evaluate('()=>{sendMessage();return true}'); ex.wait_for_timeout(60); est=ex.locator('#examined-stop-btn'); evis=est.is_visible();
            if evis: est.focus(); ex.keyboard.press('Enter')
            ex.wait_for_timeout(650); add(bname,'CB-12','Examined Stop blocks delayed persistence',evis and 'C4 delayed cross-browser mock response.' not in ex.locator('#chat-messages').inner_text(),ex.locator('#chat-messages').inner_text()[-120:])
            browser.close()
finally:
    server.terminate()
    try:server.wait(timeout=3)
    except Exception:server.kill()
summary={'build':'CORRIGIBILITY-4','browsers':BROWSERS,'total':len(results),'pass':sum(r['status']=='PASS' for r in results),'fail':sum(r['status']=='FAIL' for r in results),'results':results}
(OUT/'CORRIGIBILITY-4_CROSS_BROWSER_RESULTS.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ['browsers','total','pass','fail']},indent=2))
raise SystemExit(0 if summary['fail']==0 else 2)
