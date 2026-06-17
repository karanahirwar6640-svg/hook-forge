import os
import json
from flask import Flask, render_template_string, request, jsonify, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
import requests

app = Flask(__name__)
app.secret_key = 'crimson_enterprise_lycoris_key_2026'

SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
SAMBANOVA_URL = "https://api.sambanova.ai/v1/chat/completions"

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def get_supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

SYSTEM_PROMPT = """
You are Hook Forge v2.0, an elite social media psychologist, data scientist, and master copywriter. 
Your job is to generate high-converting hooks and analyze them deeply.
You must ALWAYS respond in valid JSON format. Do not write any markdown prose outside the JSON.

The user will provide: Topic, Niche, Audience, and Tone.
You must output exactly this JSON structure:
{
  "hook_a": { "text": "Viral hook text A", "score": 8, "reasoning": "Actionable fix", "psychology": "Deep psychological breakdown" },
  "hook_b": { "text": "Viral hook text B", "score": 9, "reasoning": "Actionable fix", "psychology": "Deep psychological breakdown" },
  "dna_comparison": "Direct comparison of Hook A vs Hook B."
}
"""

# ==========================================
# 1. AUTHENTICATION UI (LOGIN/SIGNUP)
# ==========================================
HTML_LOGIN = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign In | Hook Forge</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {
            margin: 0; min-height: 100vh; font-family: 'Noto Sans JP', sans-serif;
            background-image: url('https://cdn.discordapp.com/attachments/1510192168273182745/1516483061615951952/39dbe266fbd4af345a049536b52e306a.jpg?ex=6a32ce68&is=6a317ce8&hm=140cfcc462f5342cde06034cbd97cc94656c71b19ea21994376b6b8c1858ecb1&');
            background-size: cover; background-position: center; background-attachment: fixed; background-color: #1a0505; 
            color: #fef3c7; display: flex; align-items: center; justify-content: center;
        }
        .glass-auth-panel {
            background: rgba(15, 2, 2, 0.8); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 50, 50, 0.25); border-radius: 24px;
            box-shadow: 0 30px 60px rgba(0,0,0,0.8), inset 0 0 30px rgba(255,50,50,0.05);
        }
        .anime-title { font-family: 'Cinzel', serif; text-shadow: 0 0 20px rgba(220, 38, 38, 0.8); }
        .crimson-input { background: rgba(0, 0, 0, 0.5); border: 1px solid rgba(220, 38, 38, 0.3); color: #fef3c7; transition: all 0.3s; }
        .crimson-input:focus { outline: none; border-color: #ef4444; box-shadow: 0 0 15px rgba(239, 68, 68, 0.3); }
        .auth-tab.active { color: #ef4444; border-bottom: 2px solid #ef4444; }
    </style>
</head>
<body class="p-4">
    <div class="glass-auth-panel w-full max-w-[440px] p-8 md:p-10">
        <div class="text-center mb-8">
            <h1 class="anime-title text-3xl font-black text-red-500 tracking-wider mb-1">HOOK FORGE</h1>
            <p class="text-[10px] tracking-[0.4em] text-red-400/60 uppercase">Cloud Security Connected</p>
        </div>

        <div class="flex border-b border-red-950/60 mb-6 text-sm font-bold text-red-300/50">
            <button onclick="switchAuthTab('login')" id="tab-login" class="auth-tab active flex-1 pb-3 text-center transition-all">Sign In</button>
            <button onclick="switchAuthTab('signup')" id="tab-signup" class="auth-tab flex-1 pb-3 text-center transition-all">Register</button>
        </div>

        <div id="msgBox" class="hidden p-3 rounded-xl text-xs font-mono text-center mb-4 border"></div>

        <div class="space-y-4">
            <div>
                <label class="block text-[10px] font-bold tracking-widest uppercase text-red-400/70 mb-1.5">Username</label>
                <div class="relative">
                    <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 text-red-500/50"><i class="fa-solid fa-user text-xs"></i></span>
                    <input type="text" id="auth-user" placeholder="Enter username" class="w-full crimson-input rounded-xl pl-10 pr-4 py-3 text-sm focus:outline-none">
                </div>
            </div>

            <div>
                <label class="block text-[10px] font-bold tracking-widest uppercase text-red-400/70 mb-1.5">Password</label>
                <div class="relative">
                    <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 text-red-500/50"><i class="fa-solid fa-lock text-xs"></i></span>
                    <input type="password" id="auth-pass" placeholder="••••••••" class="w-full crimson-input rounded-xl pl-10 pr-10 py-3 text-sm focus:outline-none">
                    <button onclick="togglePasswordVisibility()" class="absolute inset-y-0 right-0 flex items-center pr-3.5 text-red-400/50 hover:text-red-400">
                        <i id="password-eye" class="fa-solid fa-eye text-xs"></i>
                    </button>
                </div>
            </div>

            <button onclick="submitAuth()" id="submit-auth-btn" class="w-full bg-gradient-to-r from-red-700 to-red-600 hover:from-red-600 hover:to-red-500 border border-red-500 text-white font-bold py-3.5 rounded-xl text-xs tracking-widest uppercase transition-all shadow-lg shadow-red-950/50 mt-2">
                System Login
            </button>
        </div>
    </div>

    <script>
        let currentMode = 'login';

        function switchAuthTab(mode) {
            currentMode = mode;
            document.querySelectorAll('.auth-tab').forEach(el => el.classList.remove('active'));
            document.getElementById('tab-' + mode).classList.add('active');
            document.getElementById('submit-auth-btn').innerText = mode === 'login' ? 'System Login' : 'Create Free Account';
            document.getElementById('msgBox').style.display = 'none';
        }

        function togglePasswordVisibility() {
            const passInput = document.getElementById('auth-pass');
            const eyeIcon = document.getElementById('password-eye');
            if (passInput.type === 'password') {
                passInput.type = 'text';
                eyeIcon.className = "fa-solid fa-eye-slash text-xs";
            } else {
                passInput.type = 'password';
                eyeIcon.className = "fa-solid fa-eye text-xs";
            }
        }

        async function submitAuth() {
            const user = document.getElementById('auth-user').value.trim();
            const pass = document.getElementById('auth-pass').value.trim();
            
            if(!user || !pass) {
                showMsg('error', 'All fields required.');
                return;
            }

            try {
                const res = await fetch('/auth', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: currentMode, username: user, password: pass })
                });
                const data = await res.json();
                
                if (data.error) {
                    showMsg('error', data.error);
                } else {
                    showMsg('success', data.message || 'Access Granted!');
                    setTimeout(() => { window.location.reload(); }, 1000);
                }
            } catch(e) {
                showMsg('error', 'Database communication failed.');
            }
        }

        function showMsg(type, text) {
            const box = document.getElementById('msgBox');
            box.style.display = 'block';
            box.innerText = text;
            if (type === 'error') {
                box.className = "p-3 rounded-xl text-xs font-mono text-center mb-4 border bg-red-950/80 border-red-500/50 text-red-200";
            } else {
                box.className = "p-3 rounded-xl text-xs font-mono text-center mb-4 border bg-emerald-950/80 border-emerald-500/50 text-emerald-200";
            }
        }
    </script>
</body>
</html>
"""

# ==========================================
# 2. MAIN DASHBOARD UI (THE FORGE)
# ==========================================
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hook Forge | Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {
            margin: 0; min-height: 100vh; font-family: 'Noto Sans JP', sans-serif;
            background-image: url('https://cdn.discordapp.com/attachments/1510192168273182745/1516483061615951952/39dbe266fbd4af345a049536b52e306a.jpg?ex=6a32ce68&is=6a317ce8&hm=140cfcc462f5342cde06034cbd97cc94656c71b19ea21994376b6b8c1858ecb1&');
            background-size: cover; background-position: center; background-attachment: fixed; background-color: #1a0505; color: #fef3c7;
        }
        .glass-card {
            background: rgba(20, 2, 2, 0.65); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 50, 50, 0.3); border-radius: 16px; box-shadow: 0 25px 50px rgba(0,0,0,0.5), inset 0 0 20px rgba(255,50,50,0.1);
        }
        .anime-title { font-family: 'Cinzel', serif; text-shadow: 0 0 20px rgba(220, 38, 38, 0.9); }
        .crimson-input { background: rgba(0, 0, 0, 0.6); border: 1px solid rgba(220, 38, 38, 0.4); color: #fef3c7; transition: all 0.3s; }
        .crimson-input:focus { outline: none; border-color: #ef4444; box-shadow: 0 0 20px rgba(239, 68, 68, 0.4); }
        select.crimson-input option { background: #1a0505; color: #fef3c7; }
        .crimson-btn { background: linear-gradient(45deg, #7f1d1d, #dc2626); border: 1px solid #ef4444; box-shadow: 0 0 20px rgba(220, 38, 38, 0.5); transition: all 0.3s ease; }
        .crimson-btn:hover { background: linear-gradient(45deg, #991b1b, #f87171); box-shadow: 0 0 30px rgba(220, 38, 38, 0.8); }
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #dc2626; border-radius: 10px; }
    </style>
</head>
<body class="flex flex-col lg:flex-row items-center justify-center p-4 lg:p-10 gap-8">

    <div class="glass-card w-full max-w-md p-8 relative z-20">
        <div class="text-center mb-6">
            <h1 class="anime-title text-4xl font-black text-red-500 mb-1">HOOK FORGE</h1>
            <p class="text-xs tracking-[0.3em] text-red-300 uppercase">Lycoris Protocol</p>
        </div>
        
        <div class="flex justify-between items-center mb-6 border-b border-red-900/50 pb-3">
            <div class="text-[10px] text-red-300 tracking-widest uppercase"><i class="fa-solid fa-user-shield mr-1"></i> Active: <span class="text-white font-bold">{{ username }}</span></div>
            <a href="/logout" class="text-[10px] bg-red-950/50 hover:bg-red-600 border border-red-800 px-3 py-1.5 rounded tracking-widest uppercase transition-all"><i class="fa-solid fa-power-off mr-1"></i> Logout</a>
        </div>

        <div id="errorBox" class="hidden bg-red-900 border border-red-500 text-white p-3 rounded mb-4 text-xs font-mono"></div>

        <div class="space-y-4">
            <div>
                <label class="block text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1">Niche</label>
                <input type="text" id="niche" value="Anime & Tech" class="w-full crimson-input rounded-lg px-4 py-3 text-sm">
            </div>
            <div>
                <label class="block text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1">Audience</label>
                <input type="text" id="audience" value="Creators" class="w-full crimson-input rounded-lg px-4 py-3 text-sm">
            </div>
            <div>
                <label class="block text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1">Tone</label>
                <select id="tone" class="w-full crimson-input rounded-lg px-4 py-3 text-sm">
                    <option value="Curious">Curiosity Gap</option>
                    <option value="Aggressive">Brutally Honest</option>
                    <option value="Storytelling">Anime Protagonist Arc</option>
                </select>
            </div>
            <div>
                <label class="block text-[10px] font-bold tracking-widest uppercase text-red-400 mb-1">Topic</label>
                <textarea id="topic" rows="3" class="w-full crimson-input rounded-lg px-4 py-3 text-sm resize-none"></textarea>
            </div>
            
            <button onclick="forgeHooks()" class="w-full crimson-btn mt-4 py-4 rounded-lg font-bold tracking-widest uppercase text-xs">
                <i class="fa-solid fa-fire mr-2"></i> Ignite Engine
            </button>
        </div>
    </div>

    <div class="glass-card w-full max-w-2xl p-8 relative z-20 min-h-[500px] flex flex-col justify-center">
        <div id="loading" class="hidden text-center">
            <i class="fa-solid fa-spinner fa-spin text-5xl text-red-500 mb-4 drop-shadow-[0_0_15px_rgba(220,38,38,0.8)]"></i>
            <h2 class="anime-title text-2xl text-red-100">Extracting Psychology...</h2>
        </div>

        <div id="empty-state" class="text-center opacity-60">
            <i class="fa-solid fa-crosshairs text-6xl text-red-500/50 mb-4"></i>
            <p class="text-sm tracking-widest uppercase">Awaiting Target Parameters...</p>
        </div>

        <div id="results" class="hidden space-y-6 overflow-y-auto max-h-[600px] pr-2">
            <div class="bg-black/40 border border-red-500/30 p-5 rounded-xl">
                <div class="flex justify-between items-center mb-3">
                    <span class="text-[10px] bg-red-900 text-red-200 px-2 py-1 rounded font-bold uppercase tracking-wider">Option A</span>
                    <span class="text-[10px] text-red-300 font-black tracking-widest">SCORE: <span id="scoreA" class="text-red-500 text-base"></span></span>
                </div>
                <h3 id="textA" class="text-lg font-bold text-amber-50 mb-3"></h3>
                <div class="text-xs text-red-200/80 space-y-2 border-t border-red-900/50 pt-3">
                    <p><strong class="text-red-400">Psychology:</strong> <span id="psychA"></span></p>
                    <p><strong class="text-red-400">Fix:</strong> <span id="fixA"></span></p>
                </div>
                <button onclick="copyText('textA')" class="mt-3 text-[10px] uppercase tracking-widest text-red-400 hover:text-red-200"><i class="fa-regular fa-copy mr-1"></i> Copy</button>
            </div>

            <div class="bg-black/40 border border-amber-500/30 p-5 rounded-xl">
                <div class="flex justify-between items-center mb-3">
                    <span class="text-[10px] bg-amber-900 text-amber-200 px-2 py-1 rounded font-bold uppercase tracking-wider">Option B</span>
                    <span class="text-[10px] text-amber-300 font-black tracking-widest">SCORE: <span id="scoreB" class="text-amber-500 text-base"></span></span>
                </div>
                <h3 id="textB" class="text-lg font-bold text-amber-50 mb-3"></h3>
                <div class="text-xs text-red-200/80 space-y-2 border-t border-red-900/50 pt-3">
                    <p><strong class="text-amber-500">Psychology:</strong> <span id="psychB"></span></p>
                    <p><strong class="text-amber-500">Fix:</strong> <span id="fixB"></span></p>
                </div>
                <button onclick="copyText('textB')" class="mt-3 text-[10px] uppercase tracking-widest text-amber-400 hover:text-amber-200"><i class="fa-regular fa-copy mr-1"></i> Copy</button>
            </div>
            
            <div class="text-xs text-red-300 bg-red-950/30 p-4 rounded border border-red-800/30">
                <strong class="uppercase tracking-widest block mb-1"><i class="fa-solid fa-dna mr-2"></i>DNA Matrix</strong>
                <span id="dna"></span>
            </div>
        </div>
    </div>

    <script>
        async function forgeHooks() {
            try {
                document.getElementById('empty-state').style.display = 'none';
                document.getElementById('results').style.display = 'none';
                document.getElementById('errorBox').style.display = 'none';
                document.getElementById('loading').style.display = 'block';
                
                const response = await fetch('/forge', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        topic: document.getElementById('topic').value || "No topic",
                        niche: document.getElementById('niche').value,
                        audience: document.getElementById('audience').value,
                        tone: document.getElementById('tone').value
                    })
                });
                
                const data = await response.json();
                document.getElementById('loading').style.display = 'none';
                
                if (data.error) {
                    document.getElementById('errorBox').style.display = 'block';
                    document.getElementById('errorBox').innerText = data.error;
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
                
            } catch(error) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('errorBox').style.display = 'block';
                document.getElementById('errorBox').innerText = "System Fault: " + error.message;
            }
        }

        function copyText(elementId) {
            const text = document.getElementById(elementId).innerText.replace(/"/g, '');
            navigator.clipboard.writeText(text);
            alert("Hook acquired! ⚔️");
        }
    </script>
</body>
</html>
"""

# ==========================================
# 3. BACKEND ENDPOINTS
# ==========================================
@app.route('/')
def home():
    if 'user' in session:
        return render_template_string(HTML_UI, username=session['user'])
    return render_template_string(HTML_LOGIN)

@app.route('/auth', methods=['POST'])
def auth():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return jsonify({"error": "Backend Error: Supabase keys missing on Render!"})

    data = request.json
    action = data.get('action')
    username = data.get('username').strip()
    password = data.get('password').strip()

    target_url = f"{SUPABASE_URL}/rest/v1/users"

    if action == 'signup':
        check_url = f"{target_url}?username=eq.{username}"
        r_check = requests.get(check_url, headers=get_supabase_headers())
        
        if r_check.status_code == 200 and len(r_check.json()) > 0:
            return jsonify({"error": "Identity already registered."})
        
        hashed_password = generate_password_hash(password)
        payload = {"username": username, "password": hashed_password}
        r_insert = requests.post(target_url, json=payload, headers=get_supabase_headers())

        if r_insert.status_code in [200, 201]:
            session['user'] = username
            return jsonify({"success": True, "message": "Cloud registration success!"})
        return jsonify({"error": "Failed to write user to cloud storage."})

    elif action == 'login':
        login_url = f"{target_url}?username=eq.{username}"
        r_login = requests.get(login_url, headers=get_supabase_headers())

        if r_login.status_code == 200 and len(r_login.json()) > 0:
            user_data = r_login.json()[0]
            if check_password_hash(user_data['password'], password):
                session['user'] = username
                return jsonify({"success": True, "message": "Welcome back!"})
        
        return jsonify({"error": "Invalid combination. Denied entry."})

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/forge', methods=['POST'])
def forge():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized pipeline request."}), 401

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
            return jsonify({"error": "SambaNova Pipeline Error. Try again shortly."})
            
        res_data = r.json()
        ai_text = res_data['choices'][0]['message']['content'].strip()
        if ai_text.startswith("```json"):
            ai_text = ai_text.replace("```json", "", 1).strip()
            if ai_text.endswith("```"):
                ai_text = ai_text[:-3].strip()
                
        return jsonify(json.loads(ai_text))
    except Exception as e: 
        return jsonify({"error": f"Runtime fault: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
