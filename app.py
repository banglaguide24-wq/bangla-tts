from flask import Flask, request, send_file, render_template_string
import edge_tts
import asyncio
import io
import requests
import os
import time
import re

app = Flask(__name__)

# Environment Variable থেকে ElevenLabs Key পড়া (ঐচ্ছিক)
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY', '')

HTML = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>প্রো বাংলা TTS + ক্লোনিং ল্যাব</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, sans-serif;
            background: linear-gradient(145deg, #0a0f1e, #1a2639);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .card {
            background: rgba(26, 38, 57, 0.95);
            backdrop-filter: blur(12px);
            border-radius: 32px;
            padding: 35px 30px;
            max-width: 600px;
            width: 100%;
            border: 1px solid rgba(255, 255, 255, 0.06);
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.7);
        }
        .header { text-align: center; margin-bottom: 24px; }
        .logo { font-size: 42px; display: block; }
        h1 { color: #e2e8f0; font-weight: 600; font-size: 24px; }
        .subtitle { color: #94a3b8; font-size: 13px; margin-top: 4px; }

        .tabs { display: flex; gap: 8px; margin-bottom: 24px; background: rgba(15, 23, 42, 0.6); padding: 6px; border-radius: 16px; flex-wrap: wrap; }
        .tab-btn {
            flex: 1; padding: 12px; border: none; border-radius: 12px; background: transparent;
            color: #94a3b8; font-size: 14px; font-weight: 600; cursor: pointer; transition: 0.3s;
            min-width: 80px;
        }
        .tab-btn.active { background: #3b82f6; color: white; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3); }
        .tab-btn:hover:not(.active) { background: rgba(255,255,255,0.05); }

        .tab-content { display: none; }
        .tab-content.active { display: block; }

        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; color: #94a3b8; font-size: 13px; font-weight: 500; margin-bottom: 6px; }
        .form-group select, .form-group textarea, .form-group input[type="text"], .form-group input[type="password"] {
            width: 100%; padding: 14px 16px; border-radius: 16px; background: rgba(15, 23, 42, 0.8);
            color: #e2e8f0; border: 1px solid rgba(255, 255, 255, 0.06); font-size: 15px; outline: none;
            transition: 0.25s; font-family: inherit;
        }
        .form-group input[type="file"] {
            width: 100%; padding: 14px; border-radius: 16px; background: rgba(15, 23, 42, 0.8);
            color: #94a3b8; border: 1px dashed rgba(255, 255, 255, 0.15); font-size: 14px; outline: none; cursor: pointer;
        }
        .form-group input:focus, .form-group textarea:focus, .form-group select:focus {
            border-color: #3b82f6; box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.08); background: rgba(15, 23, 42, 0.95);
        }
        .form-group textarea { min-height: 100px; resize: vertical; line-height: 1.6; }

        /* ফাইল আপলোড ও কাউন্টারের জন্য নতুন স্টাইল */
        .row-flex { display: flex; gap: 15px; flex-wrap: wrap; }
        .row-flex .col { flex: 1; min-width: 120px; }
        .range-input { width: 100%; accent-color: #3b82f6; background: #0f172a; cursor: pointer; }
        .range-value { color: #e2e8f0; font-size: 14px; font-weight: 600; text-align: center; margin-top: 4px; }
        .char-counter { text-align: right; font-size: 13px; color: #64748b; padding-right: 4px; margin-top: 4px; }
        .char-counter.warning { color: #fbbf24; }
        .char-counter.danger { color: #f87171; }

        .btn {
            width: 100%; padding: 16px; border: none; border-radius: 50px; font-size: 17px;
            font-weight: 600; cursor: pointer; transition: 0.3s; display: flex; align-items: center;
            justify-content: center; gap: 10px;
        }
        .btn-primary { background: linear-gradient(135deg, #3b82f6, #7c3aed); color: white; }
        .btn-primary:hover:not(:disabled) { transform: scale(1.01); }
        .btn-success { background: linear-gradient(135deg, #059669, #10b981); color: white; }
        .btn-success:hover:not(:disabled) { transform: scale(1.01); }
        .btn-warning { background: linear-gradient(135deg, #d97706, #f59e0b); color: white; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .btn-download { background: linear-gradient(135deg, #0284c7, #2563eb); color: white; margin-top: 10px; }

        .status-box {
            margin-top: 16px; padding: 12px 16px; border-radius: 14px; background: rgba(15, 23, 42, 0.6);
            min-height: 50px; display: flex; align-items: center; gap: 12px; border: 1px solid rgba(255, 255, 255, 0.04);
        }
        .status-icon { font-size: 20px; flex-shrink: 0; }
        .status-text { color: #94a3b8; font-size: 14px; flex: 1; word-break: break-word; }
        .status-text.success { color: #34d399; }
        .status-text.error { color: #f87171; }
        .status-text.loading { color: #fbbf24; }
        .status-text.info { color: #60a5fa; }

        .audio-wrapper { margin-top: 16px; border-radius: 16px; overflow: hidden; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.04); display: none; }
        .audio-wrapper.show { display: block; }
        .audio-wrapper audio { width: 100%; display: block; padding: 12px 16px; background: transparent; outline: none; }

        .badge { background: rgba(251, 191, 36, 0.12); color: #fbbf24; padding: 2px 12px; border-radius: 20px; font-size: 11px; border: 1px solid rgba(251, 191, 36, 0.1); display: inline-block; margin-top: 4px; }
        .footer { margin-top: 20px; text-align: center; color: #475569; font-size: 11px; border-top: 1px solid rgba(255,255,255,0.04); padding-top: 16px; line-height: 1.8; }
        .footer a { color: #3b82f6; text-decoration: none; }

        .spinner { display: inline-block; width: 18px; height: 18px; border: 2px solid rgba(255,255,255,0.1); border-top-color: #fff; border-radius: 50%; animation: spin 0.7s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .info-box { background: #1e293b; padding: 12px; border-radius: 12px; border-left: 4px solid #f59e0b; margin-top: 12px; }
        .info-box p { color: #94a3b8; font-size: 13px; margin: 0; }
    </style>
</head>
<body>
<div class="card">
    <div class="header">
        <span class="logo">🎙️</span>
        <h1>প্রো বাংলা TTS</h1>
        <div class="subtitle">স্ট্যান্ডার্ড TTS + প্রো কন্ট্রোল</div>
    </div>

    <div class="tabs">
        <button class="tab-btn active" data-tab="tab1">🎧 স্ট্যান্ডার্ড</button>
        <button class="tab-btn" data-tab="tab2">🧬 ক্লোনিং ল্যাব</button>
    </div>

    <!-- Tab 1: Standard -->
    <div class="tab-content active" id="tab1">
        <div class="form-group">
            <label>🗣️ কণ্ঠ নির্বাচন</label>
            <select id="voiceSelect">
                <option value="bn-BD-NabanitaNeural">নবনীতা (নারী, বাংলাদেশ) ⭐</option>
                <option value="bn-BD-PradeepNeural">প্রদীপ (পুরুষ, বাংলাদেশ)</option>
                <option value="bn-IN-TanishaaNeural">তনিষা (নারী, ভারত)</option>
                <option value="bn-IN-SwaraNeural">স্বরা (নারী, ভারত)</option>
            </select>
        </div>

        <!-- NEW: Rate & Pitch Controls -->
        <div class="row-flex">
            <div class="col">
                <label>🐢 গতি (Speed)</label>
                <input type="range" class="range-input" id="rateControl" min="0.5" max="2.0" step="0.1" value="1.0">
                <div class="range-value" id="rateValue">1.0x</div>
            </div>
            <div class="col">
                <label>🎵 পিচ (Pitch)</label>
                <input type="range" class="range-input" id="pitchControl" min="-50" max="50" step="5" value="0">
                <div class="range-value" id="pitchValue">0%</div>
            </div>
        </div>

        <div class="form-group">
            <label>📝 টেক্সট লিখুন</label>
            <textarea id="textInput1">আমি পেশাদার কণ্ঠে বাংলায় কথা বলতে পারি।</textarea>
            <div class="char-counter" id="charCounter">0 / 3000</div>
        </div>

        <!-- NEW: File Upload -->
        <div class="form-group">
            <label>📂 টেক্সট ফাইল আপলোড (.txt)</label>
            <input type="file" id="fileUpload" accept=".txt">
        </div>

        <button class="btn btn-primary" id="speakBtn1">🔊 শুনুন ও ডাউনলোড করুন</button>
        <div class="status-box" id="statusBox1">
            <span class="status-icon">✅</span>
            <span class="status-text" id="statusText1">প্রস্তুত। টেক্সট লিখে শুনুন ক্লিক করুন।</span>
        </div>
        <div class="audio-wrapper" id="audioWrapper1"><audio id="audioPlayer1" controls></audio></div>
    </div>

    <!-- Tab 2: Cloning Lab -->
    <div class="tab-content" id="tab2">
        <div class="info-box">
            <p>🧪 <strong>ভয়েস ক্লোনিং ল্যাব</strong><br>
            ElevenLabs-এর ক্লোনিং ফিচারটি পেইড ($৫/মাস)। ফ্রিতে ব্যবহারের জন্য নিচের ওপেন-সোর্স টুল ব্যবহার করুন। <br>
            ✅ <strong>ফ্রি বিকল্প:</strong> <a href="https://github.com/debpalash/OmniVoice-Studio" target="_blank" style="color:#3b82f6;">OmniVoice Studio</a></p>
        </div>
        <div class="form-group">
            <label>🔑 ElevenLabs API Key (পেইড প্ল্যান প্রয়োজন)</label>
            <input type="password" id="apiKey" placeholder="পেইড প্ল্যানের API Key দিন (ঐচ্ছিক)">
        </div>
        <div class="form-group">
            <label>🎤 আপনার ভয়েস আপলোড করুন</label>
            <input type="file" id="voiceFile" accept="audio/*">
            <span class="badge">WAV, MP3, M4A</span>
        </div>
        <div class="form-group">
            <label>📝 টেক্সট লিখুন (আপনার কণ্ঠে শুনতে চান)</label>
            <textarea id="textInput2">আমি আমার নিজের কণ্ঠে বাংলায় কথা বলছি।</textarea>
        </div>
        <button class="btn btn-warning" id="speakBtn2">🧬 ক্লোনিং চেষ্টা করুন (পেইড)</button>
        <div class="status-box" id="statusBox2">
            <span class="status-icon">ℹ️</span>
            <span class="status-text" id="statusText2">পেইড API Key দিন অথবা ফ্রি OmniVoice Studio ব্যবহার করুন।</span>
        </div>
        <div class="audio-wrapper" id="audioWrapper2"><audio id="audioPlayer2" controls></audio></div>
    </div>

    <div class="footer">⚡ স্ট্যান্ডার্ড TTS ফ্রি · ক্লোনিং পেইড</div>
</div>

<script>
    // ============= NEW: RATE & PITCH SLIDER SYNC =============
    const rateControl = document.getElementById('rateControl');
    const pitchControl = document.getElementById('pitchControl');
    const rateValue = document.getElementById('rateValue');
    const pitchValue = document.getElementById('pitchValue');
    rateControl.addEventListener('input', () => { rateValue.textContent = rateControl.value + 'x'; });
    pitchControl.addEventListener('input', () => { pitchValue.textContent = pitchControl.value + '%'; });

    // ============= NEW: FILE UPLOAD LOGIC =============
    document.getElementById('fileUpload').addEventListener('change', function(e) {
        const file = this.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = function(ev) {
            document.getElementById('textInput1').value = ev.target.result;
            updateCharCounter();
        };
        reader.readAsText(file, 'UTF-8');
    });

    // ============= NEW: CHARACTER COUNTER (LIMIT 3000) =============
    const textInput1 = document.getElementById('textInput1');
    const charCounter = document.getElementById('charCounter');
    function updateCharCounter() {
        const len = textInput1.value.length;
        const max = 3000;  // 🔥 এখানে লিমিট ৩০০০ সেট করা আছে
        charCounter.textContent = len + ' / ' + max;
        charCounter.className = 'char-counter';
        if (len > max) charCounter.classList.add('danger');
        else if (len > max * 0.8) charCounter.classList.add('warning');
    }
    textInput1.addEventListener('input', updateCharCounter);
    updateCharCounter();

    // ============= NEW: LOCALSTORAGE AUTO-SAVE (DRAFT) =============
    window.addEventListener('load', function() {
        const saved = localStorage.getItem('bangla_tts_draft');
        if (saved) {
            textInput1.value = saved;
            updateCharCounter();
        }
    });
    textInput1.addEventListener('input', function() {
        localStorage.setItem('bangla_tts_draft', this.value);
    });

    // ============= TAB TOGGLE =============
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
            document.getElementById(this.dataset.tab).classList.add('active');
        });
    });

    // ========== STANDARD TTS ==========
    const voiceSelect = document.getElementById('voiceSelect');
    const speakBtn1 = document.getElementById('speakBtn1');
    const status1 = document.getElementById('statusText1');
    const statusIcon1 = document.querySelector('#statusBox1 .status-icon');
    const audio1 = document.getElementById('audioPlayer1');
    const wrapper1 = document.getElementById('audioWrapper1');
    let url1 = null;

    function setStatus1(msg, type='info') {
        status1.textContent = msg;
        status1.className = 'status-text';
        if(type==='success'){ status1.classList.add('success'); statusIcon1.textContent='✅'; }
        else if(type==='error'){ status1.classList.add('error'); statusIcon1.textContent='❌'; }
        else if(type==='loading'){ status1.classList.add('loading'); statusIcon1.textContent='⏳'; }
        else { statusIcon1.textContent='ℹ️'; }
    }

    speakBtn1.addEventListener('click', async function() {
        const text = textInput1.value.trim();
        const voice = voiceSelect.value;
        const rate = parseFloat(rateControl.value);
        const pitch = parseInt(pitchControl.value);

        if(!text){ setStatus1('টেক্সট লিখুন','error'); return; }
        if(text.length > 3000){ setStatus1('সর্বোচ্চ ৩০০০ অক্ষর','error'); return; } // 🔥 Limit ৩০০০

        setStatus1('জেনারেট হচ্ছে...','loading');
        speakBtn1.disabled = true;
        speakBtn1.innerHTML = '<span class="spinner"></span> জেনারেট...';
        try {
            const form = new FormData();
            form.append('text', text);
            form.append('voice', voice);
            form.append('rate', rate);
            form.append('pitch', pitch);

            const res = await fetch('/synthesize', { method:'POST', body:form });
            if(!res.ok) throw new Error(await res.text());
            const blob = await res.blob();
            if(url1) URL.revokeObjectURL(url1);
            url1 = URL.createObjectURL(blob);
            audio1.src = url1;
            wrapper1.classList.add('show');
            await audio1.play();
            setStatus1('✅ অডিও প্রস্তুত! ডাউনলোড করুন।','success');
            if(!document.getElementById('dl1')){
                const dbtn = document.createElement('button');
                dbtn.id = 'dl1';
                dbtn.className = 'btn btn-download';
                dbtn.innerHTML = '⬇️ MP3 ডাউনলোড';
                dbtn.style.marginTop = '10px';
                dbtn.onclick = () => { const a = document.createElement('a'); a.href = url1; a.download = `tts_${Date.now()}.mp3`; a.click(); };
                wrapper1.appendChild(dbtn);
            }
        } catch(e) {
            setStatus1('❌ '+e.message,'error');
        } finally {
            speakBtn1.disabled = false;
            speakBtn1.innerHTML = '🔊 শুনুন ও ডাউনলোড করুন';
        }
    });

    // ========== CLONING (PAID) ==========
    const apiKeyInput = document.getElementById('apiKey');
    const voiceFile = document.getElementById('voiceFile');
    const text2 = document.getElementById('textInput2');
    const speakBtn2 = document.getElementById('speakBtn2');
    const status2 = document.getElementById('statusText2');
    const statusIcon2 = document.querySelector('#statusBox2 .status-icon');
    const audio2 = document.getElementById('audioPlayer2');
    const wrapper2 = document.getElementById('audioWrapper2');
    let url2 = null;

    function setStatus2(msg, type='info') {
        status2.textContent = msg;
        status2.className = 'status-text';
        if(type==='success'){ status2.classList.add('success'); statusIcon2.textContent='✅'; }
        else if(type==='error'){ status2.classList.add('error'); statusIcon2.textContent='❌'; }
        else if(type==='loading'){ status2.classList.add('loading'); statusIcon2.textContent='⏳'; }
        else { statusIcon2.textContent='ℹ️'; }
    }

    speakBtn2.addEventListener('click', async function() {
        const apiKey = apiKeyInput.value.trim();
        const text = text2.value.trim();
        const file = voiceFile.files[0];

        if(!apiKey){ setStatus2('❌ ElevenLabs পেইড API Key দিন।','error'); return; }
        if(!text){ setStatus2('টেক্সট লিখুন','error'); return; }
        if(!file){ setStatus2('অডিও ফাইল আপলোড করুন','error'); return; }

        setStatus2('🔄 ক্লোনিং শুরু...','loading');
        speakBtn2.disabled = true;
        speakBtn2.innerHTML = '<span class="spinner"></span> ক্লোনিং...';

        try {
            const form = new FormData();
            form.append('api_key', apiKey);
            form.append('text', text);
            form.append('audio_file', file);

            const res = await fetch('/clone', { method:'POST', body:form });
            if(!res.ok) {
                const err = await res.text();
                throw new Error(err || 'ক্লোনিং ব্যর্থ');
            }
            const blob = await res.blob();
            if(url2) URL.revokeObjectURL(url2);
            url2 = URL.createObjectURL(blob);
            audio2.src = url2;
            wrapper2.classList.add('show');
            await audio2.play();
            setStatus2('✅ ক্লোন সফল!','success');
            if(!document.getElementById('dl2')){
                const dbtn = document.createElement('button');
                dbtn.id = 'dl2';
                dbtn.className = 'btn btn-download';
                dbtn.innerHTML = '⬇️ MP3 ডাউনলোড (ক্লোন)';
                dbtn.style.marginTop = '10px';
                dbtn.onclick = () => { const a = document.createElement('a'); a.href = url2; a.download = `cloned_${Date.now()}.mp3`; a.click(); };
                wrapper2.appendChild(dbtn);
            }
        } catch(e) {
            setStatus2('❌ '+e.message,'error');
        } finally {
            speakBtn2.disabled = false;
            speakBtn2.innerHTML = '🧬 ক্লোনিং চেষ্টা করুন (পেইড)';
        }
    });
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

# ========== STANDARD TTS (edge-tts) with SSML ==========
@app.route('/synthesize', methods=['POST'])
def synthesize():
    text = request.form.get('text', '').strip()
    voice = request.form.get('voice', 'bn-BD-NabanitaNeural')
    rate = float(request.form.get('rate', 1.0))
    pitch = int(request.form.get('pitch', 0))
    
    if not text:
        return 'টেক্সট খালি', 400

    try:
        # SSML তৈরি করা (গতি ও পিচ কন্ট্রোলের জন্য)
        pitch_str = f"+{pitch}%" if pitch >= 0 else f"{pitch}%"
        
        ssml = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="bn-BD">
            <prosody rate="{rate}" pitch="{pitch_str}">
                {text}
            </prosody>
        </speak>
        """
        
        async def gen():
            comm = edge_tts.Communicate(ssml, voice)
            data = b""
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    data += chunk["data"]
            return data
            
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_bytes = loop.run_until_complete(gen())
        loop.close()
        return send_file(io.BytesIO(audio_bytes), mimetype='audio/mpeg')
    except Exception as e:
        return str(e), 500

# ========== CLONING (PAID) ==========
@app.route('/clone', methods=['POST'])
def clone_voice():
    api_key = request.form.get('api_key', '').strip()
    text = request.form.get('text', '').strip()
    audio_file = request.files.get('audio_file')
    
    if not api_key:
        return 'ElevenLabs API Key (পেইড প্ল্যান) প্রয়োজন', 400
    if not text:
        return 'টেক্সট দিন', 400
    if not audio_file:
        return 'অডিও ফাইল দিন', 400

    try:
        temp_path = f"/tmp/clone_{int(time.time())}.wav"
        audio_file.save(temp_path)

        url_add = "https://api.elevenlabs.io/v1/voices/add"
        headers_add = {"xi-api-key": api_key}
        with open(temp_path, 'rb') as f:
            files = {'files': ('voice.wav', f, 'audio/wav')}
            data = {'name': f'Cloned_{int(time.time())}'}
            response_add = requests.post(url_add, headers=headers_add, data=data, files=files)
        
        if response_add.status_code != 200:
            os.remove(temp_path)
            return f"ক্লোনিং ব্যর্থ: {response_add.text}", 400
        
        voice_id = response_add.json()['voice_id']
        os.remove(temp_path)

        url_tts = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers_tts = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        response_tts = requests.post(url_tts, json=payload, headers=headers_tts)
        
        if response_tts.status_code != 200:
            return f"TTS ব্যর্থ: {response_tts.text}", 400

        return send_file(
            io.BytesIO(response_tts.content),
            mimetype='audio/mpeg',
            as_attachment=False
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
