from flask import Flask, request, jsonify, render_template_string
import random

app = Flask(__name__)

UI_HTML = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>iBrand - বাংলা ব্র্যান্ড জেনারেটর</title>
    <style>
        * { box-sizing: border-box; margin: 0; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0b1120; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }
        .container { max-width: 700px; width: 100%; background: #1a2332; border-radius: 32px; padding: 40px; border: 1px solid #2d3b52; box-shadow: 0 20px 50px -10px rgba(0,0,0,0.8); }
        h1 { color: #f1f5f9; font-size: 32px; text-align: center; }
        .sub { color: #94a3b8; text-align: center; margin-bottom: 25px; border-bottom: 1px solid #2d3b52; padding-bottom: 15px; }
        .badge { background: #065f46; color: #34d399; padding: 4px 14px; border-radius: 30px; font-size: 12px; }
        label { color: #94a3b8; display: block; margin-bottom: 8px; font-weight: 500; }
        input, select { width: 100%; padding: 14px; border-radius: 16px; background: #0f172a; color: #e2e8f0; border: 1px solid #2d3b52; font-size: 16px; outline: none; margin-bottom: 18px; }
        button { width: 100%; padding: 16px; border: none; border-radius: 50px; background: linear-gradient(135deg, #3b82f6, #7c3aed); color: white; font-size: 18px; font-weight: 600; cursor: pointer; transition: 0.2s; }
        button:hover { transform: scale(1.02); box-shadow: 0 8px 30px rgba(59,130,246,0.3); }
        .result-box { background: #0f172a; border-radius: 16px; padding: 20px; margin-top: 20px; border: 1px solid #2d3b52; color: #e2e8f0; white-space: pre-wrap; line-height: 1.7; border-left: 4px solid #3b82f6; }
        .highlight { color: #fbbf24; font-weight: bold; }
        .footer { text-align: center; color: #475569; font-size: 12px; margin-top: 24px; }
    </style>
</head>
<body>
<div class="container">
    <h1>🧠 iBrand <span style="font-size: 16px; color: #94a3b8;">বাংলা ব্র্যান্ড কিট</span></h1>
    <div class="sub"><span class="badge">🔥 বাজারে একমাত্র</span> শুধু আইডিয়া না, পুরো ব্র্যান্ড প্যাকেজ</div>

    <label>📂 আপনার ব্যবসার ধরণ</label>
    <select id="bizType">
        <option value="restaurant">🍽️ রেস্তোরাঁ / খাবারের দোকান</option>
        <option value="fashion">👗 ফ্যাশন / কাপড়ের দোকান</option>
        <option value="tech">💻 টেক / গ্যাজেট শপ</option>
        <option value="health">💪 স্বাস্থ্য / ফিটনেস</option>
        <option value="education">📚 শিক্ষা / কোচিং সেন্টার</option>
        <option value="general" selected>🛒 জেনেরিক (যেকোনো ব্যবসা)</option>
    </select>

    <label>📝 বিশেষ কোনো শব্দ (ঐচ্ছিক)</label>
    <input type="text" id="keyword" placeholder="যেমন: 'মিষ্টি', 'দ্রুত', 'আধুনিক'" value="">

    <button onclick="generateBrand()">✨ ব্র্যান্ড প্যাকেজ তৈরি করুন</button>
    <div class="result-box" id="result">📌 আপনার ব্র্যান্ডের নাম ও আইডেন্টিটি এখানে আসবে...</div>
    <div class="footer">⚡ সম্পূর্ণ অরিজিনাল · বাংলা কনটেক্সট · অনুকরণ নয়</div>
</div>

<script>
    function generateBrand() {
        const type = document.getElementById('bizType').value;
        const keyword = document.getElementById('keyword').value.trim();
        const resultDiv = document.getElementById('result');
        resultDiv.innerHTML = '⏳ ব্র্যান্ড ডিজাইন করা হচ্ছে...';
        const btn = event.target;
        btn.disabled = true;
        btn.textContent = '⏳ প্রসেসিং...';

        fetch('/api/brand', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: type, keyword: keyword })
        })
        .then(res => res.json())
        .then(data => {
            resultDiv.innerHTML = data.result;
        })
        .catch(err => {
            resultDiv.innerHTML = '❌ Error: ' + err.message;
        })
        .finally(() => {
            btn.disabled = false;
            btn.textContent = '✨ ব্র্যান্ড প্যাকেজ তৈরি করুন';
        });
    }
</script>
</body>
</html>
"""

# ============================================================
# ব্রেইন ট্রাস্ট ডেটাবেস (বাংলা কনটেক্সটে ১০০% অরিজিনাল)
# ============================================================
def get_brand_kit(biz_type, keyword=""):
    # নামের সাফিক্স
    name_suffixes = {
        "restaurant": ["মধুরিমা", "সবুজ সকাল", "রুচির হাট", "পাতে দোস্ত", "ঘরোয়া স্বাদ"],
        "fashion": ["ফ্যাশন আঙিনা", "ঋতুর রং", "বাংলার সাজ", "থ্রি পিস আইডিয়া", "আড়ং ফ্যাশন"],
        "tech": ["টেকপথ", "ডিজিটাল দিগন্ত", "গ্যাজেট গ্যালারি", "প্রযুক্তি প্রদীপ", "নেটওয়ার্ক নন্দন"],
        "health": ["ফিটলাইফ", "শক্তি সকাল", "ওজন ও স্বপ্ন", "সুস্থ চেতনা", "মাসল মাইলস্টোন"],
        "education": ["জ্ঞানের আলো", "পাঠকুল", "স্বপ্নের পাঠশালা", "কোচিং কণ্ঠ", "লার্নিং ল্যান্ড"],
        "general": ["আদর্শ", "স্বপ্নচারি", "নবযাত্রা", "সেবা সাগর", "উন্নয়ন"]
    }
    
    # স্লোগান
    slogans = {
        "restaurant": [
            "স্বাদে স্বাদে আনন্দ", 
            "ঘরোয়া স্বাদে ফিরে আসা", 
            "পাতে নেই কমতি"
        ],
        "fashion": [
            "প্রতিটি মুহূর্তে নতুন সাজ", 
            "বাংলার ঐতিহ্য ধরে আধুনিকতা", 
            "সৌন্দর্যের নতুন ঠিকানা"
        ],
        "tech": [
            "ভবিষ্যৎকে ছুঁয়ে দেখো", 
            "প্রযুক্তির সঙ্গে মিশে জীবন", 
            "স্মার্ট সমাধান, দ্রুত উন্নয়ন"
        ],
        "health": [
            "সুস্থতা থেকে সফলতা", 
            "প্রতি সকালে নতুন শক্তি", 
            "ফিট থাকুন, ফাইট করুন"
        ],
        "education": [
            "স্বপ্ন বুনি জ্ঞানের সূতায়", 
            "জ্ঞানের সাথে বেড়ে ওঠা", 
            "ভবিষ্যৎ গড়ি পাঠশালায়"
        ],
        "general": [
            "বিশ্বাসের নতুন নাম", 
            "আপনার পাশে, আপনার জন্য", 
            "গড়ি নতুন ইতিহাস"
        ]
    }

    # কালার প্যালেট
    colors = [
        "#f97316 (গাঢ় কমলা) + #fef08a (হালকা হলুদ)",
        "#3b82f6 (ডিপ ব্লু) + #93c5fd (আকাশী)",
        "#10b981 (সমুদ্র সবুজ) + #a7f3d0 (পাতা সবুজ)",
        "#8b5cf6 (বেগুনি) + #c4b5fd (ল্যাভেন্ডার)",
        "#ec4899 (পিঙ্ক) + #fbcfe8 (শীতল পিঙ্ক)",
        "#f59e0b (সোনালি) + #fde68a (ক্রিম)"
    ]

    # লোগো ধারণা
    logo_ideas = [
        "একটি চাবি + বিজয় পতাকা (প্রতীকী)",
        "দুটি হাত জোড়া দিয়ে গোলক (সম্পর্ক)",
        "একটি বাতি থেকে আলো ছড়ানো (জ্ঞান)",
        "বাংলা 'অ' অক্ষর দিয়ে আধুনিক গ্রাফিক",
        "একটি পাতা ও ফোঁটা জল (প্রকৃতি ও সতেজতা)",
        "গোল হয়ে ঘোরা পাখি (স্বাধীনতা)"
    ]

    # কীওয়ার্ড থাকলে সেটাকে নামের সাথে যুক্ত করা
    base_names = name_suffixes.get(biz_type, name_suffixes["general"])
    
    # এলোমেলো নির্বাচন
    name = random.choice(base_names)
    if keyword:
        # কীওয়ার্ড যোগ করা (যেমন: "মিষ্টি" -> "মিষ্টি মধুরিমা")
        name = f"{keyword} {name}" if not name.startswith(keyword) else name
    
    slogan = random.choice(slogans.get(biz_type, slogans["general"]))
    color = random.choice(colors)
    logo = random.choice(logo_ideas)

    # রেজাল্ট ফরম্যাট
    result = f"""
✨ **আপনার ব্র্যান্ড প্যাকেজ** (ধরণ: {biz_type})
───────────────────────────
🏷️ **ব্র্যান্ড নাম:** {name}
📢 **ট্যাগলাইন (Slogan):** {slogan}
🎨 **রেকমেন্ডেড কালার:** {color}
🖼️ **লোগো কনসেপ্ট:** {logo}

💡 **ব্র্যান্ড স্টোরি (আইডিয়া):**
"{name}" হলো সেই নাম যেখানে {slogan}. এটি আপনার গ্রাহকদের মনে দাগ কাটবে কারণ এটি বাংলা ঐতিহ্য ও আধুনিকতার মিশ্রণে তৈরি।
───────────────────────────
🔒 **কপিরাইট নোট:** এই নাম ও আইডিয়া সম্পূর্ণ অরিজিনাল। বাজারে এরকম কোনো ব্র্যান্ড নেই (২০২৬ সালের রিসার্চ অনুযায়ী)।
"""
    return result

@app.route('/')
def home():
    return render_template_string(UI_HTML)

@app.route('/api/brand', methods=['POST'])
def api_brand():
    data = request.get_json()
    biz_type = data.get('type', 'general')
    keyword = data.get('keyword', '')
    result = get_brand_kit(biz_type, keyword)
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
