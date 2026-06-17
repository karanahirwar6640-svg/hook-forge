import os
import json
from flask import Flask, render_template_string, request, jsonify, session, redirect
import requests

app = Flask(__name__)
app.secret_key = 'crimson_enterprise_lycoris_key_2026'

SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
SAMBANOVA_URL = "https://api.sambanova.ai/v1/chat/completions"

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

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
# 1. AUTHENTICATION UI (VIDEO BACKGROUND)
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
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    <style>
        body {
            margin: 0; min-height: 100vh; font-family: 'Noto Sans JP', sans-serif;
            background-color: #0d0202; color: #fef3c7; 
            display: flex; align-items: center; justify-content: center;
            overflow: hidden; position: relative;
        }
        .bg-video {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            object-fit: cover; z-index: 0; opacity: 0.35; pointer-events: none;
        }
        .video-overlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle, rgba(15,2,2,0.4) 0%, rgba(5,0,0,0.85) 100%);
            z-index: 1; pointer-events: none;
        }
        .glass-auth-panel {
            position: relative; z-index: 10;
            background: rgba(10, 2, 2, 0.85); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 24px;
            box-shadow: 0 40px 80px rgba(0,0,0,0.95), inset 0 0 30px rgba(255,50,50,0.03);
        }
        .anime-title { font-family: 'Cinzel', serif; text-shadow: 0 0 25px rgba(220, 38, 38, 0.8); }
        .crimson-input { background: rgba(0, 0, 0, 0.65); border: 1px solid rgba(220, 38, 38, 0.25); color: #fef3c7; transition: all 0.3s; }
        .crimson-input:focus { outline: none; border-color: #ef4444; box-shadow: 0 0 15px rgba(239, 68, 68, 0.25); }
        .github-btn { background: #141414; border: 1px solid #262626; color: white; transition: all 0.3s; }
        .github-btn:hover { background: #1f1f1f; border-color: #ef4444/40; box-shadow: 0 0 25px rgba(220,38,38,0.2); }
    </style>
</head>
<body class="p-4">

    <video autoplay muted loop playsinline class="bg-video">
        <source src="https://cdn.discordapp.com/attachments/1510192168273182745/1516741191121633311/From_Klickpin.com-_Natural_Makeup_Looks_Inspiration_for_Summer-pin-id-587860557652168444.mp4?ex=6a33becf&is=6a326d4f&hm=b90901b00ab6161677a16f22153f71174238667e81d0fef2b74ad93d2a20e5aa&" type="video/mp4">
    </video>
    <div class="video-overlay"></div>

    <div class="glass-auth-panel w-full max-w-[410px] p-8 md:p-10">
        <div class="text-center mb-8">
            <h1 class="anime-title text-4xl font-black text-red-500 tracking-wider mb-2">HOOK FORGE</h1>
            <p class="text-[10px] tracking-[0.4em] text-red-400/60 uppercase">Secure Cloud Infrastructure</p>
        </div>

        <div id="msgBox" class="hidden p-3 rounded-xl text-xs font-mono text-center mb-6 border"></div>

        <div class="space-y-5">
            <button onclick="loginGitHub()" class="w-full github-btn py-3.5 rounded-xl text-xs tracking-widest uppercase font-bold flex items-center justify-center gap-3">
                <i class="fa-brands fa-github text-base"></i> Continue with GitHub
            </button>

            <div class="relative flex py-2 items-center">
                <div class="flex-grow border-t border-red-950/60"></div>
                <span class="flex-shrink-0 mx-4 text-red-500/40 text-[9px] uppercase tracking-[0.3em] font-bold">Secure Terminal Access</span>
                <div class="flex-grow border-t border-red-950/60"></div>
            </div>

            <div>
                <div class="relative mb-3">
                    <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 text-red-500/40"><i class="fa-solid fa-shield-halved text-xs"></i></span>
                    <input type="email" id="auth-email" placeholder="Enter corporate email address" class="w-full crimson-input rounded-xl pl-10 pr-4 py-3.5 text-sm focus:outline-none">
                </div>
                <button onclick="sendMagicLink()" class="w-full bg-gradient-to-r from-red-800 to-red-600 hover:from-red-700 hover:to-red-500 border border-red-600 text-white font-bold py-3.5 rounded-xl text-xs tracking-widest uppercase transition-all shadow-lg shadow-red-950/80">
                    Request Authentication Token
                </button>
            </div>
        </div>
        
        <p class="text-center text-[9px] text-red-500/30 mt-8 uppercase tracking-widest">Authorized Personnel Only</p>
    </div>

    <script>
        const supabaseUrl = '{{ supabase_url }}';
        const supabaseKey = '{{ supabase_key }}';
        const supabase = supabase.createClient(supabaseUrl, supabaseKey);

        function showMsg(type, text) {
            const box = document.getElementById('msgBox');
            box.style.display = 'block';
            box.innerText = text;
            if (type === 'error') {
                box.className = "p-3 rounded-xl text-xs font-mono text-center mb-6 border bg-red-950/90 border-red-500/40 text-red-200";
            } else {
                box.className = "p-3 rounded-xl text-xs font-mono text-center mb-6 border bg-emerald-950/90 border-emerald-500/40 text-emerald-200";
            }
        }

        async function loginGitHub() {
            try {
                const { error } = await supabase.auth.signInWithOAuth({ 
                    provider: 'github',
                    options: { redirectTo: window.location.origin }
                });
                if (error) throw error;
            } catch (error) {
                showMsg('error', error.message);
            }
        }

        async function sendMagicLink() {
            const email = document.getElementById('auth-email').value.trim();
            if(!email) { showMsg('error', 'Please enter a valid business email.'); return; }
            
            showMsg('success', 'Verifying cloud routing parameters...');
            try {
                const { error } = await supabase.auth.signInWithOtp({ 
                    email: email,
                    options: { emailRedirectTo: window.location.origin }
                });
                if (error) throw error;
                showMsg('success', 'Access token dispatched. Check your email console.');
            } catch (error) {
                showMsg('error', error.message);
            }
        }

        supabase.auth.onAuthStateChange((event, session) => {
            if (event === 'SIGNED_IN' && session) {
                const identifier = session.user.email || 'Authorized User';
                fetch('/set_flask_session', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: identifier })
                }).then(() => {
                    window.location.href = '/';
                });
            }
        });
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
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    <style>
        body {
            margin: 0; min-height: 100vh; font-family: 'Noto Sans JP', sans-serif;
            background-color: #0d0202; color: #fef3c7;
        }
        .bg-video {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            object-fit: cover; z-index: 0; opacity: 0.15; pointer-events: none;
        }
        .glass-card {
            background: rgba(15, 2, 2, 0.75); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 50, 50, 0.25); border-radius: 16px; box-shadow: 0 25px 50px rgba(0,0,0,0.6);
        }
        .anime-title { font-family: 'Cinzel', serif; text-shadow: 0 0 20px rgba(220, 38, 38, 0.9); }
        .crimson-input { background: rgba(0, 0, 0, 0.6); border: 1px solid rgba(220, 38, 38, 0.3); color: #fef3c7; transition: all 0.3s; }
        .crimson-input:focus { outline: none; border-color: #ef4444; box-shadow: 0 0 20px rgba(239, 68, 68, 0.4); }
        select.crimson-input option { background: #1a0505; color: #fef3c7; }
        .crimson-btn { background: linear-gradient(45deg, #7f1d1d, #dc2626); border: 1px solid #ef4444; box-shadow: 0 0 20px rgba(220, 38, 38, 0.5); transition: all 0.3s ease; }
        .crimson-btn:hover { background: linear-gradient(45deg, #991b1b, #f87171); box-shadow: 0 0 30px rgba(220, 38, 38, 0.8); }
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-thumb { background: #dc2626; border-radius: 10px; }
    </style>
</head>
<body class="flex flex-col lg:flex-row items-center justify-center p-4 lg:p-10 gap-8 relative overflow-x-hidden">

    <video autoplay muted loop playsinline class="bg-video">
        <source src="https://cdn.discordapp.com/attachments/1510192168273182745/1516741191121633311/From_Klickpin.com-_Natural_Makeup_Looks_Inspiration_for_Summer-pin-id-587860557652168444.mp4?ex=6a33becf&is=6a326d4f&hm=b90901b00ab6161677a16f22153f71174238667e81d0fef2b74ad93d2a20e5aa&" type="video/mp4">
    </video>

    <div class="glass-card w-full max-w-md p-8 relative z-20">
        <div class="text-center mb-6">
            <h1 class="anime-title text-4xl font-black text-red-500 mb-1">HOOK FORGE</h1>
            <p class="text-xs tracking-[0.3em] text-red-300 uppercase">Lycoris Protocol</p>
        </div>
        
        <div class="flex justify-between items-center mb-6 border-b border-red-900/50 pb-3">
            <div class="text-[10px] text-red-300 tracking-widest uppercase truncate max-w-[200px]"><i class="fa-solid fa-user-shield mr-1"></i> <span class="text-white font-bold">{{ username }}</span></div>
            <button onclick="handleLogout()" class="text-[10px] bg-red-950/50 hover:bg-red-600 border border-red-800 px-3 py-1.5 rounded tracking-widest uppercase transition-all"><i class="fa-solid fa-power-off mr-1"></i> Logout</button>
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
        const supabaseUrl = '{{ supabase_url }}';
        const supabaseKey = '{{ supabase_key }}';
        const supabase = supabase.createClient(supabaseUrl, supabaseKey);

        async function handleLogout() {
            await supabase.auth.signOut();
            window.location.href = '/logout';
        }

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
        return render_template_string(HTML_UI, username=session['user'], supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY)
    return render_template_string(HTML_LOGIN, supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY)

@app.route('/set_flask_session', methods=['POST'])
def set_flask_session():
    data = request.json
    session['user'] = data.get('email', 'Authorized User')
    return jsonify({"success": True})

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
