import os
import json
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
SAMBANOVA_URL = "https://api.sambanova.ai/v1/chat/completions"

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# ==========================================
# ELITE AI PROMPTS
# ==========================================
HOOK_SYSTEM_PROMPT = """
You are Hook Forge v2.0, an elite social media psychologist, data scientist, and master copywriter. 
Your job is to generate high-converting hooks and analyze them deeply.
You must ALWAYS respond in valid JSON format. Do not write any markdown prose outside the JSON.

The user will provide: Topic, Niche, Audience, and Tone.
You must output exactly this JSON structure:
{
  "hook_a": { "text": "Viral hook text A", "score": 8, "reasoning": "Actionable fix", "psychology": "Deep psychological breakdown" },
  "hook_b": { "text": "Viral hook text B", "score": 9, "reasoning": "Actionable fix", "psychology": "Deep psychological breakdown" },
  "dna_comparison": "Direct comparison of Hook A vs Hook B."
}
"""

SCRIPT_SYSTEM_PROMPT = """
You are Script Forge, an elite 9-figure social media retention engineer and master copywriter.
Your job is to take a raw, boring script and transform it into a highly engaging, fast-paced, viral short-form video script.
Focus on:
1. A scroll-stopping 3-second hook at the very beginning.
2. Removing all fluff and boring pauses.
3. Fast pacing and high retention mechanics (curiosity loops, pattern interrupts).
4. A strong, clear CTA (Call to Action) at the end.

You must ALWAYS respond in valid JSON format. Do not write any markdown prose outside the JSON.
You must output exactly this JSON structure:
{
  "retention_score": 95,
  "hook_extracted": "The explosive opening line used...",
  "master_script": "The FULL upgraded, pacing-optimized script including the hook and CTA...",
  "psychology_breakdown": "Explanation of changes, fluff removed, and why this script will hold retention..."
}
"""

# ==========================================
# ROBUST COMBINED MASTER FRONTEND (SPA STYLE)
# ==========================================
MASTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hook Forge | Enterprise</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    <style>
        body {
            margin: 0; min-height: 100vh; font-family: 'Noto Sans JP', sans-serif;
            background-color: #000; color: #fef3c7; 
            display: flex; align-items: center; justify-content: center; flex-direction: column;
            overflow-x: hidden; position: relative;
        }
        .bg-video {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            object-fit: cover; z-index: 0; pointer-events: none;
        }
        .video-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.2); z-index: 1; pointer-events: none;
        }
        
        .glass-panel {
            background: rgba(5, 0, 0, 0.25);
            backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 50, 50, 0.4); border-radius: 24px;
            box-shadow: 0 40px 80px rgba(0,0,0,0.95);
        }
        
        @media (max-width: 768px) {
            .glass-panel {
                background: rgba(3, 0, 0, 0.15) !important;
                backdrop-filter: none !important; -webkit-backdrop-filter: none !important;
                border: 1px solid rgba(255, 50, 50, 0.5) !important;
            }
        }
        
        .anime-title { font-family: 'Cinzel', serif; text-shadow: 0 0 30px rgba(255, 20, 20, 1); }
        .crimson-input { background: rgba(0, 0, 0, 0.7); border: 1px solid rgba(220, 38, 38, 0.35); color: #fef3c7; transition: all 0.3s; }
        .crimson-input:focus { outline: none; border-color: #ef4444; box-shadow: 0 0 20px rgba(239, 68, 68, 0.4); }
        select.crimson-input option { background: #000; color: #fef3c7; }
        .github-btn { background: rgba(15, 15, 15, 0.6); border: 1px solid rgba(255, 50, 50, 0.3); color: white; transition: all 0.3s; }
        .github-btn:hover { background: rgba(30, 30, 30, 0.9); box-shadow: 0 0 20px rgba(220,38,38,0.3); }
        .crimson-btn { background: linear-gradient(45deg, #7f1d1d, #dc2626); border: 1px solid #ef4444; box-shadow: 0 0 20px rgba(220, 38, 38, 0.5); transition: all 0.3s ease; }
        .crimson-btn:hover { background: linear-gradient(45deg, #991b1b, #f87171); box-shadow: 0 0 30px rgba(220, 38, 38, 0.8); }
        
        .audio-btn {
            position: fixed; bottom: 20px; right: 20px; z-index: 100;
            background: rgba(0,0,0,0.6); padding: 12px; border-radius: 50%;
            border: 1px solid rgba(255,50,50,0.4); color: #ef4444; transition: all 0.3s;
        }
        
        /* TAB STYLES */
        .tab-btn { padding: 10px 20px; font-size: 10px; font-weight: bold; letter-spacing: 0.2em; text-transform: uppercase; border-radius: 8px; transition: all 0.3s; }
        .tab-active { background: rgba(220, 38, 38, 0.2); border: 1px solid #ef4444; color: #fef3c7; box-shadow: 0 0 15px rgba(220,38,38,0.4); }
        .tab-inactive { background: rgba(0, 0, 0, 0.5); border: 1px solid rgba(255,50,50,0.2); color: rgba(254, 243, 199, 0.5); }
        .tab-inactive:hover { color: #fef3c7; border-color: rgba(255,50,50,0.4); }

        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-thumb { background: #dc2626; border-radius: 10px; }
    </style>
</head>
<body class="p-4">

    <video id="bg-vid" autoplay muted loop playsinline class="bg-video">
        <source src="https://subczjjxgexeraofhykl.supabase.co/storage/v1/object/public/Assets/From%20Klickpin.com-%20Natural%20Makeup%20Looks%20Inspiration%20for%20Summer-pin-id-587860557652168444.mp4" type="video/mp4">
    </video>
    <div class="video-overlay"></div>

    <button onclick="toggleAudio()" class="audio-btn shadow-lg"><i id="audio-icon" class="fa-solid fa-volume-xmark text-lg"></i></button>

    <div id="login-viewport" class="w-full max-w-[410px] p-8 md:p-10 glass-panel relative z-10">
        <div class="text-center mb-8">
            <h1 class="anime-title text-4xl md:text-5xl font-black text-red-500 tracking-widest mb-2">HOOK FORGE</h1>
            <p class="text-[10px] tracking-[0.4em] text-red-300/80 uppercase font-bold">Secure Cloud Portal</p>
        </div>
        <div id="msgBox" class="hidden p-3 rounded-xl text-xs font-mono text-center mb-6 border bg-red-950/80 border-red-500/50 text-red-200"></div>
        <div class="space-y-5">
            <button onclick="loginGitHub()" id="btn-github" class="w-full github-btn py-4 rounded-xl text-xs tracking-widest uppercase font-bold flex items-center justify-center gap-3 shadow-md">
                <i class="fa-brands fa-github text-base"></i> Continue with GitHub
            </button>
            <div class="relative flex py-2 items-center">
                <div class="flex-grow border-t border-red-500/30"></div>
                <span class="flex-shrink-0 mx-4 text-red-400/60 text-[9px] uppercase tracking-[0.3em] font-bold">Secure Routing</span>
                <div class="flex-grow border-t border-red-500/30"></div>
            </div>
            <div>
                <div class="relative mb-3">
                    <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 text-red-400/60"><i class="fa-solid fa-shield-halved text-xs"></i></span>
                    <input type="email" id="auth-email" placeholder="Enter security email" class="w-full crimson-input rounded-xl pl-10 pr-4 py-3.5 text-sm focus:outline-none">
                </div>
                <button onclick="sendMagicLink()" id="btn-email" class="w-full crimson-btn text-white font-bold py-4 rounded-xl text-xs tracking-widest uppercase transition-all shadow-lg">
                    Request Entry Token
                </button>
            </div>
            <div class="pt-6 text-center">
                <button onclick="founderOverride()" class="text-[9px] text-red-500/40 hover:text-red-400 uppercase tracking-widest transition-all">
                    [ Developer Override Access ]
                </button>
            </div>
        </div>
    </div>

    <div id="dashboard-viewport" class="hidden w-full max-w-6xl flex-col relative z-10">
        
        <div class="w-full flex flex-col md:flex-row justify-between items-center mb-6 px-4">
            <div class="text-center md:text-left mb-4 md:mb-0">
                <h1 class="anime-title text-3xl font-black text-red-500 mb-1">HOOK FORGE</h1>
                <p class="text-[9px] tracking-[0.4em] text-red-300 uppercase"><i class="fa-solid fa-user-shield mr-1"></i> <span id="user-display"></span></p>
            </div>
            
            <div class="flex space-x-3 bg-black/40 p-1.5 rounded-xl border border-red-900/50 backdrop-blur-sm">
                <button id="tab-hook" onclick="switchMode('hook')" class="tab-btn tab-active"><i class="fa-solid fa-fire mr-1"></i> Hook Forge</button>
                <button id="tab-script" onclick="switchMode('script')" class="tab-btn tab-inactive"><i class="fa-solid fa-scroll mr-1"></i> Script Forge</button>
            </div>
            
            <button onclick="handleLogout()" class="mt-4 md:mt-0 bg-red-950/60 hover:bg-red-700 border border-red-800 px-4 py-2 rounded-lg text-[9px] uppercase tracking-widest text-white font-bold transition-all hidden md:block"><i class="fa-solid fa-power-off"></i></button>
        </div>

        <div id="errorBox" class="hidden bg-red-900/80 border border-red-500 text-white p-3 rounded mb-4 text-xs font-mono w-full"></div>

        <div class="flex flex-col lg:flex-row gap-6 w-full items-stretch">
            
            <div class="glass-panel w-full lg:max-w-md p-6 flex flex-col justify-between">
                
                <div id="inputs-hook" class="space-y-4">
                    <div>
                        <label class="block text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1">Niche</label>
                        <input type="text" id="h-niche" value="Anime & Tech" class="w-full crimson-input rounded-lg px-4 py-3 text-sm">
                    </div>
                    <div>
                        <label class="block text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1">Audience</label>
                        <input type="text" id="h-audience" value="Creators" class="w-full crimson-input rounded-lg px-4 py-3 text-sm">
                    </div>
                    <div>
                        <label class="block text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1">Tone Matrix (15+ Options)</label>
                        <select id="h-tone" class="w-full crimson-input rounded-lg px-4 py-3 text-sm">
                            <option value="Curious">Curiosity Gap</option>
                            <option value="Aggressive">Brutally Honest</option>
                            <option value="Storytelling">Anime Protagonist Arc</option>
                            <option value="Controversial">Controversial / Polarizing</option>
                            <option value="Educational">Educational / Value-Bomb</option>
                            <option value="Urgent">Urgent / FOMO</option>
                            <option value="Inspirational">Inspirational / Cinematic</option>
                            <option value="Sarcastic">Sarcastic / Witty</option>
                            <option value="Empathetic">Empathetic / Relatable</option>
                            <option value="Analytical">Data-Driven / Analytical</option>
                            <option value="Vulnerable">Vulnerable / Authentic</option>
                            <option value="Hype">High Energy / Hype</option>
                            <option value="Minimalist">Minimalist / Straight to Point</option>
                            <option value="Philosophical">Deep / Philosophical</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1">Topic</label>
                        <textarea id="h-topic" rows="3" class="w-full crimson-input rounded-lg px-4 py-3 text-sm resize-none" placeholder="Enter core concept..."></textarea>
                    </div>
                </div>

                <div id="inputs-script" class="hidden space-y-4 flex-grow flex flex-col">
                    <p class="text-[10px] tracking-widest text-red-300/80 uppercase border-b border-red-900/50 pb-2 mb-2">Transform raw script into highly retained viral content.</p>
                    <div class="flex-grow flex flex-col">
                        <label class="block text-[10px] font-bold tracking-widest uppercase text-amber-400 mb-1"><i class="fa-solid fa-code mr-1"></i> Raw Script Input</label>
                        <textarea id="s-raw" class="w-full flex-grow min-h-[250px] crimson-input rounded-lg px-4 py-3 text-sm resize-none" placeholder="Paste your boring, unoptimized script here..."></textarea>
                    </div>
                </div>

                <button onclick="igniteEngine()" id="btn-ignite" class="w-full crimson-btn py-4 rounded-lg font-bold tracking-widest uppercase text-xs mt-6">
                    <i class="fa-solid fa-fire mr-2"></i> Ignite Hook Engine
                </button>
            </div>

            <div class="glass-panel flex-grow p-6 flex flex-col justify-center min-h-[500px]">
                <div id="loading" class="hidden text-center">
                    <i class="fa-solid fa-spinner fa-spin text-5xl text-red-500 mb-4 drop-shadow-[0_0_15px_rgba(220,38,38,0.8)]"></i>
                    <h2 id="loading-text" class="anime-title text-2xl text-red-100">Extracting Psychology Matrix...</h2>
                </div>

                <div id="empty-state" class="text-center opacity-50">
                    <i class="fa-solid fa-crosshairs text-6xl text-red-500/50 mb-4"></i>
                    <p id="empty-text" class="text-xs font-mono tracking-widest uppercase">Awaiting Target Parameters...</p>
                </div>

                <div id="results-hook" class="hidden space-y-5 overflow-y-auto max-h-[620px] pr-2">
                    <div class="bg-black/50 border border-red-500/20 p-5 rounded-xl">
                        <div class="flex justify-between items-center mb-3">
                            <span class="text-[10px] bg-red-950/80 text-red-300 border border-red-800 px-2 py-0.5 rounded font-bold uppercase tracking-wider">Option A</span>
                            <span class="text-[10px] text-red-400 font-black tracking-widest">MATRIX SCORE: <span id="scoreA" class="text-red-500 text-base"></span></span>
                        </div>
                        <h3 id="textA" class="text-base md:text-lg font-bold text-amber-50 mb-3 tracking-wide"></h3>
                        <div class="text-xs text-red-200/80 space-y-2 border-t border-red-900/30 pt-3">
                            <p><strong class="text-red-400">Psychology:</strong> <span id="psychA"></span></p>
                            <p><strong class="text-red-400">Tactical Fix:</strong> <span id="fixA"></span></p>
                        </div>
                        <button onclick="copyText('textA')" class="mt-3 text-[10px] uppercase tracking-widest text-red-400 hover:text-red-200 transition-all"><i class="fa-regular fa-copy mr-1"></i> Copy</button>
                    </div>

                    <div class="bg-black/50 border border-amber-500/20 p-5 rounded-xl">
                        <div class="flex justify-between items-center mb-3">
                            <span class="text-[10px] bg-amber-950/80 text-amber-300 border border-amber-800 px-2 py-0.5 rounded font-bold uppercase tracking-wider">Option B</span>
                            <span class="text-[10px] text-amber-400 font-black tracking-widest">MATRIX SCORE: <span id="scoreB" class="text-amber-500 text-base"></span></span>
                        </div>
                        <h3 id="textB" class="text-base md:text-lg font-bold text-amber-50 mb-3 tracking-wide"></h3>
                        <div class="text-xs text-red-200/80 space-y-2 border-t border-red-900/30 pt-3">
                            <p><strong class="text-amber-400">Psychology:</strong> <span id="psychB"></span></p>
                            <p><strong class="text-amber-400">Tactical Fix:</strong> <span id="fixB"></span></p>
                        </div>
                        <button onclick="copyText('textB')" class="mt-3 text-[10px] uppercase tracking-widest text-amber-400 hover:text-amber-200 transition-all"><i class="fa-regular fa-copy mr-1"></i> Copy</button>
                    </div>
                    
                    <div class="text-xs text-red-300 bg-red-950/20 p-4 rounded border border-red-900/40 font-mono leading-relaxed">
                        <strong class="uppercase tracking-widest block mb-1 text-red-400"><i class="fa-solid fa-dna mr-2"></i>DNA Matrix Analysis</strong>
                        <span id="dna"></span>
                    </div>
                </div>

                <div id="results-script" class="hidden space-y-5 overflow-y-auto max-h-[620px] pr-2">
                    <div class="bg-black/50 border border-amber-500/30 p-5 rounded-xl relative shadow-[0_0_30px_rgba(245,158,11,0.1)]">
                        <div class="absolute top-4 right-4 text-center">
                            <span class="block text-[8px] tracking-[0.3em] text-amber-500/80 uppercase">Retention Score</span>
                            <span id="s-score" class="text-3xl font-black text-amber-400 font-mono text-shadow-glow"></span><span class="text-sm text-amber-500/50">/100</span>
                        </div>
                        
                        <h2 class="text-[10px] tracking-widest text-amber-500 font-bold uppercase mb-4 border-b border-amber-900/50 pb-2"><i class="fa-solid fa-bolt mr-2"></i>Optimized Master Script</h2>
                        
                        <div class="bg-black/40 p-4 rounded-lg border border-amber-900/30 mb-4">
                            <span class="text-[9px] bg-red-900 text-red-200 px-2 py-0.5 rounded uppercase tracking-wider mb-2 inline-block">Extracted Hook</span>
                            <p id="s-hook" class="text-sm font-bold text-red-100 italic mb-1"></p>
                        </div>

                        <div class="text-sm text-amber-50 whitespace-pre-wrap leading-relaxed font-medium mb-4" id="s-master"></div>
                        
                        <button onclick="copyText('s-master')" class="w-full bg-amber-950/40 hover:bg-amber-900/60 border border-amber-700/50 py-3 rounded-lg text-[10px] uppercase tracking-widest text-amber-300 hover:text-amber-100 transition-all"><i class="fa-regular fa-copy mr-2"></i> Copy Master Script</button>
                    </div>

                    <div class="text-xs text-amber-200/80 bg-black/40 p-5 rounded-xl border border-amber-900/30 leading-relaxed">
                        <strong class="uppercase tracking-widest block mb-2 text-amber-500"><i class="fa-solid fa-brain mr-2"></i>Psychology Breakdown</strong>
                        <span id="s-psych"></span>
                    </div>
                </div>

            </div>
        </div>
    </div>

    <script>
        const vid = document.getElementById('bg-vid');
        vid.volume = 0.2; 
        function toggleAudio() {
            if (vid.muted) { vid.muted = false; document.getElementById('audio-icon').className = "fa-solid fa-volume-low text-lg"; } 
            else { vid.muted = true; document.getElementById('audio-icon').className = "fa-solid fa-volume-xmark text-lg"; }
        }
        document.addEventListener('DOMContentLoaded', () => { if (vid) { vid.play().catch(e => console.log("Autoplay blocked")); } });

        const sbClient = window.supabase.createClient('{{ supabase_url }}', '{{ supabase_key }}', {
            auth: { flowType: 'implicit', autoRefreshToken: true, persistSession: true, detectSessionInUrl: true }
        });

        let activeUserEmail = null;
        let currentMode = 'hook'; // 'hook' or 'script'

        function showMsg(type, text) {
            const box = document.getElementById('msgBox');
            box.style.display = 'block';
            box.innerText = text;
            box.className = type === 'error' 
                ? "p-3 rounded-xl text-xs font-mono text-center mb-6 border bg-red-950/90 border-red-500/50 text-red-200"
                : "p-3 rounded-xl text-xs font-mono text-center mb-6 border bg-emerald-950/90 border-emerald-500/50 text-emerald-200";
        }

        function renderView(session) {
            const loginVp = document.getElementById('login-viewport');
            const dashVp = document.getElementById('dashboard-viewport');
            if (session && session.user) {
                activeUserEmail = session.user.email || 'Authorized Founder';
                document.getElementById('user-display').innerText = activeUserEmail;
                loginVp.style.display = 'none'; dashVp.style.display = 'flex';
            } else {
                activeUserEmail = null; dashVp.style.display = 'none'; loginVp.style.display = 'block';
            }
        }

        function founderOverride() { renderView({ user: { email: 'founder@hookforge.app' } }); showMsg('success', 'Override Active: Welcome Founder!'); }

        sbClient.auth.getSession().then(({ data, error }) => { if (!error) renderView(data.session); });
        sbClient.auth.onAuthStateChange((event, session) => { if (event === 'SIGNED_IN' || event === 'INITIAL_SESSION') renderView(session); else if (event === 'SIGNED_OUT') renderView(null); });

        async function loginGitHub() {
            try { document.getElementById('btn-github').innerHTML = '<i class="fa-solid fa-spinner fa-spin text-base"></i> Connecting...';
                const { error } = await sbClient.auth.signInWithOAuth({ provider: 'github' });
                if (error) throw error;
            } catch (error) { showMsg('error', 'Auth Error: ' + error.message); document.getElementById('btn-github').innerHTML = '<i class="fa-brands fa-github text-base"></i> Continue with GitHub'; }
        }

        async function handleLogout() { await sbClient.auth.signOut(); }

        // --- DUAL ENGINE LOGIC ---
        function switchMode(mode) {
            currentMode = mode;
            // Tabs
            document.getElementById('tab-hook').className = mode === 'hook' ? 'tab-btn tab-active' : 'tab-btn tab-inactive';
            document.getElementById('tab-script').className = mode === 'script' ? 'tab-btn tab-active' : 'tab-btn tab-inactive';
            // Inputs
            document.getElementById('inputs-hook').style.display = mode === 'hook' ? 'block' : 'none';
            document.getElementById('inputs-script').style.display = mode === 'script' ? 'flex' : 'none';
            // Button & Text
            const btn = document.getElementById('btn-ignite');
            if(mode === 'hook'){
                btn.innerHTML = '<i class="fa-solid fa-fire mr-2"></i> Ignite Hook Engine';
                document.getElementById('empty-text').innerText = 'Awaiting Target Parameters...';
            } else {
                btn.innerHTML = '<i class="fa-solid fa-bolt mr-2"></i> Forge Master Script';
                document.getElementById('empty-text').innerText = 'Awaiting Raw Script Data...';
            }
            // Reset Results UI
            document.getElementById('empty-state').style.display = 'block';
            document.getElementById('results-hook').style.display = 'none';
            document.getElementById('results-script').style.display = 'none';
            document.getElementById('errorBox').style.display = 'none';
        }

        async function igniteEngine() {
            if (!activeUserEmail) { alert("Session expired."); return; }
            
            document.getElementById('empty-state').style.display = 'none';
            document.getElementById('results-hook').style.display = 'none';
            document.getElementById('results-script').style.display = 'none';
            document.getElementById('errorBox').style.display = 'none';
            document.getElementById('loading').style.display = 'block';
            
            const endpoint = currentMode === 'hook' ? '/forge_hook' : '/forge_script';
            document.getElementById('loading-text').innerText = currentMode === 'hook' ? 'Extracting Psychology Matrix...' : 'Forging Elite Script...';
            
            let payload = { email: activeUserEmail };
            if(currentMode === 'hook') {
                payload.topic = document.getElementById('h-topic').value;
                payload.niche = document.getElementById('h-niche').value;
                payload.audience = document.getElementById('h-audience').value;
                payload.tone = document.getElementById('h-tone').value;
            } else {
                const raw = document.getElementById('s-raw').value.trim();
                if(!raw) { 
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('errorBox').style.display = 'block';
                    document.getElementById('errorBox').innerText = "Please paste a raw script first.";
                    return;
                }
                payload.script = raw;
            }

            try {
                const response = await fetch(endpoint, {
                    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
                });
                
                const data = await response.json();
                document.getElementById('loading').style.display = 'none';
                
                if (data.error) {
                    document.getElementById('errorBox').style.display = 'block';
                    document.getElementById('errorBox').innerText = data.error;
                    return;
                }

                if(currentMode === 'hook') {
                    document.getElementById('textA').innerText = `"` + data.hook_a.text + `"`;
                    document.getElementById('scoreA').innerText = data.hook_a.score;
                    document.getElementById('psychA').innerText = data.hook_a.psychology;
                    document.getElementById('fixA').innerText = data.hook_a.reasoning;
                    document.getElementById('textB').innerText = `"` + data.hook_b.text + `"`;
                    document.getElementById('scoreB').innerText = data.hook_b.score;
                    document.getElementById('psychB').innerText = data.hook_b.psychology;
                    document.getElementById('fixB').innerText = data.hook_b.reasoning;
                    document.getElementById('dna').innerText = data.dna_comparison;
                    document.getElementById('results-hook').style.display = 'block';
                } else {
                    document.getElementById('s-score').innerText = data.retention_score;
                    document.getElementById('s-hook').innerText = `"` + data.hook_extracted + `"`;
                    document.getElementById('s-master').innerText = data.master_script;
                    document.getElementById('s-psych').innerText = data.psychology_breakdown;
                    document.getElementById('results-script').style.display = 'block';
                }
            } catch(error) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('errorBox').style.display = 'block';
                document.getElementById('errorBox').innerText = "System Fault: " + error.message;
            }
        }

        function copyText(elementId) {
            const text = document.getElementById(elementId).innerText.replace(/^"|"$/g, '');
            navigator.clipboard.writeText(text);
            alert("Copied to clipboard! ⚔️");
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(MASTER_HTML, supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY)

def run_sambanova(prompt, system_prompt):
    payload = {
        "model": "Meta-Llama-3.3-70B-Instruct", 
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}], 
        "temperature": 0.7
    }
    headers = {"Authorization": f"Bearer {SAMBANOVA_API_KEY}", "Content-Type": "application/json"}
    
    r = requests.post(SAMBANOVA_URL, json=payload, headers=headers, timeout=15)
    if r.status_code != 200:
        return {"error": "SambaNova engine offline. Try again shortly."}
        
    res_data = r.json()
    ai_text = res_data['choices'][0]['message']['content'].strip()
    if ai_text.startswith("```json"):
        ai_text = ai_text.replace("```json", "", 1).strip()
        if ai_text.endswith("```"):
            ai_text = ai_text[:-3].strip()
            
    return json.loads(ai_text)

@app.route('/forge_hook', methods=['POST'])
def forge_hook():
    data = request.json
    if not data.get('email'): return jsonify({"error": "Unauthorized."}), 401
    prompt = f"Topic: {data.get('topic')}\\nNiche: {data.get('niche')}\\nAudience: {data.get('audience')}\\nTone: {data.get('tone')}"
    try:
        return jsonify(run_sambanova(prompt, HOOK_SYSTEM_PROMPT))
    except Exception as e: 
        return jsonify({"error": f"Runtime fault: {str(e)}"})

@app.route('/forge_script', methods=['POST'])
def forge_script():
    data = request.json
    if not data.get('email'): return jsonify({"error": "Unauthorized."}), 401
    prompt = f"Raw Script:\\n{data.get('script')}"
    try:
        return jsonify(run_sambanova(prompt, SCRIPT_SYSTEM_PROMPT))
    except Exception as e: 
        return jsonify({"error": f"Runtime fault: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
