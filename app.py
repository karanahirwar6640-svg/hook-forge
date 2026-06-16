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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hook Forge | Crimson Anime Edition</title>
    <script src="https://cdn.tailwindcss.com"></script>
    
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700;900&family=Noto+Sans+JP:wght@300;400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        body {
            margin: 0;
            min-height: 100vh;
            font-family: 'Noto Sans JP', sans-serif;
            /* Yahan teri di hui Chisato ki image background me set ki hai */
            background-image: url('https://i.pinimg.com/originals/39/db/e2/39dbe266fbd4af345a049536b52e306a.jpg');
            background-size: cover;
            background-position: center right;
            background-attachment: fixed;
            background-color: #1a0505;
            color: #fef3c7; /* Warm cream color text */
        }

        /* Red Glassmorphism Panel */
        .glass-panel {
            background: rgba(15, 2, 2, 0.75); /* Dark translucent red/black */
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-right: 1px solid rgba(220, 38, 38, 0.2);
            box-shadow: 10px 0 30px rgba(0,0,0,0.7);
        }

        .glass-card {
            background: rgba(30, 5, 5, 0.6);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(220, 38, 38, 0.3);
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            transition: all 0.3s ease;
        }

        .glass-card:hover {
            border-color: rgba(220, 38, 38, 0.6);
            box-shadow: 0 0 20px rgba(220, 38, 38, 0.2);
        }

        /* Anime Title Font */
        .anime-title {
            font-family: 'Cinzel', serif;
            letter-spacing: 0.15em;
            text-shadow: 0 0 15px rgba(220, 38, 38, 0.8);
        }

        /* Inputs */
        .crimson-input {
            background: rgba(20, 0, 0, 0.5);
            border: 1px solid rgba(220, 38, 38, 0.3);
            color: #fef3c7;
            transition: all 0.3s;
        }
        .crimson-input:focus {
            outline: none;
            border-color: #ef4444;
            box-shadow: 0 0 15px rgba(239, 68, 68, 0.3);
            background: rgba(40, 0, 0, 0.7);
        }
        
        select.crimson-input option { background: #1a0505; color: #fef3c7; }

        /* Button */
        .crimson-btn {
            background: linear-gradient(45deg, #7f1d1d, #b91c1c);
            border: 1px solid #ef4444;
            box-shadow: 0 0 15px rgba(185, 28, 28, 0.4);
            transition: all 0.3s ease;
        }
        .crimson-btn:hover {
            background: linear-gradient(45deg, #991b1b, #dc2626);
            box-shadow: 0 0 25px rgba(220, 38, 38, 0.7);
            transform: translateY(-2px);
        }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: rgba(0,0,0,0.5); }
        ::-webkit-scrollbar-thumb { background: #991b1b; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: #dc2626; }

        .fade-in { animation: fadeIn 0.5s ease-in; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body class="flex flex-col md:flex-row overflow-hidden">

    <aside class="w-full md:w-5/12 lg:w-1/3 h-screen glass-panel overflow-y-auto flex flex-col p-6 md:p-8 relative z-20">
        
        <div class="mb-8 mt-4 text-center md:text-left">
            <h1 class="anime-title text-4xl font-black text-red-500 mb-1">HOOK FORGE</h1>
            <p class="text-xs tracking-[0.3em] text-red-300/70 uppercase">Crimson Protocol</p>
        </div>

        <div class="space-y-5 flex-1">
            <div id="errorBox" class="hidden bg-red-950/80 border border-red-500 text-red-200 p-3 rounded-lg text-xs font-mono shadow-lg shadow-red-900/50"></div>

            <div class="space-y-4">
                <div>
                    <label class="block text-[10px] font-bold tracking-widest uppercase text-red-400/80 mb-1.5">Target Niche</label>
                    <input type="text" id="niche" value="Anime & Tech" class="w-full crimson-input rounded-lg px-4 py-3 text-sm">
                </div>
                <div>
                    <label class="block text-[10px] font-bold tracking-widest uppercase text-red-400/80 mb-1.5">Audience</label>
                    <input type="text" id="audience" value="Weebs & Creators" class="w-full crimson-input rounded-lg px-4 py-3 text-sm">
                </div>
                <div>
                    <label class="block text-[10px] font-bold tracking-widest uppercase text-red-400/80 mb-1.5">Psychological Tone</label>
                    <select id="tone" class="w-full crimson-input rounded-lg px-4 py-3 text-sm">
                        <option value="Curious">Curiosity Gap</option>
                        <option value="Aggressive">Brutally Honest</option>
                        <option value="Storytelling">Anime Protagonist Arc</option>
                    </select>
                </div>
                <div>
                    <label class="block text-[10px] font-bold tracking-widest uppercase text-red-400/80 mb-1.5">Core Content Topic</label>
                    <textarea id="topic" rows="3" placeholder="Apna idea yahan likho..." class="w-full crimson-input rounded-lg px-4 py-3 text-sm resize-none"></textarea>
                </div>
            </div>

            <button onclick="forgeHooks()" class="w-full crimson-btn mt-6 py-4 rounded-lg font-bold tracking-widest uppercase text-xs flex items-center justify-center space-x-2">
                <i class="fa-solid fa-fire"></i>
                <span>Ignite The Forge</span>
            </button>
        </div>

        <div class="mt-8 text-center md:text-left text-[10px] tracking-wider text-red-500/50 uppercase">
            <i class="fa-solid fa-shield-halved mr-1"></i> System Online • Llama 3 Engine
        </div>
    </aside>

    <main class="w-full md:w-7/12 lg:w-2/3 h-screen overflow-y-auto p-6 md:p-10 relative z-10 hide-scrollbar flex flex-col justify-center">
        
        <div id="loading" class="hidden text-center fade-in">
            <i class="fa-solid fa-circle-notch fa-spin text-5xl text-red-600 mb-4 drop-shadow-[0_0_15px_rgba(220,38,38,0.8)]"></i>
            <h2 class="anime-title text-2xl text-red-100">Extracting Psychology...</h2>
            <p class="text-sm text-red-300/70 mt-2 tracking-widest">Bridging neural pathways.</p>
        </div>

        <div id="results" class="hidden space-y-6 max-w-2xl ml-auto mr-auto md:ml-0 fade-in pb-20">
            
            <div class="glass-card p-6 relative overflow-hidden group">
                <div class="absolute top-0 left-0 w-1 h-full bg-red-600 shadow-[0_0_10px_#dc2626]"></div>
                <div class="flex justify-between items-center mb-4">
                    <span class="text-[10px] font-bold tracking-widest bg-red-950/80 text-red-400 px-3 py-1 rounded border border-red-800/50 uppercase">Option A</span>
                    <span class="text-[10px] font-black tracking-widest text-red-200">POWER LEVEL: <span id="scoreA" class="text-red-500 text-lg"></span></span>
                </div>
                <h3 id="textA" class="text-xl md:text-2xl font-bold leading-relaxed mb-5 text-amber-50"></h3>
                
                <div class="space-y-3 pt-4 border-t border-red-900/50">
                    <div>
                        <span class="text-[10px] text-red-400 tracking-widest uppercase font-bold flex items-center"><i class="fa-solid fa-brain mr-2"></i>Psychology</span>
                        <p id="psychA" class="text-xs text-red-100/80 mt-1 leading-relaxed"></p>
                    </div>
                    <div>
                        <span class="text-[10px] text-red-400 tracking-widest uppercase font-bold flex items-center"><i class="fa-solid fa-wrench mr-2"></i>Actionable Fix</span>
                        <p id="fixA" class="text-xs text-red-100/80 mt-1 leading-relaxed"></p>
                    </div>
                </div>
                <button onclick="copyText('textA')" class="mt-4 bg-red-950/50 hover:bg-red-900/80 border border-red-800/50 text-red-200 text-[10px] tracking-widest uppercase px-4 py-2 rounded transition-all"><i class="fa-regular fa-copy mr-1"></i> Copy</button>
            </div>

            <div class="glass-card p-6 relative overflow-hidden group">
                <div class="absolute top-0 left-0 w-1 h-full bg-amber-500 shadow-[0_0_10px_#f59e0b]"></div>
                <div class="flex justify-between items-center mb-4">
                    <span class="text-[10px] font-bold tracking-widest bg-amber-950/80 text-amber-400 px-3 py-1 rounded border border-amber-800/50 uppercase">Option B</span>
                    <span class="text-[10px] font-black tracking-widest text-amber-200">POWER LEVEL: <span id="scoreB" class="text-amber-500 text-lg"></span></span>
                </div>
                <h3 id="textB" class="text-xl md:text-2xl font-bold leading-relaxed mb-5 text-amber-50"></h3>
                
                <div class="space-y-3 pt-4 border-t border-amber-900/30">
                    <div>
                        <span class="text-[10px] text-amber-500 tracking-widest uppercase font-bold flex items-center"><i class="fa-solid fa-brain mr-2"></i>Psychology</span>
                        <p id="psychB" class="text-xs text-red-100/80 mt-1 leading-relaxed"></p>
                    </div>
                    <div>
                        <span class="text-[10px] text-amber-500 tracking-widest uppercase font-bold flex items-center"><i class="fa-solid fa-wrench mr-2"></i>Actionable Fix</span>
                        <p id="fixB" class="text-xs text-red-100/80 mt-1 leading-relaxed"></p>
                    </div>
                </div>
                <button onclick="copyText('textB')" class="mt-4 bg-amber-950/30 hover:bg-amber-900/60 border border-amber-800/50 text-amber-200 text-[10px] tracking-widest uppercase px-4 py-2 rounded transition-all"><i class="fa-regular fa-copy mr-1"></i> Copy</button>
            </div>

            <div class="bg-red-950/40 border border-red-500/30 p-5 rounded-lg backdrop-blur-md">
                <div class="text-[10px] text-red-400 tracking-widest uppercase font-bold flex items-center mb-2">
                    <i class="fa-solid fa-dna mr-2 animate-pulse"></i> DNA Comparison Matrix
                </div>
                <p id="dna" class="text-xs text-red-100/90 leading-relaxed"></p>
            </div>

        </div>
    </main>

    <script>
        async function forgeHooks() {
            document.getElementById('results').style.display = 'none';
            document.getElementById('errorBox').style.display = 'none';
            document.getElementById('loading').style.display = 'block';
            
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
                    document.getElementById('errorBox').style.display = 'block';
                    document.getElementById('errorBox').innerText = "System Error: " + data.error;
                    return;
                }

                document.getElementById('textA').innerText = `"${data.hook_a.text}"`;
                document.getElementById('scoreA').innerText = data.hook_a.score;
                document.getElementById('psychA').innerText = data.hook_a.psychology;
                document.getElementById('fixA').innerText = data.hook_a.reasoning;

                document.getElementById('textB').innerText = `"${data.hook_b.text}"`;
                document.getElementById('scoreB').innerText = data.hook_b.score;
                document.getElementById('psychB').innerText = data.hook_b.psychology;
                document.getElementById('fixB').innerText = data.hook_b.reasoning;

                document.getElementById('dna').innerText = data.dna_comparison;
                
                document.getElementById('results').style.display = 'block';
                
            } catch(e) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('errorBox').style.display = 'block';
                document.getElementById('errorBox').innerText = "Network Fault: " + e.message;
            }
        }

        function copyText(elementId) {
            const text = document.getElementById(elementId).innerText.replace(/"/g, '');
            navigator.clipboard.writeText(text);
            alert("Hook acquired successfully! ⚔️");
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
            return jsonify({"error": f"SambaNova Status {r.status_code} | {r.text}"})
            
        res_data = r.json()
        ai_text = res_data['choices'][0]['message']['content'].strip()
        
        if ai_text.startswith("```json"):
            ai_text = ai_text.replace("```json", "", 1).strip()
            if ai_text.endswith("```"):
                ai_text = ai_text[:-3].strip()
                
        return jsonify(json.loads(ai_text))
        
    except requests.exceptions.Timeout:
        return jsonify({"error": "Gateway timeout hit."})
    except Exception as e: 
        return jsonify({"error": f"Backend Runtime: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
