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
                        darkbg: '#09090b',
                        darkcard: '#111113',
                        darkborder: '#27272a'
                    }
                }
            }
        }
    </script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { font-family: 'Inter', sans-serif; transition: background-color 0.3s ease, color 0.3s ease; }
        .sidebar-link.active { color: #f97316; border-right: 4px solid #f97316; }
        .dark .sidebar-link.active { background-color: #27272a; }
        .sidebar-link.active:not(.dark *) { background-color: #fff7ed; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #d4d4d8; border-radius: 10px; }
        .dark ::-webkit-scrollbar-thumb { background: #27272a; }
    </style>
</head>
<body class="bg-slate-50 text-slate-800 dark:bg-darkbg dark:text-[#f4f4f5] h-screen flex flex-col md:flex-row overflow-hidden transition-colors duration-300">

    <div class="w-full md:w-64 bg-white dark:bg-darkcard border-b md:border-b-0 md:border-r border-slate-200 dark:border-darkborder flex flex-col justify-between p-5 z-50 transition-colors duration-300">
        <div>
            <div class="flex items-center justify-between mb-8">
                <div class="flex items-center space-x-3">
                    <div class="bg-orange-500 p-2 rounded-lg text-white font-black text-xl flex items-center justify-center w-10 h-10 shadow-lg shadow-orange-500/20">
                        <i class="fa-solid fa-fire"></i>
                    </div>
                    <div>
                        <h1 class="text-lg font-bold tracking-wider text-slate-900 dark:text-white">HOOK FORGE</h1>
                        <span class="text-xs text-slate-500 dark:text-zinc-500 font-medium">SaaS v2.0 Live</span>
                    </div>
                </div>
                
                <button onclick="toggleTheme()" class="text-slate-400 hover:text-orange-500 dark:text-zinc-500 dark:hover:text-orange-400 transition-colors w-8 h-8 rounded-full flex items-center justify-center bg-slate-100 dark:bg-zinc-800">
                    <i id="theme-icon" class="fa-solid fa-moon"></i>
                </button>
            </div>
            
            <nav class="space-y-2">
                <button onclick="switchTab('forge-tab')" id="btn-forge-tab" class="sidebar-link active w-full flex items-center space-x-3 px-4 py-3 text-slate-600 dark:text-zinc-400 rounded-lg text-sm font-semibold transition-all hover:bg-slate-100 dark:hover:bg-zinc-800/50">
                    <i class="fa-solid fa-wand-magic-sparkles text-base w-5"></i>
                    <span>Forge Studio</span>
                </button>
                <button onclick="switchTab('persona-tab')" id="btn-persona-tab" class="sidebar-link w-full flex items-center space-x-3 px-4 py-3 text-slate-600 dark:text-zinc-400 rounded-lg text-sm font-semibold transition-all hover:bg-slate-100 dark:hover:bg-zinc-800/50">
                    <i class="fa-solid fa-user-gear text-base w-5"></i>
                    <span>Creator Persona</span>
                </button>
                <button onclick="switchTab('vault-tab')" id="btn-vault-tab" class="sidebar-link w-full flex items-center space-x-3 px-4 py-3 text-slate-600 dark:text-zinc-400 rounded-lg text-sm font-semibold transition-all hover:bg-slate-100 dark:hover:bg-zinc-800/50">
                    <i class="fa-solid fa-vault text-base w-5"></i>
                    <span>Hook Vault</span>
                </button>
                <button onclick="switchTab('trends-tab')" id="btn-trends-tab" class="sidebar-link w-full flex items-center space-x-3 px-4 py-3 text-slate-600 dark:text-zinc-400 rounded-lg text-sm font-semibold transition-all hover:bg-slate-100 dark:hover:bg-zinc-800/50">
                    <i class="fa-solid fa-arrow-trend-up text-base w-5"></i>
                    <span>Trend Hijack</span>
                </button>
            </nav>
        </div>
        <div class="pt-4 border-t border-slate-200 dark:border-darkborder text-xs text-slate-500 dark:text-zinc-500 flex items-center justify-between">
            <span>Status: Premium Client</span>
            <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
        </div>
    </div>

    <div class="flex-1 flex flex-col overflow-y-auto p-4 md:p-8">
        
        <div id="forge-tab" class="tab-content space-y-6">
            <div class="border-b border-slate-200 dark:border-zinc-800 pb-4 transition-colors">
                <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Forge Studio</h2>
                <p class="text-sm text-slate-500 dark:text-zinc-400">Generate hooks backed by deep social psychology analytics.</p>
            </div>

            <div id="errorBox" class="hidden bg-red-100 dark:bg-red-950/50 border border-red-400 dark:border-red-500 text-red-700 dark:text-red-200 p-4 rounded-xl text-sm font-mono break-all flex items-start space-x-3 transition-colors">
                <i class="fa-solid fa-circle-exclamation text-red-500 text-lg mt-0.5"></i>
                <span id="errorText"></span>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
                <div class="lg:col-span-1 bg-white dark:bg-darkcard border border-slate-200 dark:border-darkborder rounded-xl p-5 space-y-4 shadow-lg transition-colors">
                    <div>
                        <label class="block text-xs font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider mb-2">Niche</label>
                        <input type="text" id="niche" value="Tech & AI Business" class="w-full bg-slate-50 dark:bg-darkbg border border-slate-300 dark:border-zinc-800 rounded-lg px-3 py-2.5 text-sm text-slate-900 dark:text-white focus:outline-none focus:border-orange-500 dark:focus:border-orange-500 transition-colors">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider mb-2">Target Audience</label>
                        <input type="text" id="audience" value="Young Creators & Hustlers" class="w-full bg-slate-50 dark:bg-darkbg border border-slate-300 dark:border-zinc-800 rounded-lg px-3 py-2.5 text-sm text-slate-900 dark:text-white focus:outline-none focus:border-orange-500 dark:focus:border-orange-500 transition-colors">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider mb-2">Psychological Tone</label>
                        <select id="tone" class="w-full bg-slate-50 dark:bg-darkbg border border-slate-300 dark:border-zinc-800 rounded-lg px-3 py-2.5 text-sm text-slate-900 dark:text-white focus:outline-none focus:border-orange-500 dark:focus:border-orange-500 transition-colors">
                            <option value="Curious" selected>Curious (Curiosity Gap)</option>
                            <option value="Aggressive">Aggressive (Brutally Honest)</option>
                            <option value="Storytelling">Storytelling (Narrative Setup)</option>
                            <option value="FOMO">Urgent (Loss Aversion / FOMO)</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider mb-2">Core Content Topic</label>
                        <textarea id="topic" rows="3" placeholder="e.g., Kaise bina kisi laptop ke phone se AI software bana kar deploy karein..." class="w-full bg-slate-50 dark:bg-darkbg border border-slate-300 dark:border-zinc-800 rounded-lg px-3 py-2.5 text-sm text-slate-900 dark:text-white focus:outline-none focus:border-orange-500 dark:focus:border-orange-500 transition-colors resize-none"></textarea>
                    </div>
                    <button onclick="forgeHooks()" class="w-full bg-gradient-to-r from-orange-600 to-amber-500 text-white font-bold py-3 px-4 rounded-lg shadow-lg shadow-orange-600/20 hover:opacity-90 active:scale-[0.98] transition-all flex items-center justify-center space-x-2">
                        <i class="fa-solid fa-fire-burner"></i>
                        <span>Forge AI Hooks 🚀</span>
                    </button>
                </div>

                <div class="lg:col-span-2 space-y-6">
                    <div id="loading" class="hidden bg-white dark:bg-darkcard border border-slate-200 dark:border-zinc-800 rounded-xl p-12 text-center space-y-4 shadow-sm transition-colors">
                        <div class="inline-block relative w-12 h-12">
                            <div class="absolute inset-0 rounded-full border-4 border-slate-200 dark:border-zinc-800"></div>
                            <div class="absolute inset-0 rounded-full border-4 border-t-orange-500 animate-spin"></div>
                        </div>
                        <p class="text-sm font-semibold text-orange-500 dark:text-orange-400">🔨 Hook Psychology Analyze ho rahi hai... Sabr rakho bhai...</p>
                    </div>

                    <div id="results" class="hidden space-y-6">
                        <div class="bg-white dark:bg-darkcard border border-slate-200 dark:border-zinc-800 rounded-xl p-5 shadow-sm relative overflow-hidden transition-colors">
                            <div class="flex justify-between items-start mb-3">
                                <span class="bg-orange-100 dark:bg-orange-500/10 text-orange-600 dark:text-orange-400 text-xs font-bold px-2.5 py-1 rounded-md border border-orange-200 dark:border-orange-500/20">HOOK OPTION A</span>
                                <div class="flex items-center space-x-2">
                                    <span class="text-xs text-slate-500 dark:text-zinc-500">Scroll Stopper Score:</span>
                                    <span id="scoreA" class="bg-emerald-100 dark:bg-emerald-500 text-emerald-800 dark:text-black font-black text-xs px-2 py-0.5 rounded-full"></span>
                                </div>
                            </div>
                            <div id="textA" class="bg-slate-50 dark:bg-darkbg border border-slate-200 dark:border-zinc-800 p-4 rounded-lg text-lg font-bold text-slate-900 dark:text-white mb-4 select-all transition-colors"></div>
                            
                            <div class="space-y-2 text-sm border-t border-slate-100 dark:border-zinc-800/60 pt-3 transition-colors">
                                <p class="text-slate-600 dark:text-zinc-400"><strong class="text-orange-500 dark:text-orange-400/90"><i class="fa-solid fa-brain mr-1.5"></i>Psychology Explainer:</strong> <span id="psychA"></span></p>
                                <p class="text-slate-600 dark:text-zinc-400"><strong class="text-amber-500 dark:text-amber-400/90"><i class="fa-solid fa-wrench mr-1.5"></i>Actionable Fix for 10/10:</strong> <span id="fixA"></span></p>
                            </div>
                            <div class="mt-4 flex justify-end">
                                <button onclick="copyText('textA')" class="bg-slate-100 dark:bg-zinc-800 hover:bg-slate-200 dark:hover:bg-zinc-700 text-slate-700 dark:text-white text-xs font-bold px-3 py-1.5 rounded-md flex items-center space-x-1 transition-colors"><i class="fa-regular fa-copy"></i> <span>Copy Hook</span></button>
                            </div>
                        </div>

                        <div class="bg-white dark:bg-darkcard border border-slate-200 dark:border-zinc-800 rounded-xl p-5 shadow-sm relative overflow-hidden transition-colors">
                            <div class="flex justify-between items-start mb-3">
                                <span class="bg-indigo-100 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 text-xs font-bold px-2.5 py-1 rounded-md border border-indigo-200 dark:border-indigo-500/20">HOOK OPTION B</span>
                                <div class="flex items-center space-x-2">
                                    <span class="text-xs text-slate-500 dark:text-zinc-500">Scroll Stopper Score:</span>
                                    <span id="scoreB" class="bg-emerald-100 dark:bg-emerald-500 text-emerald-800 dark:text-black font-black text-xs px-2 py-0.5 rounded-full"></span>
                                </div>
                            </div>
                            <div id="textB" class="bg-slate-50 dark:bg-darkbg border border-slate-200 dark:border-zinc-800 p-4 rounded-lg text-lg font-bold text-slate-900 dark:text-white mb-4 select-all transition-colors"></div>
                            
                            <div class="space-y-2 text-sm border-t border-slate-100 dark:border-zinc-800/60 pt-3 transition-colors">
                                <p class="text-slate-600 dark:text-zinc-400"><strong class="text-indigo-500 dark:text-indigo-400/90"><i class="fa-solid fa-brain mr-1.5"></i>Psychology Explainer:</strong> <span id="psychB"></span></p>
                                <p class="text-slate-600 dark:text-zinc-400"><strong class="text-amber-500 dark:text-amber-400/90"><i class="fa-solid fa-wrench mr-1.5"></i>Actionable Fix for 10/10:</strong> <span id="fixB"></span></p>
                            </div>
                            <div class="mt-4 flex justify-end">
                                <button onclick="copyText('textB')" class="bg-slate-100 dark:bg-zinc-800 hover:bg-slate-200 dark:hover:bg-zinc-700 text-slate-700 dark:text-white text-xs font-bold px-3 py-1.5 rounded-md flex items-center space-x-1 transition-colors"><i class="fa-regular fa-copy"></i> <span>Copy Hook</span></button>
                            </div>
                        </div>

                        <div class="bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-purple-950/20 dark:to-indigo-950/20 border border-purple-200 dark:border-purple-500/30 rounded-xl p-5 shadow-sm transition-colors">
                            <div class="flex items-center space-x-2 mb-3 text-purple-700 dark:text-purple-400 font-bold text-sm">
                                <i class="fa-solid fa-dna text-base"></i>
                                <span>A/B DNA COMPARISON INSIGHT</span>
                            </div>
                            <p id="dna" class="text-sm text-slate-700 dark:text-zinc-300 leading-relaxed"></p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div id="persona-tab" class="tab-content hidden space-y-4">
            <div class="border-b border-slate-200 dark:border-zinc-800 pb-4 transition-colors">
                <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Creator Persona Setup</h2>
                <p class="text-sm text-slate-500 dark:text-zinc-400">Save your profile so you never have to re-type your niche details.</p>
            </div>
            <div class="bg-white dark:bg-darkcard border border-slate-200 dark:border-zinc-800 rounded-xl p-6 max-w-xl shadow-sm transition-colors">
                <p class="text-slate-600 dark:text-zinc-400 text-sm mb-4"><i class="fa-solid fa-database text-orange-500 mr-2"></i><strong>Phase 3 Deployment Notice:</strong> Database connection incoming. Is page par tumhari permanent settings save hongi.</p>
                <div class="space-y-4 opacity-50 pointer-events-none">
                    <input type="text" placeholder="Default Brand Niche" class="w-full bg-slate-50 dark:bg-darkbg border border-slate-300 dark:border-zinc-800 rounded-lg px-3 py-2 text-sm">
                    <input type="text" placeholder="Default Audience Persona" class="w-full bg-slate-50 dark:bg-darkbg border border-slate-300 dark:border-zinc-800 rounded-lg px-3 py-2 text-sm">
                    <button class="bg-slate-800 dark:bg-zinc-700 font-bold py-2 px-4 rounded-lg text-sm text-white">Lock Persona 🔒</button>
                </div>
            </div>
        </div>

        <div id="vault-tab" class="tab-content hidden space-y-4">
            <div class="border-b border-slate-200 dark:border-zinc-800 pb-4 transition-colors">
                <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Hook Vault (Personal Library)</h2>
                <p class="text-sm text-slate-500 dark:text-zinc-400">Your personalized library that analyzes high-performing hook patterns.</p>
            </div>
            <div class="bg-white dark:bg-darkcard border border-slate-200 dark:border-zinc-800 rounded-xl p-6 text-center text-slate-500 dark:text-zinc-500 shadow-sm transition-colors">
                <i class="fa-solid fa-chart-line text-4xl mb-3 text-slate-300 dark:text-zinc-700"></i>
                <p class="text-sm font-medium">Jaise hi hum Database jodenge, yahan tumhare saved hooks ka pattern analytics live ho jayega!</p>
            </div>
        </div>

        <div id="trends-tab" class="tab-content hidden space-y-4">
            <div class="border-b border-slate-200 dark:border-zinc-800 pb-4 transition-colors">
                <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Trend Hijack Engine</h2>
                <p class="text-sm text-slate-500 dark:text-zinc-400">Bridge trending global internet topics with your specific industry niche instantly.</p>
            </div>
            <div class="bg-white dark:bg-darkcard border border-slate-200 dark:border-zinc-800 rounded-xl p-6 max-w-xl space-y-4 shadow-sm transition-colors">
                <p class="text-xs text-orange-600 dark:text-orange-400 font-semibold uppercase tracking-wider"><i class="fa-solid fa-bolt mr-1.5"></i>Viral Bridge Mode</p>
                <div>
                    <label class="block text-xs text-slate-500 dark:text-zinc-400 mb-2 font-bold">What is trending right now?</label>
                    <input type="text" id="trendInput" placeholder="e.g., Apple Vision Pro 2 Launch, IPL Super Over..." class="w-full bg-slate-50 dark:bg-darkbg border border-slate-300 dark:border-zinc-800 rounded-lg px-3 py-2.5 text-sm text-slate-900 dark:text-white focus:outline-none focus:border-orange-500 transition-colors">
                </div>
                <button onclick="alert('Bhai, Next Phase me Trend Engine active hoga!')" class="bg-orange-600 font-bold py-2.5 px-4 rounded-lg text-sm text-white hover:bg-orange-500 transition-colors">Generate Trend-Hijack Hook 🚀</button>
            </div>
        </div>

    </div>

    <script>
        // THEME MANAGEMENT (Light / Dark Mode)
        function initTheme() {
            if (localStorage.getItem('theme') === 'light') {
                document.documentElement.classList.remove('dark');
                document.getElementById('theme-icon').className = "fa-solid fa-sun text-orange-500";
            } else {
                document.documentElement.classList.add('dark');
                document.getElementById('theme-icon').className = "fa-solid fa-moon";
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
                document.getElementById('theme-icon').className = "fa-solid fa-moon";
            }
        }
        
        initTheme();

        // TAB NAVIGATION
        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.sidebar-link').forEach(el => el.classList.remove('active'));
            
            document.getElementById(tabId).classList.remove('hidden');
            document.getElementById('btn-' + tabId).classList.add('active');
        }

        // API CALL FUNCTION
        async function forgeHooks() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').style.display = 'none';
            document.getElementById('errorBox').style.display = 'none';
            
            try {
                const res = await fetch('/forge', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        topic: document.getElementById('topic').value,
                        niche: document.getElementById('niche').value,
                        audience: document.getElementById('audience').value,
                        tone: document.getElementById('tone').value
                    })
                });
                
                const data = await res.json();
                document.getElementById('loading').style.display = 'none';
                
                if (data.error) {
                    document.getElementById('errorBox').style.removeProperty('display');
                    document.getElementById('errorBox').classList.remove('hidden');
                    document.getElementById('errorText').innerText = "SambaNova Pipeline Error: " + data.error;
                    return;
                }

                document.getElementById('textA').innerText = data.hook_a.text;
                document.getElementById('scoreA').innerText = data.hook_a.score + "/10";
                document.getElementById('psychA').innerText = data.hook_a.psychology;
                document.getElementById('fixA').innerText = data.hook_a.reasoning;

                document.getElementById('textB').innerText = data.hook_b.text;
                document.getElementById('scoreB').innerText = data.hook_b.score + "/10";
                document.getElementById('psychB').innerText = data.hook_b.psychology;
                document.getElementById('fixB').innerText = data.hook_b.reasoning;

                document.getElementById('dna').innerText = data.dna_comparison;
                
                document.getElementById('results').style.removeProperty('display');
                document.getElementById('results').classList.remove('hidden');
                
            } catch(e) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('errorBox').style.removeProperty('display');
                document.getElementById('errorBox').classList.remove('hidden');
                document.getElementById('errorText').innerText = "Frontend Dashboard Engine Fault: " + e.message;
            }
        }

        // COPY TO CLIPBOARD
        function copyText(elementId) {
            const text = document.getElementById(elementId).innerText;
            navigator.clipboard.writeText(text);
            alert("Hook copied to clipboard, Santosh bhai! 🔥");
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): 
    return render_template_string(HTML_UI)

@app.route('/forge', methods=['POST'])
def forge():
    data = request.json
    prompt = f"Topic: {data.get('topic')}\\nNiche: {data.get('niche')}\\nAudience: {data.get('audience')}\\nTone: {data.get('tone')}"
    
    payload = {
        "model": "Meta-Llama-3.3-70B-Instruct", 
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}], 
        "temperature": 0.7
    }
    
    headers = {"Authorization": f"Bearer {SAMBANOVA_API_KEY}", "Content-Type": "application/json"}
    
    try:
        r = requests.post(SAMBANOVA_URL, json=payload, headers=headers, timeout=15)
        
        if r.status_code != 200:
            return jsonify({"error": f"SambaNova Returned Status {r.status_code} | Details: {r.text}"})
            
        res_data = r.json()
        ai_text = res_data['choices'][0]['message']['content'].strip()
        
        if ai_text.startswith("```json"):
            ai_text = ai_text.replace("```json", "", 1).strip()
            if ai_text.endswith("```"):
                ai_text = ai_text[:-3].strip()
                
        return jsonify(json.loads(ai_text))
        
    except requests.exceptions.Timeout:
        return jsonify({"error": "SambaNova Gateway API timeout (15 Seconds Limit Hit)"})
    except Exception as e: 
        return jsonify({"error": f"Backend Runtime Exception: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
