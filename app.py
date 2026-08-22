from flask import Flask, request, jsonify, render_template_string
import random
import requests
import json
import urllib.parse

app = Flask(__name__)

# ============================================================
# HTML টেমপ্লেট (সুপার-মডার্ন ইউআই)
# ============================================================
UI_HTML = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>নেক্সট-জেন AI ক্রিয়েটর ল্যাব</title>
    <style>
        * { box-sizing: border-box; margin: 0; }
        body { font-family: system-ui, sans-serif; background: #0b1120; min-height: 100vh; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { color: #f1f5f9; font-size: 28px; text-align: center; }
        .sub { color: #94a3b8; text-align: center; margin-bottom: 24px; border-bottom: 1px solid #2d3b52; padding-bottom: 16px; }
        .grid { display: grid; grid-template-columns: 1fr; gap: 20px; margin: 20px 0; }
        .card { background: #1a2332; border-radius: 20px; padding: 24px; border: 1px solid #2d3b52; transition: 0.3s; }
        .card:hover { border-color: #3b82f6; }
        .card h3 { color: #f1f5f9; margin-bottom: 8px; }
        .card p { color: #94a3b8; font-size: 14px; margin-bottom: 12px; }
        input, textarea { width: 100%; padding: 14px; border-radius: 16px; background: #0f172a; color: #e2e8f0; border: 1px solid #2d3b52; font-size: 15px; outline: none; }
        button { padding: 14px 28px; border: none; border-radius: 50px; background: linear-gradient(135deg, #3b82f6, #7c3aed); color: white; font-size: 16px; font-weight: 600; cursor: pointer; transition: 0.2s; margin-top: 12px; width: 100%; }
        button:hover { transform: scale(1.01); box-shadow: 0 8px 24px rgba(59,130,246,0.35); }
        .result-box { background: #0f172a; border-radius: 16px; padding: 16px; margin-top: 16px; border: 1px solid #2d3b52; color: #e2e8f0; white-space: pre-wrap; font-size: 14px; line-height: 1.6; min-height: 60px; }
        .badge { background: #065f46; color: #34d399; padding: 2px 12px; border-radius: 30px; font-size: 11px; margin-left: 8px; }
        .footer { text-align: center; color: #475569; font-size: 12px; margin-top: 30px; border-top: 1px solid #2d3b52; padding-top: 16px; }
        .highlight { color: #fbbf24; }
        @media (max-width: 640px) { .card { padding: 16px; } }
    </style>
</head>
<body>
<div class="container">
    <h1>🧠 নেক্সট-জেন AI ল্যাব</h1>
    <div class="sub">শুধু কন্টেন্ট না — পুরো স্ট্র্যাটেজি তৈরি করুন <span class="badge">🔥 ব্র্যান্ড নতুন</span></div>

    <div class="grid">
        <!-- কার্ড ১: হুক জেনারেটর -->
        <div class="card">
            <h3>🎯 হুক জেনারেটর</h3>
            <p>ভিডিও বা পোস্টের জন্য ৫টি হুক (আকর্ষণীয় শুরুর লাইন)</p>
            <input type="text" id="hookTopic" placeholder="টপিক লিখুন (যেমন: ওজন কমানো)" value="মোবাইল ব্যাটারি">
            <button onclick="fetchAI('hook')">🎯 হুক তৈরি করুন</button>
            <div class="result-box" id="hookResult"></div>
        </div>

        <!-- কার্ড ২: শর্টস স্ক্রিপ্ট -->
        <div class="card">
            <h3>🎬 শর্টস স্ক্রিপ্ট</h3>
            <p>৬০ সেকেন্ডের ইউটিউব শর্টস/রিলস স্ক্রিপ্ট (টাইমস্ট্যাম্প সহ)</p>
            <input type="text" id="scriptTopic" placeholder="টপিক লিখুন" value="ব্যাটারি সেভ">
            <button onclick="fetchAI('script')">🎬 স্ক্রিপ্ট তৈরি করুন</button>
            <div class="result-box" id="scriptResult"></div>
        </div>

        <!-- কার্ড ৩: ভিজুয়াল ব্লুপ্রিন্ট -->
        <div class="card">
            <h3>🖼️ ভিজুয়াল ব্লুপ্রিন্ট</h3>
            <p>থাম্বনেইল বা পোস্টারের ডিজাইন আইডিয়া (কালার + কম্পোজিশন)</p>
            <input type="text" id="visualTopic" placeholder="টপিক লিখুন" value="সুস্থ জীবন">
            <button onclick="fetchAI('visual')">🖼️ ডিজাইন আইডিয়া পান</button>
            <div class="result-box" id="visualResult"></div>
        </div>

        <!-- কার্ড ৪: ব্রেনস্টর্ম প্রশ্ন -->
        <div class="card">
            <h3>🧠 ব্রেনস্টর্ম প্রশ্ন</h3>
            <p>আপনার টপিক নিয়ে মানুষ কী কী প্রশ্ন করবে (কমেন্ট আইডিয়া)</p>
            <input type="text" id="qaTopic" placeholder="টপিক লিখুন" value="অনলাইন আয়">
            <button onclick="fetchAI('qa')">🧠 প্রশ্ন তৈরি করুন</button>
            <div class="result-box" id="qaResult"></div>
        </div>

        <!-- কার্ড ৫: কন্টেন্ট অ্যাঙ্গেল -->
        <div class="card">
            <h3>🔮 কন্টেন্ট অ্যাঙ্গেল</h3>
            <p>একই টপিককে ৫টি ভিন্ন দৃষ্টিকোণ থেকে দেখার উপায়</p>
            <input type="text" id="angleTopic" placeholder="টপিক লিখুন" value="ডিজিটাল মার্কেটিং">
            <button onclick="fetchAI('angle')">🔮 অ্যাঙ্গেল তৈরি করুন</button>
            <div class="result-box" id="angleResult"></div>
        </div>
    </div>
    <div class="footer">⚡ ১০০% অরিজিনাল · কোনো লিমিট নেই · শুধু তোমার জন্য</div>
</div>

<script>
    function fetchAI(type) {
        let url = '', body = {}, resultId = '';
        if (type === 'hook') {
            url = '/api/hook';
            body = { topic: document.getElementById('hookTopic').value };
            resultId = 'hookResult';
        } else if (type === 'script') {
            url = '/api/script';
            body = { topic: document.getElementById('scriptTopic').value };
            resultId = 'scriptResult';
        } else if (type === 'visual') {
            url = '/api/visual';
            body = { topic: document.getElementById('visualTopic').value };
            resultId = 'visualResult';
        } else if (type === 'qa') {
            url = '/api/qa';
            body = { topic: document.getElementById('qaTopic').value };
            resultId = 'qaResult';
        } else if (type === 'angle') {
            url = '/api/angle';
            body = { topic: document.getElementById('angleTopic').value };
            resultId = 'angleResult';
        }

        const resultDiv = document.getElementById(resultId);
        resultDiv.innerHTML = '⏳ আইডিয়া তৈরি হচ্ছে...';
        const btn = event.target;
        btn.disabled = true;
        btn.textContent = '⏳ প্রসেসিং...';

        fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        })
        .then(res => res.json())
        .then(data => {
            resultDiv.innerHTML = data.result || '✅ সম্পন্ন!';
        })
        .catch(err => {
            resultDiv.innerHTML = '❌ Error: ' + err.message;
        })
        .finally(() => {
            btn.disabled = false;
            btn.textContent = btn.textContent.replace('⏳ প্রসেসিং...', '');
        });
    }
</script>
</body>
</html>
"""

# ============================================================
# ইনোভেটিভ AI লজিক (এখানে চমক!)
# ============================================================

# 1. হুক জেনারেটর
def generate_hooks(topic):
    hooks = [
        f"❌ ৯০% মানুষ এই কাজটা ভুল করে, আর তুমি যদি এটি করো তাহলে...",
        f"🤯 {topic} সম্পর্কে এই সত্যটি জানলে তুমি চমকে যাবে!",
        f"⚡ {topic} নিয়ে এই ১টি কৌশল জানলে বাকি সব ভুলে যাবে!",
        f"🔥 {topic} উপেক্ষা করছো? তাহলে এই ভিডিওটি তোমার জন্য!",
        f"💡 {topic} নিয়ে বিশেষজ্ঞরা যা বলে না, সেটাই আজ বলবো!"
    ]
    return "\n".join([f"{i+1}. {hook}" for i, hook in enumerate(hooks)])

# 2. শর্টস স্ক্রিপ্ট (সময় অনুযায়ী)
def generate_script(topic):
    return f"""
🎬 ৬০ সেকেন্ড স্ক্রিপ্ট: {topic}
─────────────────────────
🕐 ০:০০ - ০:০৫ | হুক: 
"আজ {topic} নিয়ে যে টিপস দেবো, তা তোমার জীবন বদলে দিতে পারে!"

🕐 ০:০৫ - ০:২০ | কনফ্লিক্ট:
"অনেকেই এই কাজটি করে, কিন্তু সঠিক পদ্ধতি জানলে কাজ ৫ গুণ বাড়বে!"

🕐 ০:২০ - ০:৪০ | সলিউশন:
"পদক্ষেপ ১: প্রথমে এটি করুন। পদক্ষেপ ২: তারপর এটি করুন। 
এত সহজ! তবুও কেউ করে না।"

🕐 ০:৪০ - ০:৫৫ | ফলাফল + প্রুফ:
"আমি নিজে এটি ব্যবহার করেছি, এবং ফলাফল পেয়েছি। 
তোমার কি এখনও বিশ্বাস হচ্ছে না?"

🕐 ০:৫৫ - ১:০০ | কলে টু অ্যাকশন:
"ভিডিওটি লাইক ও শেয়ার করো, এবং কমেন্টে জানাও তুমি এটি করবে কিনা!"
"""

# 3. ভিজুয়াল ব্লুপ্রিন্ট
def generate_visual(topic):
    colors = ["#f97316 (হট অরেঞ্জ)", "#3b82f6 (ডিপ ব্লু)", "#10b981 (গ্রিন)", "#8b5cf6 (পার্পল)", "#ec4899 (পিঙ্ক)"]
    styles = ["মিনিমালিস্ট", "বোল্ড টাইপোগ্রাফি", "গ্রেডিয়েন্ট ব্যাকগ্রাউন্ড", "অ্যাবস্ট্রাক্ট শেপ", "নেচার থিম"]
    comps = ["বামে টেক্সট, ডানে আইকন", "মাঝখানে বড় টেক্সট", "নিচে CTA ব্যারন", "উপরে ব্র্যান্ড লোগো"]
    return f"""
🖼️ ভিজুয়াল ব্লুপ্রিন্ট: {topic}
─────────────────────────
🎨 প্রাথমিক কালার: {random.choice(colors)}
📐 ডিজাইন স্টাইল: {random.choice(styles)}
📸 কম্পোজিশন: {random.choice(comps)}
💡 টেক্সট: "{random.choice(['বিশ্বাস করো', 'জানো', 'বদলাও', 'সাহস রাখো'])} {topic}"
🖍️ ইউজার ইমোশন: {random.choice(['কৌতূহল', 'উত্তেজনা', 'আত্মবিশ্বাস', 'আতঙ্ক'])}
""" 

# 4. ব্রেনস্টর্ম প্রশ্ন
def generate_qa(topic):
    questions = [
        f"❓ {topic} শুরু করতে কী কী লাগে?",
        f"❓ {topic} এ সফল হওয়ার প্রথম ধাপ কী?",
        f"❓ {topic} নিয়ে সবচেয়ে বড় ভুল কী?",
        f"❓ {topic} থেকে আসলে কী লাভ হয়?",
        f"❓ {topic} এর ভবিষ্যৎ কী?"
    ]
    return "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])

# 5. কন্টেন্ট অ্যাঙ্গেল
def generate_angles(topic):
    angles = [
        f"1️⃣ {topic} এর দার্শনিক দিক — কেন মানুষ এটি করে?",
        f"2️⃣ {topic} এর ব্যবহারিক দিক — হাতে-কলমে গাইড",
        f"3️⃣ {topic} এর ভুল ধারণা — মানুষ যা জানে না",
        f"4️⃣ {topic} এর ফিউচার ট্রেন্ড — আগামী ৫ বছর কী হবে?",
        f"5️⃣ {topic} এর হ্যাকস — সময় ও খরচ বাঁচানোর উপায়"
    ]
    return "\n".join(angles)

# ============================================================
# Flask রাউটসমূহ
# ============================================================
@app.route('/')
def home():
    return render_template_string(UI_HTML)

@app.route('/api/hook', methods=['POST'])
def api_hook():
    topic = request.get_json().get('topic', 'এই টপিক')
    return jsonify({"result": generate_hooks(topic)})

@app.route('/api/script', methods=['POST'])
def api_script():
    topic = request.get_json().get('topic', 'এই টপিক')
    return jsonify({"result": generate_script(topic)})

@app.route('/api/visual', methods=['POST'])
def api_visual():
    topic = request.get_json().get('topic', 'এই টপিক')
    return jsonify({"result": generate_visual(topic)})

@app.route('/api/qa', methods=['POST'])
def api_qa():
    topic = request.get_json().get('topic', 'এই টপিক')
    return jsonify({"result": generate_qa(topic)})

@app.route('/api/angle', methods=['POST'])
def api_angle():
    topic = request.get_json().get('topic', 'এই টপিক')
    return jsonify({"result": generate_angles(topic)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
