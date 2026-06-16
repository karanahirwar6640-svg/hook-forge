import os
import json
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
SAMBANOVA_URL = "https://api.sambanova.ai/v1/chat/completions"

SYSTEM_PROMPT = """
You are Hook Forge v2.0, an elite social media psychologist, data scientist, and master copywriter. 
Your job is to generate high-converting hooks and analyze them deeply.
You must ALWAYS respond in valid JSON format. Do not write any markdown prose outside the JSON.

The user will provide: Topic, Niche, Audience, and Tone.
You must output exactly this JSON structure:
{
  "hook_a": {
    "text": "The first viral hook text",
    "score": 8,
    "reasoning": "What exactly to change/add to make this an absolute 10/10 actionable fix",
    "psychology": "Deep psychological breakdown. Explain triggers used like Curiosity Gap, FOMO, or Loss Aversion."
  },
  "hook_b": {
    "text": "The second distinct viral hook text using a completely different psychological angle",
    "score": 9,
    "reasoning": "Actionable fix to polish it to 10/10",
    "psychology": "Psychological breakdown and emotional triggers used."
  },
  "dna_comparison": "A brutal, data-backed comparison of Hook A vs Hook B. Explain exactly which audience sub-segment or platform dynamic will favor which hook."
}
"""

HTML_UI = """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hook Forge - Premium Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        obsidian: '#0b0b0f',
                        cybercard: '#14141a',
                        cyberborder: '#22222a',
                        lightbg: '#f8f9fa',
                        lightcard: '#ffffff',
                        lightborder: '#eef0f2'
                    }
                }
            }
        }
    </script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { font-family: '-apple-system', BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; transition: background-color 0.3s, color 0.3s; }
        .tab-btn.active { color: #f97316; border-bottom: 2px solid #f97316; }
        .hide-scrollbar::-webkit-scrollbar { display: none; }
        .hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
    </style>
</head>
<body class="bg-lightbg text-slate-800 dark:bg-obsidian dark:text-zinc-200 min-h-screen flex flex-col">

    <header class="bg-white dark:bg-cybercard border-b border-lightborder dark:border-cyberborder px-4 py-3.5 sticky top-0 z-50 transition-colors">
        <div class="max-w-3xl mx-auto flex items-center justify-between">
            <div class="flex items-center space-x-2.5">
                <div class="bg-gradient-to-tr from-orange-600 to-amber-500 p-2 rounded-xl text-white shadow-md shadow-orange-500/10 flex items-center justify-center w-9 h-9">
                    <i class="fa-solid fa-fire-burner text-sm"></i>
                </div>
                <div>
                    <h1 class="text-base font-black tracking-tight text-slate-900 dark:text-white">HOOK FORGE</h1>
                    <p class="text-[10px] text-slate-400 dark:text-zinc-500 font-bold tracking-wider uppercase -mt-0.5">SaaS Engine v2.0</p>
                </div>
            </div>
            
            <button onclick="toggleTheme()" class="w-9 h-9 rounded-xl flex items-center justify-center bg-slate-100 dark:bg-zinc-900 text-slate-500 dark:text-zinc-400 hover:text-orange-500 dark:hover:text-orange-400 transition-all">
                <i id="theme-icon" class="fa-solid fa-moon text-sm"></i>
            </button>
        </div>
    </header>

    <div class="bg-white dark:bg-cybercard border-b border-lightborder dark:border-cyberborder sticky top-[65px] z-40 transition-colors">
        <div class="max-w-3xl mx-auto flex overflow-x-auto hide-scrollbar px-2">
            <button onclick="switchTab('forge-tab')" id="btn-forge-tab" class="tab-btn active whitespace-nowrap px-4 py-3 text-sm font-bold text-slate-500 dark:text-zinc-400 transition-colors flex items-center space-x-1.5">
                <i class="fa-solid fa-wand-magic-sparkles text-xs"></i>
                <span>Studio</span>
            </button>
            <button onclick="switchTab('persona-tab')" id="btn-persona-tab" class="tab-btn whitespace-nowrap px-4 py-3 text-sm font-bold text-slate-500 dark:text-zinc-400 transition-colors flex items-center space-x-1.5">
                <i class="fa-solid fa-user-gear text-xs"></i>
                <span>Persona</span>
            </button>
            <button onclick="switchTab('vault-tab')" id="btn-vault-tab" class="tab-btn whitespace-nowrap px-4 py-3 text-sm font-bold text-slate-500 dark:text-zinc-400 transition-colors flex items-center space-x-1.5">
                <i class="fa-solid fa-vault text-xs"></i>
                <span>Vault</span>
            </button>
            <button onclick="switchTab('trends-tab')" id="btn-trends-tab" class="tab-btn whitespace-nowrap px-4 py-3 text-sm font-bold text-slate-500 dark:text-zinc-400 transition-colors flex items-center space-x-1.5">
                <i class="fa-solid fa-arrow-trend-up text-xs"></i>
                <span>Trends</span>
            </button>
        </div>
    </div>

    <main class="flex-1 max-w-2xl w-full mx-auto p-4 md:py-8 space-y-6 overflow-y-auto">

        <div id="forge-tab" class="tab-content space-y-6">
            
            <div id="errorBox" class="hidden bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/50 text-red-700 dark:text-red-300 p-4 rounded-2xl text-xs font-mono break-all flex items-start space-x-2.5">
                <i class="fa-solid fa-triangle-exclamation text-red-500 text-sm mt-0.5"></i>
                <span id="errorText"></span>
            </div>

            <div class="bg-white dark:bg-cybercard border border-lightborder dark:border-cyberborder rounded-2xl p-5 space-y-4 shadow-sm transition-colors">
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-[10px] font-black text-slate-400 dark:text-zinc-500 uppercase tracking-wider mb-1.5">Niche</label>
                        <input type="text" id="niche" value="Tech & AI Business" class="w-full bg-slate-50 dark:bg-obsidian border border-slate-200 dark:border-zinc-800 rounded-xl px-3 py-2.5 text-xs font-semibold focus:outline-none focus:border-orange-500 dark:focus:border-orange-500 focus:ring-1 focus:ring-orange-500/20 transition-all">
                    </div>
                    <div>
                        <label class="block text-[10px] font-black text-slate-400 dark:text-zinc-500 uppercase tracking-wider mb-1.5">Audience</label>
                        <input type="text" id="audience" value="Creators & Hustlers" class="w-full bg-slate-50 dark:bg-obsidian border border-slate-200 dark:border-zinc-800 rounded-xl px-3 py-2.5 text-xs font-semibold focus:outline-none focus:border-orange-500 dark:focus:border-orange-500 focus:ring-1 focus:ring-orange-500/20 transition-all">
                    </div>
                </div>
                
                <div>
                    <label class="block text-[10px] font-black text-slate-400 dark:text-zinc-500 uppercase tracking-wider mb-1.5">Psychological Angle</label>
                    <select id="tone" class="w-full bg-slate-50 dark:bg-obsidian border border-slate-200 dark:border-zinc-800 rounded-xl px-3 py-2.5 text-xs font-semibold focus:outline-none focus:border-orange-500 dark:focus:border-orange-500 transition-all">
                        <option value="Curious" selected>Curious (Curiosity Gap)</option>
                        <option value="Aggressive">Aggressive (Brutally Honest)</option>
                        <option value="Storytelling">Storytelling (Narrative)</option>
                        <option value="FOMO">Urgent (Loss Aversion)</option>
                    </select>
                </div>

                <div>
                    <label class="block text-[10px] font-black text-slate-400 dark:text-zinc-500 uppercase tracking-wider mb-1.5">Core Topic</label>
                    <textarea id="topic" rows="3" placeholder="e.g., Kaise bina kisi laptop ke phone se AI software banayein..." class="w-full bg-slate-50 dark:bg-obsidian border border-slate-200 dark:border-zinc-800 rounded-xl px-3 py-2.5 text-xs font-semibold focus:outline-none focus:border-orange-500 dark:focus:border-orange-500 focus:ring-1 focus:ring-orange-500/20 transition-all resize-none"></textarea>
                </div>

                <button onclick="forgeHooks()" class="w-full bg-gradient-to-r from-orange-600 to-amber-500 text-white font-bold text-xs py-3.5 px-4 rounded-xl shadow-md shadow-orange-600/10 hover:opacity-95 active:scale-[0.99] transition-all flex items-center justify-center space-x-2">
                    <i class="fa-solid fa-bolt-lightning text-xs"></i>
                    <span>FORGE AI INSIGHTS</span>
                </button>
            </div>

            <div id="loading" class="hidden bg-white dark:bg-cybercard border border-lightborder dark:border-cyberborder rounded-2xl p-10 text-center space-y-3 shadow-sm transition-colors">
                <div class="inline-block relative w-9 h-9">
                    <div class="absolute inset-0 rounded-full border-3 border-slate-100 dark:border-zinc-800"></div>
                    <div class="absolute inset-0 rounded-full border-3 border-t-orange-500 animate-spin"></div>
                </div>
                <p class="text-xs font-bold text-orange-500 dark:text-orange-400 tracking-wide">🔨 Forging premium psychology matrix...</p>
            </div>

            <div id="results" class="hidden space-y-5">
                
                <div class="bg-white dark:bg-cybercard border border-lightborder dark:border-cyberborder rounded-2xl p-5 shadow-sm relative transition-colors">
                    <div class="flex items-center justify-between border-b border-slate-100 dark:border-zinc-800/60 pb-3 mb-4">
                        <span class="text-[10px] font-black tracking-wider px-2.5 py-1 rounded-lg bg-orange-50 text-orange-600 dark:bg-orange-500/10 dark:text-orange-400 border border-orange-100 dark:border-orange-500/10">OPTION A</span>
                        <div class="flex items-center space-x-1.5">
                            <span class="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase">Score:</span>
                            <span id="scoreA" class="bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-black text-xs px-2 py-0.5 rounded-md"></span>
                        </div>
                    </div>
                    
                    <div id="textA" class="text-slate-900 dark:text-white text-base font-bold leading-snug mb-4 select-all bg-slate-50 dark:bg-obsidian border border-slate-100 dark:border-zinc-800/40 p-3.5 rounded-xl"></div>
                    
                    <div class="space-y-3 text-xs">
                        <div class="p-3 rounded-xl bg-slate-50 dark:bg-obsidian/40 border border-slate-100 dark:border-zinc-800/40">
                            <span class="block font-black text-orange-500 text-[10px] uppercase tracking-wider mb-1"><i class="fa-solid fa-brain mr-1.5"></i>Psychology Explainer</span>
                            <p id="psychA" class="text-slate-600 dark:text-zinc-400 leading-relaxed font-medium"></p>
                        </div>
                        <div class="p-3 rounded-xl bg-slate-50 dark:bg-obsidian/40 border border-slate-100 dark:border-zinc-800/40">
                            <span class="block font-black text-amber-500 text-[10px] uppercase tracking-wider mb-1"><i class="fa-solid fa-wand-magic text-mr-1.5"></i>Actionable Fix (To Make it 10/10)</span>
                            <p id="fixA" class="text-slate-600 dark:text-zinc-400 leading-relaxed font-medium"></p>
                        </div>
                    </div>
                    
                    <div class="mt-4 flex justify-end">
                        <button onclick="copyText('textA')" class="bg-slate-100 dark:bg-zinc-900 hover:bg-slate-200 dark:hover:bg-zinc-800 text-slate-700 dark:text-zinc-300 text-[11px] font-bold px-3 py-2 rounded-xl flex items-center space-x-1.5 transition-all"><i class="fa-regular fa-copy"></i> <span>Copy Hook</span></button>
                    </div>
                </div>

                <div class="bg-white dark:bg-cybercard border border-lightborder dark:border-cyberborder rounded-2xl p-5 shadow-sm relative transition-colors">
                    <div class="flex items-center justify-between border-b border-slate-100 dark:border-zinc-800/60 pb-3 mb-4">
                        <span class="text-[10px] font-black tracking-wider px-2.5 py-1 rounded-lg bg-indigo-50 text-indigo-600 dark:bg-indigo-500/10 dark:text-indigo-400 border border-indigo-100 dark:border-indigo-500/10">OPTION B</span>
                        <div class="flex items-center space-x-1.5">
                            <span class="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase">Score:</span>
                            <span id="scoreB" class="bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-black text-xs px-2 py-0.5 rounded-md"></span>
                        </div>
                    </div>
                    
                    <div id="textB" class="text-slate-900 dark:text-white text-base font-bold leading-snug mb-4 select-all bg-slate-50 dark:bg-obsidian border border-slate-100 dark:border-zinc-800/40 p-3.5 rounded-xl"></div>
                    
                    <div class="space-y-3 text-xs">
                        <div class="p-3 rounded-xl bg-slate-50 dark:bg-obsidian/40 border border-slate-100 dark:border-zinc-800/40">
                            <span class="block font-black text-indigo-500 text-[10px] uppercase tracking-wider mb-1"><i class="fa-solid fa-brain mr-1.5"></i>Psychology Explainer</span>
                            <p id="psychB" class="text-slate-600 dark:text-zinc-400 leading-relaxed font-medium"></p>
                        </div>
                        <div class="p-3 rounded-xl bg-slate-50 dark:bg-obsidian/40 border border-slate-100 dark:border-zinc-800/40">
                            <span class="block font-black text-amber-500 text-[10px] uppercase tracking-wider mb-1"><i class="fa-solid fa-wand-magic mr-1.5"></i>Actionable Fix (To Make it 10/10)</span>
                            <p id="fixB" class="text-slate-600 dark:text-zinc-400 leading-relaxed font-medium"></p>
                        </div>
                    </div>
                    
                    <div class="mt-4 flex justify-end">
                        <button onclick="copyText('textB')" class="bg-slate-100 dark:bg-zinc-900 hover:bg-slate-200 dark:hover:bg-zinc-800 text-slate-700 dark:text-zinc-300 text-[11px] font-bold px-3 py-2 rounded-xl flex items-center space-x-1.5 transition-all"><i class="fa-regular fa-copy"></i> <span>Copy Hook</span></button>
                    </div>
                </div>

                <div class="bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-purple-950/10 dark:to-indigo-950/10 border border-purple-100 dark:border-purple-900/30 rounded-2xl p-4.5 shadow-sm transition-all">
                    <div class="flex items-center space-x-2 mb-2 text-purple-600 dark:text-purple-400 font-black text-[10px] tracking-wider uppercase">
                        <i class="fa-solid fa-dna text-xs animate-pulse"></i>
                        <span>A/B DNA Comparison Matrix</span>
                    </div>
                    <p id="dna" class="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed font-medium"></p>
                </div>
                
            </div>
        </div>

        <div id="persona-tab" class="tab-content hidden">
            <div class="bg-white dark:bg-cybercard border border-lightborder dark:border-cyberborder rounded-2xl p-5 shadow-sm text-center text-slate-400 dark:text-zinc-500 py-12 transition-colors">
                <i class="fa-solid fa-user-gear text-3xl mb-3 text-slate-300 dark:text-zinc-700"></i>
                <h3 class="text-sm font-bold text-slate-800 dark:text-zinc-300">Creator Persona Vault</h3>
                <p class="text-xs max-w-xs mx-auto mt-1 leading-relaxed">Phase 3 Deployment Notice: Permanent online database connection incoming. Settings will lock here.</p>
            </div>
        </div>

        <div id="vault-tab" class="tab-content hidden">
            <div class="bg-white dark:bg-cybercard border border-lightborder dark:border-cyberborder rounded-2xl p-5 shadow-sm text-center text-slate-400 dark:text-zinc-500 py-12 transition-colors">
                <i class="fa-solid fa-vault text-3xl mb-3 text-slate-300 dark:text-zinc-700"></i>
                <h3 class="text-sm font-bold text-slate-800 dark:text-zinc-300">Personal Vault Library</h3>
                <p class="text-xs max-w-xs mx-auto mt-1 leading-relaxed">Pattern metrics analytics dashboard will go live as soon as database connects.</p>
            </div>
        </div>

        <div id="trends-tab" class="tab-content hidden">
            <div class="bg-white dark:bg-cybercard border border-lightborder dark:border-cyberborder rounded-2xl p-5 shadow-sm text-center text-slate-400 dark:text-zinc-500 py-12 transition-colors">
                <i class="fa-solid fa-arrow-trend-up text-3xl mb-3 text-slate-300 dark:text-zinc-700"></i>
                <h3 class="text-sm font-bold text-slate-800 dark:text-zinc-300">Trend Hijack Engine</h3>
                <p class="text-xs max-w-xs mx-auto mt-1 leading-relaxed">Bridge global web trends instantly. Active engine incoming in Next Phase.</p>
            </div>
        </div>

    </main>

    <script>
        function initTheme() {
            if (localStorage.getItem('theme') === 'light') {
                document.documentElement.classList.remove('dark');
                document.getElementById('theme-icon').className = "fa-solid fa-sun text-orange-500";
            } else {
                document.documentElement.classList.add('dark');
                document.getElementById('theme-icon').className = "fa-solid fa-moon text-zinc-400";
            }
        }
        
        function toggleTheme() {
            if (document.documentElement.classList.contains('dark')) {
                document.documentElement.classList.remove('dark');
                localStorage.setItem('theme', 'light');
                document.getElementById('theme-icon').className = "fa-solid fa-sun text-orange-500";
            } else {
                document.documentElement.classList.add('dark');
                localStorage.setItem('theme', 'dark');
                document.getElementById('theme-icon').className = "fa-solid fa-moon text-zinc-400";
            }
        }
        
        initTheme();

        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            
            document.getElementById(tabId).classList.remove('hidden');
            document.getElementById('btn-' + tabId).classList.add('active');
        }

        async function forgeHooks() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').style.display = 'none';
            document.getEl
