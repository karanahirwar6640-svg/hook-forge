import os
import json
import re
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
SAMBANOVA_URL = "https://api.sambanova.ai/v1/chat/completions"

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
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Noto+Sans+JP:wght@400;700&family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {
            margin: 0; min-height: 100vh; font-family: 'Noto Sans JP', sans-serif;
            background-color: #000; color: #fef3c7; 
            display: flex; align-items: center; justify-content: center; flex-direction: column;
            overflow-x: hidden; position: relative;
            transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        /* TRANSITION OVERLAY (The Cinematic Flash) */
        #cinematic-flash {
            position: fixed; inset: 0; background-color: #000;
            z-index: 9999; opacity: 0; pointer-events: none;
            transition: opacity 0.4s ease-in-out;
        }

        .bg-video {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            object-fit: cover; z-index: 0; pointer-events: none;
            transition: opacity 0.5s ease;
        }
        .video-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.35); z-index: 1; pointer-events: none;
            transition: all 0.5s ease;
        }
        
        .glass-panel {
            background: rgba(10, 0, 0, 0.3);
            backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 50, 50, 0.3); border-radius: 24px;
            box-shadow: 0 40px 80px rgba(0,0,0,0.95);
            transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        @media (max-width: 768px) {
            .glass-panel {
                backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
            }
        }
        
        .anime-title { font-family: 'Cinzel', serif; text-shadow: 0 0 30px rgba(255, 20, 20, 1); transition: all 0.5s ease; }
        .crimson-input { background: rgba(0, 0, 0, 0.7); border: 1px solid rgba(220, 38, 38, 0.35); color: #fef3c7; transition: all 0.3s; }
        .crimson-input:focus { outline: none; border-color: #ef4444; box-shadow: 0 0 20px rgba(239, 68, 68, 0.4); }
        select.crimson-input option { background: #000; color: #fef3c7; }
        
        .crimson-btn { background: linear-gradient(45deg, #7f1d1d, #dc2626); border: 1px solid #ef4444; box-shadow: 0 0 20px rgba(220, 38, 38, 0.5); transition: all 0.3s ease; }
        .crimson-btn:hover { background: linear-gradient(45deg, #991b1b, #f87171); box-shadow: 0 0 30px rgba(220, 38, 38, 0.8); transform: translateY(-2px); }
        
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
           AURA 1: COSMIC BLUE ("Your Name" Theme)
           ========================================== */
        body.theme-aura-1 .glass-panel { border-color: rgba(50, 150, 255, 0.4); box-shadow: 0 40px 80px rgba(0,0,0,0.95), inset 0 0 20px rgba(50,150,255,0.05); }
        body.theme-aura-1 .anime-title { color: #60a5fa !important; text-shadow: 0 0 30px rgba(50, 150, 255, 0.8); }
        body.theme-aura-1 .crimson-btn { background: linear-gradient(45deg, #1e3a8a, #2563eb); border-color: #3b82f6; box-shadow: 0 0 20px rgba(59, 130, 246, 0.5); }
        body.theme-aura-1 .crimson-btn:hover { background: linear-gradient(45deg, #1e40af, #3b82f6); box-shadow: 0 0 30px rgba(59, 130, 246, 0.8); }
        body.theme-aura-1 .text-red-400, body.theme-aura-1 .text-red-500 { color: #60a5fa !important; }
        body.theme-aura-1 .border-red-900\/50, body.theme-aura-1 .border-red-500\/50 { border-color: rgba(59, 130, 246, 0.4) !important; }
        body.theme-aura-1 .bg-red-900\/40 { background-color: rgba(30, 58, 138, 0.4) !important; }
        body.theme-aura-1 .tab-active { background: rgba(59, 130, 246, 0.2); border-color: #3b82f6; box-shadow: 0 0 15px rgba(59, 130, 246, 0.4); }

        /* ==========================================
           AURA 2: AMETHYST PURPLE (Video 3 Theme)
           ========================================== */
        body.theme-aura-2 .glass-panel { border-color: rgba(168, 85, 247, 0.4); box-shadow: 0 40px 80px rgba(0,0,0,0.95), inset 0 0 20px rgba(168,85,247,0.05); }
        body.theme-aura-2 .anime-title { color: #c084fc !important; text-shadow: 0 0 30px rgba(168, 85, 247, 0.8); }
        body.theme-aura-2 .crimson-btn { background: linear-gradient(45deg, #581c87, #9333ea); border-color: #a855f7; box-shadow: 0 0 20px rgba(168, 85, 247, 0.5); }
        body.theme-aura-2 .crimson-btn:hover { background: linear-gradient(45deg, #6b21a8, #a855f7); box-shadow: 0 0 30px rgba(168, 85, 247, 0.8); }
        body.theme-aura-2 .text-red-400, body.theme-aura-2 .text-red-500 { color: #c084fc !important; }
        body.theme-aura-2 .border-red-900\/50, body.theme-aura-2 .border-red-500\/50 { border-color: rgba(168, 85, 247, 0.4) !important; }
        body.theme-aura-2 .bg-red-900\/40 { background-color: rgba(88, 28, 135, 0.4) !important; }
        body.theme-aura-2 .tab-active { background: rgba(168, 85, 247, 0.2); border-color: #a855f7; box-shadow: 0 0 15px rgba(168, 85, 247, 0.4); }

        /* ==========================================
           THEME: ENTERPRISE LUXURY (Next-Gen UI)
           ========================================== */
        @keyframes luxuryGradient { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        
        body.theme-luxury { 
            background: linear-gradient(135deg, #020617 0%, #000000 50%, #0f172a 100%);
            background-size: 200% 200%;
            animation: luxuryGradient 15s ease infinite;
            color: #e2e8f0; font-family: 'Inter', sans-serif; 
        }
        /* The Subtle Enterprise Tech Grid */
        body.theme-luxury::before {
            content: ""; position: fixed; inset: 0; z-index: -1; pointer-events: none;
            background-image: linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
            background-size: 40px 40px;
        }

        body.theme-luxury .glass-panel { 
            background: rgba(15, 15, 20, 0.6) !important; 
            backdrop-filter: blur(25px) saturate(120%) !important; -webkit-backdrop-filter: blur(25px) saturate(120%) !important; 
            border: 1px solid rgba(212, 175, 55, 0.15) !important; 
            box-shadow: 0 25px 50px -12px rgba(0,0,0,1), inset 0 1px 0 rgba(255,255,255,0.05) !important; 
        }
        body.theme-luxury .anime-title { 
            font-family: 'Inter', sans-serif !important; font-weight: 800 !important; letter-spacing: 0.15em !important; text-shadow: none !important; 
            background: linear-gradient(135deg, #fef3c7 0%, #d4af37 50%, #b45309 100%) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; color: transparent !important; 
        }
        body.theme-luxury .crimson-input { background: rgba(0, 0, 0, 0.4) !important; border: 1px solid rgba(255, 255, 255, 0.05) !important; color: #fff !important; box-shadow: inset 0 2px 4px rgba(0,0,0,0.3) !important; transition: all 0.3s ease; }
        body.theme-luxury .crimson-input:focus { border-color: rgba(212, 175, 55, 0.4) !important; box-shadow: 0 0 15px rgba(212, 175, 55, 0.05) !important; background: rgba(0,0,0,0.6) !important; }
        body.theme-luxury .crimson-btn { background: linear-gradient(135deg, #111, #1a1a1a) !important; border: 1px solid rgba(212, 175, 55, 0.3) !important; color: #d4af37 !important; box-shadow: 0 4px 15px rgba(0,0,0,0.4) !important; }
        body.theme-luxury .crimson-btn:hover { background: linear-gradient(135deg, #1a1a1a, #222) !important; border-color: rgba(212, 175, 55, 0.8) !important; color: #fef3c7 !important; transform: translateY(-2px); }
        body.theme-luxury .tab-active { background: rgba(212, 175, 55, 0.05) !important; border: 1px solid rgba(212, 175, 55, 0.4) !important; color: #d4af37 !important; box-shadow: none !important; }
        body.theme-luxury .tab-inactive { border: 1px solid rgba(255, 255, 255, 0.03) !important; }
        body.theme-luxury .bg-video { opacity: 0 !important; visibility: hidden; }
        body.theme-luxury .video-overlay { background: transparent !important; }
        body.theme-luxury #aura-controls { opacity: 0; pointer-events: none; transform: translate(-50%, 20px); }
        
        /* Adapting internal text colors for Luxury mode */
        body.theme-luxury .text-red-400, body.theme-luxury .text-amber-400 { color: #94a3b8 !important; }
        body.theme-luxury .text-red-500 { color: #d4af37 !important; }
    </style>
</head>
<body class="p-4">

    <div id="cinematic-flash"></div>

    <video id="bg-vid" autoplay muted loop playsinline class="bg-video">
        <source src="https://subczjjxgexeraofhykl.supabase.co/storage/v1/object/public/Assets/From%20Klickpin.com-%20Natural%20Makeup%20Looks%20Inspiration%20for%20Summer-pin-id-587860557652168444.mp4" type="video/mp4">
    </video>
    <div class="video-overlay"></div>

    <button onclick="toggleDomainExpansion()" id="theme-btn" class="fixed top-5 right-5 md:top-8 md:right-8 z-[100] bg-black/60 p-4 rounded-full border border-yellow-500/50 text-yellow-500 shadow-[0_0_15px_rgba(212,175,55,0.4)] transition-all hover:scale-110">
        <i id="theme-icon" class="fa-solid fa-crown text-xl transition-all"></i>
    </button>

    <div id="aura-controls" class="fixed bottom-8 left-1/2 transform -translate-x-1/2 z-[100] flex gap-4 bg-black/50 py-2 px-5 border border-red-900/50 rounded-full backdrop-blur-md transition-all duration-500" style="border-color: inherit;">
        <button onclick="switchAura(0)" id="dot-0" class="w-3 h-3 rounded-full bg-red-500 shadow-[0_0_10px_red] transition-all hover:scale-125"></button>
        <button onclick="switchAura(1)" id="dot-1" class="w-3 h-3 rounded-full bg-white/20 hover:bg-blue-500 transition-all hover:scale-125"></button>
        <button onclick="switchAura(2)" id="dot-2" class="w-3 h-3 rounded-full bg-white/20 hover:bg-purple-500 transition-all hover:scale-125"></button>
    </div>

    <button onclick="toggleAudio()" class="audio-btn shadow-lg hover:scale-110"><i id="audio-icon" class="fa-solid fa-volume-xmark text-lg"></i></button>

    <div id="dashboard-viewport" class="w-full max-w-6xl flex-col relative z-10 flex mt-4 md:mt-0">
        
        <div class="w-full flex flex-col md:flex-row justify-between items-center mb-6 px-4">
            <div class="text-center md:text-left mb-4 md:mb-0">
                <h1 class="anime-title text-3xl md:text-4xl font-black text-red-500 mb-1" id="main-title">HOOK FORGE</h1>
                <p class="text-[9px] tracking-[0.4em] text-red-300 uppercase"><i class="fa-solid fa-user-shield mr-1"></i> <span id="user-display">Founder</span></p>
            </div>
            
            <div class="flex space-x-3 bg-black/40 p-1.5 rounded-xl border border-red-900/50 backdrop-blur-sm transition-colors" id="tab-container">
                <button id="tab-hook" onclick="switchMode('hook')" class="tab-btn tab-active"><i class="fa-solid fa-fire mr-1"></i> Hook Forge</button>
                <button id="tab-script" onclick="switchMode('script')" class="tab-btn tab-inactive"><i class="fa-solid fa-scroll mr-1"></i> Script Forge</button>
            </div>
        </div>

        <div id="errorBox" class="hidden bg-red-900/80 border border-red-500 text-white p-3 rounded mb-4 text-xs font-mono w-full"></div>

        <div class="flex flex-col lg:flex-row gap-6 w-full items-stretch">
            
            <div class="glass-panel w-full lg:max-w-md p-6 flex flex-col justify-between">
                
                <div id="inputs-hook" class="space-y-4">
                    <div>
                        <label class="block text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1" id="lbl-niche">Niche</label>
                        <input type="text" id="h-niche" value="Anime & Tech" class="w-full crimson-input rounded-lg px-4 py-3 text-sm">
                    </div>
                    <div>
                        <label class="block text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1" id="lbl-aud">Audience</label>
                        <input type="text" id="h-audience" value="Creators" class="w-full crimson-input rounded-lg px-4 py-3 text-sm">
                    </div>
                    <div>
                        <label class="block text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1" id="lbl-tone">Tone Matrix</label>
                        <select id="h-tone" class="w-full crimson-input rounded-lg px-4 py-3 text-sm">
                            <option value="Curious">Curiosity Gap</option>
                            <option value="Aggressive">Brutally Honest</option>
                            <option value="Controversial">Controversial / Polarizing</option>
                            <option value="Minimalist">Minimalist / Straight to Point</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1" id="lbl-top">Topic</label>
                        <textarea id="h-topic" rows="3" class="w-full crimson-input rounded-lg px-4 py-3 text-sm resize-none" placeholder="Enter core concept..."></textarea>
                    </div>
                </div>

                <div id="inputs-script" class="hidden space-y-4 flex-grow flex flex-col">
                    <p class="text-[10px] tracking-widest text-red-300/80 uppercase border-b border-red-900/50 pb-2 mb-2 transition-colors" id="lbl-transform">Transform raw script into highly retained viral content.</p>
                    
                    <div>
                        <label class="block text-[10px] font-bold tracking-widest uppercase text-red-500 mb-1" id="lbl-url"><i class="fa-solid fa-crosshairs mr-1"></i> Target Competitor URL (Optional)</label>
                        <input type="url" id="s-url" class="w-full crimson-input rounded-lg px-4 py-3 text-sm mb-2" placeholder="Paste YouTube/Insta link to snipe...">
                    </div>

                    <div class="flex-grow flex flex-col">
                        <label class="block text-[10px] font-bold tracking-widest uppercase text-amber-400 mb-1" id="lbl-raw"><i class="fa-solid fa-code mr-1"></i> Raw Script Input</label>
                        <textarea id="s-raw" class="w-full flex-grow min-h-[250px] crimson-input rounded-lg px-4 py-3 text-sm resize-none" placeholder="Paste your boring, unoptimized script here..."></textarea>
                    </div>
                </div>

                <button onclick="igniteEngine()" id="btn-ignite" class="w-full crimson-btn py-4 rounded-lg font-bold tracking-widest uppercase text-xs mt-6">
                    <i class="fa-solid fa-fire mr-2"></i> Ignite Hook Engine
                </button>
            </div>

            <div class="glass-panel flex-grow p-6 flex flex-col justify-center min-h-[500px]">
                <div id="loading" class="hidden text-center">
                    <i id="loading-icon" class="fa-solid fa-spinner fa-spin text-5xl text-red-500 mb-4 drop-shadow-[0_0_15px_rgba(220,38,38,0.8)]"></i>
                    <h2 id="loading-text" class="anime-title text-2xl text-red-100 transition-colors">Extracting Matrix...</h2>
                </div>

                <div id="empty-state" class="text-center opacity-50">
                    <i class="fa-solid fa-crosshairs text-6xl text-red-500/50 mb-4 transition-colors" id="empty-icon"></i>
                    <p id="empty-text" class="text-xs font-mono tracking-widest uppercase">Awaiting Target Parameters...</p>
                </div>

                <div id="results-hook" class="hidden space-y-5 overflow-y-auto max-h-[620px] pr-2">
                    <div class="bg-black/40 border border-red-500/20 p-5 rounded-xl transition-colors">
                        <div class="flex justify-between items-center mb-3">
                            <span class="text-[10px] bg-red-950/80 text-red-300 border border-red-800 px-2 py-0.5 rounded font-bold uppercase tracking-wider transition-colors">Option A</span>
                            <span class="text-[10px] text-red-400 font-black tracking-widest transition-colors">SCORE: <span id="scoreA" class="text-red-500 text-base"></span></span>
                        </div>
                        <h3 id="textA" class="text-base md:text-lg font-bold text-amber-50 mb-3 tracking-wide transition-colors"></h3>
                        <button onclick="copyText('textA')" class="mt-3 text-[10px] uppercase tracking-widest text-red-400 hover:text-white transition-all"><i class="fa-regular fa-copy mr-1"></i> Copy</button>
                    </div>

                    <div class="bg-black/40 border border-amber-500/20 p-5 rounded-xl transition-colors">
                        <div class="flex justify-between items-center mb-3">
                            <span class="text-[10px] bg-amber-950/80 text-amber-300 border border-amber-800 px-2 py-0.5 rounded font-bold uppercase tracking-wider transition-colors">Option B</span>
                            <span class="text-[10px] text-amber-400 font-black tracking-widest transition-colors">SCORE: <span id="scoreB" class="text-amber-500 text-base"></span></span>
                        </div>
                        <h3 id="textB" class="text-base md:text-lg font-bold text-amber-50 mb-3 tracking-wide transition-colors"></h3>
                        <button onclick="copyText('textB')" class="mt-3 text-[10px] uppercase tracking-widest text-amber-400 hover:text-white transition-all"><i class="fa-regular fa-copy mr-1"></i> Copy</button>
                    </div>
                </div>

                <div id="results-script" class="hidden space-y-5 overflow-y-auto max-h-[620px] pr-2">
                    <div class="bg-black/40 border border-red-500/20 p-5 rounded-xl flex justify-between items-center transition-colors">
                        <div>
                            <h3 class="text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1 transition-colors">Viral Retention Score</h3>
                        </div>
                        <div class="text-4xl font-black text-amber-500 drop-shadow-[0_0_10px_rgba(245,158,11,0.5)] transition-colors">
                            <span id="s-score"></span><span class="text-lg text-amber-500/50">/100</span>
                        </div>
                    </div>

                    <div class="bg-black/40 border border-red-500/20 p-5 rounded-xl relative transition-colors">
                        <span class="text-[10px] bg-red-950/80 text-red-300 border border-red-800 px-2 py-0.5 rounded font-bold uppercase tracking-wider mb-3 inline-block transition-colors">Master Script</span>
                        <p id="s-master" class="text-sm text-amber-50 leading-relaxed font-mono whitespace-pre-line transition-colors"></p>
                        <button onclick="copyText('s-master')" class="mt-4 text-[10px] uppercase tracking-widest text-red-400 hover:text-white transition-all"><i class="fa-regular fa-copy mr-1"></i> Copy Script</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentMode = 'hook';
        let isMuted = true;
        let isLuxuryMode = false;

        // MULTIVERSE VIDEOS
        const videos = [
            "https://subczjjxgexeraofhykl.supabase.co/storage/v1/object/public/Assets/From%20Klickpin.com-%20Natural%20Makeup%20Looks%20Inspiration%20for%20Summer-pin-id-587860557652168444.mp4",
            "https://subczjjxgexeraofhykl.supabase.co/storage/v1/object/public/Assets/your_name.mp4",
            "https://subczjjxgexeraofhykl.supabase.co/storage/v1/object/public/Assets/From%20Klickpin.com-%20From%20beginner%20to%20obsessed%20Love%20these%20easy%20pet-friendly%20home%20ideas%20youll%20want%20to%20recreate%20this%20weekend%20that%20balance%20trend%20comfor%20(1).mp4"
        ];

        function playCinematicTransition(callback) {
            const flash = document.getElementById('cinematic-flash');
            // Fade to black
            flash.style.opacity = '1';
            
            setTimeout(() => {
                // Execute the UI changes while screen is black
                callback();
                
                // Wait a tiny bit for video to buffer the first frame, then fade back in
                setTimeout(() => {
                    flash.style.opacity = '0';
                }, 150);
            }, 400); // 400ms is the duration of the fade-out
        }

        function switchAura(index) {
            if (isLuxuryMode) return; // Disable aura switch if in luxury mode
            
            playCinematicTransition(() => {
                const vid = document.getElementById('bg-vid');
                vid.src = videos[index];
                vid.play();
                
                // Remove old aura classes
                document.body.classList.remove('theme-aura-1', 'theme-aura-2');
                
                // Apply new aura class
                if(index === 1) document.body.classList.add('theme-aura-1');
                if(index === 2) document.body.classList.add('theme-aura-2');
                
                // Update dots UI
                const dot0 = document.getElementById('dot-0');
                const dot1 = document.getElementById('dot-1');
                const dot2 = document.getElementById('dot-2');
                
                // Reset all dots
                dot0.className = 'w-3 h-3 rounded-full bg-white/20 hover:bg-red-500 transition-all hover:scale-125';
                dot1.className = 'w-3 h-3 rounded-full bg-white/20 hover:bg-blue-500 transition-all hover:scale-125';
                dot2.className = 'w-3 h-3 rounded-full bg-white/20 hover:bg-purple-500 transition-all hover:scale-125';
                
                // Activate selected dot
                if(index === 0) dot0.className = 'w-3 h-3 rounded-full bg-red-500 shadow-[0_0_10px_red] transition-all hover:scale-125';
                if(index === 1) dot1.className = 'w-3 h-3 rounded-full bg-blue-500 shadow-[0_0_10px_blue] transition-all hover:scale-125';
                if(index === 2) dot2.className = 'w-3 h-3 rounded-full bg-purple-500 shadow-[0_0_10px_purple] transition-all hover:scale-125';
            });
        }

        function toggleDomainExpansion() {
            playCinematicTransition(() => {
                const body = document.body;
                const icon = document.getElementById('theme-icon');
                const themeBtn = document.getElementById('theme-btn');
                
                isLuxuryMode = !isLuxuryMode;
                
                if (isLuxuryMode) {
                    body.classList.add('theme-luxury');
                    icon.className = 'fa-solid fa-eye text-xl'; // Turns to Eye
                    themeBtn.className = 'fixed top-5 right-5 md:top-8 md:right-8 z-[100] bg-black/60 p-4 rounded-full border border-red-500/50 text-red-500 shadow-[0_0_15px_rgba(255,0,0,0.4)] transition-all hover:scale-110';
                    document.getElementById('empty-icon').classList.replace('text-red-500/50', 'text-[#d4af37]');
                } else {
                    body.classList.remove('theme-luxury');
                    icon.className = 'fa-solid fa-crown text-xl'; // Turns to Crown
                    themeBtn.className = 'fixed top-5 right-5 md:top-8 md:right-8 z-[100] bg-black/60 p-4 rounded-full border border-yellow-500/50 text-yellow-500 shadow-[0_0_15px_rgba(212,175,55,0.4)] transition-all hover:scale-110';
                    document.getElementById('empty-icon').classList.replace('text-[#d4af37]', 'text-red-500/50');
                }
            });
        }

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

            if(isLuxuryMode) {
                document.getElementById('loading-icon').classList.replace('text-red-500', 'text-[#d4af37]');
                document.getElementById('loading-text').classList.replace('text-red-100', 'text-[#d4af37]');
            } else {
                document.getElementById('loading-icon').classList.replace('text-[#d4af37]', 'text-red-500');
                document.getElementById('loading-text').classList.replace('text-[#d4af37]', 'text-red-100');
            }

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

                if (data.error) throw new Error(data.error);

                if (currentMode === 'hook') {
                    document.getElementById('scoreA').innerText = data.hook_a.score;
                    document.getElementById('textA').innerText = `"${data.hook_a.text}"`;
                    document.getElementById('scoreB').innerText = data.hook_b.score;
                    document.getElementById('textB').innerText = `"${data.hook_b.text}"`;
                    document.getElementById('results-hook').style.display = 'block';
                } else {
                    document.getElementById('s-score').innerText = data.retention_score;
                    document.getElementById('s-master').innerText = data.master_script;
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
