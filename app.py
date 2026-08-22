from flask import Flask, request, jsonify, render_template_string
import random
import requests
import json

app = Flask(__name__)

# ============================================================
# HTML টেমপ্লেট (UI)
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
        @media (max-width: 640px) { .card { padding: 16px; } }
    </style>
</head>
<body>
<div class="container">
    <h1>🧠 নেক্সট-জেন AI ল্যাব</h1>
    <div class="sub">শুধু কন্টেন্ট না — পুরো স্ট্র্যাটেজি <span class="badge">🔥 ব্র্যান্ড নতুন</span></div>

    <div class="grid">
        <!-- কার্ড ১: হুক -->
        <div class="card">
            <h3>🎯 হুক জেনারেটর</h3>
            <input type="text" id="hookTopic" placeholder="টপিক" value="মোবাইল ব্যাটারি">
            <button onclick="fetchAI('hook')">🎯 হুক তৈরি করুন</button>
            <div class="result-box" id="hookResult"></div>
        </div>
        <!-- কার্ড ২: স্ক্রিপ্ট -->
        <div class="card">
            <h3>🎬 শর্টস স্ক্রিপ্ট</h3>
            <input type="text" id="scriptTopic" placeholder="টপিক" value="ব্যাটারি সেভ">
            <button onclick="fetchAI('script')">🎬 স্ক্রিপ্ট তৈরি</button>
            <div class="result-box" id="scriptResult"></div>
        </div>
        <!-- কার্ড ৩: ভিজুয়াল -->
        <div class="card">
            <h3>🖼️ ভিজুয়াল ব্লুপ্রিন্ট</h3>
            <input type="text" id="visualTopic" placeholder="টপিক" value="সুস্থ জীবন">
            <button onclick="fetchAI('visual')">🖼️ ডিজাইন আইডিয়া</button>
            <div class="result-box" id="visualResult"></div>
        </div>
        <!-- কার্ড ৪: প্রশ্ন -->
        <div class="card">
            <h3>🧠 ব্রেনস্টর্ম প্রশ্ন</h3>
            <input type="text" id="qaTopic" placeholder="টপিক" value="অনলাইন আয়">
            <button onclick="fetchAI('qa')">🧠 প্রশ্ন তৈরি</button>
            <div class="result-box" id="qaResult"></div>
        </div>
        <!-- কার্ড ৫: অ্যাঙ্গেল -->
        <div class="card">
            <h3>🔮 কন্টেন্ট অ্যাঙ্গেল</h3>
            <input type="text" id="angleTopic" placeholder="টপিক" value="ডিজিটাল মার্কেটিং">
            <button onclick="fetchAI('angle')">🔮 অ্যাঙ্গেল তৈরি</button>
            <div class="result-box" id="angleResult"></div>
        </div>
        <!-- কার্ড ৬: কন্টেন্ট আইডিয়া (নতুন) -->
        <div class="card">
            <h3>💡 কন্টেন্ট আইডিয়া</h3>
            <input type="text" id="ideaTopic" placeholder="টপিক" value="ডিজিটাল মার্কেটিং">
            <button onclick="fetchAI('idea')">💡 আইডিয়া তৈরি</button>
            <div class="result-box" id="ideaResult"></div>
        </div>
    </div>
    <div class="footer">⚡ ১০০% অরিজিনাল · তোমার জন্য</div>
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
        } else if (type === 'idea') {
            url = '/api/ideas';
            body = { topic: document.getElementById('ideaTopic').value };
            resultId = 'ideaResult';
        }

        const resultDiv = document.getElementById(resultId);
        resultDiv.innerHTML = '⏳ তৈরি হচ্ছে...';
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
# হেল্পার ফাংশন (ইনোভেটিভ লজিক)
# ============================================================
def generate_hooks(topic):
    hooks = [
        f"❌ ৯০% মানুষ এই কাজটা ভুল করে, আর তুমি যদি এটি করো তাহলে...",
        f"🤯 {topic} সম্পর্কে এই সত্যটি জানলে তুমি চমকে যাবে!",
        f"⚡ {topic} নিয়ে এই ১টি কৌশল জানলে বাকি সব ভুলে যাবে!",
        f"🔥 {topic} উপেক্ষা করছো? তাহলে এই ভিডিওটি তোমার জন্য!",
        f"💡 {topic} নিয়ে বিশেষজ্ঞরা যা বলে না, সেটাই আজ বলবো!"
    ]
    return "\n".join([f"{i+1}. {hook}" for i, hook in enumerate(hooks)])

def generate_script(topic):
    return f"""
🎬 ৬০ সেকেন্ড স্ক্রিপ্ট: {topic}
─────────────────────────
🕐 ০:০০-০:০৫ | হুক: "আজ {topic} নিয়ে যে টিপস দেবো, তা তোমার জীবন বদলে দিতে পারে!"
🕐 ০:০৫-০:২০ | কনফ্লিক্ট: "অনেকেই এই কাজটি করে, কিন্তু সঠিক পদ্ধতি জানলে কাজ ৫ গুণ বাড়বে!"
🕐 ০:২০-০:৪০ | সলিউশন: "পদক্ষেপ ১: এটি করুন। পদক্ষেপ ২: এটি করুন। এত সহজ!"
🕐 ০:৪০-০:৫৫ | ফলাফল: "আমি নিজে এটি ব্যবহার করেছি, এবং ফল পেয়েছি।"
🕐 ০:৫৫-১:০০ | CTA: "ভিডিওটি লাইক ও শেয়ার করো!"
"""

def generate_visual(topic):
    colors = ["#f97316 (হট অরেঞ্জ)", "#3b82f6 (ডিপ ব্লু)", "#10b981 (গ্রিন)", "#8b5cf6 (পার্পল)"]
    styles = ["মিনিমালিস্ট", "বোল্ড টাইপোগ্রাফি", "গ্রেডিয়েন্ট", "অ্যাবস্ট্রাক্ট"]
    comps = ["বামে টেক্সট, ডানে আইকন", "মাঝখানে বড় টেক্সট", "নিচে CTA"]
    return f"""
🖼️ ভিজুয়াল ব্লুপ্রিন্ট: {topic}
🎨 কালার: {random.choice(colors)}
📐 স্টাইল: {random.choice(styles)}
📸 কম্পোজিশন: {random.choice(comps)}
"""

def generate_qa(topic):
    qs = [f"❓ {topic} শুরু করতে কী কী লাগে?", f"❓ {topic} এ সফল হওয়ার প্রথম ধাপ কী?", f"❓ {topic} নিয়ে সবচেয়ে বড় ভুল কী?"]
    return "\n".join(qs)

def generate_angles(topic):
    angles = [f"{i+1}. {topic} এর {d}" for i, d in enumerate(["দার্শনিক দিক", "ব্যবহারিক দিক", "ভুল ধারণা", "ফিউচার ট্রেন্ড", "হ্যাকস"])]
    return "\n".join(angles)

def generate_ideas(topic):
    ideas = [
        f"📌 {topic} এর ৫টি সিক্রেট",
        f"📌 {topic} দিয়ে মাসে ৫০,০০০ টাকা আয়",
        f"📌 {topic} শেখার সেরা ৩টি ফ্রি রিসোর্স",
        f"📌 {topic} এ নতুনদের করা ৭টি ভুল",
        f"📌 {topic} এর ভবিষ্যৎ ২০২৭"
    ]
    return "\n".join(ideas)

# ============================================================
# API রাউটসমূহ (সবগুলো এখানে)
# ============================================================
@app.route('/')
def home():
    return render_template_string(UI_HTML)

@app.route('/api/hook', methods=['POST'])
def api_hook():
    topic = request.get_json().get('topic', '')
    return jsonify({"result": generate_hooks(topic)})

@app.route('/api/script', methods=['POST'])
def api_script():
    topic = request.get_json().get('topic', '')
    return jsonify({"result": generate_script(topic)})

@app.route('/api/visual', methods=['POST'])
def api_visual():
    topic = request.get_json().get('topic', '')
    return jsonify({"result": generate_visual(topic)})

@app.route('/api/qa', methods=['POST'])
def api_qa():
    topic = request.get_json().get('topic', '')
    return jsonify({"result": generate_qa(topic)})

@app.route('/api/angle', methods=['POST'])
def api_angle():
    topic = request.get_json().get('topic', '')
    return jsonify({"result": generate_angles(topic)})

# 👇 নতুন রাউট (ঠিক এখানে)
@app.route('/api/ideas', methods=['POST'])
def api_ideas():
    topic = request.get_json().get('topic', '')
    return jsonify({"result": generate_ideas(topic)})

# ============================================================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
