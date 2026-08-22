from flask import Flask, request, render_template_string, jsonify
import requests
import json
import time
import traceback

app = Flask(__name__)

# Hugging Face API (ব্যাকআপ সহ)
MODELS = [
    "https://api-inference.huggingface.co/models/google/flan-t5-large",
    "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
]

# ============================================================
# ইউজার ইন্টারফেস (UI) — আগের মতোই
# ============================================================
UI_HTML = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ব্লগ পোস্ট জেনারেটর (SEO-ফ্রেন্ডলি)</title>
    <style>
        * { box-sizing: border-box; margin: 0; }
        body { font-family: 'Segoe UI', sans-serif; background: #0b1120; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }
        .card { background: #1a2332; border-radius: 32px; padding: 40px; max-width: 700px; width: 100%; border: 1px solid rgba(255,255,255,0.06); }
        h1 { color: #f1f5f9; font-size: 28px; margin-bottom: 20px; }
        label { color: #94a3b8; display: block; margin-bottom: 6px; font-weight: 500; }
        input, select { width: 100%; padding: 14px; border-radius: 16px; background: #0f172a; color: #e2e8f0; border: 1px solid #2d3b52; font-size: 16px; margin-bottom: 16px; }
        button { width: 100%; padding: 16px; border: none; border-radius: 50px; background: linear-gradient(135deg, #3b82f6, #7c3aed); color: white; font-size: 18px; font-weight: 600; cursor: pointer; }
        button:disabled { opacity: 0.5; }
        .status { color: #94a3b8; margin-top: 12px; text-align: center; }
        .output-box { background: #0f172a; border-radius: 16px; padding: 20px; margin-top: 20px; max-height: 500px; overflow-y: auto; display: none; }
        .output-box pre { color: #e2e8f0; white-space: pre-wrap; font-family: monospace; font-size: 13px; }
        .btn-group { display: flex; gap: 12px; margin-top: 12px; flex-wrap: wrap; }
        .btn-group button { flex: 1; min-width: 100px; background: #059669; }
        .btn-group button:last-child { background: #d97706; }
        .footer { color: #475569; text-align: center; font-size: 12px; margin-top: 20px; }
    </style>
</head>
<body>
<div class="card">
    <h1>✍️ SEO-ফ্রেন্ডলি ব্লগ জেনারেটর</h1>
    <label>📝 আর্টিকেলের টাইটেল</label>
    <input type="text" id="titleInput" value="মোবাইলের ব্যাটারি লাইফ বাড়ানোর ১০টি টিপস (২০২৬)">
    <label>🌐 ভাষা</label>
    <select id="langSelect">
        <option value="bn">বাংলা</option>
        <option value="en">English</option>
    </select>
    <button id="generateBtn">🚀 সম্পূর্ণ আর্টিকেল তৈরি করুন</button>
    <div class="status" id="statusText">টাইটেল লিখে জেনারেট ক্লিক করুন।</div>
    <div class="output-box" id="outputBox">
        <pre id="outputContent"></pre>
        <div class="btn-group">
            <button id="copyBtn">📋 কপি</button>
            <button id="downloadBtn">⬇️ HTML ডাউনলোড</button>
        </div>
    </div>
    <div class="footer">⚡ Google AdSense · News · E-E-A-T · Overview Feature</div>
</div>
<script>
    const titleInput = document.getElementById('titleInput');
    const langSelect = document.getElementById('langSelect');
    const generateBtn = document.getElementById('generateBtn');
    const statusText = document.getElementById('statusText');
    const outputBox = document.getElementById('outputBox');
    const outputContent = document.getElementById('outputContent');
    let generatedHtml = '';

    function setStatus(msg) { statusText.textContent = msg; }

    generateBtn.addEventListener('click', async function() {
        const title = titleInput.value.trim();
        const lang = langSelect.value;
        if (!title) { setStatus('দয়া করে টাইটেল লিখুন।'); return; }
        setStatus('⏳ জেনারেট হচ্ছে (৪০-৬০ সেকেন্ড)...');
        generateBtn.disabled = true;
        generateBtn.textContent = '⏳ তৈরি হচ্ছে...';
        try {
            const res = await fetch('/generate_post', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, lang })
            });
            const data = await res.json();
            if (data.error) throw new Error(data.error);
            generatedHtml = data.html;
            outputContent.textContent = generatedHtml;
            outputBox.style.display = 'block';
            setStatus('✅ সম্পূর্ণ! কপি বা ডাউনলোড করুন।');
        } catch (err) {
            setStatus('❌ ' + err.message);
        } finally {
            generateBtn.disabled = false;
            generateBtn.textContent = '🚀 সম্পূর্ণ আর্টিকেল তৈরি করুন';
        }
    });

    document.getElementById('copyBtn').addEventListener('click', function() {
        if (!generatedHtml) return;
        navigator.clipboard.writeText(generatedHtml).then(() => setStatus('✅ কপি করা হয়েছে!'));
    });

    document.getElementById('downloadBtn').addEventListener('click', function() {
        if (!generatedHtml) return;
        const blob = new Blob([generatedHtml], { type: 'text/html;charset=utf-8' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = (titleInput.value.trim().slice(0, 30) || 'post') + '.html';
        a.click();
    });
</script>
</body>
</html>
"""

# ============================================================
# সম্পূর্ণ SEO-অপটিমাইজড HTML টেমপ্লেট
# ============================================================
BLOG_TEMPLATE = """
<!-- ============================================================ -->
<!-- সম্পূর্ণ SEO-ফ্রেন্ডলি ব্লগ পোস্ট ({title}) -->
<!-- ============================================================ -->
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">

    <title>{headline}</title>
    <meta name="description" content="{description}">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
    <link rel="canonical" href="https://www.yourblog.com/{slug}">

    <!-- ওপেন গ্রাফ -->
    <meta property="og:title" content="{headline}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="https://images.pexels.com/photos/2582937/pexels-photo-2582937.jpeg?auto=compress&cs=tinysrgb&w=1200&h=630&fit=crop">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://www.yourblog.com/{slug}">

    <!-- টুইটার -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{headline}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="https://images.pexels.com/photos/2582937/pexels-photo-2582937.jpeg?auto=compress&cs=tinysrgb&w=1200&h=630&fit=crop">

    <!-- স্কিমা: NewsArticle -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "NewsArticle",
      "headline": "{headline}",
      "description": "{description}",
      "image": "https://images.pexels.com/photos/2582937/pexels-photo-2582937.jpeg?auto=compress&cs=tinysrgb&w=1200&h=630&fit=crop",
      "datePublished": "{publish_date}",
      "dateModified": "{update_date}",
      "author": {{
        "@type": "Person",
        "name": "{author_name}",
        "url": "https://www.yourblog.com/about"
      }},
      "publisher": {{
        "@type": "Organization",
        "name": "BanglaGuide24",
        "logo": {{
          "@type": "ImageObject",
          "url": "https://www.yourblog.com/logo.png"
        }}
      }},
      "mainEntityOfPage": {{
        "@type": "WebPage",
        "@id": "https://www.yourblog.com/{slug}"
      }}
    }}
    </script>

    <!-- স্কিমা: FAQPage -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": {faq_json}
    }}
    </script>

    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; line-height: 1.6; color: #1e293b; max-width: 880px; margin: auto; padding: 20px; background: #ffffff; }}
        h1 {{ font-size: 2rem; border-left: 4px solid #1e3c72; padding-left: 16px; }}
        h2 {{ font-size: 1.5rem; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; margin-top: 2rem; }}
        .tip-card {{ background: #f8fafc; padding: 20px; border-radius: 16px; margin-bottom: 20px; border-left: 5px solid #1e3c72; }}
        .author-box {{ background: #fef9e6; padding: 16px; border-radius: 16px; display: flex; align-items: center; gap: 16px; }}
        .author-avatar {{ width: 60px; height: 60px; background: #1e3c72; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.5rem; }}
        .faq-item {{ background: #f1f5f9; padding: 14px 16px; border-radius: 12px; margin-bottom: 12px; }}
        .overview-box {{ background: #ecfdf5; padding: 16px; border-radius: 16px; border-left: 4px solid #1e3c72; margin: 20px 0; }}
        .toc-box {{ background: #f1f5f9; padding: 16px 20px; border-radius: 16px; margin: 20px 0; }}
        .toc-box ul {{ list-style: none; padding-left: 0; columns: 2; column-gap: 20px; }}
        @media (max-width: 640px) {{ .author-box {{ flex-direction: column; text-align: center; }} .toc-box ul {{ columns: 1; }} }}
        img.featured {{ width: 100%; border-radius: 16px; margin-bottom: 20px; }}
        footer {{ text-align: center; font-size: 14px; color: #64748b; border-top: 1px solid #e2e8f0; padding-top: 16px; margin-top: 24px; }}
    </style>
</head>
<body>

    <img src="https://images.pexels.com/photos/2582937/pexels-photo-2582937.jpeg?auto=compress&cs=tinysrgb&w=1200&h=630&fit=crop" alt="{title}" class="featured">

    <h1>{headline}</h1>
    <p><strong>প্রকাশ:</strong> {publish_date} &nbsp;|&nbsp; <strong>আপডেট:</strong> {update_date} &nbsp;|&nbsp; <strong>লেখক:</strong> {author_name}</p>

    <div class="overview-box">
        <strong>🤖 সংক্ষিপ্ত সারাংশ:</strong> {ai_summary}
    </div>

    <div class="toc-box">
        <h3>📖 সূচিপত্র</h3>
        <ul>
            {toc_list}
        </ul>
    </div>

    {tips_html}

    <h2>🛑 ভুল ধারণা ও সঠিক তথ্য</h2>
    <ul>
        {myth_fact_html}
    </ul>

    <h2>❓ সচরাচর জিজ্ঞাসা (FAQ)</h2>
    {faq_items}

    <h2>📌 শেষ কথা</h2>
    <p>{conclusion}</p>

    <div class="author-box">
        <div class="author-avatar">✍️</div>
        <div>
            <h4 style="margin:0;">লেখক: {author_name}</h4>
            <p style="margin:4px 0 0;">{author_bio} | <a href="mailto:info@yourblog.com">info@yourblog.com</a></p>
        </div>
    </div>

    <hr>
    <p><strong>আরও পড়ুন:</strong> <a href="/guest-post">গেস্ট পোস্ট গাইডলাইন</a> | <a href="/mobile-tips">মোবাইল টিপস</a></p>

    <footer>
        © {year} BanglaGuide24 — সর্বস্বত্ব সংরক্ষিত
    </footer>

</body>
</html>
"""

# ============================================================
# হেল্পার ফাংশন
# ============================================================
def generate_fallback_data(lang):
    """AI-মুক্ত ফ্যালব্যাক (যখন API কাজ করবে না)"""
    if lang == 'bn':
        return {
            "ai_summary": "আমার নিজের অভিজ্ঞতা থেকে বলছি, এই টিপসগুলো সত্যিই কাজ করে।",
            "tips": [{"title": f"টিপ {i+1}: একটি কার্যকরী পদ্ধতি", "description": f"আমি নিজেও এই পদ্ধতি ব্যবহার করেছি এবং দেখেছি এটি সত্যিই কাজ করে। প্রতিদিনের ব্যস্ত জীবনে এটি খুবই সহজ একটি উপায় যা আপনার ফোনের ব্যাটারি লাইফ উল্লেখযোগ্যভাবে বাড়িয়ে দিতে পারে।"} for i in range(10)],
            "myth_facts": [{"myth": "ফোন সারারাত চার্জে রাখলে ব্যাটারি নষ্ট হয়", "fact": "আধুনিক ফোনে ওভারচার্জ প্রটেকশন থাকে, তবে ১০০% চার্জে রেখে দিলে ব্যাটারির চাপ বাড়ে।"}],
            "faq": [{"question": "ফোন সারারাত চার্জে রাখা কি ঠিক?", "answer": "আধুনিক ফোনে ওভারচার্জ প্রটেকশন আছে, কিন্তু ১০০% চার্জে রেখে দিলে ব্যাটারির চাপ বাড়ে।"}],
            "conclusion": "সবশেষে বলবো, এই টিপসগুলো শুধু তত্ত্ব নয়—আমি নিজে এগুলো অনুসরণ করেছি এবং ফল পেয়েছি।"
        }
    else:
        return {
            "ai_summary": "From my own experience, these tips really work.",
            "tips": [{"title": f"Tip {i+1}: An effective method", "description": "I personally used this method and saw great results."} for i in range(10)],
            "myth_facts": [{"myth": "Charging overnight ruins battery", "fact": "Modern phones have overcharge protection, but keeping at 100% adds stress."}],
            "faq": [{"question": "Is it okay to charge overnight?", "answer": "Yes, but it's better to keep between 20-80%."}],
            "conclusion": "In conclusion, these tips are practical and effective."
        }

def parse_ai_output(text, lang):
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != 0:
            json_str = text[start:end]
            return json.loads(json_str)
        else:
            return json.loads(text)
    except:
        return generate_fallback_data(lang)

def generate_blog_html(title, lang, data):
    """পূর্ণ SEO-অপটিমাইজড HTML তৈরি করে"""
    # স্লাগ তৈরি
    slug = title.replace(' ', '-').lower()[:50]

    # টিপস ও সূচিপত্র
    tips_html = ""
    toc_items = []
    for i, tip in enumerate(data['tips'], 1):
        tip_id = f"tip{i}"
        tips_html += f"""
    <div class="tip-card" id="{tip_id}">
        <h3>{i}. {tip['title']}</h3>
        <p>{tip['description']}</p>
    </div>
"""
        toc_items.append(f'<li><a href="#{tip_id}">🌞 {i}. {tip["title"]}</a></li>')
    toc_list = "\n".join(toc_items)

    # FAQ
    faq_items = ""
    for faq in data['faq']:
        faq_items += f"""
    <div class="faq-item"><strong>প্রশ্ন: {faq['question']}</strong><p>উত্তর: {faq['answer']}</p></div>
"""

    # মিথ-ফ্যাক্ট
    myth_fact_html = ""
    for mf in data['myth_facts']:
        myth_fact_html += f"<li><strong>মিথ:</strong> \"{mf['myth']}\" <strong>সত্য:</strong> {mf['fact']}</li>\n"

    # FAQ JSON (স্কিমার জন্য)
    faq_json = json.dumps([
        {"@type": "Question", "name": f"{faq['question']}",
         "acceptedAnswer": {"@type": "Answer", "text": f"{faq['answer']}"}}
        for faq in data['faq']
    ], ensure_ascii=False)

    now = time.strftime("%Y-%m-%dT%H:%M:%S+06:00")
    display_date = time.strftime("%d %B, %Y")
    year = time.strftime("%Y")

    # ডেটা প্রস্তুত
    placeholders = {
        "title": title,
        "slug": slug,
        "headline": title,
        "description": data['ai_summary'][:160],
        "ai_summary": data['ai_summary'],
        "publish_date": display_date,
        "update_date": display_date,
        "year": year,
        "author_name": "BanglaGuide24 টিম" if lang == 'bn' else "BanglaGuide24 Team",
        "author_bio": "প্রযুক্তি ও মোবাইল বিশেষজ্ঞ | ১০+ বছর অভিজ্ঞতা" if lang == 'bn' else "Technology & Mobile Expert | 10+ years experience",
        "toc_list": toc_list,
        "tips_html": tips_html,
        "myth_fact_html": myth_fact_html,
        "faq_items": faq_items,
        "faq_json": faq_json,
        "conclusion": data['conclusion']
    }

    return BLOG_TEMPLATE.format(**placeholders)

# ============================================================
# API প্রম্পট জেনারেট
# ============================================================
def generate_prompt(title, lang):
    if lang == 'bn':
        return f"""
আপনি একজন অভিজ্ঞ ব্লগার। নিচের টাইটেলের ওপর ১০টি টিপস সম্বলিত একটি ব্লগ পোস্ট তৈরি করুন (২০০০+ শব্দ)।

টাইটেল: "{title}"

আউটপুট হবে JSON:
{{
  "ai_summary": "সংক্ষিপ্ত সারাংশ (গল্প দিয়ে শুরু)",
  "tips": [{{"title": "টিপ ১: শিরোনাম", "description": "বিস্তারিত (১৫০-২০০ শব্দ)"}}, ...],
  "myth_facts": [{{"myth": "ভুল ধারণা", "fact": "সত্য"}}, ...],
  "faq": [{{"question": "প্রশ্ন", "answer": "উত্তর"}}, ...],
  "conclusion": "উপসংহার"
}}
শুধু JSON দিন।
"""
    else:
        return f"""
Write a blog post with 10 tips (2000+ words) on: "{title}".

Output JSON:
{{
  "ai_summary": "Brief intro with a story",
  "tips": [{{"title": "Tip 1: Title", "description": "Detailed description"}}, ...],
  "myth_facts": [{{"myth": "Myth", "fact": "Fact"}}, ...],
  "faq": [{{"question": "Q", "answer": "A"}}, ...],
  "conclusion": "Conclusion"
}}
Output only JSON.
"""

# ============================================================
# রাউট
# ============================================================
@app.route('/')
def home():
    return render_template_string(UI_HTML)

@app.route('/generate_post', methods=['POST'])
def generate_post():
    data = request.get_json()
    title = data.get('title', '').strip()
    lang = data.get('lang', 'bn')
    if not title:
        return jsonify({"error": "টাইটেল খালি"}), 400

    prompt = generate_prompt(title, lang)
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 2000,
            "temperature": 0.8,
            "return_full_text": False
        }
    }
    headers = {"Content-Type": "application/json"}

    for model_url in MODELS:
        try:
            response = requests.post(model_url, headers=headers, json=payload, timeout=50)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and 'generated_text' in result[0]:
                    text = result[0]['generated_text']
                elif isinstance(result, dict) and 'generated_text' in result:
                    text = result['generated_text']
                else:
                    text = str(result)
                parsed = parse_ai_output(text, lang)
                html = generate_blog_html(title, lang, parsed)
                return jsonify({"html": html})
        except Exception as e:
            print(f"Model failed: {e}")
            continue

    # ফ্যালব্যাক
    fallback = generate_fallback_data(lang)
    html = generate_blog_html(title, lang, fallback)
    return jsonify({"html": html}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
