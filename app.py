from flask import Flask, request, render_template_string, jsonify
import requests
import json
import time
import traceback

app = Flask(__name__)

# মডেল লিস্ট (শুধু ছোট মডেল ব্যবহার করছি, টাইমআউট কম)
MODELS = [
    "https://api-inference.huggingface.co/models/google/flan-t5-large",
    "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
]

# UI HTML (আগের মতোই, সংক্ষিপ্ততার জন্য এখানে ফুল UI দেওয়া হলো না—আপনি আগের UI থেকে কপি করুন)

UI_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>হিউম্যান-স্টাইল ব্লগ জেনারেটর</title>
    <style>
        /* আপনার আগের UI-র স্টাইল এখানে বসান */
        body { font-family: 'Segoe UI', sans-serif; background: #0b1120; padding: 20px; }
        .card { max-width: 700px; margin: auto; background: #1a2332; padding: 30px; border-radius: 20px; }
        /* ... বাকি স্টাইল */
    </style>
</head>
<body>
    <div class="card">
        <h1>হিউম্যান-স্টাইল জেনারেটর</h1>
        <input type="text" id="titleInput" placeholder="টাইটেল দিন" value="মোবাইলের ব্যাটারি লাইফ টিপস">
        <select id="langSelect"><option value="bn">বাংলা</option><option value="en">English</option></select>
        <button onclick="generate()">জেনারেট করুন</button>
        <pre id="output"></pre>
    </div>
    <script>
        async function generate() {
            const title = document.getElementById('titleInput').value;
            const lang = document.getElementById('langSelect').value;
            const res = await fetch('/generate_post', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({title, lang})
            });
            const data = await res.json();
            document.getElementById('output').textContent = data.html;
        }
    </script>
</body>
</html>
"""

# ব্লগ টেমপ্লেট (আগের মতো) — সংক্ষিপ্ত
BLOG_TEMPLATE = """
<!-- শুরু: {title} -->
<meta charset="UTF-8">
<meta name="description" content="{description}">
<h1>{headline}</h1>
<p>{ai_summary}</p>
<ul>{toc_list}</ul>
{content}
"""

def generate_fallback_data(lang):
    """AI-মুক্ত ফ্যালব্যাক ডেটা (সর্বদা কাজ করবে)"""
    if lang == 'bn':
        return {
            "ai_summary": "আমার নিজের অভিজ্ঞতা থেকে বলছি, এই টিপসগুলো সত্যিই কাজ করে।",
            "tips": [{"title": f"টিপ {i+1}: একটি কার্যকরী পদ্ধতি", "description": f"আমি নিজেও এই পদ্ধতি ব্যবহার করেছি এবং দেখেছি এটি সত্যিই কাজ করে। প্রতিদিনের ব্যস্ত জীবনে এটি খুবই সহজ একটি উপায় যা আপনার ফোনের ব্যাটারি লাইফ উল্লেখযোগ্যভাবে বাড়িয়ে দিতে পারে।"} for i in range(10)],
            "myth_facts": [{"myth": "মিথ", "fact": "সত্য"}],
            "faq": [{"question": "প্রশ্ন", "answer": "উত্তর"}],
            "conclusion": "সবশেষে বলবো, এই টিপসগুলো শুধু তত্ত্ব নয়—আমি নিজে এগুলো অনুসরণ করেছি এবং ফল পেয়েছি।"
        }
    else:
        return {
            "ai_summary": "From my own experience, these tips really work.",
            "tips": [{"title": f"Tip {i+1}: An effective method", "description": "I personally used this method and saw great results."} for i in range(10)],
            "myth_facts": [{"myth": "Myth", "fact": "Fact"}],
            "faq": [{"question": "Q", "answer": "A"}],
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
    # সহজ HTML জেনারেট
    tips_html = ""
    toc_items = ""
    for i, tip in enumerate(data['tips'], 1):
        tips_html += f"<h3>{i}. {tip['title']}</h3><p>{tip['description']}</p>"
        toc_items += f"<li>{i}. {tip['title']}</li>"
    faq_html = "".join([f"<p><b>{q['question']}</b><br>{q['answer']}</p>" for q in data['faq']])
    myth_html = "".join([f"<p><b>মিথ:</b> {m['myth']}<br><b>সত্য:</b> {m['fact']}</p>" for m in data['myth_facts']])
    return BLOG_TEMPLATE.format(
        title=title,
        description=data['ai_summary'][:150],
        headline=title,
        ai_summary=data['ai_summary'],
        toc_list=toc_items,
        content=tips_html + myth_html + faq_html + f"<p>{data['conclusion']}</p>"
    )

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

    prompt = f"Write a blog post with 10 tips about: {title}. Output JSON with fields: ai_summary, tips (array of title, description), myth_facts (array of myth, fact), faq (array of question, answer), conclusion."
    if lang == 'bn':
        prompt = f"বাংলায় একটি ব্লগ পোস্ট লিখুন: {title}। JSON আউটপুট দিন।"

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1500,
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
            print(f"Model {model_url} failed: {e}")
            continue

    # ফ্যালব্যাক
    fallback = generate_fallback_data(lang)
    html = generate_blog_html(title, lang, fallback)
    return jsonify({"html": html}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
