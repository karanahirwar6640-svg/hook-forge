import os,json,re,requests
from flask import Flask,render_template_string,request,jsonify

app=Flask(__name__)
SAMBANOVA_API_KEY=os.environ.get("SAMBANOVA_API_KEY")
SAMBANOVA_URL="https://api.sambanova.ai/v1/chat/completions"

HOOK_SYSTEM_PROMPT="""
You are Hook Forge v2.0, an elite 9-figure direct-response copywriter and behavioral psychologist. 
Your singular goal is to craft hooks that paralyze the user's thumb and force them to watch. You despise polite, boring "AI-sounding" text.
STRICT RULES:
1. NO AI-SPEAK: Never use words like "Unlock", "Delve", "Discover", "Elevate", "In today's world", "Embark", "Hey guys". If you use these, you fail.
2. BE HUMAN & RUTHLESS: Write like a slightly aggressive, highly authoritative expert speaking directly to a friend. Start mid-thought.
3. PSYCHOLOGICAL TRIGGERS: Use 'The Curiosity Gap', 'Fear of Missing Out (FOMO)', 'Contrarian Truths', or 'Negativity Bias'.
4. EXTREME BREVITY: Keep hooks under 15 words. Punchy. Visceral.
The user will provide: Topic, Niche, Audience, and Tone.
You must output exactly this JSON structure:
{
  "hook_a": { "text": "High-tension hook text", "score": 95, "reasoning": "Actionable tactical fix", "psychology": "Deep psychological breakdown" },
  "hook_b": { "text": "Contrarian hook text", "score": 98, "reasoning": "Actionable tactical fix", "psychology": "Deep psychological breakdown" },
  "dna_comparison": "Direct ruthless comparison of Hook A vs Hook B."
}
"""

SCRIPT_SYSTEM_PROMPT="""
You are Script Forge, an elite 9-figure Short-Form Content Strategist and Behavioral Psychologist. 
Your only objective is to maximize AUDIENCE RETENTION. You transform weak, boring inputs into highly aggressive, fast-paced, and dopamine-driven viral scripts.
YOUR TRAINING & CONDITIONING:
❌ THE BANNED "AI" DICTIONARY: "Unlock", "Delve", "Discover", "Crucial", "Game-changer", "Hey guys". 
✅ THE "RETENTION" RULES:
1. THE 3-SECOND RULE: Trigger an immediate emotional response. 
2. EXTREME BREVITY: No sentence longer than 12 words. Cut adjectives. 
3. CONVERSATIONAL TONE: Write exactly how a fast-talking YouTuber speaks.
YOUR TASK:
Rewrite the user's raw script. Output strictly in JSON format:
{
  "retention_score": 98,
  "hook_extracted": "The explosive 1-2 sentence hook",
  "master_script": "The FULL upgraded, fast-paced script",
  "psychology_breakdown": "Explain exactly which psychological triggers you used"
}
"""

HTML_PART_1="""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Hook Forge</title><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Noto+Sans+JP:wght@400;700&family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>
body{margin:0;min-height:100vh;font-family:'Noto Sans JP',sans-serif;background:#000;color:#fef3c7;display:flex;align-items:center;justify-content:center;flex-direction:column;overflow-x:hidden;transition:all .6s cubic-bezier(.4,0,.2,1);perspective:1500px}
.bg-vid{position:fixed;top:0;left:0;width:100%;height:100%;object-fit:cover;z-index:0;pointer-events:none;transition:opacity .3s,transform .5s;transform-origin:center}
.v-anim{opacity:0!important;transform:scale(1.05)}
.v-over{position:fixed;inset:0;background:rgba(0,0,0,.05);z-index:1;pointer-events:none}
.gl-pan{background:rgba(0,0,0,.65);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid rgba(255,50,50,.4);border-radius:24px;box-shadow:0 40px 80px rgba(0,0,0,.95);transition:all .6s cubic-bezier(.4,0,.2,1);transform-style:preserve-3d;will-change:transform}
.a-title{font-family:'Cinzel',serif;text-shadow:0 0 30px #ff1414;transition:all .5s}
.c-in{background:rgba(0,0,0,.7);border:1px solid rgba(220,38,38,.35);color:#fef3c7;transition:all .3s}
.c-in:focus{outline:0;border-color:#ef4444;box-shadow:0 0 20px rgba(239,68,68,.4)}
.c-btn{position:relative;overflow:hidden;background:linear-gradient(45deg,#7f1d1d,#dc2626);border:1px solid #ef4444;box-shadow:0 0 20px rgba(220,38,38,.5);transition:all .3s}
.c-btn:hover{background:linear-gradient(45deg,#991b1b,#f87171);box-shadow:0 0 30px rgba(220,38,38,.8);transform:translateY(-2px)}
.sw{position:absolute;background:rgba(255,255,255,.6);border-radius:50%;transform:scale(0);animation:rp .6s linear;pointer-events:none}
@keyframes rp{to{transform:scale(4);opacity:0}}
@keyframes sl{0%{transform:scale(1);text-shadow:0 0 10px rgba(245,158,11,.5)}50%{transform:scale(1.4);text-shadow:0 0 40px #f59e0b;color:#fff}100%{transform:scale(1);text-shadow:0 0 15px rgba(245,158,11,.8)}}
.s-anim{animation:sl .5s ease-out}
.a-btn{position:fixed;bottom:20px;right:20px;z-index:100;background:rgba(0,0,0,.6);padding:12px;border-radius:50%;border:1px solid rgba(255,50,50,.4);color:#ef4444;transition:all .3s}
.t-btn{padding:10px 20px;font-size:10px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;border-radius:8px;transition:all .3s}
.t-act{background:rgba(220,38,38,.2);border:1px solid #ef4444;color:#fef3c7;box-shadow:0 0 15px rgba(220,38,38,.4)}
.t-in{background:rgba(0,0,0,.5);border:1px solid rgba(255,50,50,.2);color:rgba(254,243,199,.5)}
body.t-a1 .gl-pan{border-color:rgba(50,150,255,.5)} body.t-a1 .a-title,body.t-a1 .text-red-400,body.t-a1 .text-red-500{color:#60a5fa!important;text-shadow:0 0 30px rgba(50,150,255,.8)} body.t-a1 .c-btn{background:linear-gradient(45deg,#1e3a8a,#2563eb);border-color:#3b82f6;box-shadow:0 0 20px rgba(59,130,246,.5)} body.t-a1 .t-act{background:rgba(59,130,246,.2);border-color:#3b82f6;box-shadow:0 0 15px rgba(59,130,246,.4)} body.t-a1 #m-btn{border-color:#3b82f6;color:#3b82f6;box-shadow:0 0 15px rgba(59,130,246,.5)}
body.t-a2 .gl-pan{border-color:rgba(168,85,247,.5)} body.t-a2 .a-title,body.t-a2 .text-red-400,body.t-a2 .text-red-500{color:#c084fc!important;text-shadow:0 0 30px rgba(168,85,247,.8)} body.t-a2 .c-btn{background:linear-gradient(45deg,#581c87,#9333ea);border-color:#a855f7;box-shadow:0 0 20px rgba(168,85,247,.5)} body.t-a2 .t-act{background:rgba(168,85,247,.2);border-color:#a855f7;box-shadow:0 0 15px rgba(168,85,247,.4)} body.t-a2 #m-btn{border-color:#a855f7;color:#a855f7;box-shadow:0 0 15px rgba(168,85,247,.5)}
body.t-lux{background:#050505;color:#fff;font-family:'Inter',sans-serif} body.t-lux .gl-pan{background:#0a0a0a!important;backdrop-filter:none!important;border:1px solid rgba(255,255,255,.1)!important;box-shadow:0 20px 50px #000!important} body.t-lux .a-title{font-family:'Inter',sans-serif!important;font-weight:800!important;letter-spacing:.05em!important;text-shadow:0 0 20px rgba(255,255,255,.2)!important;color:#fff!important} body.t-lux .c-in{background:#111!important;border:1px solid rgba(255,255,255,.15)!important;color:#fff!important} body.t-lux .c-in:focus{border-color:#fff!important} body.t-lux .c-btn{background:#fff!important;border:none!important;color:#000!important;font-weight:800!important;box-shadow:0 4px 15px rgba(255,255,255,.2)!important} body.t-lux .c-btn:hover{background:#e5e5e5!important;box-shadow:0 6px 20px rgba(255,255,255,.4)!important} body.t-lux .t-act{background:#fff!important;border:none!important;color:#000!important} body.t-lux .t-in{border:1px solid rgba(255,255,255,.1)!important;color:#888!important} body.t-lux .bg-vid{opacity:0!important;visibility:hidden} body.t-lux .v-over{background:0 0!important} body.t-lux .text-red-400,body.t-lux .text-amber-400,body.t-lux .text-red-500{color:#fff!important} body.t-lux .border-red-500\\/20,body.t-lux .border-amber-500\\/20{border-color:rgba(255,255,255,.1)!important;background:#111!important} body.t-lux #m-btn{opacity:0;pointer-events:none}
.m-txt{white-space:pre-line;word-break:break-word}
</style></head><body class="p-4">
"""
HTML_PART_2="""<video id="bg-v" autoplay muted loop playsinline class="bg-vid"><source src="https://subczjjxgexeraofhykl.supabase.co/storage/v1/object/public/Assets/From%20Klickpin.com-%20Natural%20Makeup%20Looks%20Inspiration%20for%20Summer-pin-id-587860557652168444.mp4" type="video/mp4"></video><div class="v-over"></div>
<button onclick="tLux(event)" id="t-btn" class="fixed top-5 right-5 md:top-8 md:right-8 z-[100] bg-black/60 p-4 rounded-full border border-yellow-500/50 text-yellow-500 shadow-[0_0_15px_rgba(212,175,55,.4)] transition-all hover:scale-110 overflow-hidden"><i id="t-ico" class="fa-solid fa-crown text-xl"></i></button>
<button onclick="cAura(event)" id="m-btn" class="fixed bottom-8 left-1/2 transform -translate-x-1/2 z-[100] bg-black/60 p-4 rounded-full border border-red-500 text-red-500 shadow-[0_0_15px_rgba(255,0,0,.5)] transition-all hover:scale-110 overflow-hidden"><i class="fa-solid fa-infinity text-2xl"></i></button>
<button onclick="tAud()" class="a-btn shadow-lg hover:scale-110"><i id="a-ico" class="fa-solid fa-volume-xmark text-lg"></i></button>
<div id="dash" class="w-full max-w-6xl flex-col relative z-10 flex mt-4 md:mt-0">
<div class="w-full flex flex-col md:flex-row justify-between items-center mb-6 px-4"><div class="text-center md:text-left mb-4 md:mb-0"><h1 class="a-title text-3xl md:text-4xl font-black text-red-500 mb-1" id="m-tit">HOOK FORGE</h1><p class="text-[9px] tracking-[0.4em] text-red-300 uppercase"><i class="fa-solid fa-user-shield mr-1"></i> <span>Founder</span></p></div><div class="flex space-x-3 bg-black/40 p-1.5 rounded-xl border border-red-900/50 backdrop-blur-sm"><button id="tb-h" onclick="sMod('h')" class="t-btn t-act"><i class="fa-solid fa-fire mr-1"></i> Hook Forge</button><button id="tb-s" onclick="sMod('s')" class="t-btn t-in"><i class="fa-solid fa-scroll mr-1"></i> Script Forge</button></div></div>
<div id="err" class="hidden bg-red-900/80 border border-red-500 text-white p-3 rounded mb-4 text-xs font-mono w-full"></div>
<div class="flex flex-col lg:flex-row gap-6 w-full items-stretch">
<div class="gl-pan plx w-full lg:max-w-md p-6 flex flex-col justify-between">
<div id="in-h" class="space-y-4">
<div><label class="block text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1">Niche</label><input type="text" id="h-n" value="Anime & Tech" class="w-full c-in rounded-lg px-4 py-3 text-sm"></div>
<div><label class="block text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1">Audience</label><input type="text" id="h-a" value="Creators" class="w-full c-in rounded-lg px-4 py-3 text-sm"></div>
<div><label class="block text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1">Tone Matrix</label><select id="h-t" class="w-full c-in rounded-lg px-4 py-3 text-sm"><option value="Curious">Curiosity Gap</option><option value="Aggressive">Brutally Honest</option></select></div>
<div><label class="block text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1">Topic</label><textarea id="h-top" rows="3" class="w-full c-in rounded-lg px-4 py-3 text-sm resize-none" placeholder="Enter core concept..."></textarea></div>
</div>
<div id="in-s" class="hidden space-y-4 flex-grow flex flex-col">
<p class="text-[10px] tracking-widest text-red-300/80 uppercase border-b border-red-900/50 pb-2 mb-2">Transform raw script into viral content.</p>
<div><label class="block text-[10px] font-bold tracking-widest uppercase text-red-500 mb-1"><i class="fa-solid fa-crosshairs mr-1"></i> Target URL</label><input type="url" id="s-u" class="w-full c-in rounded-lg px-4 py-3 text-sm mb-2" placeholder="Paste link..."></div>
<div class="flex-grow flex flex-col"><label class="block text-[10px] font-bold tracking-widest uppercase text-amber-400 mb-1"><i class="fa-solid fa-code mr-1"></i> Raw Script</label><textarea id="s-r" class="w-full flex-grow min-h-[250px] c-in rounded-lg px-4 py-3 text-sm resize-none" placeholder="Paste script..."></textarea></div>
</div>
<button onclick="cSw(event);ig();" id="b-ig" class="w-full c-btn py-4 rounded-lg font-bold tracking-widest uppercase text-xs mt-6 overflow-hidden"><i class="fa-solid fa-fire mr-2"></i> Ignite Engine</button>
</div>
<div class="gl-pan plx flex-grow p-6 flex flex-col justify-center min-h-[500px]">
<div id="ld" class="hidden text-center"><i class="fa-solid fa-spinner fa-spin text-5xl text-red-500 mb-4 drop-shadow-[0_0_15px_rgba(220,38,38,.8)]"></i><h2 class="a-title text-2xl text-red-100">Extracting Matrix...</h2></div>
<div id="emp" class="text-center opacity-50"><i class="fa-solid fa-crosshairs text-6xl text-red-500/50 mb-4" id="e-ico"></i><p class="text-xs font-mono tracking-widest uppercase">Awaiting Parameters...</p></div>
<div id="res-h" class="hidden space-y-5 overflow-y-auto max-h-[620px] pr-2">
<div class="bg-black/40 border border-red-500/20 p-5 rounded-xl"><div class="flex justify-between items-center mb-3"><span class="text-[10px] bg-red-950/80 text-red-300 border border-red-800 px-2 py-0.5 rounded font-bold uppercase tracking-wider">Option A</span><span class="text-[10px] text-red-400 font-black tracking-widest">SCORE: <span id="scA" class="text-red-500 text-base"></span></span></div><h3 id="txA" class="m-txt text-base md:text-lg font-bold text-amber-50 mb-3 tracking-wide"></h3><button onclick="cp('txA')" class="mt-3 text-[10px] uppercase tracking-widest text-red-400 hover:text-white"><i class="fa-regular fa-copy mr-1"></i> Copy</button></div>
<div class="bg-black/40 border border-amber-500/20 p-5 rounded-xl"><div class="flex justify-between items-center mb-3"><span class="text-[10px] bg-amber-950/80 text-amber-300 border border-amber-800 px-2 py-0.5 rounded font-bold uppercase tracking-wider">Option B</span><span class="text-[10px] text-amber-400 font-black tracking-widest">SCORE: <span id="scB" class="text-amber-500 text-base"></span></span></div><h3 id="txB" class="m-txt text-base md:text-lg font-bold text-amber-50 mb-3 tracking-wide"></h3><button onclick="cp('txB')" class="mt-3 text-[10px] uppercase tracking-widest text-amber-400 hover:text-white"><i class="fa-regular fa-copy mr-1"></i> Copy</button></div>
</div>
<div id="res-s" class="hidden space-y-5 overflow-y-auto max-h-[620px] pr-2">
<div class="bg-black/40 border border-red-500/20 p-5 rounded-xl flex justify-between items-center"><div><h3 class="text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1">Retention Score</h3></div><div class="text-4xl font-black text-amber-500 drop-shadow-[0_0_10px_rgba(245,158,11,.5)]"><span id="ss" class="inline-block">0</span><span class="text-lg text-amber-500/50">/100</span></div></div>
<div class="bg-black/40 border border-red-500/20 p-5 rounded-xl relative"><span class="text-[10px] bg-red-950/80 text-red-300 border border-red-800 px-2 py-0.5 rounded font-bold uppercase tracking-wider mb-3 inline-block">Master Script</span><p id="sm" class="m-txt text-sm text-amber-50 leading-relaxed font-mono whitespace-pre-line"></p><button onclick="cp('sm')" class="mt-4 text-[10px] uppercase tracking-widest text-red-400 hover:text-white"><i class="fa-regular fa-copy mr-1"></i> Copy Script</button></div>
</div>
</div></div></div>
<script>
const $=(i)=>document.getElementById(i);
let cM='h', mut=1, lux=0, cA=0;
const vs=["https://subczjjxgexeraofhykl.supabase.co/storage/v1/object/public/Assets/From%20Klickpin.com-%20Natural%20Makeup%20Looks%20Inspiration%20for%20Summer-pin-id-587860557652168444.mp4","https://subczjjxgexeraofhykl.supabase.co/storage/v1/object/public/Assets/your_name.mp4","https://subczjjxgexeraofhykl.supabase.co/storage/v1/object/public/Assets/From%20Klickpin.com-%20From%20beginner%20to%20obsessed%20Love%20these%20easy%20pet-friendly%20home%20ideas%20youll%20want%20to%20recreate%20this%20weekend%20that%20balance%20trend%20comfor%20(1).mp4"];
document.querySelectorAll('.plx').forEach(p=>{
p.addEventListener('mousemove',e=>{if(window.innerWidth<768)return;let r=p.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top,cx=r.width/2,cy=r.height/2;p.style.transform=`perspective(1000px) rotateX(${((y-cy)/cy)*-4}deg) rotateY(${((x-cx)/cx)*4}deg)`;});
p.addEventListener('mouseleave',()=>{if(window.innerWidth>=768)p.style.transform='perspective(1000px) rotateX(0) rotateY(0)';});});
function mDec(id,t){let e=$(id),c='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*<>?',i=0,m=25,int=setInterval(()=>{e.innerText=t.split('').map((ch,idx)=>{if(idx<(i/m)*t.length)return ch;if(ch===' '||ch==='\\n')return ch;return c[Math.floor(Math.random()*c.length)];}).join('');if(++i>=m){clearInterval(int);e.innerText=t;}},30);}
function cSw(e){let b=e.currentTarget,c=document.createElement('span'),d=Math.max(b.clientWidth,b.clientHeight),r=d/2;c.style.cssText=`width:${d}px;height:${d}px;left:${e.clientX-b.getBoundingClientRect().left-r}px;top:${e.clientY-b.getBoundingClientRect().top-r}px`;c.className='sw';let o=b.querySelector('.sw');if(o)o.remove();b.appendChild(c);}
function aSc(t){let e=$('ss');e.classList.remove('s-anim');let s=0,d=1200,st=null;function f(tm){if(!st)st=tm;let p=Math.min((tm-st)/d,1);e.innerText=Math.floor(p*(t-s)+s);if(p<1)requestAnimationFrame(f);else{e.innerText=t;e.classList.add('s-anim');}}requestAnimationFrame(f);}
function pW(cb){let v=$('bg-v');v.classList.add('v-anim');setTimeout(()=>{cb();setTimeout(()=>v.classList.remove('v-anim'),100);},300);}
function cAura(e){if(lux)return;cSw(e);cA=(cA+1)%vs.length;pW(()=>{let v=$('bg-v');v.src=vs[cA];v.play();document.body.className='p-4';let b=$('m-btn');if(cA===1){document.body.classList.add('t-a1');b.className='fixed bottom-8 left-1/2 transform -translate-x-1/2 z-[100] bg-black/60 p-4 rounded-full border border-blue-500 text-blue-500 shadow-[0_0_15px_rgba(59,130,246,.5)] transition-all hover:scale-110 overflow-hidden';}else if(cA===2){document.body.classList.add('t-a2');b.className='fixed bottom-8 left-1/2 transform -translate-x-1/2 z-[100] bg-black/60 p-4 rounded-full border border-purple-500 text-purple-500 shadow-[0_0_15px_rgba(168,85,247,.5)] transition-all hover:scale-110 overflow-hidden';}else b.className='fixed bottom-8 left-1/2 transform -translate-x-1/2 z-[100] bg-black/60 p-4 rounded-full border border-red-500 text-red-500 shadow-[0_0_15px_rgba(255,0,0,.5)] transition-all hover:scale-110 overflow-hidden';});}
function tLux(e){cSw(e);pW(()=>{lux=!lux;document.body.className='p-4';if(lux){document.body.classList.add('t-lux');$('t-ico').className='fa-solid fa-eye text-xl';$('t-btn').className='fixed top-5 right-5 md:top-8 md:right-8 z-[100] bg-black/60 p-4 rounded-full border border-white/50 text-white shadow-[0_0_15px_rgba(255,255,255,.4)] transition-all hover:scale-110 overflow-hidden';$('e-ico').className='fa-solid fa-crosshairs text-6xl text-white/50 mb-4';}else{$('t-ico').className='fa-solid fa-crown text-xl';$('t-btn').className='fixed top-5 right-5 md:top-8 md:right-8 z-[100] bg-black/60 p-4 rounded-full border border-yellow-500/50 text-yellow-500 shadow-[0_0_15px_rgba(212,175,55,.4)] transition-all hover:scale-110 overflow-hidden';$('e-ico').className='fa-solid fa-crosshairs text-6xl text-red-500/50 mb-4';cAura({currentTarget:$('m-btn'),clientX:0,clientY:0});}});}
function tAud(){mut=!mut;$('bg-v').muted=mut;$('a-ico').className=mut?'fa-solid fa-volume-xmark text-lg':'fa-solid fa-volume-high text-lg';}
function sMod(m){cM=m;$('tb-h').className=m==='h'?'t-btn t-act':'t-btn t-in';$('tb-s').className=m==='s'?'t-btn t-act':'t-btn t-in';$('in-h').style.display=m==='h'?'block':'none';$('in-s').style.display=m==='s'?'flex':'none';$('b-ig').innerHTML=m==='h'?'<i class="fa-solid fa-fire mr-2"></i> Ignite Engine':'<i class="fa-solid fa-scroll mr-2"></i> Forge Script';$('emp').style.display='block';$('res-h').style.display='none';$('res-s').style.display='none';}
async function ig(){$('emp').style.display='none';$('res-h').style.display='none';$('res-s').style.display='none';$('err').style.display='none';$('ld').style.display='block';try{let p=cM==='h'?{niche:$('h-n').value,audience:$('h-a').value,tone:$('h-t').value,topic:$('h-top').value}:{script:$('s-r').value,url:$('s-u').value};let r=await fetch(cM==='h'?'/fh':'/fs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});let d=await r.json();$('ld').style.display='none';if(d.error)throw new Error(d.error);if(cM==='h'){$('scA').innerText=d.hook_a.score;$('scB').innerText=d.hook_b.score;$('res-h').style.display='block';mDec('txA',`"${d.hook_a.text}"`);mDec('txB',`"${d.hook_b.text}"`);}else{$('res-s').style.display='block';aSc(d.retention_score);mDec('sm',d.master_script);}}catch(e){$('ld').style.display='none';$('err').innerText="ERR: "+e.message;$('err').style.display='block';}}
function cp(i){navigator.clipboard.writeText($(i).innerText);}
</script></body></html>"""
MASTER_HTML = HTML_PART_1 + HTML_PART_2

@app.route('/')
def home(): 
    return render_template_string(MASTER_HTML)

@app.route('/fh', methods=['POST'])
def fh():
    d = request.json
    p = f"Topic: {d.get('topic')}\nNiche: {d.get('niche')}\nAudience: {d.get('audience')}\nTone: {d.get('tone')}"
    try:
        r = requests.post(SAMBANOVA_URL, json={"model": "Meta-Llama-3.3-70B-Instruct", "messages": [{"role": "system", "content": HOOK_SYSTEM_PROMPT}, {"role": "user", "content": p}]}, headers={"Authorization": f"Bearer {SAMBANOVA_API_KEY}", "Content-Type": "application/json"})
        return jsonify(json.loads(r.json()['choices'][0]['message']['content'].strip()))
    except: return jsonify({"error": "Failed to parse AI output."})

@app.route('/fs', methods=['POST'])
def fs():
    d = request.json
    s = d.get('script', '')
    u = d.get('url', '').strip()
    i = f"\n\n🚨 CRUSH COMPETITOR URL: {u}" if u else ""
    try:
        r = requests.post(SAMBANOVA_URL, json={"model": "Meta-Llama-3.3-70B-Instruct", "messages": [{"role": "system", "content": SCRIPT_SYSTEM_PROMPT}, {"role": "user", "content": s + i}]}, headers={"Authorization": f"Bearer {SAMBANOVA_API_KEY}", "Content-Type": "application/json"})
        c = r.json()['choices'][0]['message']['content'].strip()
        if c.startswith("
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1

**Bhai, is tareeke se tera code kabhi nahi katega kyunki koi bhi tukda bada nahi hai!** Ek ke neeche ek 1, 2, 3 paste kar aur deploy maar de. Isme sab kuch—Matrix Text, 3D Panels, naya UI aur Infinity button add ho chuka hai. 🚀🔥
