from flask import Flask, request, send_file, render_template_string
import edge_tts
import asyncio
import io
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>প্রো বাংলা TTS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, sans-serif;
            background: #0b1120;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .card {
            background: #1a2332;
            border-radius: 32px;
            padding: 35px 30px;
            max-width: 560px;
            width: 100%;
            border: 1px solid rgba(255, 255, 255, 0.06);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8);
        }
        .header { text-align: center; margin-bottom: 28px; }
        .logo { font-size: 44px; display: block; }
        h1 { color: #f1f5f9; font-weight: 600; font-size: 26px; }
        .subtitle {
            color: #94a3b8;
            font-size: 13px;
            margin-top: 4px;
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
        }
        .badge {
            background: #065f46;
            color: #34d399;
            padding: 2px 14px;
            border-radius: 30px;
            font-size: 11px;
            font-weight: 600;
            border: 1px solid rgba(16, 185, 129, 0.15);
        }

        .form-group { margin-bottom: 18px; }
        .form-group label {
            display: block;
            color: #94a3b8;
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 6px;
        }
        .form-group select, .form-group textarea {
            width: 100%;
            padding: 14px 16px;
            border-radius: 16px;
            background: #0f172a;
            color: #e2e8f0;
            border: 1px solid #2d3b52;
            font-size: 15px;
            outline: none;
            transition: 0.2s;
            font-family: inherit;
        }
        .form-group input[type="file"] {
            width: 100%;
            padding: 14px;
            border-radius: 16px;
            background: #0f172a;
            color: #94a3b8;
            border: 1px dashed #2d3b52;
            font-size: 14px;
            cursor: pointer;
        }
        .form-group select:focus, .form-group textarea:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.08);
        }
        .form-group textarea {
            min-height: 120px;
            resize: vertical;
            line-height: 1.6;
        }

        .row-flex { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 6px; }
        .row-flex .col { flex: 1; min-width: 120px; }
        .range-input { width: 100%; accent-color: #3b82f6; cursor: pointer; }
        .range-value { color: #e2e8f0; font-size: 14px; font-weight: 600; text-align: center; margin-top: 2px; }

        .char-counter {
            text-align: right;
            font-size: 13px;
            color: #64748b;
            margin-top: 4px;
        }
        .char-counter.danger { color: #f87171; }

        .btn {
            width: 100%;
            padding: 16px;
            border: none;
            border-radius: 50px;
            font-size: 17px;
            font-weight: 600;
            cursor: pointer;
            transition: 0.25s;
            background: linear-gradient(135deg, #3b82f6, #7c3aed);
            color: white;
            box-shadow: 0 8px 24px rgba(59, 130, 246, 0.2);
        }
        .btn:hover:not(:disabled) { transform: scale(1.01); box-shadow: 0 12px 32px rgba(59, 130, 246, 0.35); }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .btn-download {
            background: linear-gradient(135deg, #0284c7, #2563eb);
            margin-top: 10px;
        }

        .status-box {
            margin-top: 16px;
            padding: 12px 16px;
            border-radius: 14px;
            background: #0f172a;
            min-height: 50px;
            display: flex;
            align-items: center;
            gap: 12px;
            border: 1px solid rgba(255, 255, 255, 0.04);
        }
        .status-icon { font-size: 20px; }
        .status-text { color: #94a3b8; font-size: 14px; flex: 1; }
        .status-text.success { color: #34d399; }
        .status-text.error { color: #f87171; }
        .status-text.loading { color: #fbbf24; }

        .audio-wrapper {
            margin-top: 16px;
            border-radius: 16px;
            overflow: hidden;
            background: #0f172a;
            border: 1px solid rgba(255, 255, 255, 0.04);
            display: none;
        }
        .audio-wrapper.show { display: block; }
        .audio-wrapper audio {
            width: 100%;
            display: block;
            padding: 12px 16px;
            background: transparent;
            outline: none;
        }

        .footer {
            margin-top: 24px;
            text-align: center;
            color: #475569;
            font-size: 11px;
            border-top: 1px solid rgba(255, 255, 255, 0.04);
            padding-top: 16px;
        }
        .spinner {
            display: inline-block;
            width: 18px;
            height: 18px;
            border: 2px solid rgba(255,255,255,0.1);
            border-top-color: #fff;
            border-radius: 50%;
            animation: spin 0.7s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        @media (max-width: 480px) {
            .card { padding: 25px 18px; }
            h1 { font-size: 22px; }
            .btn { font-size: 15px; padding: 14px; }
        }
    </style>
</head>
<body>
<div class="card">
    <div class="header">
        <span class="logo">🎙️</span>
        <h1>প্রো বাংলা TTS</h1>
        <div class="subtitle">
            <span>Microsoft Edge Neural</span>
            <span class="badge">✅ MP3 ডাউনলোড</span>
        </div>
    </div>

    <div class="form-group">
        <label>🗣️ কণ্ঠ নির্বাচন</label>
        <select id="voiceSelect">
            <option value="bn-BD-NabanitaNeural">নবনীতা (নারী, বাংলাদেশ) ⭐</option>
            <option value="bn-BD-PradeepNeural">প্রদীপ (পুরুষ, বাংলাদেশ)</option>
            <option value="bn-IN-TanishaaNeural">তনিষা (নারী, ভারত)</option>
            <option value="bn-IN-SwaraNeural">স্বরা (নারী, ভারত)</option>
        </select>
    </div>

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
        <label>📝 বাংলা টেক্সট লিখুন</label>
        <textarea id="textInput1" placeholder="এখানে বাংলা টেক্সট লিখুন...">আমি পেশাদার কণ্ঠে বাংলায় কথা বলতে পারি। এটি অত্যন্ত স্বাভাবিক শোনাচ্ছে এবং সম্পূর্ণ বিনামূল্যে।</textarea>
        <div class="char-counter" id="charCounter">0 / 3000</div>
    </div>

    <div class="form-group">
        <label>📂 টেক্সট ফাইল আপলোড করুন (.txt)</label>
        <input type="file" id="fileUpload" accept=".txt">
    </div>

    <button class="btn" id="speakBtn">🔊 শুনুন ও ডাউনলোড করুন</button>

    <div class="status-box" id="statusBox">
        <span class="status-icon">✅</span>
        <span class="status-text" id="statusText">প্রস্তুত। টেক্সট লিখে শুনুন ক্লিক করুন।</span>
    </div>

    <div class="audio-wrapper" id="audioWrapper">
        <audio id="audioPlayer" controls></audio>
    </div>

    <div class="footer">⚡ সম্পূর্ণ ফ্রি · Edge Neural TTS</div>
</div>

<script>
    // ===== স্লাইডার সিঙ্ক =====
    document.getElementById('rateControl').addEventListener('input', function() {
        document.getElementById('rateValue').textContent = this.value + 'x';
    });
    document.getElementById('pitchControl').addEventListener('input', function() {
        document.getElementById('pitchValue').textContent = this.value + '%';
    });

    // ===== ক্যারেক্টার কাউন্টার =====
    const textInput = document.getElementById('textInput1');
    const charCounter = document.getElementById('charCounter');
    const MAX_CHARS = 3000;
    
    function updateCounter() {
        const len = textInput.value.length;
        charCounter.textContent = len + ' / ' + MAX_CHARS;
        charCounter.className = 'char-counter';
        if (len > MAX_CHARS) charCounter.classList.add('danger');
    }
    textInput.addEventListener('input', updateCounter);
    updateCounter(); // পেজ লোডে আপডেট

    // ===== ফাইল আপলোড =====
    document.getElementById('fileUpload').addEventListener('change', function(e) {
        const file = this.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = function(ev) {
            textInput.value = ev.target.result;
            updateCounter();
        };
        reader.readAsText(file, 'UTF-8');
        this.value = '';
    });

    // ===== লোকালস্টোরেজ অটো-সেভ =====
    window.addEventListener('load', function() {
        const saved = localStorage.getItem('bangla_tts_draft');
        if (saved) {
            textInput.value = saved;
            updateCounter();
        }
    });
    textInput.addEventListener('input', function() {
        localStorage.setItem('bangla_tts_draft', this.value);
    });

    // ===== TTS জেনারেট =====
    const speakBtn = document.getElementById('speakBtn');
    const statusText = document.getElementById('statusText');
    const statusIcon = document.querySelector('#statusBox .status-icon');
    const audioPlayer = document.getElementById('audioPlayer');
    const audioWrapper = document.getElementById('audioWrapper');
    let currentAudioUrl = null;

    function setStatus(msg, type = 'info') {
        statusText.textContent = msg;
        statusText.className = 'status-text';
        if (type === 'success') { statusText.classList.add('success'); statusIcon.textContent = '✅'; }
        else if (type === 'error') { statusText.classList.add('error'); statusIcon.textContent = '❌'; }
        else if (type === 'loading') { statusText.classList.add('loading'); statusIcon.textContent = '⏳'; }
        else { statusIcon.textContent = 'ℹ️'; }
    }

    speakBtn.addEventListener('click', async function() {
        const text = textInput.value.trim();
        const voice = document.getElementById('voiceSelect').value;
        const rate = parseFloat(document.getElementById('rateControl').value);
        const pitch = parseInt(document.getElementById('pitchControl').value);

        if (!text) { setStatus('দয়া করে কিছু টেক্সট লিখুন।', 'error'); return; }
        if (text.length > MAX_CHARS) { setStatus('সর্বোচ্চ ' + MAX_CHARS + ' অক্ষর।', 'error'); return; }

        setStatus('⏳ ভয়েস জেনারেট হচ্ছে...', 'loading');
        speakBtn.disabled = true;
        speakBtn.innerHTML = '<span class="spinner"></span> জেনারেট হচ্ছে...';

        try {
            const formData = new FormData();
            formData.append('text', text);
            formData.append('voice', voice);
            formData.append('rate', rate);
            formData.append('pitch', pitch);

            const response = await fetch('/synthesize', { method: 'POST', body: formData });
            if (!response.ok) {
                const err = await response.text();
                throw new Error(err || 'সার্ভার সমস্যা');
            }

            const blob = await response.blob();
            if (currentAudioUrl) URL.revokeObjectURL(currentAudioUrl);
            currentAudioUrl = URL.createObjectURL(blob);

            audioPlayer.src = currentAudioUrl;
            audioWrapper.classList.add('show');
            await audioPlayer.play();

            setStatus('✅ সফল! অডিও বাজছে। এখন ডাউনলোড করতে পারেন।', 'success');

            if (!document.getElementById('dlBtn')) {
                const dlBtn = document.createElement('button');
                dlBtn.id = 'dlBtn';
                dlBtn.className = 'btn btn-download';
                dlBtn.innerHTML = '⬇️ MP3 ডাউনলোড';
                dlBtn.style.marginTop = '10px';
                dlBtn.onclick = () => {
                    const a = document.createElement('a');
                    a.href = currentAudioUrl;
                    a.download = `tts_${Date.now()}.mp3`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                };
                audioWrapper.appendChild(dlBtn);
            }

        } catch (error) {
            console.error(error);
            setStatus('❌ সমস্যা: ' + error.message, 'error');
        } finally {
            speakBtn.disabled = false;
            speakBtn.innerHTML = '🔊 শুনুন ও ডাউনলোড করুন';
        }
    });

    // ===== Ctrl+Enter শর্টকাট =====
    textInput.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            speakBtn.click();
        }
    });
</script>
</body>
</html>
"""


@app.route('/')
def home():
    return render_template_string(HTML)


@app.route('/synthesize', methods=['POST'])
def synthesize():
    text = request.form.get('text', '').strip()
    voice = request.form.get('voice', 'bn-BD-NabanitaNeural')
    rate = float(request.form.get('rate', 1.0))
    pitch = int(request.form.get('pitch', 0))

    if not text:
        return 'টেক্সট খালি', 400
    if len(text) > 3000:
        return 'সর্বোচ্চ ৩০০০ অক্ষর', 400

    try:
        pitch_str = f"+{pitch}%" if pitch >= 0 else f"{pitch}%"
        ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="bn-BD">
            <prosody rate="{rate}" pitch="{pitch_str}">
                {text}
            </prosody>
        </speak>"""

        async def generate_audio():
            communicate = edge_tts.Communicate(ssml, voice)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return audio_data

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_bytes = loop.run_until_complete(generate_audio())
        loop.close()

        return send_file(
            io.BytesIO(audio_bytes),
            mimetype='audio/mpeg',
            as_attachment=False
        )

    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
