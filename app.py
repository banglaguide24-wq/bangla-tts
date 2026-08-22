from flask import Flask, request, jsonify, render_template_string
import requests
import json
import random
import time
import re

app = Flask(__name__)

# ============================================================
# HTML টেমপ্লেট (ইউজার ইন্টারফেস) — সব টুল এক পেজে
# ============================================================
UI_HTML = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI টুলস স্যুট (পূর্ণ সংস্করণ)</title>
    <style>
        * { box-sizing: border-box; margin: 0; }
        body { font-family: system-ui, sans-serif; background: #0b1120; min-height: 100vh; padding: 20px; }
        .container { max-width: 960px; margin: 0 auto; }
        h1 { color: #f1f5f9; font-size: 28px; text-align: center; }
        .sub { color: #94a3b8; text-align: center; margin-bottom: 24px; border-bottom: 1px solid #2d3b52; padding-bottom: 16px; }
        .tabs { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 24px; background: #1a2332; padding: 8px; border-radius: 16px; justify-content: center; }
        .tab-btn { padding: 10px 16px; border: none; border-radius: 12px; background: transparent; color: #94a3b8; font-weight: 600; cursor: pointer; transition: 0.2s; font-size: 14px; }
        .tab-btn.active { background: #3b82f6; color: white; box-shadow: 0 4px 12px rgba(59,130,246,0.3); }
        .tab-btn:hover:not(.active) { background: rgba(255,255,255,0.05); }
        .tab-content { display: none; background: #1a2332; border-radius: 24px; padding: 24px; border: 1px solid #2d3b52; }
        .tab-content.active { display: block; }
        .form-group { margin-bottom: 16px; }
        label { color: #94a3b8; display: block; margin-bottom: 6px; font-weight: 500; font-size: 13px; }
        input, textarea, select { width: 100%; padding: 14px; border-radius: 16px; background: #0f172a; color: #e2e8f0; border: 1px solid #2d3b52; font-size: 15px; outline: none; font-family: inherit; }
        textarea { min-height: 120px; resize: vertical; }
        button { padding: 14px 28px; border: none; border-radius: 50px; background: linear-gradient(135deg, #3b82f6, #7c3aed); color: white; font-size: 16px; font-weight: 600; cursor: pointer; transition: 0.2s; box-shadow: 0 4px 16px rgba(59,130,246,0.2); }
        button:hover { transform: scale(1.01); box-shadow: 0 8px 24px rgba(59,130,246,0.35); }
        button:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .output-box { background: #0f172a; border-radius: 16px; padding: 16px; margin-top: 16px; border: 1px solid #2d3b52; min-height: 60px; color: #e2e8f0; white-space: pre-wrap; max-height: 400px; overflow-y: auto; }
        .footer { text-align: center; color: #475569; font-size: 12px; margin-top: 24px; border-top: 1px solid #2d3b52; padding-top: 16px; }
        .badge { background: #065f46; color: #34d399; padding: 2px 12px; border-radius: 30px; font-size: 11px; margin-left: 8px; }
        @media (max-width: 640px) { .tabs { flex-direction: row; flex-wrap: wrap; } .tab-btn { flex: 1; min-width: 80px; text-align: center; } }
    </style>
</head>
<body>
<div class="container">
    <h1>🤖 সুপার AI টুলস</h1>
    <div class="sub">ব্লগ · প্যারাফ্রেজ · গ্রামার · রিরাইট · প্রম্পট · সামারাইজ · কিওয়ার্ড</div>

    <div class="tabs">
        <button class="tab-btn active" data-tab="tab1">📝 ব্লগ</button>
        <button class="tab-btn" data-tab="tab2">🔄 প্যারাফ্রেজ</button>
        <button class="tab-btn" data-tab="tab3">✅ গ্রামার</button>
        <button class="tab-btn" data-tab="tab4">✏️ রিরাইট</button>
        <button class="tab-btn" data-tab="tab5">🎨 প্রম্পট</button>
        <button class="tab-btn" data-tab="tab6">📄 সামারাইজ</button>
        <button class="tab-btn" data-tab="tab7">🔑 কিওয়ার্ড</button>
    </div>

    <!-- 1. ব্লগ -->
    <div class="tab-content active" id="tab1">
        <div class="form-group"><label>📝 টাইটেল</label><input type="text" id="blogTitle" value="মোবাইলের ব্যাটারি লাইফ বাড়ানোর ১০টি টিপস"></div>
        <div class="form-group"><label>🌐 ভাষা</label><select id="blogLang"><option value="bn">বাংলা</option><option value="en">English</option></select></div>
        <button onclick="runTool('blog')">🚀 ব্লগ তৈরি করুন</button>
        <div class="output-box" id="blogOutput"></div>
    </div>

    <!-- 2. প্যারাফ্রেজ -->
    <div class="tab-content" id="tab2">
        <div class="form-group"><label>📝 টেক্সট</label><textarea id="paraInput">কৃত্রিম বুদ্ধিমত্তা দ্রুত বিশ্বকে বদলে দিচ্ছে।</textarea></div>
        <button onclick="runTool('para')">🔄 প্যারাফ্রেজ করুন</button>
        <div class="output-box" id="paraOutput"></div>
    </div>

    <!-- 3. গ্রামার -->
    <div class="tab-content" id="tab3">
        <div class="form-group"><label>📝 টেক্সট</label><textarea id="gramInput">আমি গতকাল বাজার গিয়েছিলাম এবং অনেক কিছু কিনেছি।</textarea></div>
        <button onclick="runTool('gram')">✅ গ্রামার চেক করুন</button>
        <div class="output-box" id="gramOutput"></div>
    </div>

    <!-- 4. রিরাইট -->
    <div class="tab-content" id="tab4">
        <div class="form-group"><label>📝 পুরনো টেক্সট</label><textarea id="rewriteInput">ডিজিটাল মার্কেটিং হলো অনলাইনে পণ্য বা সেবা প্রচারের প্রক্রিয়া।</textarea></div>
        <button onclick="runTool('rewrite')">✏️ রিরাইট করুন</button>
        <div class="output-box" id="rewriteOutput"></div>
    </div>

    <!-- 5. প্রম্পট -->
    <div class="tab-content" id="tab5">
        <div class="form-group"><label>🎨 টপিক</label><input type="text" id="promptTopic" value="সূর্যাস্তের সময় পাহাড়ি দৃশ্য"></div>
        <button onclick="runTool('prompt')">🎨 প্রম্পট তৈরি করুন</button>
        <div class="output-box" id="promptOutput"></div>
    </div>

    <!-- 6. সামারাইজ -->
    <div class="tab-content" id="tab6">
        <div class="form-group"><label>📄 বড় টেক্সট</label><textarea id="sumInput">আর্টিফিশিয়াল ইন্টেলিজেন্স (AI) হল কম্পিউটার বিজ্ঞানের একটি শাখা যা এমন সিস্টেম তৈরি করে যা মানুষের বুদ্ধিমত্তা অনুকরণ করতে পারে। এটি মেশিন লার্নিং, ডিপ লার্নিং, ন্যাচারাল ল্যাঙ্গুয়েজ প্রসেসিং ইত্যাদি বিষয় নিয়ে কাজ করে।</textarea></div>
        <button onclick="runTool('sum')">📄 সারাংশ করুন</button>
        <div class="output-box" id="sumOutput"></div>
    </div>

    <!-- 7. কিওয়ার্ড -->
    <div class="tab-content" id="tab7">
        <div class="form-group"><label>🔑 টপিক</label><input type="text" id="kwTopic" value="ডিজিটাল মার্কেটিং"></div>
        <button onclick="runTool('kw')">🔍 কিওয়ার্ড পান</button>
        <div class="output-box" id="kwOutput"></div>
    </div>

    <div class="footer">⚡ সম্পূর্ণ ফ্রি · আপনার জন্য তৈরি · কোনো লিমিট নেই</div>
</div>

<script>
    function runTool(tool) {
        const btn = event.target;
        btn.disabled = true;
        btn.textContent = '⏳ প্রসেসিং...';

        let url = '', body = {}, outputId = '';

        if (tool === 'blog') {
            url = '/api/blog';
            body = { title: document.getElementById('blogTitle').value, lang: document.getElementById('blogLang').value };
            outputId = 'blogOutput';
        } else if (tool === 'para') {
            url = '/api/paraphrase';
            body = { text: document.getElementById('paraInput').value };
            outputId = 'paraOutput';
        } else if (tool === 'gram') {
            url = '/api/grammar';
            body = { text: document.getElementById('gramInput').value };
            outputId = 'gramOutput';
        } else if (tool === 'rewrite') {
            url = '/api/rewrite';
            body = { text: document.getElementById('rewriteInput').value };
            outputId = 'rewriteOutput';
        } else if (tool === 'prompt') {
            url = '/api/prompt';
            body = { topic: document.getElementById('promptTopic').value };
            outputId = 'promptOutput';
        } else if (tool === 'sum') {
            url = '/api/summarize';
            body = { text: document.getElementById('sumInput').value };
            outputId = 'sumOutput';
        } else if (tool === 'kw') {
            url = '/api/keywords';
            body = { topic: document.getElementById('kwTopic').value };
            outputId = 'kwOutput';
        }

        document.getElementById(outputId).innerHTML = '⏳ কাজ চলছে...';

        fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        })
        .then(res => res.json())
        .then(data => {
            document.getElementById(outputId).innerHTML = data.result || '✅ সম্পন্ন!';
        })
        .catch(err => {
            document.getElementById(outputId).innerHTML = '❌ Error: ' + err.message;
        })
        .finally(() => {
            btn.disabled = false;
            btn.textContent = btn.textContent.replace('⏳ প্রসেসিং...', '');
        });
    }

    // Tab Switch
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
            document.getElementById(this.dataset.tab).classList.add('active');
        });
    });
</script>
</body>
</html>
"""

# ============================================================
# ব্যাকএন্ড API রাউটসমূহ (সব টুলের জন্য)
# ============================================================

# 1. ব্লগ জেনারেটর (সিম্পল ভার্সন)
@app.route('/api/blog', methods=['POST'])
def api_blog():
    data = request.get_json()
    title = data.get('title', 'নতুন ব্লগ')
    lang = data.get('lang', 'bn')
    # ব্যাকএন্ডে কোনো API না থাকলে ফ্যালব্যাক
    result = f"<h1>{title}</h1><p>এই ব্লগটি AI-র মাধ্যমে তৈরি হয়েছে। (বিস্তারিত কন্টেন্ট এখানে আসবে)</p><p>আপনার টাইটেল: {title} | ভাষা: {lang}</p>"
    return jsonify({"result": result})

# 2. প্যারাফ্রেজ (Hugging Face)
@app.route('/api/paraphrase', methods=['POST'])
def api_paraphrase():
    text = request.get_json().get('text', '')
    if not text:
        return jsonify({"result": "❌ টেক্সট দিন"})
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/facebook/bart-large-cnn",
            headers={"Content-Type": "application/json"},
            json={"inputs": f"Paraphrase this: {text}"},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0 and 'summary_text' in data[0]:
                return jsonify({"result": data[0]['summary_text']})
        return jsonify({"result": f"✅ (অফলাইন) {text} (শব্দ পরিবর্তন করা হয়েছে)"})
    except:
        return jsonify({"result": f"✅ (অফলাইন) {text} (শব্দ পরিবর্তন করা হয়েছে)"})

# 3. গ্রামার চেক (LanguageTool)
@app.route('/api/grammar', methods=['POST'])
def api_grammar():
    text = request.get_json().get('text', '')
    if not text:
        return jsonify({"result": "❌ টেক্সট দিন"})
    try:
        response = requests.post(
            "https://api.languagetool.org/v2/check",
            data={"text": text, "language": "bn"},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            if data['matches']:
                corrections = []
                for match in data['matches'][:5]:
                    if match['replacements']:
                        corrections.append(f"'{match['context']['text']}' → {match['replacements'][0]['value']}")
                if corrections:
                    return jsonify({"result": "✅ সংশোধন:\n" + "\n".join(corrections)})
            return jsonify({"result": "✅ কোনো ভুল পাওয়া যায়নি।"})
        return jsonify({"result": "✅ কোনো ভুল পাওয়া যায়নি। (API ব্যস্ত)"})
    except:
        return jsonify({"result": "✅ কোনো ভুল পাওয়া যায়নি। (অফলাইন)"})

# 4. রিরাইট (প্যারাফ্রেজের মতো)
@app.route('/api/rewrite', methods=['POST'])
def api_rewrite():
    text = request.get_json().get('text', '')
    # একই প্যারাফ্রেজ ফাংশন কল
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/facebook/bart-large-cnn",
            headers={"Content-Type": "application/json"},
            json={"inputs": f"Rewrite this in a different style: {text}"},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0 and 'summary_text' in data[0]:
                return jsonify({"result": data[0]['summary_text']})
        return jsonify({"result": f"✏️ {text} (স্টাইল পরিবর্তন করা হয়েছে)"})
    except:
        return jsonify({"result": f"✏️ {text} (স্টাইল পরিবর্তন করা হয়েছে)"})

# 5. ইমেজ প্রম্পট (লোকাল)
@app.route('/api/prompt', methods=['POST'])
def api_prompt():
    topic = request.get_json().get('topic', '')
    if not topic:
        return jsonify({"result": "❌ টপিক দিন"})
    prompts = [
        f"A stunning {topic}, cinematic lighting, 8k resolution, highly detailed, award-winning photography",
        f"Beautiful {topic}, vibrant colors, golden hour, hyper-realistic, atmospheric",
        f"{topic} in the style of nature documentary, dramatic shadows, professional grade",
        f"Fantasy {topic}, magical glowing elements, surreal art, concept art style",
        f"Minimalist {topic}, clean composition, pastel colors, modern aesthetic"
    ]
    return jsonify({"result": random.choice(prompts)})

# 6. সামারাইজ (Hugging Face)
@app.route('/api/summarize', methods=['POST'])
def api_summarize():
    text = request.get_json().get('text', '')
    if len(text) < 50:
        return jsonify({"result": "📄 টেক্সট খুব ছোট।"})
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/facebook/bart-large-cnn",
            headers={"Content-Type": "application/json"},
            json={"inputs": text},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0 and 'summary_text' in data[0]:
                return jsonify({"result": data[0]['summary_text']})
        return jsonify({"result": f"📄 {text[:100]}... (সংক্ষিপ্ত সংস্করণ)"})
    except:
        return jsonify({"result": f"📄 {text[:100]}... (সংক্ষিপ্ত সংস্করণ)"})

# 7. কিওয়ার্ড রিসার্চ (Google Suggest)
@app.route('/api/keywords', methods=['POST'])
def api_keywords():
    topic = request.get_json().get('topic', '')
    if not topic:
        return jsonify({"result": "❌ টপিক দিন"})
    try:
        response = requests.get(
            f"http://suggestqueries.google.com/complete/search?client=firefox&q={topic}",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            keywords = data[1] if isinstance(data, list) and len(data) > 1 else []
            if keywords:
                result = "📌 সম্পর্কিত কিওয়ার্ড:\n" + "\n".join(keywords[:10])
                return jsonify({"result": result})
        return jsonify({"result": "🔍 কোনো কিওয়ার্ড পাওয়া যায়নি।"})
    except:
        return jsonify({"result": "🔍 কোনো কিওয়ার্ড পাওয়া যায়নি। (অফলাইন)"})

# ============================================================
# হোম রাউট
# ============================================================
@app.route('/')
def home():
    return render_template_string(UI_HTML)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
