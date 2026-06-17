import os
import json
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# Environment variables
SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
SAMBANOVA_URL = "https://api.sambanova.ai/v1/chat/completions"
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# ==========================================
# PROMPTS
# ==========================================
HOOK_SYSTEM_PROMPT = """
You are Hook Forge v2.0. Output only valid JSON.
{
  "hook_a": { "text": "...", "score": 95, "reasoning": "...", "psychology": "..." },
  "hook_b": { "text": "...", "score": 98, "reasoning": "...", "psychology": "..." },
  "dna_comparison": "..."
}
"""

SCRIPT_SYSTEM_PROMPT = """
You are Script Forge. Rewrite the script to be viral. Output only valid JSON.
{
  "retention_score": 98,
  "hook_extracted": "...",
  "master_script": "...",
  "psychology_breakdown": "..."
}
"""

# ==========================================
# ORIGINAL MASTER HTML (RESTORED)
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
    <style>
        body { margin: 0; min-height: 100vh; font-family: 'Noto Sans JP', sans-serif; background-color: #000; color: #fef3c7; display: flex; align-items: center; justify-content: center; flex-direction: column; }
        .glass-panel { background: rgba(5, 0, 0, 0.25); backdrop-filter: blur(12px); border: 1px solid rgba(255, 50, 50, 0.4); border-radius: 24px; box-shadow: 0 40px 80px rgba(0,0,0,0.95); }
        .anime-title { font-family: 'Cinzel', serif; text-shadow: 0 0 30px rgba(255, 20, 20, 1); }
        .crimson-input { background: rgba(0, 0, 0, 0.7); border: 1px solid rgba(220, 38, 38, 0.35); color: #fef3c7; }
        .crimson-btn { background: linear-gradient(45deg, #7f1d1d, #dc2626); border: 1px solid #ef4444; }
        .tab-btn { padding: 10px 20px; font-size: 10px; font-weight: bold; letter-spacing: 0.2em; text-transform: uppercase; border-radius: 8px; }
        .tab-active { background: rgba(220, 38, 38, 0.2); border: 1px solid #ef4444; color: #fef3c7; }
        .tab-inactive { background: rgba(0, 0, 0, 0.5); border: 1px solid rgba(255,50,50,0.2); color: rgba(254, 243, 199, 0.5); }
    </style>
</head>
<body class="p-4">
    <div id="dashboard-viewport" class="w-full max-w-6xl flex flex-col">
        <div class="flex space-x-3 mb-6 justify-center">
            <button id="tab-hook" onclick="switchMode('hook')" class="tab-btn tab-active">Hook Forge</button>
            <button id="tab-script" onclick="switchMode('script')" class="tab-btn tab-inactive">Script Forge</button>
        </div>
        <div class="flex flex-col lg:flex-row gap-6">
            <div class="glass-panel w-full lg:max-w-md p-6">
                <div id="inputs-hook" class="space-y-4">
                    <input type="text" id="h-niche" class="w-full crimson-input rounded-lg p-3" value="Anime & Tech">
                    <textarea id="h-topic" class="w-full crimson-input rounded-lg p-3" placeholder="Topic..."></textarea>
                </div>
                <div id="inputs-script" class="hidden space-y-4">
                    <textarea id="s-raw" class="w-full crimson-input rounded-lg p-3 h-64" placeholder="Script..."></textarea>
                </div>
                <button onclick="ignite()" class="w-full crimson-btn py-4 rounded-lg mt-4 font-bold uppercase">Ignite</button>
            </div>
            <div class="glass-panel flex-grow p-6" id="result-box">Result will appear here...</div>
        </div>
    </div>
    <script>
        let currentMode = 'hook';
        function switchMode(m) { currentMode = m; document.getElementById('inputs-hook').style.display = m==='hook'?'block':'none'; document.getElementById('inputs-script').style.display = m==='script'?'block':'none'; }
        async function ignite() {
            const body = currentMode === 'hook' ? {topic: document.getElementById('h-topic').value} : {script: document.getElementById('s-raw').value};
            const res = await fetch('/'+currentMode, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});
            document.getElementById('result-box').innerText = JSON.stringify(await res.json(), null, 2);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(MASTER_HTML)

@app.route('/hook', methods=['POST'])
def forge_hook():
    r = requests.post(SAMBANOVA_URL, json={"model": "Meta-Llama-3.3-70B-Instruct", "messages": [{"role": "system", "content": HOOK_SYSTEM_PROMPT}, {"role": "user", "content": request.json.get('topic')}]}, headers={"Authorization": f"Bearer {SAMBANOVA_API_KEY}"})
    return jsonify(json.loads(r.json()['choices'][0]['message']['content'].strip()))

@app.route('/script', methods=['POST'])
def forge_script():
    r = requests.post(SAMBANOVA_URL, json={"model": "Meta-Llama-3.3-70B-Instruct", "messages": [{"role": "system", "content": SCRIPT_SYSTEM_PROMPT}, {"role": "user", "content": request.json.get('script')}]}, headers={"Authorization": f"Bearer {SAMBANOVA_API_KEY}"})
    return jsonify(json.loads(r.json()['choices'][0]['message']['content'].strip()))

if __name__ == '__main__': app.run(host='0.0.0.0', port=5000)
