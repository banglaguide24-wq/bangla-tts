from flask import Flask, request, send_file, render_template_string
import edge_tts
import asyncio
import io
import requests
import os
import time

app = Flask(__name__)

# পরিবেশ চলক থেকে ElevenLabs API Key পড়া (ঐচ্ছিক, UI-তেও দেওয়া যায়)
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY', '')

HTML = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>প্রো বাংলা TTS স্টুডিও</title>
    <style>
        /* ===== গ্লোবাল রিসেট ও ফন্ট ===== */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #0b1120;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        /* ===== প্রধান কার্ড ===== */
        .card {
            background: #1a2332;
            border-radius: 32px;
            padding: 35px 30px;
            max-width: 580px;
            width: 100%;
            border: 1px solid rgba(255, 255, 255, 0.06);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8);
            transition: all 0.3s ease;
        }
        .card:hover { border-color: rgba(59, 130, 246, 0.15); }

        /* ===== হেডার ===== */
        .header { text-align: center; margin-bottom: 28px; }
        .logo { font-size: 44px; display: block; margin-bottom: 4px; }
        h1 {
            color: #f1f5f9;
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
            gap: 10px;
            flex-wrap: wrap;
        }
        .badge-free {
            background: #065f46;
            color: #34d399;
            padding: 2px 14px;
            border-radius: 30px;
            font-size: 11px;
            font-weight: 600;
            border: 1px solid rgba(16, 185, 129, 0.15);
        }
        .badge-paid {
            background: #451a1a;
            color: #fca5a5;
            padding: 2px 14px;
            border-radius: 30px;
            font-size: 11px;
            font-weight: 600;
            border: 1px solid rgba(248, 113, 113, 0.15);
        }

        /* ===== ট্যাব ===== */
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
        .tab-btn.active {
            background: #3b82f6;
            color: white;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }
        .tab-btn:hover:not(.active) { background: rgba(255, 255, 255, 0.05); }

        /* ===== কন্টেন্ট ===== */
        .tab-content { display: none; animation: fadeIn 0.3s ease; }
        .tab-content.active { display: block; }
        @keyframes fadeIn { from { opacity: 0.5; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

        /* ===== ফর্ম এলিমেন্ট ===== */
        .form-group { margin-bottom: 18px; }
        .form-group label {
            display: block;
            color: #94a3b8;
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 6px;
            letter-spacing: 0.3px;
        }
        .form-group select,
        .form-group textarea,
        .form-group input[type="password"] {
            width: 100%;
            padding: 14px 16px;
            border-radius: 16px;
            background: #0f172a;
            color: #e2e8f0;
            border: 1px solid #2d3b52;
            font-size: 15px;
            outline: none;
            transition: all 0.2s ease;
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
            transition: 0.2s;
        }
        .form-group input[type="file"]:hover { border-color: #3b82f6; }
        .form-group select:focus,
        .form-group textarea:focus,
        .form-group input:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.08);
            background: #0f172a;
        }
        .form-group textarea {
            min-height: 110px;
            resize: vertical;
            line-height: 1.6;
        }

        /* ===== রেঞ্জ স্লাইডার ===== */
        .row-flex {
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
            margin-bottom: 6px;
        }
        .row-flex .col {
            flex: 1;
            min-width: 120px;
        }
        .range-input {
            width: 100%;
            accent-color: #3b82f6;
            background: #0f172a;
            height: 4px;
            cursor: pointer;
        }
        .range-value {
            color: #e2e8f0;
            font-size: 14px;
            font-weight: 600;
            text-align: center;
            margin-top: 2px;
        }

        /* ===== ক্যারেক্টার কাউন্টার ===== */
        .char-counter {
            text-align: right;
            font-size: 13px;
            color: #64748b;
            padding-right: 4px;
            margin-top: 4px;
        }
        .char-counter.warning { color: #fbbf24; }
        .char-counter.danger { color: #f87171; }

        /* ===== বাটন ===== */
        .btn {
            width: 100%;
            padding: 16px;
            border: none;
            border-radius: 50px;
            font-size: 17px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.25s ease;
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
        .btn-primary:hover:not(:disabled) {
            transform: scale(1.01);
            box-shadow: 0 12px 32px rgba(59, 130, 246, 0.35);
        }
        .btn-warning {
            background: linear-gradient(135deg, #d97706, #f59e0b);
            color: white;
            box-shadow: 0 8px 24px rgba(245, 158, 11, 0.2);
        }
        .btn-warning:hover:not(:disabled) {
            transform: scale(1.01);
            box-shadow: 0 12px 32px rgba(245, 158, 11, 0.35);
        }
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none !important;
        }
        .btn-download {
            background: linear-gradient(135deg, #0284c7, #2563eb);
            color: white;
            margin-top: 10px;
        }
        .btn-download:hover { opacity: 0.9; transform: scale(1.01); }

        /* ===== স্ট্যাটাস বক্স ===== */
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
        .status-icon { font-size: 20px; flex-shrink: 0; }
        .status-text {
            color: #94a3b8;
            font-size: 14px;
            flex: 1;
            word-break: break-word;
        }
        .status-text.success { color: #34d399; }
        .status-text.error { color: #f87171; }
        .status-text.loading { color: #fbbf24; }

        /* ===== অডিও প্লেয়ার ===== */
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

        /* ===== ফুটার ===== */
        .footer {
            margin-top: 24px;
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
        .footer a:hover { text-decoration: underline; }

        .spinner {
            display: inline-block;
            width: 18px;
            height: 18px;
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-top-color: #fff;
            border-radius: 50%;
            animation: spin 0.7s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        .info-box {
            background: #1e293b;
            padding: 12px 16px;
            border-radius: 12px;
            border-left: 4px solid #f59e0b;
            margin-bottom: 16px;
        }
        .info-box p {
            color: #94a3b8;
            font-size: 13px;
            margin: 0;
            line-height: 1.6;
        }
        .info-box strong { color: #e2e8f0; }

        /* ===== মোবাইল রেস্পন্সিভ ===== */
        @media (max-width: 480px) {
            .card { padding: 25px 18px; }
            h1 { font-size: 22px; }
            .btn { font-size: 15px; padding: 14px; }
            .tab-btn { font-size: 12px; padding: 10px 6px; }
        }
    </style>
</head>
<body>

<div class="card">
    <!-- হেডার -->
    <div class="header">
        <span class="logo">🎙️</span>
        <h1>প্রো বাংলা TTS</h1>
        <div class="subtitle">
            <span>Microsoft Edge Neural</span>
            <span class="badge-free">✅ MP3 ডাউনলোড</span>
            <span class="badge-free">📱 মোবাইল+ডেস্কটপ</span>
        </div>
    </div>

    <!-- ট্যাব -->
    <div class="tabs">
        <button class="tab-btn active" data-tab="tab1">🎧 স্ট্যান্ডার্ড</button>
        <button class="tab-btn" data-tab="tab2">🧬 ক্লোনিং ল্যাব</button>
    </div>

    <!-- ============================================ -->
    <!-- ট্যাব ১: স্ট্যান্ডার্ড TTS (ফ্রি) -->
    <!-- ============================================ -->
    <div class="tab-content active" id="tab1">
        <div class="form-group">
            <label>🗣️ কণ্ঠ নির্বাচন করুন</label>
            <select id="voiceSelect">
                <option value="bn-BD-NabanitaNeural">নবনীতা (নারী, বাংলাদেশ) ⭐</option>
                <option value="bn-BD-PradeepNeural">প্রদীপ (পুরুষ, বাংলাদেশ)</option>
                <option value="bn-IN-TanishaaNeural">তনিষা (নারী, ভারত)</option>
                <option value="bn-IN-SwaraNeural">স্বরা (নারী, ভারত)</option>
            </select>
        </div>

        <!-- স্পিড ও পিচ -->
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

        <!-- টেক্সট ইনপুট -->
        <div class="form-group">
            <label>📝 বাংলা টেক্সট লিখুন</label>
            <textarea id="textInput1" placeholder="এখানে বাংলা টেক্সট লিখুন...">আমি পেশাদার কণ্ঠে বাংলায় কথা বলতে পারি। এটি অত্যন্ত স্বাভাবিক শোনাচ্ছে এবং সম্পূর্ণ বিনামূল্যে।</textarea>
            <div class="char-counter" id="charCounter">0 / 3000</div>
        </div>

        <!-- ফাইল আপলোড -->
        <div class="form-group">
            <label>📂 টেক্সট ফাইল আপলোড করুন (.txt)</label>
            <input type="file" id="fileUpload" accept=".txt">
        </div>

        <!-- অ্যাকশন বাটন -->
        <button class="btn btn-primary" id="speakBtn1">🔊 শুনুন ও ডাউনলোড করুন</button>

        <!-- স্ট্যাটাস -->
        <div class="status-box" id="statusBox1">
            <span class="status-icon">✅</span>
            <span class="status-text" id="statusText1">প্রস্তুত। টেক্সট লিখে শুনুন ক্লিক করুন।</span>
        </div>

        <!-- অডিও প্লেয়ার -->
        <div class="audio-wrapper" id="audioWrapper1">
            <audio id="audioPlayer1" controls></audio>
        </div>
    </div>

    <!-- ============================================ -->
    <!-- ট্যাব ২: ক্লোনিং ল্যাব (ElevenLabs পেইড) -->
    <!-- ============================================ -->
    <div class="tab-content" id="tab2">
        <div class="info-box">
            <p><strong>🧪 ভয়েস ক্লোনিং ল্যাব</strong><br>
            ElevenLabs-এর API ব্যবহার করে (পেইড প্ল্যান $৫/মাস প্রয়োজন)। 
            <br>💡 <strong>ফ্রি বিকল্প:</strong> <a href="https://github.com/debpalash/OmniVoice-Studio" target="_blank" style="color:#3b82f6;">OmniVoice Studio</a> আপনার কম্পিউটারে ব্যবহার করুন।
            </p>
        </div>

        <div class="form-group">
            <label>🔑 ElevenLabs API Key (পেইড প্ল্যান)</label>
            <input type="password" id="apiKey" placeholder="আপনার ElevenLabs API Key দিন">
        </div>

        <div class="form-group">
            <label>🎤 আপনার ভয়েস আপলোড করুন (৩০-৬০ সেকেন্ড)</label>
            <input type="file" id="voiceFile" accept="audio/*">
            <div style="margin-top:6px; font-size:12px; color:#64748b;">সাপোর্টেড: WAV, MP3, M4A</div>
        </div>

        <div class="form-group">
            <label>📝 টেক্সট লিখুন (আপনার কণ্ঠে শুনতে চান)</label>
            <textarea id="textInput2">এই টেক্সটটি আমার নিজের কণ্ঠে শুনতে চাই। এটি অত্যন্ত বাস্তবসম্মত শোনাচ্ছে।</textarea>
        </div>

        <button class="btn btn-warning" id="speakBtn2">🧬 ক্লোন ভয়েস তৈরি করুন</button>

        <div class="status-box" id="statusBox2">
            <span class="status-icon">ℹ️</span>
            <span class="status-text" id="statusText2">ভয়েস আপলোড করে বাটনে ক্লিক করুন।</span>
        </div>

        <div class="audio-wrapper" id="audioWrapper2">
            <audio id="audioPlayer2" controls></audio>
        </div>
    </div>

    <!-- ফুটার -->
    <div class="footer">
        ⚡ স্ট্যান্ডার্ড TTS সম্পূর্ণ ফ্রি · ক্লোনিং ElevenLabs API-ভিত্তিক (পেইড)
    </div>
</div>

<script>
    // ============================================================
    // ১. ট্যাব টগল
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
    // ২. স্পিড ও পিচ স্লাইডার সিঙ্ক
    // ============================================================
    document.getElementById('rateControl').addEventListener('input', function() {
        document.getElementById('rateValue').textContent = this.value + 'x';
    });
    document.getElementById('pitchControl').addEventListener('input', function() {
        document.getElementById('pitchValue').textContent = this.value + '%';
    });

    // ============================================================
    // ৩. ক্যারেক্টার কাউন্টার (লিমিট ৩০০০)
    // ============================================================
    const textInput1 = document.getElementById('textInput1');
    const charCounter = document.getElementById('charCounter');
    const MAX_CHARS = 3000;

    function updateCharCounter() {
        const len = textInput1.value.length;
        charCounter.textContent = len + ' / ' + MAX_CHARS;
        charCounter.className = 'char-counter';
        if (len > MAX_CHARS) charCounter.classList.add('danger');
        else if (len > MAX_CHARS * 0.8) charCounter.classList.add('warning');
    }
    textInput1.addEventListener('input', updateCharCounter);
    updateCharCounter();

    // ============================================================
    // ৪. লোকালস্টোরেজে অটো-সেভ (ড্রাফট)
    // ============================================================
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

    // ============================================================
    // ৫. টেক্সট ফাইল আপলোড
    // ============================================================
    document.getElementById('fileUpload').addEventListener('change', function(e) {
        const file = this.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = function(ev) {
            textInput1.value = ev.target.result;
            updateCharCounter();
        };
        reader.readAsText(file, 'UTF-8');
        // ফাইল সিলেক্ট রিসেট (যাতে একই ফাইল আবার আপলোড করলে কাজ করে)
        this.value = '';
    });

    // ============================================================
    // ৬. স্ট্যান্ডার্ড TTS (ট্যাব ১)
    // ============================================================
    const speakBtn1 = document.getElementById('speakBtn1');
    const status1 = document.getElementById('statusText1');
    const statusIcon1 = document.querySelector('#statusBox1 .status-icon');
    const audio1 = document.getElementById('audioPlayer1');
    const wrapper1 = document.getElementById('audioWrapper1');
    let audioUrl1 = null;

    function setStatus1(msg, type = 'info') {
        status1.textContent = msg;
        status1.className = 'status-text';
        if (type === 'success') { status1.classList.add('success'); statusIcon1.textContent = '✅'; }
        else if (type === 'error') { status1.classList.add('error'); statusIcon1.textContent = '❌'; }
        else if (type === 'loading') { status1.classList.add('loading'); statusIcon1.textContent = '⏳'; }
        else { statusIcon1.textContent = 'ℹ️'; }
    }

    speakBtn1.addEventListener('click', async function() {
        const text = textInput1.value.trim();
        const voice = document.getElementById('voiceSelect').value;
        const rate = parseFloat(document.getElementById('rateControl').value);
        const pitch = parseInt(document.getElementById('pitchControl').value);

        // ভ্যালিডেশন
        if (!text) { setStatus1('দয়া করে কিছু টেক্সট লিখুন।', 'error'); return; }
        if (text.length > MAX_CHARS) { setStatus1('সর্বোচ্চ ' + MAX_CHARS + ' অক্ষর।', 'error'); return; }

        setStatus1('⏳ ভয়েস জেনারেট হচ্ছে (Edge Neural)...', 'loading');
        speakBtn1.disabled = true;
        speakBtn1.innerHTML = '<span class="spinner"></span> জেনারেট হচ্ছে...';

        try {
            const formData = new FormData();
            formData.append('text', text);
            formData.append('voice', voice);
            formData.append('rate', rate);
            formData.append('pitch', pitch);

            const response = await fetch('/synthesize', { method: 'POST', body: formData });
            if (!response.ok) {
                const errText = await response.text();
                throw new Error(errText || 'সার্ভার সমস্যা');
            }

            const blob = await response.blob();
            if (audioUrl1) URL.revokeObjectURL(audioUrl1);
            audioUrl1 = URL.createObjectURL(blob);

            audio1.src = audioUrl1;
            wrapper1.classList.add('show');
            await audio1.play();

            setStatus1('✅ সফল! অডিও বাজছে। এখন ডাউনলোড করতে পারেন।', 'success');

            // ডাউনলোড বাটন যোগ করা (যদি না থাকে)
            if (!document.getElementById('dlBtn1')) {
                const dlBtn = document.createElement('button');
                dlBtn.id = 'dlBtn1';
                dlBtn.className = 'btn btn-download';
                dlBtn.innerHTML = '⬇️ MP3 ডাউনলোড';
                dlBtn.style.marginTop = '10px';
                dlBtn.onclick = () => {
                    const a = document.createElement('a');
                    a.href = audioUrl1;
                    a.download = `tts_${Date.now()}.mp3`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                };
                wrapper1.appendChild(dlBtn);
            }

        } catch (error) {
            console.error(error);
            setStatus1('❌ সমস্যা: ' + error.message, 'error');
        } finally {
            speakBtn1.disabled = false;
            speakBtn1.innerHTML = '🔊 শুনুন ও ডাউনলোড করুন';
        }
    });

    // ============================================================
    // ৭. ভয়েস ক্লোনিং (ট্যাব ২ - ElevenLabs)
    // ============================================================
    const speakBtn2 = document.getElementById('speakBtn2');
    const status2 = document.getElementById('statusText2');
    const statusIcon2 = document.querySelector('#statusBox2 .status-icon');
    const audio2 = document.getElementById('audioPlayer2');
    const wrapper2 = document.getElementById('audioWrapper2');
    let audioUrl2 = null;

    function setStatus2(msg, type = 'info') {
        status2.textContent = msg;
        status2.className = 'status-text';
        if (type === 'success') { status2.classList.add('success'); statusIcon2.textContent = '✅'; }
        else if (type === 'error') { status2.classList.add('error'); statusIcon2.textContent = '❌'; }
        else if (type === 'loading') { status2.classList.add('loading'); statusIcon2.textContent = '⏳'; }
        else { statusIcon2.textContent = 'ℹ️'; }
    }

    speakBtn2.addEventListener('click', async function() {
        const apiKey = document.getElementById('apiKey').value.trim();
        const text = document.getElementById('textInput2').value.trim();
        const file = document.getElementById('voiceFile').files[0];

        if (!apiKey) { setStatus2('ElevenLabs API Key দিন (পেইড প্ল্যান প্রয়োজন)।', 'error'); return; }
        if (!text) { setStatus2('টেক্সট লিখুন।', 'error'); return; }
        if (!file) { setStatus2('একটি অডিও ফাইল আপলোড করুন।', 'error'); return; }

        setStatus2('⏳ ক্লোনিং শুরু হয়েছে (১-২ মিনিট সময় লাগতে পারে)...', 'loading');
        speakBtn2.disabled = true;
        speakBtn2.innerHTML = '<span class="spinner"></span> ক্লোনিং...';

        try {
            const formData = new FormData();
            formData.append('api_key', apiKey);
            formData.append('text', text);
            formData.append('audio_file', file);

            const response = await fetch('/clone', { method: 'POST', body: formData });
            if (!response.ok) {
                const errText = await response.text();
                throw new Error(errText || 'ক্লোনিং ব্যর্থ');
            }

            const blob = await response.blob();
            if (audioUrl2) URL.revokeObjectURL(audioUrl2);
            audioUrl2 = URL.createObjectURL(blob);

            audio2.src = audioUrl2;
            wrapper2.classList.add('show');
            await audio2.play();

            setStatus2('✅ ক্লোন ভয়েস তৈরি! এখন ডাউনলোড করতে পারেন।', 'success');

            if (!document.getElementById('dlBtn2')) {
                const dlBtn = document.createElement('button');
                dlBtn.id = 'dlBtn2';
                dlBtn.className = 'btn btn-download';
                dlBtn.innerHTML = '⬇️ MP3 ডাউনলোড (ক্লোন)';
                dlBtn.style.marginTop = '10px';
                dlBtn.onclick = () => {
                    const a = document.createElement('a');
                    a.href = audioUrl2;
                    a.download = `cloned_${Date.now()}.mp3`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                };
                wrapper2.appendChild(dlBtn);
            }

        } catch (error) {
            console.error(error);
            setStatus2('❌ সমস্যা: ' + error.message, 'error');
        } finally {
            speakBtn2.disabled = false;
            speakBtn2.innerHTML = '🧬 ক্লোন ভয়েস তৈরি করুন';
        }
    });

    // ============================================================
    // ৮. কিবোর্ড শর্টকাট: Ctrl+Enter দিয়ে সাবমিট (ট্যাব ১)
    // ============================================================
    textInput1.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            speakBtn1.click();
        }
    });
</script>
</body>
</html>
"""


# ============================================================
# রাউট ১: হোম পেজ
# ============================================================
@app.route('/')
def home():
    return render_template_string(HTML)


# ============================================================
# রাউট ২: স্ট্যান্ডার্ড TTS (Edge TTS - ফ্রি)
# ============================================================
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
        # পিচ স্ট্রিং ফরম্যাট করা (SSML অনুযায়ী)
        pitch_str = f"+{pitch}%" if pitch >= 0 else f"{pitch}%"

        # SSML তৈরি করা (গতি ও পিচ নিয়ন্ত্রণের জন্য)
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
            as_attachment=False,
            download_name='tts_output.mp3'
        )

    except Exception as e:
        return str(e), 500


# ============================================================
# রাউট ৩: ভয়েস ক্লোনিং (ElevenLabs - পেইড)
# ============================================================
@app.route('/clone', methods=['POST'])
def clone_voice():
    # UI থেকে Key নিন, না থাকলে Env Var ব্যবহার করুন
    api_key = request.form.get('api_key', '').strip() or ELEVENLABS_API_KEY
    text = request.form.get('text', '').strip()
    audio_file = request.files.get('audio_file')

    if not api_key:
        return 'ElevenLabs API Key প্রয়োজন (পেইড প্ল্যান)', 400
    if not text:
        return 'টেক্সট দিন', 400
    if not audio_file:
        return 'অডিও ফাইল দিন', 400

    try:
        # ১. অডিও ফাইল টেম্পরারি সেভ
        temp_path = f"/tmp/clone_{int(time.time())}.wav"
        audio_file.save(temp_path)

        # ২. ElevenLabs-এ ভয়েস যোগ করুন
        url_add = "https://api.elevenlabs.io/v1/voices/add"
        headers_add = {"xi-api-key": api_key}

        with open(temp_path, 'rb') as f:
            files = {'files': ('voice.wav', f, 'audio/wav')}
            data = {'name': f'Cloned_{int(time.time())}'}
            response_add = requests.post(url_add, headers=headers_add, data=data, files=files)

        if response_add.status_code != 200:
            os.remove(temp_path)
            return f"ক্লোনিং ব্যর্থ (ভয়েস যোগ): {response_add.text}", 400

        voice_id = response_add.json()['voice_id']
        os.remove(temp_path)

        # ৩. টেক্সট টু স্পিচ (ক্লোন করা ভয়েস দিয়ে)
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
            as_attachment=False,
            download_name='cloned_voice.mp3'
        )

    except Exception as e:
        return str(e), 500


# ============================================================
# অ্যাপ রান
# ============================================================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
