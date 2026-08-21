from flask import Flask, request, send_file, render_template_string
import edge_tts
import asyncio
import io

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>প্রো বাংলা TTS</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background:#0b1120; display:flex; justify-content:center; align-items:center; min-height:100vh; padding:20px; font-family:'Segoe UI',sans-serif; }
        .card { background:#1a2332; padding:35px; border-radius:30px; max-width:500px; width:100%; border:1px solid #2a3a50; }
        h1 { color:#b9d1f0; text-align:center; font-weight:400; }
        .sub { color:#64748b; text-align:center; font-size:13px; margin:5px 0 15px; }
        .badge { background:#065f46; color:#34d399; padding:4px 12px; border-radius:30px; font-size:12px; display:block; text-align:center; margin-bottom:18px; }
        select, textarea { width:100%; padding:14px; border-radius:14px; background:#0f172a; color:#e2e8f0; border:1px solid #2d3b52; font-size:15px; outline:none; margin-bottom:14px; font-family:inherit; }
        textarea { min-height:110px; resize:vertical; }
        button { width:100%; padding:16px; border:none; border-radius:50px; background:linear-gradient(135deg,#3b82f6,#7c3aed); color:white; font-size:18px; font-weight:600; cursor:pointer; margin-top:10px; }
        button:hover { transform:scale(1.02); opacity:0.9; }
        .status { color:#94a3b8; text-align:center; margin-top:15px; font-size:14px; min-height:24px; }
        audio { width:100%; margin-top:15px; border-radius:30px; }
        .footnote { color:#475569; text-align:center; font-size:11px; margin-top:18px; }
    </style>
</head>
<body>
<div class="card">
    <h1>🎙️ প্রো বাংলা TTS</h1>
    <div class="sub">সার্ভার-সাইড (MP3 ডাউনলোড)</div>
    <div class="badge">⚡ মোবাইল + ডেস্কটপে কাজ করে</div>
    <select id="voice">
        <option value="bn-BD-NabanitaNeural">নবনীতা (নারী, বাংলাদেশ)</option>
        <option value="bn-BD-PradeepNeural">প্রদীপ (পুরুষ, বাংলাদেশ)</option>
        <option value="bn-IN-TanishaaNeural">তনিষা (নারী, ভারত)</option>
    </select>
    <textarea id="text">আমি পেশাদার কণ্ঠে বাংলায় কথা বলতে পারি। এটি মোবাইল ও ডেস্কটপ উভয় জায়গায় ডাউনলোড করা যায়।</textarea>
    <button onclick="speak()">▶️ শুনুন ও ডাউনলোড করুন</button>
    <div class="status" id="status">✅ প্রস্তুত</div>
    <audio id="audio" controls></audio>
    <div class="footnote">🚀 চালানোর জন্য শুধু একটি আধুনিক ব্রাউজার লাগবে।</div>
</div>
<script>
    async function speak() {
        const text = document.getElementById('text').value;
        const voice = document.getElementById('voice').value;
        const status = document.getElementById('status');
        const audio = document.getElementById('audio');
        if (!text.trim()) { status.innerText = '❌ টেক্সট লিখুন'; return; }
        status.innerText = '⏳ জেনারেট হচ্ছে...';
        try {
            const form = new FormData();
            form.append('text', text);
            form.append('voice', voice);
            const res = await fetch('/synthesize', { method:'POST', body:form });
            if (!res.ok) throw new Error(await res.text());
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            audio.src = url;
            await audio.play();
            const a = document.createElement('a');
            a.href = url;
            a.download = `tts_${Date.now()}.mp3`;
            a.click();
            status.innerText = '✅ সম্পন্ন! MP3 ডাউনলোড শুরু হয়েছে।';
        } catch(e) {
            status.innerText = '❌ ' + e.message;
        }
    }
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
        return 'Text empty', 400

    async def gen():
        comm = edge_tts.Communicate(text, voice)
        data = b""
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                data += chunk["data"]
        return data

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    audio_bytes = loop.run_until_complete(gen())
    return send_file(io.BytesIO(audio_bytes), mimetype='audio/mpeg')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
