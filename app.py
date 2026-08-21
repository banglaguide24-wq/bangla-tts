from flask import Flask, request, send_file, render_template_string
import edge_tts
import asyncio
import io
import uuid
from datetime import datetime

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>প্রো বাংলা TTS</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
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
            padding: 40px 35px;
            max-width: 540px;
            width: 100%;
            border: 1px solid rgba(255, 255, 255, 0.06);
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.7);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            border-color: rgba(59, 130, 246, 0.2);
        }
        
        .header {
            text-align: center;
            margin-bottom: 28px;
        }
        
        .logo {
            font-size: 42px;
            display: block;
            margin-bottom: 6px;
        }
        
        h1 {
            color: #e2e8f0;
            font-weight: 600;
            font-size: 26px;
            letter-spacing: -0.5px;
        }
        
        .subtitle {
            color: #94a3b8;
            font-size: 13px;
            margin-top: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            flex-wrap: wrap;
        }
        
        .badge {
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            padding: 3px 14px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            border: 1px solid rgba(16, 185, 129, 0.15);
        }
        
        .badge-warning {
            background: rgba(251, 191, 36, 0.12);
            color: #fbbf24;
            border-color: rgba(251, 191, 36, 0.12);
        }
        
        .form-group {
            margin-bottom: 16px;
        }
        
        .form-group label {
            display: block;
            color: #94a3b8;
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 6px;
            letter-spacing: 0.3px;
        }
        
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 14px 16px;
            border-radius: 16px;
            background: rgba(15, 23, 42, 0.8);
            color: #e2e8f0;
            border: 1px solid rgba(255, 255, 255, 0.06);
            font-size: 15px;
            outline: none;
            transition: all 0.25s ease;
            font-family: inherit;
        }
        
        .form-group select:focus,
        .form-group textarea:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.08);
            background: rgba(15, 23, 42, 0.95);
        }
        
        .form-group textarea {
            min-height: 100px;
            resize: vertical;
            line-height: 1.6;
        }
        
        .form-group select {
            cursor: pointer;
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%2394a3b8' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 16px center;
        }
        
        .btn {
            width: 100%;
            padding: 16px;
            border: none;
            border-radius: 50px;
            font-size: 17px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #3b82f6, #7c3aed);
            color: white;
            box-shadow: 0 8px 24px rgba(59, 130, 246, 0.25);
        }
        
        .btn-primary:hover:not(:disabled) {
            transform: scale(1.01);
            box-shadow: 0 12px 32px rgba(59, 130, 246, 0.35);
        }
        
        .btn-primary:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .btn-download {
            background: linear-gradient(135deg, #059669, #10b981);
            color: white;
            box-shadow: 0 8px 24px rgba(16, 185, 129, 0.2);
            margin-top: 10px;
        }
        
        .btn-download:hover:not(:disabled) {
            transform: scale(1.01);
            box-shadow: 0 12px 32px rgba(16, 185, 129, 0.3);
        }
        
        .btn-download:disabled {
            opacity: 0.4;
            cursor: not-allowed;
            transform: none;
        }
        
        .status-container {
            margin-top: 18px;
            padding: 12px 16px;
            border-radius: 14px;
            background: rgba(15, 23, 42, 0.6);
            min-height: 50px;
            display: flex;
            align-items: center;
            gap: 12px;
            border: 1px solid rgba(255, 255, 255, 0.04);
        }
        
        .status-icon {
            font-size: 20px;
            flex-shrink: 0;
        }
        
        .status-text {
            color: #94a3b8;
            font-size: 14px;
            flex: 1;
            word-break: break-word;
        }
        
        .status-text.success {
            color: #34d399;
        }
        
        .status-text.error {
            color: #f87171;
        }
        
        .status-text.loading {
            color: #fbbf24;
        }
        
        .audio-wrapper {
            margin-top: 16px;
            border-radius: 16px;
            overflow: hidden;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.04);
            display: none;
        }
        
        .audio-wrapper.show {
            display: block;
        }
        
        .audio-wrapper audio {
            width: 100%;
            display: block;
            padding: 12px 16px;
            background: transparent;
            outline: none;
        }
        
        .footer {
            margin-top: 20px;
            text-align: center;
            color: #475569;
            font-size: 11px;
            border-top: 1px solid rgba(255, 255, 255, 0.04);
            padding-top: 16px;
            line-height: 1.8;
        }
        
        .footer a {
            color: #3b82f6;
            text-decoration: none;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
        
        .spinner {
            display: inline-block;
            width: 18px;
            height: 18px;
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-top-color: #fff;
            border-radius: 50%;
            animation: spin 0.7s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .voice-indicator {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            color: #64748b;
            margin-top: 4px;
        }
        
        .voice-indicator .dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #34d399;
            display: inline-block;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        
        @media (max-width: 480px) {
            .card {
                padding: 25px 18px;
            }
            h1 {
                font-size: 22px;
            }
            .btn {
                font-size: 15px;
                padding: 14px;
            }
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <span class="logo">🎙️</span>
            <h1>প্রো বাংলা TTS</h1>
            <div class="subtitle">
                <span>সার্ভার-সাইড</span>
                <span class="badge">✅ MP3 ডাউনলোড</span>
                <span class="badge badge-warning">📱 মোবাইল+ডেস্কটপ</span>
            </div>
        </div>

        <div class="form-group">
            <label for="voiceSelect">🗣️ কণ্ঠ নির্বাচন করুন</label>
            <select id="voiceSelect">
                <option value="bn-BD-NabanitaNeural">নবনীতা (নারী, বাংলাদেশ) ⭐</option>
                <option value="bn-BD-PradeepNeural">প্রদীপ (পুরুষ, বাংলাদেশ)</option>
                <option value="bn-IN-TanishaaNeural">তনিষা (নারী, ভারত)</option>
                <option value="bn-IN-SwaraNeural">স্বরা (নারী, ভারত)</option>
            </select>
            <div class="voice-indicator">
                <span class="dot"></span>
                <span>নিউরাল ভয়েস · Azure প্রযুক্তি</span>
            </div>
        </div>

        <div class="form-group">
            <label for="textInput">📝 বাংলা টেক্সট লিখুন</label>
            <textarea id="textInput" placeholder="এখানে বাংলা টেক্সট লিখুন...">আমি পেশাদার কণ্ঠে বাংলায় কথা বলতে পারি। এটি অত্যন্ত স্বাভাবিক শোনাচ্ছে এবং মোবাইল ও ডেস্কটপ উভয় জায়গায় ডাউনলোড করা যায়।</textarea>
        </div>

        <button class="btn btn-primary" id="speakBtn">
            🔊 শুনুন ও ডাউনলোড করুন
        </button>

        <div class="status-container" id="statusContainer">
            <span class="status-icon">✅</span>
            <span class="status-text" id="statusText">প্রস্তুত। টেক্সট লিখে বাটনে ক্লিক করুন।</span>
        </div>

        <div class="audio-wrapper" id="audioWrapper">
            <audio id="audioPlayer" controls preload="metadata"></audio>
        </div>

        <div class="footer">
            ⚡ সম্পূর্ণ ফ্রি · Microsoft Edge Neural TTS · 
            <a href="#" onclick="event.preventDefault(); location.reload();">🔄 রিফ্রেশ</a>
        </div>
    </div>

    <script>
        const textInput = document.getElementById('textInput');
        const voiceSelect = document.getElementById('voiceSelect');
        const speakBtn = document.getElementById('speakBtn');
        const statusText = document.getElementById('statusText');
        const statusIcon = document.querySelector('.status-icon');
        const audioPlayer = document.getElementById('audioPlayer');
        const audioWrapper = document.getElementById('audioWrapper');

        let currentAudioUrl = null;

        function setStatus(message, type = 'info') {
            statusText.textContent = message;
            statusText.className = 'status-text';
            
            if (type === 'success') {
                statusText.classList.add('success');
                statusIcon.textContent = '✅';
            } else if (type === 'error') {
                statusText.classList.add('error');
                statusIcon.textContent = '❌';
            } else if (type === 'loading') {
                statusText.classList.add('loading');
                statusIcon.textContent = '⏳';
            } else {
                statusIcon.textContent = 'ℹ️';
            }
        }

        function showAudio(url) {
            if (currentAudioUrl) {
                URL.revokeObjectURL(currentAudioUrl);
            }
            currentAudioUrl = url;
            audioPlayer.src = url;
            audioWrapper.classList.add('show');
            audioPlayer.load();
            
            // অটো প্লে করার চেষ্টা (ব্যবহারকারীর ইন্টারঅ্যাকশন প্রয়োজন)
            audioPlayer.play().catch(() => {
                // অটো প্লে না হলে ইউজার নিজে প্লে করবে
                setStatus('🔊 অডিও প্রস্তুত। প্লে বাটনে ক্লিক করুন।', 'success');
            });
        }

        async function generateSpeech() {
            const text = textInput.value.trim();
            const voice = voiceSelect.value;

            if (!text) {
                setStatus('দয়া করে কিছু টেক্সট লিখুন।', 'error');
                return;
            }

            setStatus('⏳ ভয়েস জেনারেট হচ্ছে... এটি ১০-১৫ সেকেন্ড সময় নিতে পারে।', 'loading');
            speakBtn.disabled = true;
            speakBtn.innerHTML = '<span class="spinner"></span> জেনারেট হচ্ছে...';

            try {
                const formData = new FormData();
                formData.append('text', text);
                formData.append('voice', voice);

                const response = await fetch('/synthesize', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(errorText || 'সার্ভার সমস্যা');
                }

                const blob = await response.blob();
                const url = URL.createObjectURL(blob);

                showAudio(url);
                setStatus('✅ সফল! অডিও তৈরি হয়েছে। এখন ডাউনলোড করতে পারেন।', 'success');

            } catch (error) {
                console.error('Error:', error);
                setStatus('❌ সমস্যা: ' + error.message, 'error');
            } finally {
                speakBtn.disabled = false;
                speakBtn.innerHTML = '🔊 শুনুন ও ডাউনলোড করুন';
            }
        }

        // অডিও ডাউনলোড ফিচার
        audioPlayer.addEventListener('canplaythrough', function() {
            // অডিও লোড হলে ডাউনলোড অপশন যোগ করা
            if (!document.getElementById('downloadBtn')) {
                const downloadBtn = document.createElement('button');
                downloadBtn.id = 'downloadBtn';
                downloadBtn.className = 'btn btn-download';
                downloadBtn.innerHTML = '⬇️ MP3 ডাউনলোড করুন';
                downloadBtn.style.marginTop = '10px';
                downloadBtn.addEventListener('click', function() {
                    if (currentAudioUrl) {
                        const a = document.createElement('a');
                        a.href = currentAudioUrl;
                        const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '');
                        a.download = `tts_${timestamp}.mp3`;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        setStatus('✅ MP3 ডাউনলোড শুরু হয়েছে!', 'success');
                    }
                });
                audioWrapper.appendChild(downloadBtn);
            }
        });

        speakBtn.addEventListener('click', generateSpeech);

        // Ctrl+Enter বা Cmd+Enter চাপলেও কাজ করবে
        textInput.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                generateSpeech();
            }
        });

        // পেজ লোড হলে ফোকাস
        textInput.focus();
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
    
    if not text:
        return 'টেক্সট খালি', 400

    try:
        async def generate_audio():
            communicate = edge_tts.Communicate(text, voice)
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
            as_attachment=False,
            download_name='tts_output.mp3'
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
