import os
import json
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

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
# ROBUST COMBINED MASTER FRONTEND (SPA STYLE)
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
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    <style>
        body {
            margin: 0; min-height: 100vh; font-family: 'Noto Sans JP', sans-serif;
            background-color: #000; color: #fef3c7; 
            display: flex; align-items: center; justify-content: center;
            overflow-x: hidden; position: relative;
        }
        .bg-video {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            object-fit: cover; z-index: 0; pointer-events: none;
        }
        .video-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.2); z-index: 1; pointer-events: none;
        }
        
        /* PC GLASS PANEL STYLE */
        .glass-auth-panel {
            background: rgba(5, 0, 0, 0.25);
            backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 50, 50, 0.4); border-radius: 24px;
            box-shadow: 0 40px 80px rgba(0,0,0,0.95);
        }
        
        /* MOBILE OPTIMIZATION: REMOVE BLUR, PURE CRYSTAL CLEAR GLASS */
        @media (max-width: 768px) {
            .glass-auth-panel {
                background: rgba(3, 0, 0, 0.15) !important;
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
                border: 1px solid rgba(255, 50, 50, 0.5) !important;
            }
        }
        
        .anime-title { font-family: 'Cinzel', serif; text-shadow: 0 0 30px rgba(255, 20, 20, 1); }
        .crimson-input { background: rgba(0, 0, 0, 0.7); border: 1px solid rgba(220, 38, 38, 0.35); color: #fef3c7; transition: all 0.3s; }
        .crimson-input:focus { outline: none; border-color: #ef4444; box-shadow: 0 0 20px rgba(239, 68, 68, 0.4); }
        select.crimson-input option { background: #000; color: #fef3c7; }
        .github-btn { background: rgba(15, 15, 15, 0.6); border: 1px solid rgba(255, 50, 50, 0.3); color: white; transition: all 0.3s; }
        .github-btn:hover { background: rgba(30, 30, 30, 0.9); box-shadow: 0 0 20px rgba(220,38,38,0.3); }
        .crimson-btn { background: linear-gradient(45deg, #7f1d1d, #dc2626); border: 1px solid #ef4444; box-shadow: 0 0 20px rgba(220, 38, 38, 0.5); transition: all 0.3s ease; }
        .crimson-btn:hover { background: linear-gradient(45deg, #991b1b, #f87171); box-shadow: 0 0 30px rgba(220, 38, 38, 0.8); }
        
        .audio-btn {
            position: fixed; bottom: 20px; right: 20px; z-index: 100;
            background: rgba(0,0,0,0.6); padding: 12px; border-radius: 50%;
            border: 1px solid rgba(255,50,50,0.4); color: #ef4444; transition: all 0.3s;
        }
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-thumb { background: #dc2626; border-radius: 10px; }
    </style>
</head>
<body class="p-4">

    <video id="bg-vid" autoplay muted loop playsinline class="bg-video">
        <source src="https://subczjjxgexeraofhykl.supabase.co/storage/v1/object/public/Assets/From%20Klickpin.com-%20Natural%20Makeup%20Looks%20Inspiration%20for%20Summer-pin-id-587860557652168444.mp4" type="video/mp4">
    </video>
    <div class="video-overlay"></div>

    <button onclick="toggleAudio()" class="audio-btn shadow-lg">
        <i id="audio-icon" class="fa-solid fa-volume-xmark text-lg"></i>
    </button>

    <div id="login-viewport" class="hidden w-full max-w-[410px] p-8 md:p-10 glass-auth-panel relative z-10">
        <div class="text-center mb-8">
            <h1 class="anime-title text-4xl md:text-5xl font-black text-red-500 tracking-widest mb-2">HOOK FORGE</h1>
            <p class="text-[10px] tracking-[0.4em] text-red-300/80 uppercase font-bold">Secure Cloud Portal</p>
        </div>

        <div id="msgBox" class="hidden p-3 rounded-xl text-xs font-mono text-center mb-6 border bg-red-950/80 border-red-500/50 text-red-200"></div>

        <div class="space-y-5">
            <button onclick="loginGitHub()" id="btn-github" class="w-full github-btn py-4 rounded-xl text-xs tracking-widest uppercase font-bold flex items-center justify-center gap-3 shadow-md">
                <i class="fa-brands fa-github text-base"></i> Continue with GitHub
            </button>

            <div class="relative flex py-2 items-center">
                <div class="flex-grow border-t border-red-500/30"></div>
                <span class="flex-shrink-0 mx-4 text-red-400/60 text-[9px] uppercase tracking-[0.3em] font-bold">Secure Routing</span>
                <div class="flex-grow border-t border-red-500/30"></div>
            </div>

            <div>
                <div class="relative mb-3">
                    <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 text-red-400/60"><i class="fa-solid fa-shield-halved text-xs"></i></span>
                    <input type="email" id="auth-email" placeholder="Enter security email" class="w-full crimson-input rounded-xl pl-10 pr-4 py-3.5 text-sm focus:outline-none">
                </div>
                <button onclick="sendMagicLink()" id="btn-email" class="w-full crimson-btn text-white font-bold py-4 rounded-xl text-xs tracking-widest uppercase transition-all shadow-lg">
                    Request Entry Token
                </button>
            </div>
        </div>
    </div>

    <div id="dashboard-viewport" class="hidden w-full max-w-6xl flex flex-col lg:flex-row gap-8 relative z-10 items-stretch justify-center">
        
        <div class="glass-auth-panel w-full lg:max-w-md p-6 flex flex-col justify-between">
            <div>
                <div class="text-center mb-6">
                    <h1 class="anime-title text-3xl font-black text-red-500 mb-1">HOOK FORGE</h1>
                    <p class="text-xs tracking-[0.3em] text-red-300 uppercase">Lycoris Protocol</p>
                </div>
                
                <div class="flex justify-between items-center mb-6 border-b border-red-900/40 pb-3 text-xs">
                    <div class="text-red-300 truncate max-w-[180px] font-mono"><i class="fa-solid fa-user-shield mr-1"></i> <span id="user-display" class="text-white"></span></div>
                    <button onclick="handleLogout()" class="bg-red-950/60 hover:bg-red-700 border border-red-800 px-3 py-1.5 rounded text-[10px] uppercase tracking-widest text-white font-bold transition-all"><i class="fa-solid fa-power-off mr-1"></i> Exit</button>
                </div>

                <div id="errorBox" class="hidden bg-red-900/80 border border-red-500 text-white p-3 rounded mb-4 text-xs font-mono"></div>

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
                        <textarea id="topic" rows="3" class="w-full crimson-input rounded-lg px-4 py-3 text-sm resize-none" placeholder="Enter core concept..."></textarea>
                    </div>
                </div>
            </div>
            
            <button onclick="forgeHooks()" class="w-full crimson-btn py-4 rounded-lg font-bold tracking-widest uppercase text-xs mt-6">
                <i class="fa-solid fa-fire mr-2"></i> Ignite Engine
            </button>
        </div>

        <div class="glass-auth-panel flex-grow p-6 flex flex-col justify-center min-h-[500px]">
            <div id="loading" class="hidden text-center">
                <i class="fa-solid fa-spinner fa-spin text-5xl text-red-500 mb-4 drop-shadow-[0_0_15px_rgba(220,38,38,0.8)]"></i>
                <h2 class="anime-title text-2xl text-red-100">Extracting Psychology Matrix...</h2>
            </div>

            <div id="empty-state" class="text-center opacity-50">
                <i class="fa-solid fa-crosshairs text-6xl text-red-500/50 mb-4"></i>
                <p class="text-xs font-mono tracking-widest uppercase">Awaiting Data Core Parameters...</p>
            </div>

            <div id="results" class="hidden space-y-5 overflow-y-auto max-h-[620px] pr-2">
                <div class="bg-black/50 border border-red-500/20 p-5 rounded-xl">
                    <div class="flex justify-between items-center mb-3">
                        <span class="text-[10px] bg-red-950/80 text-red-300 border border-red-800 px-2 py-0.5 rounded font-bold uppercase tracking-wider">Option A</span>
                        <span class="text-[10px] text-red-400 font-black tracking-widest">MATRIX SCORE: <span id="scoreA" class="text-red-500 text-base"></span></span>
                    </div>
                    <h3 id="textA" class="text-base md:text-lg font-bold text-amber-50 mb-3 tracking-wide"></h3>
                    <div class="text-xs text-red-200/80 space-y-2 border-t border-red-900/30 pt-3">
                        <p><strong class="text-red-400">Psychology:</strong> <span id="psychA"></span></p>
                        <p><strong class="text-red-400">Tactical Fix:</strong> <span id="fixA"></span></p>
                    </div>
                    <button onclick="copyText('textA')" class="mt-3 text-[10px] uppercase tracking-widest text-red-400 hover:text-red-200 transition-all"><i class="fa-regular fa-copy mr-1"></i> Extract Hook</button>
                </div>

                <div class="bg-black/50 border border-amber-500/20 p-5 rounded-xl">
                    <div class="flex justify-between items-center mb-3">
                        <span class="text-[10px] bg-amber-950/80 text-amber-300 border border-amber-800 px-2 py-0.5 rounded font-bold uppercase tracking-wider">Option B</span>
                        <span class="text-[10px] text-amber-400 font-black tracking-widest">MATRIX SCORE: <span id="scoreB" class="text-amber-500 text-base"></span></span>
                    </div>
                    <h3 id="textB" class="text-base md:text-lg font-bold text-amber-50 mb-3 tracking-wide"></h3>
                    <div class="text-xs text-red-200/80 space-y-2 border-t border-red-900/30 pt-3">
                        <p><strong class="text-amber-400">Psychology:</strong> <span id="psychB"></span></p>
                        <p><strong class="text-amber-400">Tactical Fix:</strong> <span id="fixB"></span></p>
                    </div>
                    <button onclick="copyText('textB')" class="mt-3 text-[10px] uppercase tracking-widest text-amber-400 hover:text-amber-200 transition-all"><i class="fa-regular fa-copy mr-1"></i> Extract Hook</button>
                </div>
                
                <div class="text-xs text-red-300 bg-red-950/20 p-4 rounded border border-red-900/40 font-mono leading-relaxed">
                    <strong class="uppercase tracking-widest block mb-1 text-red-400"><i class="fa-solid fa-dna mr-2"></i>DNA Matrix Analysis</strong>
                    <span id="dna"></span>
                </div>
            </div>
        </div>
    </div>

    <script>
        const vid = document.getElementById('bg-vid');
        vid.volume = 0.2; 

        function toggleAudio() {
            if (vid.muted) {
                vid.muted = false;
                document.getElementById('audio-icon').className = "fa-solid fa-volume-low text-lg";
            } else {
                vid.muted = true;
                document.getElementById('audio-icon').className = "fa-solid fa-volume-xmark text-lg";
            }
        }

        // Initialize Supabase Client
        const supabaseUrl = '{{ supabase_url }}';
        const supabaseKey = '{{ supabase_key }}';
        const sbClient = window.supabase.createClient(supabaseUrl, supabaseKey);

        let activeUserEmail = null;

        // SPA ROUTING LOGIC: Anti-Cookie Lock Mechanism
        function renderView(session) {
            const loginVp = document.getElementById('login-viewport');
            const dashVp = document.getElementById('dashboard-viewport');
            
            if (session && session.user) {
                activeUserEmail = session.user.email;
                document.getElementById('user-display').innerText = activeUserEmail;
                loginVp.style.display = 'none';
                dashVp.style.display = 'flex';
            } else {
                activeUserEmail = null;
                dashVp.style.display = 'none';
                loginVp.style.display = 'block';
            }
        }

        // Check active token state on boot
        sbClient.auth.getSession().then(({ data: { session } }) => {
            renderView(session);
        });

        // Watch authentication mutations in real-time
        sbClient.auth.onAuthStateChange((event, session) => {
            renderView(session);
        });

        async function loginGitHub() {
            try {
                document.getElementById('btn-github').innerHTML = '<i class="fa-solid fa-spinner fa-spin text-base"></i> Connecting Pipeline...';
                const { error } = await sbClient.auth.signInWithOAuth({ 
                    provider: 'github',
                    options: { redirectTo: window.location.origin }
                });
                if (error) throw error;
            } catch (error) {
                document.getElementById('msgBox').style.display = 'block';
                document.getElementById('msgBox').innerText = error.message;
                document.getElementById('btn-github').innerHTML = '<i class="fa-brands fa-github text-base"></i> Continue with GitHub';
            }
        }

        async function sendMagicLink() {
            const email = document.getElementById('auth-email').value.trim();
            if(!email) { alert("Please enter an email address."); return; }
            
            const btn = document.getElementById('btn-email');
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Dispatching...';
            
            try {
                const { error } = await sbClient.auth.signInWithOtp({ 
                    email: email,
                    options: { emailRedirectTo: window.location.origin }
                });
                if (error) throw error;
                alert("Secure access token dispatched to your inbox!");
                btn.innerHTML = 'Token Sent';
            } catch (error) {
                alert("Token Routing Error: " + error.message);
                btn.innerHTML = 'Request Entry Token';
            }
        }

        async function handleLogout() {
            await sbClient.auth.signOut();
        }

        async function forgeHooks() {
            if (!activeUserEmail) { alert("Session expired. Please re-authenticate."); return; }
            
            document.getElementById('empty-state').style.display = 'none';
            document.getElementById('results').style.display = 'none';
            document.getElementById('errorBox').style.display = 'none';
            document.getElementById('loading').style.display = 'block';
            
            try {
                const response = await fetch('/forge', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        email: activeUserEmail,
                        topic: document.getElementById('topic').value || "General Concept",
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
            alert("Hook acquired safely! ⚔️");
        }
    </script>
</body>
</html>
"""

# ==========================================
# 3. SECURE BACKEND ENDPOINTS (SESSIONLESS)
# ==========================================
@app.route('/')
def home():
    # Render unified layout directly. Frontend handles authorization states.
    return render_template_string(MASTER_HTML, supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY)

@app.route('/forge', methods=['POST'])
def forge():
    data = request.json
    # Authenticate via JSON payload email directly (bypasses broken mobile cookies)
    user_identity = data.get('email')
    if not user_identity:
        return jsonify({"error": "Unauthorized request parameters."}), 401

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
            return jsonify({"error": "SambaNova engine offline. Try again shortly."})
            
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
