from flask import Flask, request, send_file, render_template_string
import edge_tts
import asyncio
import io
import os
from gtts import gTTS

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
            max-width: 580px;
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
        .badge { background: #065f46; color: #34d399; padding: 2px 14px; border-radius: 30px; font-size: 11px; font-weight: 600; border: 1px solid rgba(16, 185, 129, 0.15); }
        .badge-gtts { background: #1e293b; color: #60a5fa; padding: 2px 14px; border-radius: 30px; font-size: 11px; font-weight: 600; border: 1px solid rgba(96, 165, 250, 0.15); }

        .tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 28px;
            background: #0f172a;
            padding: 6px;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.03);
        }
        .tab-btn {
            flex: 1;
            padding: 12px 8px;
            border: none;
            border-radius: 12px;
            background: transparent;
            color: #94a3b8;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.25s ease;
        }
        .tab-btn.active { background: #3b82f6; color: white; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3); }
        .tab-btn:hover:not(.active) { background: rgba(255, 255, 255, 0.05); }

        .tab-content { display: none; animation: fadeIn 0.3s ease; }
        .tab-content.active { display: block; }
        @keyframes fadeIn { from { opacity: 0.5; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

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
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #3b82f6, #7c3aed);
            color: white;
            box-shadow: 0 8px 24px rgba(59, 130, 246, 0.2);
        }
        .btn-primary:hover:not(:disabled) { transform: scale(1.01); box-shadow: 0 12px 32px rgba(59, 130, 246, 0.35); }
        .btn-gtts {
            background: linear-gradient(135deg, #059669, #10b981);
            color: white;
            box-shadow: 0 8px 24px rgba(16, 185, 129, 0.2);
        }
        .btn-gtts:hover:not(:disabled) { transform: scale(1.01); }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none !important; }
        .btn-download {
            background: linear-gradient(135deg, #0284c7, #2563eb);
            color: white;
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
            line-height: 1.8;
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
            .tab-btn { font-size: 12px; padding: 10px 6px; }
        }
        .info-box {
            background: #1e293b;
            padding: 10px 14px;
            border-radius: 10px;
            border-left: 4px solid #f59e0b;
            margin-bottom: 16px;
        }
        .info-box p { color: #94a3b8; font-size: 13px; margin: 0; line-height: 1.6; }
        .info-box strong { color: #e2e8f0; }
    </style>
</head>
<body>

<div class="card">
    <div class="header">
        <span class="logo">🎙️</span>
        <h1>প্রো বাংলা TTS</h1>
        <div class="subtitle">
            <span class="badge">✅ Edge Neural (ফ্রি)</span>
            <span class="badge-gtts">🔵 gTTS (ফ্রি)</span>
        </div>
    </div>

    <div class="tabs">
        <button class="tab-btn active" data-tab="tab1">🎧 Edge TTS</button>
        <button class="tab-btn" data-tab="tab2">🔵 gTTS</button>
    </div>

    <!-- ============================ -->
    <!-- ট্যাব ১: Edge TTS -->
    <!-- ============================ -->
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

        <div class="row-flex">
            <div class="col">
                <label>🐢 গতি</label>
                <input type="range" class="range-input" id="rateControl" min="0.5" max="2.0" step="0.1" value="1.0">
                <div class="range-value" id="rateValue">1.0x</div>
            </div>
            <div class="col">
                <label>🎵 পিচ</label>
                <input type="range" class="range-input" id="pitchControl" min="-50" max="50" step="5" value="0">
                <div class="range-value" id="pitchValue">0%</div>
            </div>
        </div>

        <div class="form-group">
            <label>📝 টেক্সট লিখুন</label>
            <textarea id="textInput1" placeholder="বাংলা টেক্সট লিখুন...">আমি Edge Neural ভয়েসে বাংলায় কথা বলছি। এটি সম্পূর্ণ বিনামূল্যে।</textarea>
            <div class="char-counter" id="charCounter1">0 / 3000</div>
        </div>

        <div class="form-group">
            <label>📂 টেক্সট ফাইল আপলোড (.txt)</label>
            <input type="file" id="fileUpload1" accept=".txt">
        </div>

        <button class="btn btn-primary" id="speakBtn1">🔊 শুনুন ও ডাউনলোড করুন</button>

        <div class="status-box" id="statusBox1">
            <span class="status-icon">✅</span>
            <span class="status-text" id="statusText1">প্রস্তুত।</span>
        </div>

        <div class="audio-wrapper" id="audioWrapper1">
            <audio id="audioPlayer1" controls></audio>
        </div>
    </div>

    <!-- ============================ -->
    <!-- ট্যাব ২: gTTS -->
    <!-- ============================ -->
    <div class="tab-content" id="tab2">
        <div class="info-box">
            <p><strong>🔵 gTTS (Google Translate TTS)</strong><br>
            Google Translate-এর TTS ইঞ্জিন। <br>
            ✅ কোনো API Key লাগে না <br>
            ✅ কোনো সাইনআপ লাগে না <br>
            ✅ সম্পূর্ণ ফ্রি
            </p>
        </div>

        <div class="form-group">
            <label>📝 টেক্সট লিখুন</label>
            <textarea id="textInput2" placeholder="বাংলা টেক্সট লিখুন...">আমি Google Translate-এর ভয়েসে বাংলায় কথা বলছি। এটি সম্পূর্ণ বিনামূল্যে।</textarea>
            <div class="char-counter" id="charCounter2">0 / 5000</div>
        </div>

        <div class="form-group">
            <label>📂 টেক্সট ফাইল আপলোড (.txt)</label>
            <input type="file" id="fileUpload2" accept=".txt">
        </div>

        <button class="btn btn-gtts" id="speakBtn2">🔊 Google ভয়েস তৈরি করুন</button>

        <div class="status-box" id="statusBox2">
            <span class="status-icon">✅</span>
            <span class="status-text" id="statusText2">প্রস্তুত।</span>
        </div>

        <div class="audio-wrapper" id="audioWrapper2">
            <audio id="audioPlayer2" controls></audio>
        </div>
    </div>

    <div class="footer">⚡ Edge Neural · gTTS — উভয়ই সম্পূর্ণ ফ্রি (কার্ড/সাইনআপ ছাড়া)</div>
</div>

<script>
    // ============================================================
    // ট্যাব টগল
    // ============================================================
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
            document.getElementById(this.dataset.tab).classList.add('active');
        });
    });

    // ============================================================
    // Edge TTS (ট্যাব ১)
    // ============================================================
    document.getElementById('rateControl').addEventListener('input', function() {
        document.getElementById('rateValue').textContent = this.value + 'x';
    });
    document.getElementById('pitchControl').addEventListener('input', function() {
        document.getElementById('pitchValue').textContent = this.value + '%';
    });

    const textInput1 = document.getElementById('textInput1');
    const charCounter1 = document.getElementById('charCounter1');
    const MAX_CHARS1 = 3000;
    textInput1.addEventListener('input', function() {
        const len = this.value.length;
        charCounter1.textContent = len + ' / ' + MAX_CHARS1;
        charCounter1.className = 'char-counter';
        if (len > MAX_CHARS1) charCounter1.classList.add('danger');
    });

    document.getElementById('fileUpload1').addEventListener('change', function(e) {
        const file = this.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = function(ev) {
            textInput1.value = ev.target.result;
            textInput1.dispatchEvent(new Event('input'));
        };
        reader.readAsText(file, 'UTF-8');
        this.value = '';
    });

    // ===== Edge TTS জেনারেট =====
    const speakBtn1 = document.getElementById('speakBtn1');
    const statusText1 = document.getElementById('statusText1');
    const statusIcon1 = document.querySelector('#statusBox1 .status-icon');
    const audioPlayer1 = document.getElementById('audioPlayer1');
    const audioWrapper1 = document.getElementById('audioWrapper1');
    let currentAudioUrl1 = null;

    function setStatus1(msg, type = 'info') {
        statusText1.textContent = msg;
        statusText1.className = 'status-text';
        if (type === 'success') { statusText1.classList.add('success'); statusIcon1.textContent = '✅'; }
        else if (type === 'error') { statusText1.classList.add('error'); statusIcon1.textContent = '❌'; }
        else if (type === 'loading') { statusText1.classList.add('loading'); statusIcon1.textContent = '⏳'; }
        else { statusIcon1.textContent = 'ℹ️'; }
    }

    speakBtn1.addEventListener('click', async function() {
        const text = textInput1.value.trim();
        const voice = document.getElementById('voiceSelect').value;
        const rate = parseFloat(document.getElementById('rateControl').value);
        const pitch = parseInt(document.getElementById('pitchControl').value);

        if (!text) { setStatus1('টেক্সট লিখুন।', 'error'); return; }
        if (text.length > MAX_CHARS1) { setStatus1('সর্বোচ্চ ' + MAX_CHARS1 + ' অক্ষর।', 'error'); return; }

        setStatus1('⏳ জেনারেট...', 'loading');
        speakBtn1.disabled = true;
        speakBtn1.innerHTML = '<span class="spinner"></span> জেনারেট...';

        try {
            const formData = new FormData();
            formData.append('text', text);
            formData.append('voice', voice);
            formData.append('rate', rate);
            formData.append('pitch', pitch);

            const response = await fetch('/synthesize_edge', { method: 'POST', body: formData });
            if (!response.ok) throw new Error(await response.text());

            const blob = await response.blob();
            if (currentAudioUrl1) URL.revokeObjectURL(currentAudioUrl1);
            currentAudioUrl1 = URL.createObjectURL(blob);

            audioPlayer1.src = currentAudioUrl1;
            audioWrapper1.classList.add('show');
            await audioPlayer1.play();

            setStatus1('✅ সফল! ডাউনলোড করুন।', 'success');
            if (!document.getElementById('dlBtn1')) {
                const dlBtn = document.createElement('button');
                dlBtn.id = 'dlBtn1';
                dlBtn.className = 'btn btn-download';
                dlBtn.innerHTML = '⬇️ MP3 ডাউনলোড';
                dlBtn.style.marginTop = '10px';
                dlBtn.onclick = () => {
                    const a = document.createElement('a');
                    a.href = currentAudioUrl1;
                    a.download = `tts_${Date.now()}.mp3`;
                    a.click();
                };
                audioWrapper1.appendChild(dlBtn);
            }
        } catch (error) {
            setStatus1('❌ ' + error.message, 'error');
        } finally {
            speakBtn1.disabled = false;
            speakBtn1.innerHTML = '🔊 শুনুন ও ডাউনলোড করুন';
        }
    });

    // ============================================================
    // gTTS (ট্যাব ২)
    // ============================================================
    const textInput2 = document.getElementById('textInput2');
    const charCounter2 = document.getElementById('charCounter2');
    const MAX_CHARS2 = 5000;
    textInput2.addEventListener('input', function() {
        const len = this.value.length;
        charCounter2.textContent = len + ' / ' + MAX_CHARS2;
        charCounter2.className = 'char-counter';
        if (len > MAX_CHARS2) charCounter2.classList.add('danger');
    });

    document.getElementById('fileUpload2').addEventListener('change', function(e) {
        const file = this.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = function(ev) {
            textInput2.value = ev.target.result;
            textInput2.dispatchEvent(new Event('input'));
        };
        reader.readAsText(file, 'UTF-8');
        this.value = '';
    });

    const speakBtn2 = document.getElementById('speakBtn2');
    const statusText2 = document.getElementById('statusText2');
    const statusIcon2 = document.querySelector('#statusBox2 .status-icon');
    const audioPlayer2 = document.getElementById('audioPlayer2');
    const audioWrapper2 = document.getElementById('audioWrapper2');
    let currentAudioUrl2 = null;

    function setStatus2(msg, type = 'info') {
        statusText2.textContent = msg;
        statusText2.className = 'status-text';
        if (type === 'success') { statusText2.classList.add('success'); statusIcon2.textContent = '✅'; }
        else if (type === 'error') { statusText2.classList.add('error'); statusIcon2.textContent = '❌'; }
        else if (type === 'loading') { statusText2.classList.add('loading'); statusIcon2.textContent = '⏳'; }
        else { statusIcon2.textContent = 'ℹ️'; }
    }

    speakBtn2.addEventListener('click', async function() {
        const text = textInput2.value.trim();

        if (!text) { setStatus2('টেক্সট লিখুন।', 'error'); return; }
        if (text.length > MAX_CHARS2) { setStatus2('সর্বোচ্চ ' + MAX_CHARS2 + ' অক্ষর।', 'error'); return; }

        setStatus2('⏳ Google ভয়েস জেনারেট...', 'loading');
        speakBtn2.disabled = true;
        speakBtn2.innerHTML = '<span class="spinner"></span> জেনারেট...';

        try {
            const formData = new FormData();
            formData.append('text', text);

            const response = await fetch('/synthesize_gtts', { method: 'POST', body: formData });
            if (!response.ok) throw new Error(await response.text());

            const blob = await response.blob();
            if (currentAudioUrl2) URL.revokeObjectURL(currentAudioUrl2);
            currentAudioUrl2 = URL.createObjectURL(blob);

            audioPlayer2.src = currentAudioUrl2;
            audioWrapper2.classList.add('show');
            await audioPlayer2.play();

            setStatus2('✅ Google ভয়েস তৈরি!', 'success');
            if (!document.getElementById('dlBtn2')) {
                const dlBtn = document.createElement('button');
                dlBtn.id = 'dlBtn2';
                dlBtn.className = 'btn btn-download';
                dlBtn.innerHTML = '⬇️ MP3 ডাউনলোড';
                dlBtn.style.marginTop = '10px';
                dlBtn.onclick = () => {
                    const a = document.createElement('a');
                    a.href = currentAudioUrl2;
                    a.download = `gtts_${Date.now()}.mp3`;
                    a.click();
                };
                audioWrapper2.appendChild(dlBtn);
            }
        } catch (error) {
            setStatus2('❌ ' + error.message, 'error');
        } finally {
            speakBtn2.disabled = false;
            speakBtn2.innerHTML = '🔊 Google ভয়েস তৈরি করুন';
        }
    });
</script>
</body>
</html>
"""


# ============================================================
# রাউট ১: হোম
# ============================================================
@app.route('/')
def home():
    return render_template_string(HTML)


# ============================================================
# রাউট ২: Edge TTS (ফ্রি)
# ============================================================
@app.route('/synthesize_edge', methods=['POST'])
def synthesize_edge():
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


# ============================================================
# রাউট ৩: gTTS (Google Translate TTS — কার্ড/সাইনআপ ছাড়া)
# ============================================================
@app.route('/synthesize_gtts', methods=['POST'])
def synthesize_gtts():
    text = request.form.get('text', '').strip()

    if not text:
        return 'টেক্সট খালি', 400
    if len(text) > 5000:
        return 'সর্বোচ্চ ৫০০০ অক্ষর', 400

    try:
        tts = gTTS(text=text, lang='bn', slow=False)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)

        return send_file(
            audio_bytes,
            mimetype='audio/mpeg',
            as_attachment=False
        )

    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
