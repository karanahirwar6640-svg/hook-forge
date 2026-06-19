import os
import json
import re
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
SAMBANOVA_URL = "https://api.sambanova.ai/v1/chat/completions"

HOOK_SYSTEM_PROMPT = """
You are Hook Forge v2.0. Write short, punchy hooks (under 15 words).
OUTPUT STRICTLY IN JSON FORMAT ONLY. Do not write any introduction or conclusion text.
{
  "hook_a": { "text": "High-tension hook text", "score": 95, "reasoning": "Reason", "psychology": "Psychology" },
  "hook_b": { "text": "Contrarian hook text", "score": 98, "reasoning": "Reason", "psychology": "Psychology" },
  "dna_comparison": "Comparison text"
}
"""

SCRIPT_SYSTEM_PROMPT = """
You are Script Forge. Rewrite the script to maximize retention.
OUTPUT STRICTLY IN JSON FORMAT ONLY. Do not write any introduction or conclusion text.
{
  "retention_score": 98,
  "hook_extracted": "The explosive hook",
  "master_script": "The FULL upgraded script",
  "psychology_breakdown": "Explanation"
}
"""

def clean_json_output(text):
    """Smart regex function to extract JSON even if AI adds extra text"""
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(text)
    except:
        return None

@app.route('/')
def home():
    with open('index.html', 'r', encoding='utf-8') as f:
        return render_template_string(f.read())

@app.route('/forge_hook', methods=['POST'])
def forge_hook():
    d = request.json
    p = f"Topic: {d.get('topic')}\nNiche: {d.get('niche')}\nAudience: {d.get('audience')}\nTone: {d.get('tone')}"
    try:
        r = requests.post(SAMBANOVA_URL, json={"model": "Meta-Llama-3.3-70B-Instruct", "messages": [{"role": "system", "content": HOOK_SYSTEM_PROMPT}, {"role": "user", "content": p}], "temperature": 0.4}, headers={"Authorization": f"Bearer {SAMBANOVA_API_KEY}", "Content-Type": "application/json"})
        raw_text = r.json()['choices'][0]['message']['content']
        parsed_json = clean_json_output(raw_text)
        
        if parsed_json:
            return jsonify(parsed_json)
        return jsonify({"error": "AI response was unstructured. Click Ignite again."})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/forge_script', methods=['POST'])
def forge_script():
    d = request.json
    s = d.get('script', '')
    u = d.get('url', '').strip()
    try:
        r = requests.post(SAMBANOVA_URL, json={"model": "Meta-Llama-3.3-70B-Instruct", "messages": [{"role": "system", "content": SCRIPT_SYSTEM_PROMPT}, {"role": "user", "content": s + " Target URL: " + u}], "temperature": 0.4}, headers={"Authorization": f"Bearer {SAMBANOVA_API_KEY}", "Content-Type": "application/json"})
        raw_text = r.json()['choices'][0]['message']['content']
        parsed_json = clean_json_output(raw_text)
        
        if parsed_json:
            return jsonify(parsed_json)
        return jsonify({"error": "AI response was unstructured. Click Ignite again."})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
