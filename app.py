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
    <title>Hook Forge | Cinematic SaaS</title>
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Elegant Fonts matching the Reference Image -->
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Lato:wght@300;400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        :root {
            --dark-side: #584a5e; /* Deep elegant purple */
            --light-side: #f5eedc; /* Warm aesthetic beige */
            --text-light: #f5eedc;
            --text-dark: #3a2e3f;
        }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: 'Lato', sans-serif;
            overflow-x: hidden;
            /* The Diagonal Split Background */
            background: linear-gradient(180deg, var(--dark-side) 50%, var(--light-side) 50%);
        }

        @media (min-width: 768px) {
            body {
                background: linear-gradient(108deg, var(--dark-side) 50.5%, var(--light-side) 50.5%);
            }
        }

        /* 3D Parallax Container */
        .scene { perspective: 1000px; }
        .tilt-card {
            transform-style: preserve-3d;
            transition: transform 0.1s ease-out;
        }

        /* Typography */
        .font-serif-elegant { font-family: 'Playfair Display', serif; }
        
        .title-text {
            font-size: clamp(3rem, 6vw, 5rem);
            line-height: 1.1;
            letter-spacing: 0.1em;
            text-shadow: 2px 5px 15px rgba(0,0,0,0.2);
            transform: translateZ(40px); /* 3D pop out */
        }

        /* Glassmorphic Inputs & Buttons */
        .glass-input {
            background: rgba(255, 255, 255, 0.05);
            border: none;
            border-bottom: 1px solid rgba(245, 238, 220, 0.3);
            color: var(--text-light);
            transition: all 0.3s;
        }
        .glass-input:focus {
            outline: none;
            border-bottom: 1px solid rgba(245, 238, 220, 0.9);
            background: rgba(255, 255, 255, 0.1);
        }
        .glass-input::placeholder { color: rgba(245, 238, 220, 0.5); }
        
        select.glass-input option { background: var(--dark-side); color: var(--text-light); }

        .glass-btn {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: var(--text-light);
            transition: all 0.4s ease;
            transform: translateZ(30px);
        }
        .glass-btn:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateZ(35px) scale(1.02);
            box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.2); }

        /* Cinematic Loading Animation */
        .fade-pulse { animation: fadePulse 2s infinite; }
        @keyframes fadePulse {
            0% { opacity: 0.3; transform: scale(0.98); }
            50% { opacity: 1; transform: scale(1); }
            100% { opacity: 0.3; transform: scale(0.98); }
        }

        /* Result Cards on the Light Side */
        .light-card {
            background: transparent;
            border-left: 2px solid rgba(58, 46, 63, 0.2);
            padding-left: 1.5rem;
            transform: translateZ(20px);
        }
    </style>
</head>
<body class="text-white relative">

    <!-- Navbar -->
    <nav class="absolute top-0 w-full p-6 md:px-12 flex justify-between items-center z-50">
        <div class="flex space-x-6 text-sm tracking-widest uppercase font-bold text-[#f5eedc]">
            <a href="#" class="hover:opacity-70 transition">Studio</a>
            <a href="#" class="hover:opacity-70 transition">Persona</a>
            <a href="#" class="hover:opacity-70 transition border-b border-[#f5eedc]">Forge</a>
        </div>
        <button class="text-[#f5eedc] text-2xl hover:opacity-70"><i class="fa-solid fa-bars"></i></button>
    </nav>

    <!-- Main Content Split -->
    <main class="min-h-screen flex flex-col md:flex-row relative scene pt-24 md:pt-0">
        
        <!-- Left Side: Inputs (Dark Purple) -->
        <section class="w-full md:w-1/2 p-8 md:p-16 xl:p-24 flex flex-col justify-center relative z-10 tilt-card" id="left-card">
            
            <p class="font-serif-elegant italic text-lg opacity-80 mb-2 translate-z-10">2026 SaaS Engine</p>
            <h1 class="font-serif-elegant title-text mb-8">
                HOOK<br>FORGE.
            </h1>

            <div class="space-y-6 max-w-md transform translate-z-20">
                <div id="errorBox" class="hidden bg-red-900/40 border border-red-500/50 p-4 rounded text-xs tracking-wider"></div>

                <div class="grid grid-cols-2 gap-6">
                    <div>
                        <label class="block text-[10px] uppercase tracking-widest opacity-60 mb-2">Target Niche</label>
                        <input type="text" id="niche" value="Tech Business" class="w-full glass-input pb-2 text-sm">
                    </div>
                    <div>
                        <label class="block text-[10px] uppercase tracking-widest opacity-60 mb-2">Audience</label>
                        <input type="text" id="audience" value="Creators" class="w-full glass-input pb-2 text-sm">
                    </div>
                </div>

                <div>
                    <label class="block text-[10px] uppercase tracking-widest opacity-60 mb-2">Psychological Tone</label>
                    <select id="tone" class="w-full glass-input pb-2 text-sm">
                        <option value="Curious">Curiosity Gap</option>
                        <option value="Aggressive">Brutally Honest</option>
                        <option value="Storytelling">Narrative Story</option>
                    </select>
                </div>

                <div>
                    <label class="block text-[10px] uppercase tracking-widest opacity-60 mb-2">Core Content Topic</label>
                    <textarea id="topic" rows="2" placeholder="Describe your post idea here..." class="w-full glass-input pb-2 text-sm resize-none"></textarea>
                </div>

                <div class="pt-4 flex items-center space-x-6">
                    <button onclick="forgeHooks()" class="glass-btn px-8 py-3.5 text-xs font-bold tracking-widest uppercase flex items-center space-x-3 cursor-pointer">
                        <i class="fa-solid fa-play"></i>
                        <span>Ignite AI Forge</span>
                    </button>
                    <span class="text-xs tracking-widest opacity-50 uppercase font-serif-elegant italic">Secure API</span>
                </div>
            </div>
        </section>

        <!-- Right Side: Results (Warm Beige) -->
        <section class="w-full md:w-1/2 p-8 md:p-16 xl:p-24 flex flex-col justify-center relative z-10 text-[var(--text-dark)] tilt-card" id="right-card">
            
            <!-- Cinematic Loader -->
            <div id="loading" class="hidden h-full flex-col justify-center space-y-4 fade-pulse">
                <i class="fa-solid fa-pen-nib text-4xl opacity-50 mb-4"></i>
                <h3 class="font-serif-elegant text-2xl">"Analyzing psychology..."</h3>
                <p class="text-sm opacity-70 leading-relaxed max-w-sm">The AI is weaving emotional triggers and loss aversion into your content. Please wait a moment.</p>
            </div>

            <!-- Empty State / Intro Text -->
            <div id="intro-state" class="space-y-6 max-w-lg">
                <h3 class="font-serif-elegant text-2xl">"Words that command attention."</h3>
                <p class="text-sm leading-loose opacity-80 text-justify">
                    Welcome to the elite tier of content creation. Hook Forge doesn't just generate text; it analyzes the deep psychology of your audience. Enter your topic on the left, and watch as raw ideas are transformed into magnetic, data-backed hooks that dominate the timeline.
                </p>
                <p class="text-xs font-bold tracking-widest uppercase mt-8 opacity-60">Engine: SambaNova Llama 3</p>
            </div>

            <!-- Actual Results Output -->
            <div id="results" class="hidden space-y-10 max-w-lg max-h-[80vh] overflow-y-auto pr-4 pb-12">
                
                <!-- Hook A -->
                <div class="light-card group">
                    <div class="flex justify-between items-baseline mb-2">
                        <span class="text-xs font-bold tracking-widest uppercase opacity-50">Option A</span>
                        <span class="text-[10px] bg-[var(--dark-side)] text-[#f5eedc] px-2 py-1 tracking-wider">SCORE: <span id="scoreA"></span>/10</span>
                    </div>
                    <h2 id="textA" class="font-serif-elegant text-xl lg:text-2xl leading-snug mb-4 group-hover:text-orange-800 transition-colors"></h2>
                    <div class="space-y-3 text-xs leading-relaxed opacity-80">
                        <p><strong class="font-bold tracking-wider uppercase text-[10px]">Psychology:</strong> <span id="psychA"></span></p>
                        <p><strong class="font-bold tracking-wider uppercase text-[10px]">Actionable Fix:</strong> <span id="fixA"></span></p>
                    </div>
                    <button onclick="copyText('textA')" class="mt-4 text-[10px] font-bold tracking-widest uppercase opacity-50 hover:opacity-100 transition-opacity flex items-center space-x-2"><i class="fa-regular fa-copy"></i> <span>Copy</span></button>
                </div>

                <!-- Hook B -->
                <div class="light-card group">
                    <div class="flex justify-between items-baseline mb-2">
                        <span class="text-xs font-bold tracking-widest uppercase opacity-50">Option B</span>
                        <span class="text-[10px] bg-[var(--dark-side)] text-[#f5eedc] px-2 py-1 tracking-wider">SCORE: <span id="scoreB"></span>/10</span>
                    </div>
                    <h2 id="textB" class="font-serif-elegant text-xl lg:text-2xl leading-snug mb-4 group-hover:text-orange-800 transition-colors"></h2>
                    <div class="space-y-3 text-xs leading-relaxed opacity-80">
                        <p><strong class="font-bold tracking-wider uppercase text-[10px]">Psychology:</strong> <span id="psychB"></span></p>
                        <p><strong class="font-bold tracking-wider uppercase text-[10px]">Actionable Fix:</strong> <span id="fixB"></span></p>
                    </div>
                    <button onclick="copyText('textB')" class="mt-4 text-[10px] font-bold tracking-widest uppercase opacity-50 hover:opacity-100 transition-opacity flex items-center space-x-2"><i class="fa-regular fa-copy"></i> <span>Copy</span></button>
                </div>

                <!-- DNA -->
                <div class="p-5 border border-dashed border-[#3a2e3f]/30 bg-white/30 backdrop-blur-sm rounded-sm">
                    <div class="flex items-center space-x-2 mb-3 font-bold text-[10px] tracking-widest uppercase">
                        <i class="fa-solid fa-dna"></i><span>DNA Matrix</span>
                    </div>
                    <p id="dna" class="text-xs leading-relaxed opacity-90"></p>
                </div>
            </div>
        </section>
    </main>

    <!-- 3D Interactions & API Logic -->
    <script>
        // 3D Parallax Tilt Effect for Desktop
        document.addEventListener('mousemove', (e) => {
            if(window.innerWidth > 768) {
                const xAxis = (window.innerWidth / 2 - e.pageX) / 60;
                const yAxis = (window.innerHeight / 2 - e.pageY) / 60;
                
                document.getElementById('left-card').style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
                document.getElementById('right-card').style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
            }
        });

        // API Integration
        async function forgeHooks() {
            document.getElementById('intro-state').style.display = 'none';
            document.getElementById('results').style.display = 'none';
            document.getElementById('errorBox').style.display = 'none';
            document.getElementById('loading').style.display = 'flex';
            
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
                    document.getElementById('errorBox').innerText = "System Anomaly: " + data.error;
                    document.getElementById('intro-state').style.display = 'block';
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
                document.getElementById('intro-state').style.display = 'block';
            }
        }

        function copyText(elementId) {
            const text = document.getElementById(elementId).innerText.replace(/"/g, '');
            navigator.clipboard.writeText(text);
            alert("Hook copied securely. 🔥");
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
            ai_text = ai_text.replace("
```json", "", 1).strip()
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
