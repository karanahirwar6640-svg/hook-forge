import os
import json
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)
# [KEEP YOUR ENV VARIABLES SAME AS BEFORE]
SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
SAMBANOVA_URL = "https://api.sambanova.ai/v1/chat/completions"
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# ==========================================
# MASTER UI (RESTORING YOUR ANIME DESIGN)
# ==========================================
MASTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hook Forge | Restore</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    <style>
        body { background: #000; color: #fef3c7; font-family: 'Noto Sans JP', sans-serif; }
        .glass { background: rgba(5, 0, 0, 0.4); backdrop-filter: blur(10px); border: 1px solid rgba(255,50,50,0.3); border-radius: 20px; }
        .crimson-btn { background: linear-gradient(45deg, #7f1d1d, #dc2626); }
        .anime-title { font-family: 'Cinzel', serif; text-shadow: 0 0 20px rgba(255,20,20,0.8); }
    </style>
</head>
<body class="p-6">
    <div class="max-w-4xl mx-auto">
        <h1 class="anime-title text-4xl font-black text-red-500 mb-8 text-center tracking-widest">HOOK FORGE: RETENTION ENGINE</h1>
        
        <!-- RESTORED INTERFACE -->
        <div class="glass p-8">
            <textarea id="raw-script" class="w-full bg-black/50 text-white p-4 rounded-xl border border-red-900 h-40 mb-4 focus:border-red-500 outline-none" placeholder="Paste your boring script..."></textarea>
            <button onclick="forge()" class="w-full crimson-btn py-4 rounded-xl font-bold uppercase tracking-widest text-white shadow-lg shadow-red-900/50">Forge Master Script</button>
        </div>

        <div id="results" class="hidden mt-8 space-y-6">
            <div class="glass p-6 flex justify-between items-center">
                <h2 class="text-xl font-bold text-amber-500">VIRAL SCORE: <span id="s-score"></span>/100</h2>
                <div id="heatmap-tags" class="flex gap-2"></div>
            </div>
            <div class="glass p-6">
                <h3 class="text-red-400 font-bold mb-3 uppercase tracking-widest text-xs">Optimized Master Script</h3>
                <p id="s-master" class="text-sm leading-relaxed text-amber-50"></p>
            </div>
        </div>
    </div>

    <script>
        async function forge() {
            const script = document.getElementById('raw-script').value;
            const res = await fetch('/forge', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({script})
            });
            const data = await res.json();
            document.getElementById('s-score').innerText = data.retention_score;
            document.getElementById('s-master').innerText = data.master_script;
            document.getElementById('heatmap-tags').innerHTML = data.heatmap.map(h => 
                `<span class="text-[9px] bg-red-900 text-white px-2 py-1 rounded uppercase">${h.section}: ${h.score}/10</span>`).join('');
            document.getElementById('results').style.display = 'block';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(MASTER_HTML)

@app.route('/forge', methods=['POST'])
def forge():
    prompt = f"Analyze script and return JSON with retention_score(0-100), heatmap(array of section/score/tip), and master_script: {request.json.get('script')}"
    payload = {"model": "Meta-Llama-3.3-70B-Instruct", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
    r = requests.post(SAMBANOVA_URL, json=payload, headers={"Authorization": f"Bearer {SAMBANOVA_API_KEY}"})
    return jsonify(json.loads(r.json()['choices'][0]['message']['content'].strip()))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
