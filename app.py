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

# ==========================================
# ROBUST COMBINED MASTER FRONTEND
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
        
        /* SHARP, CLEAR VIDEO BACKGROUND (No blur, no dark overlay) */
        .bg-video {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            object-fit: cover; z-index: 0; pointer-events: none;
            transition: opacity 0.3s ease-in-out, transform 0.5s ease-out;
            transform-origin: center;
        }
        .video-switch-anim {
            opacity: 0 !important; transform: scale(1.05); /* The "Warp Fade" instead of black screen */
        }
        .video-overlay {
            position: fixed; inset: 0; background: rgba(0, 0, 0, 0.05); z-index: 1; pointer-events: none; /* Almost invisible so video pops */
        }
        
        /* STRONG GLASS PANEL TO KEEP TEXT READABLE */
        .glass-panel {
            background: rgba(0, 0, 0, 0.65); /* Darker panel so video behind it doesn't wash out text */
            backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 50, 50, 0.4); border-radius: 24px;
            box-shadow: 0 40px 80px rgba(0,0,0,0.95);
            transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .anime-title { font-family: 'Cinzel', serif; text-shadow: 0 0 30px rgba(255, 20, 20, 1); transition: all 0.5s ease; }
        .crimson-input { background: rgba(0, 0, 0, 0.7); border: 1px solid rgba(220, 38, 38, 0.35); color: #fef3c7; transition: all 0.3s; }
        .crimson-input:focus { outline: none; border-color: #ef4444; box-shadow: 0 0 20px rgba(239, 68, 68, 0.4); }
        
        /* SHOCKWAVE / BUTTON RIPPLE EFFECT CSS */
        .crimson-btn { 
            position: relative; overflow: hidden;
            background: linear-gradient(45deg, #7f1d1d, #dc2626); border: 1px solid #ef4444; 
            box-shadow: 0 0 20px rgba(220, 38, 38, 0.5); transition: all 0.3s ease; 
        }
        .crimson-btn:hover { background: linear-gradient(45deg, #991b1b, #f87171); box-shadow: 0 0 30px rgba(220, 38, 38, 0.8); transform: translateY(-2px); }
        
        .shockwave {
            position: absolute; background: rgba(255, 255, 255, 0.6); border-radius: 50%;
            transform: scale(0); animation: ripple 0.6s linear; pointer-events: none;
        }
        @keyframes ripple { to { transform: scale(4); opacity: 0; } }

        /* DOPAMINE SCORE PULSE ANIMATION */
        @keyframes scoreLock {
            0% { transform: scale(1); text-shadow: 0 0 10px rgba(245,158,11,0.5); }
            50% { transform: scale(1.4); text-shadow: 0 0 40px rgba(245,158,11,1); color: #fff; }
            100% { transform: scale(1); text-shadow: 0 0 15px rgba(245,158,11,0.8); }
        }
        .score-animate { animation: scoreLock 0.5s ease-out; }

        .audio-btn { position: fixed; bottom: 20px; right: 20px; z-index: 100; background: rgba(0,0,0,0.6); padding: 12px; border-radius: 50%; border: 1px solid rgba(255,50,50,0.4); color: #ef4444; transition: all 0.3s; }
        .tab-btn { padding: 10px 20px; font-size: 10px; font-weight: bold; letter-spacing: 0.2em; text-transform: uppercase; border-radius: 8px; transition: all 0.3s; }
        .tab-active { background: rgba(220, 38, 38, 0.2); border: 1px solid #ef4444; color: #fef3c7; box-shadow: 0 0 15px rgba(220,38,38,0.4); }
        .tab-inactive { background: rgba(0, 0, 0, 0.5); border: 1px solid rgba(255,50,50,0.2); color: rgba(254, 243, 199, 0.5); }

        /* AURA 1 & 2 SYSTEMS */
        body.theme-aura-1 .glass-panel { border-color: rgba(50, 150, 255, 0.5); }
        body.theme-aura-1 .anime-title { color: #60a5fa !important; text-shadow: 0 0 30px rgba(50, 150, 255, 0.8); }
        body.theme-aura-1 .crimson-btn { background: linear-gradient(45deg, #1e3a8a, #2563eb); border-color: #3b82f6; box-shadow: 0 0 20px rgba(59, 130, 246, 0.5); }
        body.theme-aura-1 .text-red-400, body.theme-aura-1 .text-red-500 { color: #60a5fa !important; }
        body.theme-aura-1 .tab-active { background: rgba(59, 130, 246, 0.2); border-color: #3b82f6; box-shadow: 0 0 15px rgba(59, 130, 246, 0.4); }
        body.theme-aura-1 #multiverse-btn { border-color: #3b82f6; color: #3b82f6; box-shadow: 0 0 15px rgba(59,130,246,0.5); }

        body.theme-aura-2 .glass-panel { border-color: rgba(168, 85, 247, 0.5); }
        body.theme-aura-2 .anime-title { color: #c084fc !important; text-shadow: 0 0 30px rgba(168, 85, 247, 0.8); }
        body.theme-aura-2 .crimson-btn { background: linear-gradient(45deg, #581c87, #9333ea); border-color: #a855f7; box-shadow: 0 0 20px rgba(168, 85, 247, 0.5); }
        body.theme-aura-2 .text-red-400, body.theme-aura-2 .text-red-500 { color: #c084fc !important; }
        body.theme-aura-2 .tab-active { background: rgba(168, 85, 247, 0.2); border-color: #a855f7; box-shadow: 0 0 15px rgba(168, 85, 247, 0.4); }
        body.theme-aura-2 #multiverse-btn { border-color: #a855f7; color: #a855f7; box-shadow: 0 0 15px rgba(168,85,247,0.5); }

        /* NEW LUXURY ENTERPRISE MODE (Apple/Vercel Style - Pure Black, White Glow) */
        body.theme-luxury { background: #050505; color: #fff; font-family: 'Inter', sans-serif; }
        body.theme-luxury .glass-panel { background: #0a0a0a !important; backdrop-filter: none !important; border: 1px solid rgba(255,255,255,0.1) !important; box-shadow: 0 20px 50px rgba(0,0,0,1) !important; }
        body.theme-luxury .anime-title { font-family: 'Inter', sans-serif !important; font-weight: 800 !important; letter-spacing: 0.05em !important; text-shadow: 0 0 20px rgba(255,255,255,0.2) !important; color: #fff !important; }
        body.theme-luxury .crimson-input { background: #111 !important; border: 1px solid rgba(255, 255, 255, 0.15) !important; color: #fff !important; }
        body.theme-luxury .crimson-input:focus { border-color: #fff !important; }
        body.theme-luxury .crimson-btn { background: #fff !important; border: none !important; color: #000 !important; font-weight: 800 !important; box-shadow: 0 4px 15px rgba(255,255,255,0.2) !important; }
        body.theme-luxury .crimson-btn:hover { background: #e5e5e5 !important; box-shadow: 0 6px 20px rgba(255,255,255,0.4) !important; }
        body.theme-luxury .tab-active { background: #fff !important; border: none !important; color: #000 !important; }
        body.theme-luxury .tab-inactive { border: 1px solid rgba(255, 255, 255, 0.1) !important; color: #888 !important; }
        body.theme-luxury .bg-video { opacity: 0 !important; visibility: hidden; }
        body.theme-luxury .video-overlay { background: transparent !important; }
        body.theme-luxury .text-red-400, body.theme-luxury .text-amber-400, body.theme-luxury .text-red-500 { color: #fff !important; }
        body.theme-luxury .border-red-500\/20, body.theme-luxury .border-amber-500\/20 { border-color: rgba(255,255,255,0.1) !important; background: #111 !important; }
        
        /* HIDE MULTIVERSE BUTTON IN LUXURY MODE */
        body.theme-luxury #multiverse-btn { opacity: 0; pointer-events: none; }
    </style>
</head>
<body class="p-4">

    <video id="bg-vid" autoplay muted loop playsinline class="bg-video">
        <source src="https://subczjjxgexeraofhykl.supabase.co/storage/v1/object/public/Assets/From%20Klickpin.com-%20Natural%20Makeup%20Looks%20Inspiration%20for%20Summer-pin-id-587860557652168444.mp4" type="video/mp4">
    </video>
    <div class="video-overlay"></div>

    <button onclick="toggleDomainExpansion(event)" id="theme-btn" class="fixed top-5 right-5 md:top-8 md:right-8 z-[100] bg-black/60 p-4 rounded-full border border-yellow-500/50 text-yellow-500 shadow-[0_0_15px_rgba(212,175,55,0.4)] transition-all hover:scale-110 overflow-hidden">
        <i id="theme-icon" class="fa-solid fa-crown text-xl transition-all"></i>
    </button>

    <button onclick="cycleAura(event)" id="multiverse-btn" class="fixed bottom-8 left-1/2 transform -translate-x-1/2 z-[100] bg-black/60 p-4 rounded-full border border-red-500 text-red-500 shadow-[0_0_15px_rgba(255,0,0,0.5)] transition-all hover:scale-110 overflow-hidden">
        <i class="fa-solid fa-infinity text-2xl"></i>
    </button>

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
                        <label class="block text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1">Niche</label>
                        <input type="text" id="h-niche" value="Anime & Tech" class="w-full crimson-input rounded-lg px-4 py-3 text-sm">
                    </div>
                    <div>
                        <label class="block text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1">Audience</label>
                        <input type="text" id="h-audience" value="Creators" class="w-full crimson-input rounded-lg px-4 py-3 text-sm">
                    </div>
                    <div>
                        <label class="block text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1">Tone Matrix</label>
                        <select id="h-tone" class="w-full crimson-input rounded-lg px-4 py-3 text-sm">
                            <option value="Curious">Curiosity Gap</option>
                            <option value="Aggressive">Brutally Honest</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1">Topic</label>
                        <textarea id="h-topic" rows="3" class="w-full crimson-input rounded-lg px-4 py-3 text-sm resize-none" placeholder="Enter core concept..."></textarea>
                    </div>
                </div>

                <div id="inputs-script" class="hidden space-y-4 flex-grow flex flex-col">
                    <p class="text-[10px] tracking-widest text-red-300/80 uppercase border-b border-red-900/50 pb-2 mb-2 transition-colors">Transform raw script into highly retained viral content.</p>
                    <div>
                        <label class="block text-[10px] font-bold tracking-widest uppercase text-red-500 mb-1"><i class="fa-solid fa-crosshairs mr-1"></i> Target URL</label>
                        <input type="url" id="s-url" class="w-full crimson-input rounded-lg px-4 py-3 text-sm mb-2" placeholder="Paste YouTube/Insta link...">
                    </div>
                    <div class="flex-grow flex flex-col">
                        <label class="block text-[10px] font-bold tracking-widest uppercase text-amber-400 mb-1"><i class="fa-solid fa-code mr-1"></i> Raw Script Input</label>
                        <textarea id="s-raw" class="w-full flex-grow min-h-[250px] crimson-input rounded-lg px-4 py-3 text-sm resize-none" placeholder="Paste script..."></textarea>
                    </div>
                </div>

                <button onclick="createShockwave(event); igniteEngine();" id="btn-ignite" class="w-full crimson-btn py-4 rounded-lg font-bold tracking-widest uppercase text-xs mt-6 overflow-hidden">
                    <i class="fa-solid fa-fire mr-2"></i> Ignite Hook Engine
                </button>
            </div>

            <div class="glass-panel flex-grow p-6 flex flex-col justify-center min-h-[500px]">
                <div id="loading" class="hidden text-center">
                    <i id="loading-icon" class="fa-solid fa-spinner fa-spin text-5xl text-red-500 mb-4 drop-shadow-[0_0_15px_rgba(220,38,38,0.8)]"></i>
                    <h2 id="loading-text" class="anime-title text-2xl text-red-100">Extracting Matrix...</h2>
                </div>

                <div id="empty-state" class="text-center opacity-50">
                    <i class="fa-solid fa-crosshairs text-6xl text-red-500/50 mb-4" id="empty-icon"></i>
                    <p id="empty-text" class="text-xs font-mono tracking-widest uppercase">Awaiting Target Parameters...</p>
                </div>

                <div id="results-hook" class="hidden space-y-5 overflow-y-auto max-h-[620px] pr-2">
                    <div class="bg-black/40 border border-red-500/20 p-5 rounded-xl">
                        <div class="flex justify-between items-center mb-3">
                            <span class="text-[10px] bg-red-950/80 text-red-300 border border-red-800 px-2 py-0.5 rounded font-bold uppercase tracking-wider">Option A</span>
                            <span class="text-[10px] text-red-400 font-black tracking-widest">SCORE: <span id="scoreA" class="text-red-500 text-base"></span></span>
                        </div>
                        <h3 id="textA" class="text-base md:text-lg font-bold text-amber-50 mb-3 tracking-wide"></h3>
                        <button onclick="copyText('textA')" class="mt-3 text-[10px] uppercase tracking-widest text-red-400 hover:text-white transition-all"><i class="fa-regular fa-copy mr-1"></i> Copy</button>
                    </div>
                </div>

                <div id="results-script" class="hidden space-y-5 overflow-y-auto max-h-[620px] pr-2">
                    <div class="bg-black/40 border border-red-500/20 p-5 rounded-xl flex justify-between items-center">
                        <div>
                            <h3 class="text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1">Viral Retention Score</h3>
                        </div>
                        <div class="text-4xl font-black text-amber-500 drop-shadow-[0_0_10px_rgba(245,158,11,0.5)]">
                            <span id="s-score" class="inline-block">0</span><span class="text-lg text-amber-500/50">/100</span>
                        </div>
                    </div>

                    <div class="bg-black/40 border border-red-500/20 p-5 rounded-xl relative">
                        <span class="text-[10px] bg-red-950/80 text-red-300 border border-red-800 px-2 py-0.5 rounded font-bold uppercase tracking-wider mb-3 inline-block">Master Script</span>
                        <p id="s-master" class="text-sm text-amber-50 leading-relaxed font-mono whitespace-pre-line"></p>
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
        let currentAura = 0;

        const videos = [
            "https://subczjjxgexeraofhykl.supabase.co/storage/v1/object/public/Assets/From%20Klickpin.com-%20Natural%20Makeup%20Looks%20Inspiration%20for%20Summer-pin-id-587860557652168444.mp4",
            "https://subczjjxgexeraofhykl.supabase.co/storage/v1/object/public/Assets/your_name.mp4",
            "https://subczjjxgexeraofhykl.supabase.co/storage/v1/object/public/Assets/From%20Klickpin.com-%20From%20beginner%20to%20obsessed%20Love%20these%20easy%20pet-friendly%20home%20ideas%20youll%20want%20to%20recreate%20this%20weekend%20that%20balance%20trend%20comfor%20(1).mp4"
        ];

        // SHOCKWAVE / RIPPLE LOGIC
        function createShockwave(e) {
            const btn = e.currentTarget;
            const circle = document.createElement('span');
            const diameter = Math.max(btn.clientWidth, btn.clientHeight);
            const radius = diameter / 2;
            
            circle.style.width = circle.style.height = `${diameter}px`;
            circle.style.left = `${e.clientX - btn.getBoundingClientRect().left - radius}px`;
            circle.style.top = `${e.clientY - btn.getBoundingClientRect().top - radius}px`;
            circle.classList.add('shockwave');
            
            const oldShockwave = btn.getElementsByClassName('shockwave')[0];
            if (oldShockwave) oldShockwave.remove();
            
            btn.appendChild(circle);
        }

        // DOPAMINE SLOT MACHINE
        function animateScore(targetValue) {
            const scoreEl = document.getElementById('s-score');
            scoreEl.classList.remove('score-animate'); 
            let startValue = 0;
            let duration = 1200; 
            let startTime = null;

            function step(timestamp) {
                if (!startTime) startTime = timestamp;
                const progress = Math.min((timestamp - startTime) / duration, 1);
                const currentScore = Math.floor(progress * (targetValue - startValue) + startValue);
                scoreEl.innerText = currentScore;
                
                if (progress < 1) {
                    window.requestAnimationFrame(step);
                } else {
                    scoreEl.innerText = targetValue;
                    scoreEl.classList.add('score-animate'); 
                }
            }
            window.requestAnimationFrame(step);
        }

        // WARP FADE (NO BLACK SCREEN)
        function playWarpTransition(callback) {
            const vid = document.getElementById('bg-vid');
            vid.classList.add('video-switch-anim'); // Fades video out smoothly
            setTimeout(() => {
                callback();
                setTimeout(() => { vid.classList.remove('video-switch-anim'); }, 100);
            }, 300);
        }

        function cycleAura(e) {
            if (isLuxuryMode) return;
            createShockwave(e);
            
            currentAura = (currentAura + 1) % videos.length;
            
            playWarpTransition(() => {
                const vid = document.getElementById('bg-vid');
                vid.src = videos[currentAura];
                vid.play();
                
                document.body.classList.remove('theme-aura-1', 'theme-aura-2');
                const btn = document.getElementById('multiverse-btn');
                
                if(currentAura === 1) {
                    document.body.classList.add('theme-aura-1');
                    btn.className = 'fixed bottom-8 left-1/2 transform -translate-x-1/2 z-[100] bg-black/60 p-4 rounded-full border border-blue-500 text-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.5)] transition-all hover:scale-110 overflow-hidden';
                } else if(currentAura === 2) {
                    document.body.classList.add('theme-aura-2');
                    btn.className = 'fixed bottom-8 left-1/2 transform -translate-x-1/2 z-[100] bg-black/60 p-4 rounded-full border border-purple-500 text-purple-500 shadow-[0_0_15px_rgba(168,85,247,0.5)] transition-all hover:scale-110 overflow-hidden';
                } else {
                    btn.className = 'fixed bottom-8 left-1/2 transform -translate-x-1/2 z-[100] bg-black/60 p-4 rounded-full border border-red-500 text-red-500 shadow-[0_0_15px_rgba(255,0,0,0.5)] transition-all hover:scale-110 overflow-hidden';
                }
            });
        }

        function toggleDomainExpansion(e) {
            createShockwave(e); 
            playWarpTransition(() => {
                const body = document.body;
                const icon = document.getElementById('theme-icon');
                const themeBtn = document.getElementById('theme-btn');
                
                isLuxuryMode = !isLuxuryMode;
                
                if (isLuxuryMode) {
                    body.classList.add('theme-luxury');
                    icon.className = 'fa-solid fa-eye text-xl';
                    themeBtn.className = 'fixed top-5 right-5 md:top-8 md:right-8 z-[100] bg-black/60 p-4 rounded-full border border-white/50 text-white shadow-[0_0_15px_rgba(255,255,255,0.4)] transition-all hover:scale-110 overflow-hidden';
                    document.getElementById('empty-icon').classList.replace('text-red-500/50', 'text-white/50');
                } else {
                    body.classList.remove('theme-luxury');
                    icon.className = 'fa-solid fa-crown text-xl';
                    themeBtn.className = 'fixed top-5 right-5 md:top-8 md:right-8 z-[100] bg-black/60 p-4 rounded-full border border-yellow-500/50 text-yellow-500 shadow-[0_0_15px_rgba(212,175,55,0.4)] transition-all hover:scale-110 overflow-hidden';
                    document.getElementById('empty-icon').classList.replace('text-white/50', 'text-red-500/50');
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
        }

        async function igniteEngine() {
            document.getElementById('empty-state').style.display = 'none';
            document.getElementById('results-hook').style.display = 'none';
            document.getElementById('results-script').style.display = 'none';
            document.getElementById('errorBox').style.display = 'none';
            document.getElementById('loading').style.display = 'block';

            try {
                let endpoint = currentMode === 'hook' ? '/forge_hook' : '/forge_script';
                let payloadData = currentMode === 'hook' ? {
                    niche: document.getElementById('h-niche').value, audience: document.getElementById('h-audience').value,
                    tone: document.getElementById('h-tone').value, topic: document.getElementById('h-topic').value
                } : {
                    script: document.getElementById('s-raw').value, url: document.getElementById('s-url').value
                };

                const res = await fetch(endpoint, {
                    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payloadData)
                });

                const data = await res.json();
                document.getElementById('loading').style.display = 'none';

                if (data.error) throw new Error(data.error);

                if (currentMode === 'hook') {
                    document.getElementById('scoreA').innerText = data.hook_a.score; document.getElementById('textA').innerText = `"${data.hook_a.text}"`;
                    document.getElementById('results-hook').style.display = 'block';
                } else {
                    document.getElementById('results-script').style.display = 'block';
                    animateScore(data.retention_score);
                    document.getElementById('s-master').innerText = data.master_script;
                }
            } catch (err) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('errorBox').innerText = "ERROR: " + err.message;
                document.getElementById('errorBox').style.display = 'block';
            }
        }
        function copyText(id) { navigator.clipboard.writeText(document.getElementById(id).innerText); }
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
    payload = {"model": "Meta-Llama-3.3-70B-Instruct", "messages": [{"role": "system", "content": HOOK_SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}]}
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
            res = requests.get(target_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            title_tag = re.search(r'<title>(.*?)</title>', res.text, re.IGNORECASE)
            video_title = title_tag.group(1) if title_tag else "this viral competitor content"
            sniper_intel = f"\n\n🚨 TARGET ACQUIRED: Crush competitor video titled '{video_title}'."
        except:
            sniper_intel = f"\n\n🚨 TARGET URL ACQUIRED: {target_url}."
    
    payload = {"model": "Meta-Llama-3.3-70B-Instruct", "messages": [{"role": "system", "content": SCRIPT_SYSTEM_PROMPT}, {"role": "user", "content": raw_script + sniper_intel}]}
    try:
        r = requests.post(SAMBANOVA_URL, json=payload, headers={"Authorization": f"Bearer {SAMBANOVA_API_KEY}", "Content-Type": "application/json"})
        content = r.json()['choices'][0]['message']['content'].strip()
        if content.startswith("
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1

### 💥 Final Checks (Bhai ka naya system):
* **Video ab ekdum raw & sharp hai** (Blur/Darkness hata diya gaya hai, har frame clear dikhega).
* **Warp Fade:** Black screen khatam! Ab video smooth scale/zoom hokar dusri video mein cross-fade ho jayegi.
* **Vercel/Apple Premium Mode:** Jab tu Crown (👑) dabayega, pura app pitch-black `#000` aur pure white glowing borders mein badal jayega. No tacky gold, sirf high-end professional look.
* **Single Portal Button:** 3 dots gaye! Ab bottom par ek "Infinity (∞)" button hai. Usko click karte ja, animations ke saath sab badal jayega. Uske pichhe ka glow bhi theme ke saath badlega (Red -> Blue -> Purple).
* **Shockwave + Slot Machine Done:** Button par Shockwave aayega aur Score spinner ekdum lock-pulse karega.

Deploy maar isko aur bata! Ye ab sach mein ek **$100M Enterprise tool** lag raha hoga. 🔥🚀
