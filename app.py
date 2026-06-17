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
# RETENTION ENGINE PROMPT
# ==========================================
SCRIPT_SYSTEM_PROMPT = """
You are Script Forge, the world's most ruthless Short-Form Video Retention Engineer.
You analyze scripts and provide a detailed 'Viral Scorecard'.

STRICT RULES:
1. PACE: Every sentence short, punchy (max 12 words).
2. FLUFF: Cut all "Hi guys", "Welcome to the video", "In this video". Start in the middle of the action.
3. OUTPUT: Always return valid JSON.

JSON STRUCTURE:
{
  "retention_score": [0-100],
  "heatmap": [
      {"section": "Hook", "score": [0-10], "tip": "Improvement tip"},
      {"section": "Body", "score": [0-10], "tip": "Improvement tip"},
      {"section": "CTA", "score": [0-10], "tip": "Improvement tip"}
  ],
  "master_script": "The final ultra-optimized script",
  "psychology_breakdown": "Deep dive into why this will hold attention"
}
"""

# ==========================================
# MASTER FRONTEND WITH SCORECARD
# ==========================================
MASTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hook Forge | Scorecard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    <style>
        body { background: #000; color: #fff; font-family: sans-serif; }
        .glass { background: rgba(20, 20, 20, 0.8); backdrop-filter: blur(10px); border: 1px solid #333; }
        .crimson-btn { background: linear-gradient(45deg, #7f1d1d, #dc2626); }
    </style>
</head>
<body class="p-6">
    <div class="max-w-4xl mx-auto">
        <h1 class="text-3xl font-black text-red-500 mb-6 text-center">HOOK FORGE: RETENTION ENGINE</h1>
        
        <div class="glass p-6 rounded-2xl mb-6">
            <textarea id="raw-script" class="w-full bg-black text-white p-4 rounded-lg border border-red-900 h-40" placeholder="Paste boring script..."></textarea>
            <button onclick="forge()" class="w-full crimson-btn py-3 mt-4 rounded-lg font-bold uppercase tracking-widest">Forge Master Script</button>
        </div>

        <div id="results" class="hidden space-y-6">
            <div class="glass p-6 rounded-2xl flex justify-between items-center">
                <h2 class="text-xl font-bold text-amber-500">VIRAL SCORE: <span id="s-score"></span>/100</h2>
                <div id="heatmap-tags" class="flex gap-2"></div>
            </div>
            <div class="glass p-6 rounded-2xl">
                <h3 class="text-red-400 font-bold mb-2">MASTER SCRIPT</h3>
                <p id="s-master" class="text-sm leading-relaxed"></p>
            </div>
        </div>
    </div>

    <script>
        async function forge() {
            const script = document.getElementById('raw-script').value;
            const res = await fetch('/forge', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({script})
            });
            const data = await res.json();
            
            document.getElementById('s-score').innerText = data.retention_score;
            document.getElementById('s-master').innerText = data.master_script;
            
            const tags = document.getElementById('heatmap-tags');
            tags.innerHTML = data.heatmap.map(h => `<span class="text-[8px] bg-red-900 px-2 py-1 rounded">${h.section}: ${h.score}/10</span>`).join('');
            
            document.getElementById('results').style.display = 'block';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(MASTER_HTML, supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY)

@app.route('/forge', methods=['POST'])
def forge():
    data = request.json
    payload = {
        "model": "Meta-Llama-3.3-70B-Instruct", 
        "messages": [{"role": "system", "content": SCRIPT_SYSTEM_PROMPT}, {"role": "user", "content": data.get('script')}], 
        "temperature": 0.7
    }
    headers = {"Authorization": f"Bearer {SAMBANOVA_API_KEY}", "Content-Type": "application/json"}
    r = requests.post(SAMBANOVA_URL, json=payload, headers=headers)
    return jsonify(json.loads(r.json()['choices'][0]['message']['content'].strip()))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
