import os
import json
import re
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
SAMBANOVA_URL = "[https://api.sambanova.ai/v1/chat/completions](https://api.sambanova.ai/v1/chat/completions)"

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

@app.route('/')
def home():
    with open('index.html', 'r', encoding='utf-8') as f:
        return render_template_string(f.read())

@app.route('/forge_hook', methods=['POST'])
def forge_hook():
    d = request.json
    p = f"Topic: {d.get('topic')}\nNiche: {d.get('niche')}\nAudience: {d.get('audience')}\nTone: {d.get('tone')}"
    try:
        r = requests.post(SAMBANOVA_URL, json={"model": "Meta-Llama-3.3-70B-Instruct", "messages": [{"role": "system", "content": HOOK_SYSTEM_PROMPT}, {"role": "user", "content": p}]}, headers={"Authorization": f"Bearer {SAMBANOVA_API_KEY}", "Content-Type": "application/json"})
        return jsonify(json.loads(r.json()['choices'][0]['message']['content'].strip()))
    except Exception as e:
        return jsonify({"error": "Failed to parse AI output."})

@app.route('/forge_script', methods=['POST'])
def forge_script():
    d = request.json
    s = d.get('script', '')
    u = d.get('url', '').strip()
    i = ""
    if u:
        try:
            res = requests.get(u, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            t = re.search(r'<title>(.*?)</title>', res.text, re.IGNORECASE)
            i = f"\n\n🚨 TARGET: Crush competitor video '{t.group(1)}'." if t else f"\n\n🚨 TARGET URL: {u}."
        except: 
            i = f"\n\n🚨 TARGET URL: {u}."
    try:
        r = requests.post(SAMBANOVA_URL, json={"model": "Meta-Llama-3.3-70B-Instruct", "messages": [{"role": "system", "content": SCRIPT_SYSTEM_PROMPT}, {"role": "user", "content": s + i}]}, headers={"Authorization": f"Bearer {SAMBANOVA_API_KEY}", "Content-Type": "application/json"})
        c = r.json()['choices'][0]['message']['content'].strip()
        
        # FIXED CLIPBOARD BUG HERE: No more direct backticks!
        backticks = chr(96) * 3
        if c.startswith(backticks + "json"): 
            c = c[7:-3].strip()
        elif c.startswith(backticks): 
            c = c[3:-3].strip()
            
        return jsonify(json.loads(c))
    except Exception as e:
        return jsonify({"error": "Failed to parse AI output."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
