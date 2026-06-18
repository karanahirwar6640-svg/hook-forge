import os
import json
import re
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
You are Hook Forge v2.0, an elite 9-figure direct-response copywriter and behavioral psychologist. 
Your singular goal is to craft hooks that paralyze the user's thumb and force them to watch. You despise polite, boring "AI-sounding" text.

STRICT RULES:
1. NO AI-SPEAK: Never use words like "Unlock", "Delve", "Discover", "Elevate", "In today's world", "Embark", "Hey guys". If you use these, you fail.
2. BE HUMAN & RUTHLESS: Write like a slightly aggressive, highly authoritative expert speaking directly to a friend. Start mid-thought.
3. PSYCHOLOGICAL TRIGGERS: Use 'The Curiosity Gap', 'Fear of Missing Out (FOMO)', 'Contrarian Truths', or 'Negativity Bias'.
4. EXTREME BREVITY: Keep hooks under 15 words. Punchy. Visceral.

FEW-SHOT EXAMPLES:
BAD (AI-Style): "Are you looking to improve your life? Discover these 3 crucial habits today."
GOOD (Your Style): "You're 90 days away from ruining your life, and you don't even know it."

BAD (AI-Style): "Unlock your financial potential with these saving tips."
GOOD (Your Style): "If your bank account has less than $10,000, stop scrolling."

The user will provide: Topic, Niche, Audience, and Tone.
You must output exactly this JSON structure:
{
  "hook_a": { "text": "High-tension hook text", "score": 95, "reasoning": "Actionable tactical fix", "psychology": "Deep psychological breakdown" },
  "hook_b": { "text": "Contrarian hook text", "score": 98, "reasoning": "Actionable tactical fix", "psychology": "Deep psychological breakdown" },
  "dna_comparison": "Direct ruthless comparison of Hook A vs Hook B."
}
"""

SCRIPT_SYSTEM_PROMPT = """
You are Script Forge, an elite 9-figure Short-Form Content Strategist and Behavioral Psychologist. 
Your only objective is to maximize AUDIENCE RETENTION. You transform weak, boring inputs into highly aggressive, fast-paced, and dopamine-driven viral scripts.

YOUR TRAINING & CONDITIONING (Follow this exactly):

❌ THE BANNED "AI" DICTIONARY (NEVER USE THESE):
"Unlock", "Delve", "Discover", "Crucial", "Game-changer", "In today's fast-paced world", "Imagine", "Let's dive in", "Hey guys". 

✅ THE "RETENTION" RULES:
1. THE 3-SECOND RULE: The first sentence must trigger an immediate emotional response (Anger, Curiosity, Fear, or Greed). 
2. AGITATION: Hit their pain points hard. Make them feel seen and slightly uncomfortable. Twist the knife.
3. EXTREME BREVITY: No sentence longer than 12 words. Cut every single unnecessary adjective. 
4. CONVERSATIONAL TONE: Write exactly how a fast-talking YouTuber speaks. Use contractions (You're, I'll, Don't). Use "..." for dramatic pauses.

YOUR TASK:
Take the user's raw script and completely rewrite it using the Viral Script style above. If there is a target competitor URL provided, analyze its structure to crush them.

Output strictly in JSON format:
{
  "retention_score": 98,
  "hook_extracted": "The explosive 1-2 sentence hook",
  "master_script": "The FULL upgraded, fast-paced script tailored for vocal delivery",
  "psychology_breakdown": "Explain exactly which psychological triggers you used to ensure this beats standard AI scripts"
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
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Noto+Sans+JP:wght@400;700&family=Inter:wght@300;400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    <style>
        body {
            margin: 0; min-height: 100vh; font-family: 'Noto Sans JP', sans-serif;
            background-color: #000; color: #fef3c7; 
            display: flex; align-items: center; justify-content: center; flex-direction: column;
            overflow-x: hidden; position: relative;
            transition: all 0.5s ease; /* Smooth transition for theme change */
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
            transition: all 0.5s ease;
        }
        
        @media (max-width: 768px) {
            .glass-panel {
                background: rgba(3, 0, 0, 0.15) !important;
                backdrop-filter: none !important; -webkit-backdrop-filter: none !important;
                border: 1px solid rgba(255, 50, 50, 0.5) !important;
            }
        }
        
        .anime-title { font-family: 'Cinzel', serif; text-shadow: 0 0 30px rgba(255, 20, 20, 1); transition: all 0.5s ease; }
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
        
        .tab-btn { padding: 10px 20px; font-size: 10px; font-weight: bold; letter-spacing: 0.2em; text-transform: uppercase; border-radius: 8px; transition: all 0.3s; }
        .tab-active { background: rgba(220, 38, 38, 0.2); border: 1px solid #ef4444; color: #fef3c7; box-shadow: 0 0 15px rgba(220,38,38,0.4); }
        .tab-inactive { background: rgba(0, 0, 0, 0.5); border: 1px solid rgba(255,50,50,0.2); color: rgba(254, 243, 199, 0.5); }
        .tab-inactive:hover { color: #fef3c7; border-color: rgba(255,50,50,0.4); }

        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-thumb { background: #dc2626; border-radius: 10px; }

        /* ==========================================
           THEME: LUXURY PREMIUM (EXECUTIVE MODE)
           ========================================== */
        body.theme-luxury { background: radial-gradient(circle at center, #111 0%, #000 100%); color: #e5e7eb; font-family: 'Inter', -apple-system, sans-serif; }
        body.theme-luxury .glass-panel { background: rgba(15, 15, 15, 0.7) !important; backdrop-filter: blur(20px) !important; -webkit-backdrop-filter: blur(20px) !important; border: 1px solid rgba(212, 175, 55, 0.3) !important; box-shadow: 0 30px 60px rgba(0,0,0,0.8), inset 0 1px 0 rgba(255,255,255,0.05) !important; }
        body.theme-luxury .anime-title { font-family: 'Inter', sans-serif; font-weight: 300; letter-spacing: 0.3em; text-shadow: none; background: linear-gradient(135deg, #fef3c7 0%, #d4af37 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        body.theme-luxury .crimson-input { background: rgba(0, 0, 0, 0.5); border: 1px solid rgba(255, 255, 255, 0.1); color: #fff; box-shadow: inset 0 2px 4px rgba(0,0,0,0.5); }
        body.theme-luxury .crimson-input:focus { border-color: rgba(212, 175, 55, 0.6); box-shadow: 0 0 15px rgba(212, 175, 55, 0.15); }
        body.theme-luxury .crimson-btn { background: linear-gradient(135deg, #1f1f1f, #2a2a2a); border: 1px solid rgba(212, 175, 55, 0.4); color: #d4af37; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        body.theme-luxury .crimson-btn:hover { background: linear-gradient(135deg, #2a2a2a, #333); border-color: rgba(212, 175, 55, 0.8); color: #fef3c7; }
        body.theme-luxury .tab-active { background: rgba(212, 175, 55, 0.1); border: 1px solid #d4af37; color: #d4af37; box-shadow: none; }
        body.theme-luxury .bg-video { display: none; } /* Hide video in luxury mode */
        body.theme-luxury .video-overlay { background: #050505; }
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
                <p class="text-[9px] tracking-[0.4em] text-red-300 uppercase"><i class="fa-solid fa-user-shield mr-1"></i> <span id="user-display">Founder</span></p>
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
                    
                    <div>
                        <label class="block text-[10px] font-bold tracking-widest uppercase text-red-500 mb-1"><i class="fa-solid fa-crosshairs mr-1"></i> Target Competitor URL (Optional)</label>
                        <input type="url" id="s-url" class="w-full crimson-input rounded-lg px-4 py-3 text-sm mb-2" placeholder="Paste YouTube/Insta link to snipe structure...">
                    </div>

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
                    <div class="bg-black/50 border border-red-500/20 p-5 rounded-xl flex justify-between items-center">
                        <div>
                            <h3 class="text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1">Viral Retention Score</h3>
                            <p class="text-[10px] text-red-200/80 font-mono">Based on 3-second hook & pacing</p>
                        </div>
                        <div class="text-4xl font-black text-amber-500 drop-shadow-[0_0_10px_rgba(245,158,11,0.5)]">
                            <span id="s-score"></span><span class="text-lg text-amber-500/50">/100</span>
                        </div>
                    </div>

                    <div class="bg-black/50 border border-amber-500/20 p-5 rounded-xl">
                        <span class="text-[10px] bg-amber-950/80 text-amber-300 border border-amber-800 px-2 py-0.5 rounded font-bold uppercase tracking-wider mb-3 inline-block">The Hook</span>
                        <h3 id="s-hook" class="text-base font-bold text-amber-50 tracking-wide italic"></h3>
                    </div>

                    <div class="bg-black/50 border border-red-500/20 p-5 rounded-xl relative">
                        <span class="text-[10px] bg-red-950/80 text-red-300 border border-red-800 px-2 py-0.5 rounded font-bold uppercase tracking-wider mb-3 inline-block">Optimized Master Script</span>
                        <p id="s-master" class="text-sm text-amber-50 leading-relaxed font-mono whitespace-pre-line"></p>
                        <button onclick="copyText('s-master')" class="mt-4 text-[10px] uppercase tracking-widest text-red-400 hover:text-red-200 transition-all"><i class="fa-regular fa-copy mr-1"></i> Copy Script</button>
                    </div>

                    <div class="text-xs text-red-300 bg-red-950/20 p-4 rounded border border-red-900/40 font-mono leading-relaxed">
                        <strong class="uppercase tracking-widest block mb-1 text-red-400"><i class="fa-solid fa-brain mr-2"></i>Psychology Breakdown</strong>
                        <span id="s-psych"></span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentMode = 'hook';
        let isMuted = true;

        function toggleAudio() {
            const vid = document.getElementById('bg-vid');
            const icon = document.getElementById('audio-icon');
            isMuted = !isMuted;
            vid.muted = isMuted;
            icon.className = isMuted ? 'fa-solid fa-volume-xmark text-lg' : 'fa-solid fa-volume-high text-lg';
        }

        function switchMode(mode) {
            currentMode = mode;
            document.getElementById('tab-hook').className = mode === 'hook' ? 'tab-btn tab-active' : 'tab-btn tab-inactive';
            document.getElementById('tab-script').className = mode === 'script' ? 'tab-btn tab-active' : 'tab-btn tab-inactive';
            
            document.getElementById('inputs-hook').style.display = mode === 'hook' ? 'block' : 'none';
            document.getElementById('inputs-script').style.display = mode === 'script' ? 'flex' : 'none';
            
            document.getElementById('btn-ignite').innerHTML = mode === 'hook' ? '<i class="fa-solid fa-fire mr-2"></i> Ignite Hook Engine' : '<i class="fa-solid fa-scroll mr-2"></i> Forge Master Script';
            
            document.getElementById('empty-state').style.display = 'block';
            document.getElementById('results-hook').style.display = 'none';
            document.getElementById('results-script').style.display = 'none';
            document.getElementById('empty-text').innerText = mode === 'hook' ? 'Awaiting Target Parameters...' : 'Awaiting Raw Script...';
        }

        async function igniteEngine() {
            document.getElementById('empty-state').style.display = 'none';
            document.getElementById('results-hook').style.display = 'none';
            document.getElementById('results-script').style.display = 'none';
            document.getElementById('errorBox').style.display = 'none';
            document.getElementById('loading').style.display = 'block';

            try {
                let endpoint = currentMode === 'hook' ? '/forge_hook' : '/forge_script';
                let payloadData = {};

                if (currentMode === 'hook') {
                    payloadData = {
                        niche: document.getElementById('h-niche').value,
                        audience: document.getElementById('h-audience').value,
                        tone: document.getElementById('h-tone').value,
                        topic: document.getElementById('h-topic').value
                    };
                } else {
                    payloadData = {
                        script: document.getElementById('s-raw').value,
                        url: document.getElementById('s-url').value
                    };
                }

                const res = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payloadData)
                });

                const data = await res.json();
                document.getElementById('loading').style.display = 'none';

                if (data.error) {
                    throw new Error(data.error);
                }

                if (currentMode === 'hook') {
                    document.getElementById('scoreA').innerText = data.hook_a.score;
                    document.getElementById('textA').innerText = `"${data.hook_a.text}"`;
                    document.getElementById('psychA').innerText = data.hook_a.psychology;
                    document.getElementById('fixA').innerText = data.hook_a.reasoning;

                    document.getElementById('scoreB').innerText = data.hook_b.score;
                    document.getElementById('textB').innerText = `"${data.hook_b.text}"`;
                    document.getElementById('psychB').innerText = data.hook_b.psychology;
                    document.getElementById('fixB').innerText = data.hook_b.reasoning;

                    document.getElementById('dna').innerText = data.dna_comparison;
                    document.getElementById('results-hook').style.display = 'block';
                } else {
                    document.getElementById('s-score').innerText = data.retention_score;
                    document.getElementById('s-hook').innerText = `"${data.hook_extracted}"`;
                    document.getElementById('s-master').innerText = data.master_script;
                    document.getElementById('s-psych').innerText = data.psychology_breakdown;
                    document.getElementById('results-script').style.display = 'block';
                }
            } catch (err) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('errorBox').innerText = "ERROR: " + err.message;
                document.getElementById('errorBox').style.display = 'block';
            }
        }

        function copyText(elementId) {
            const text = document.getElementById(elementId).innerText;
            navigator.clipboard.writeText(text);
        }

        function founderOverride() {
            document.getElementById('login-viewport').style.display = 'none';
            document.getElementById('dashboard-viewport').style.display = 'flex';
        }

        function handleLogout() {
            document.getElementById('login-viewport').style.display = 'block';
            document.getElementById('dashboard-viewport').style.display = 'none';
        }

        function loginGitHub() { founderOverride(); }
        function sendMagicLink() { founderOverride(); }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(MASTER_HTML)

@app.route('/forge_hook', methods=['POST'])
def forge_hook():
    data = request.json
    user_prompt = f"Topic: {data.get('topic')}\nNiche: {data.get('niche')}\nAudience: {data.get('audience')}\nTone: {data.get('tone')}"
    payload = {
        "model": "Meta-Llama-3.3-70B-Instruct", 
        "messages": [{"role": "system", "content": HOOK_SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}]
    }
    try:
        r = requests.post(SAMBANOVA_URL, json=payload, headers={"Authorization": f"Bearer {SAMBANOVA_API_KEY}", "Content-Type": "application/json"})
        return jsonify(json.loads(r.json()['choices'][0]['message']['content'].strip()))
    except Exception as e:
        return jsonify({"error": "Failed to parse AI output. Try again."})

@app.route('/forge_script', methods=['POST'])
def forge_script():
    data = request.json
    raw_script = data.get('script', '')
    target_url = data.get('url', '').strip()
    
    sniper_intel = ""
    if target_url:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            res = requests.get(target_url, headers=headers, timeout=5)
            html = res.text
            
            og_title = re.search(r'<meta\s+(?:property|name)="og:title"\s+content="([^"]+)"', html, re.IGNORECASE)
            title_tag = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
            
            if og_title:
                video_title = og_title.group(1)
            elif title_tag:
                video_title = title_tag.group(1)
            else:
                video_title = "this viral competitor content"
            
            video_title = re.sub(r'(\s*-\s*YouTube|\s*\|\s*TikTok|\s*on Instagram.*|\s*-\s*X)', '', video_title)
            sniper_intel = f"\n\n🚨 TARGET ACQUIRED: Crush this competitor video titled '{video_title}'. Analyze its core hook and pacing, and make our script 10x more engaging to steal their audience."
        except Exception as e:
            sniper_intel = f"\n\n🚨 TARGET URL ACQUIRED: {target_url}. Steal the pacing and engagement strategy of this competitor."

    final_prompt = raw_script + sniper_intel

    payload = {
        "model": "Meta-Llama-3.3-70B-Instruct", 
        "messages": [{"role": "system", "content": SCRIPT_SYSTEM_PROMPT}, {"role": "user", "content": final_prompt}]
    }
    try:
        r = requests.post(SAMBANOVA_URL, json=payload, headers={"Authorization": f"Bearer {SAMBANOVA_API_KEY}", "Content-Type": "application/json"})
        content = r.json()['choices'][0]['message']['content'].strip()
        
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()

        return jsonify(json.loads(content))
    except Exception as e:
        return jsonify({"error": "Failed to parse AI output. Ensure input is clear."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
