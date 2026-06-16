import os
import json
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
SAMBANOVA_URL = "https://api.sambanova.ai/v1/chat/completions"

SYSTEM_PROMPT = """
You are Hook Forge, an elite social media psychologist and copywriter. Your job is to generate hooks and analyze them.
You must ALWAYS respond in valid JSON format. Do not write any markdown prose outside the JSON.
The user will provide: Topic, Niche, Audience, and Tone.
Response Structure must be exactly like this JSON:
{
  "hook_a": { "text": "Hook text", "score": 8, "reasoning": "Actionable fix to make it 10", "psychology": "Explain why this works" },
  "hook_b": { "text": "Second distinct hook text", "score": 9, "reasoning": "Actionable fix to make it 10", "psychology": "Explain trigger used" },
  "dna_comparison": "Direct comparison of Hook A vs Hook B."
}
"""

HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hook Forge</title>
    <style>
        body { font-family: sans-serif; background: #09090b; color: white; margin: 0; padding: 20px; }
        .wrapper { max-width: 600px; margin: auto; }
        .card { background: #18181b; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #27272a; }
        input, select, textarea { width: 100%; padding: 12px; background: #09090b; border: 1px solid #3f3f46; color: white; margin-bottom: 15px; border-radius: 6px; box-sizing: border-box;}
        button { width: 100%; background: #f97316; color: white; border: none; padding: 14px; border-radius: 6px; font-weight: bold; font-size: 16px; cursor: pointer; }
        .hook-box { border-left: 4px solid #f97316; padding-left: 15px; background: #202023; padding: 10px; margin-bottom: 10px;}
        .score { background: #22c55e; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; }
        #results, #loading, #errorBox { display: none; }
        #loading { color: #f97316; text-align: center; margin: 20px; font-weight: bold; }
        #errorBox { background: #7f1d1d; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #ef4444; word-wrap: break-word; font-family: monospace; }
    </style>
</head>
<body>
    <div class="wrapper">
        <h1 style="color:#f97316; text-align:center;">🔥 Hook Forge</h1>
        <div class="card">
            <label>Niche</label> <input type="text" id="niche" value="Tech">
            <label>Audience</label> <input type="text" id="audience" value="Young Creators">
            <label>Tone</label> 
            <select id="tone"><option>Aggressive</option><option selected>Curious</option><option>Storytelling</option></select>
            <label>Topic</label> <textarea id="topic" placeholder="e.g., Kaise zero budget me SaaS banayein..."></textarea>
            <button onclick="forgeHooks()">Forge Hooks 🚀</button>
        </div>
        <div id="loading">🔨 Hook Forge kar raha hai... Thoda sabr rakho...</div>
        
        <div id="errorBox"></div>

        <div id="results">
            <div class="card">
                <h3>🪝 Hook Option A (Score: <span id="scoreA" class="score"></span>)</h3>
                <div class="hook-box" id="textA"></div>
                <p style="color:#a1a1aa; font-size:14px;"><b>Psychology:</b> <span id="psychA"></span></p>
                <p style="color:#a1a1aa; font-size:14px;"><b>Fix for 10/10:</b> <span id="fixA"></span></p>
            </div>
            <div class="card">
                <h3>🪝 Hook Option B (Score: <span id="scoreB" class="score"></span>)</h3>
                <div class="hook-box" id="textB"></div>
                <p style="color:#a1a1aa; font-size:14px;"><b>Psychology:</b> <span id="psychB"></span></p>
                <p style="color:#a1a1aa; font-size:14px;"><b>Fix for 10/10:</b> <span id="fixB"></span></p>
            </div>
            <div class="card" style="border-color: #4338ca;">
                <h3>🧬 DNA Comparison</h3>
                <p id="dna" style="font-size:14px;"></p>
            </div>
        </div>
    </div>
    <script>
        async function forgeHooks() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').style.display = 'none';
            document.getElementById('errorBox').style.display = 'none';
            try {
                const res = await fetch('/forge', {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        topic: document.getElementById('topic').value, niche: document.getElementById('niche').value,
                        audience: document.getElementById('audience').value, tone: document.getElementById('tone').value
                    })
                });
                const data = await res.json();
                document.getElementById('loading').style.display = 'none';
                
                if (data.error) {
                    document.getElementById('errorBox').style.display = 'block';
                    document.getElementById('errorBox').innerText = data.error;
                    return;
                }

                document.getElementById('textA').innerText = data.hook_a.text;
                document.getElementById('scoreA').innerText = data.hook_a.score;
                document.getElementById('psychA').innerText = data.hook_a.psychology;
                document.getElementById('fixA').innerText = data.hook_a.reasoning;

                document.getElementById('textB').innerText = data.hook_b.text;
                document.getElementById('scoreB').innerText = data.hook_b.score;
                document.getElementById('psychB').innerText = data.hook_b.psychology;
                document.getElementById('fixB').innerText = data.hook_b.reasoning;

                document.getElementById('dna').innerText = data.dna_comparison;
                document.getElementById('results').style.display = 'block';
            } catch(e) { 
                document.getElementById('loading').style.display = 'none';
                document.getElementById('errorBox').style.display = 'block';
                document.getElementById('errorBox').innerText = "Frontend Connection Error: " + e.message;
            }
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
    
    # Ye raha naya Model jo API me support karta hai
    payload = {
        "model": "Meta-Llama-3.3-70B-Instruct", 
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}], 
        "temperature": 0.7
    }
    
    headers = {"Authorization": f"Bearer {SAMBANOVA_API_KEY}", "Content-Type": "application/json"}
    
    try:
        r = requests.post(SAMBANOVA_URL, json=payload, headers=headers, timeout=15)
        
        if r.status_code != 200:
            return jsonify({"error": f"SambaNova API Error! Status Code: {r.status_code} | Message: {r.text}"})
            
        res_data = r.json()
        ai_text = res_data['choices'][0]['message']['content']
        
        if ai_text.startswith("```json"):
            ai_text = ai_text.replace("```json", "", 1).strip()
            if ai_text.endswith("```"):
                ai_text = ai_text[:-3].strip()
                
        return jsonify(json.loads(ai_text))
        
    except requests.exceptions.Timeout:
        return jsonify({"error": "SambaNova API ne bohot time lagaya, request timeout ho gayi!"})
    except Exception as e: 
        return jsonify({"error": f"Backend Failed: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
