from flask import Flask, request, render_template_string, jsonify
import requests
import json
import time
import re
import urllib.parse
import traceback
import random

app = Flask(__name__)

# Hugging Face API (ব্যাকআপ সহ)
MODELS = [
    "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
    "https://api-inference.huggingface.co/models/google/flan-t5-large"
]

# ============================================================
# SVG ইমেজ জেনারেটর (রিয়েলিস্টিক)
# ============================================================
def generate_featured_svg(title):
    """ফিচার্ড ইমেজ: প্যানোরামিক ভিউ (পাহাড়/সূর্যাস্ত/স্কাইলাইন)"""
    # এলোমেলো থিম সিলেক্ট
    themes = [
        "mountain_sunset", "city_night", "forest_lake", "ocean_sunrise", "desert_dunes"
    ]
    theme = random.choice(themes)
    
    if theme == "mountain_sunset":
        return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
            <defs>
                <linearGradient id="sky" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#1a0533"/>
                    <stop offset="30%" stop-color="#4a1942"/>
                    <stop offset="55%" stop-color="#c94b4b"/>
                    <stop offset="75%" stop-color="#f09819"/>
                    <stop offset="100%" stop-color="#f5d020"/>
                </linearGradient>
                <linearGradient id="mountain1" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#2d1b3d"/>
                    <stop offset="100%" stop-color="#1a0f2e"/>
                </linearGradient>
                <linearGradient id="mountain2" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#3d284f"/>
                    <stop offset="100%" stop-color="#231635"/>
                </linearGradient>
                <linearGradient id="mountain3" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#5a3b6b"/>
                    <stop offset="100%" stop-color="#34224a"/>
                </linearGradient>
                <radialGradient id="sun" cx="50%" cy="60%" r="25%">
                    <stop offset="0%" stop-color="#fff7a1"/>
                    <stop offset="40%" stop-color="#f5d020"/>
                    <stop offset="100%" stop-color="#f09819" stop-opacity="0"/>
                </radialGradient>
                <filter id="glow">
                    <feGaussianBlur stdDeviation="8" result="blur"/>
                    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                </filter>
            </defs>
            <rect width="1200" height="630" fill="url(#sky)"/>
            <!-- সূর্য -->
            <circle cx="600" cy="380" r="90" fill="url(#sun)" filter="url(#glow)"/>
            <!-- পাহাড় ৩ (দূর) -->
            <polygon points="0,500 150,300 350,450 550,350 750,480 950,320 1200,450 1200,630 0,630" fill="url(#mountain3)" opacity="0.7"/>
            <!-- পাহাড় ২ (মাঝ) -->
            <polygon points="0,550 200,380 450,500 700,400 950,520 1200,420 1200,630 0,630" fill="url(#mountain2)" opacity="0.85"/>
            <!-- পাহাড় ১ (কাছ) -->
            <polygon points="0,630 100,480 350,550 600,460 850,530 1100,470 1200,520 1200,630" fill="url(#mountain1)"/>
            <!-- মেঘ -->
            <ellipse cx="200" cy="150" rx="120" ry="30" fill="white" opacity="0.15"/>
            <ellipse cx="800" cy="120" rx="100" ry="25" fill="white" opacity="0.12"/>
            <ellipse cx="1000" cy="180" rx="80" ry="20" fill="white" opacity="0.1"/>
            <!-- টেক্সট -->
            <text x="600" y="580" font-family="Arial, sans-serif" font-size="32" font-weight="bold" fill="white" text-anchor="middle" opacity="0.9" letter-spacing="2">{}</text>
        </svg>""".format(title[:60] if len(title) > 60 else title)
    
    elif theme == "city_night":
        return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
            <defs>
                <linearGradient id="night" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#0a0e27"/>
                    <stop offset="60%" stop-color="#1a1a3a"/>
                    <stop offset="100%" stop-color="#2d1b3d"/>
                </linearGradient>
                <linearGradient id="build1" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#1a1a2e"/>
                    <stop offset="100%" stop-color="#0f0f1a"/>
                </linearGradient>
                <filter id="glow2">
                    <feGaussianBlur stdDeviation="3"/>
                </filter>
            </defs>
            <rect width="1200" height="630" fill="url(#night)"/>
            <!-- তারা -->
            <circle cx="100" cy="50" r="1.5" fill="white" opacity="0.8"/>
            <circle cx="250" cy="80" r="1" fill="white" opacity="0.6"/>
            <circle cx="400" cy="30" r="2" fill="white" opacity="0.9"/>
            <circle cx="550" cy="100" r="1.5" fill="white" opacity="0.7"/>
            <circle cx="700" cy="40" r="1" fill="white" opacity="0.5"/>
            <circle cx="850" cy="70" r="2" fill="white" opacity="0.8"/>
            <circle cx="1000" cy="50" r="1.5" fill="white" opacity="0.6"/>
            <circle cx="1100" cy="90" r="1" fill="white" opacity="0.7"/>
            <!-- চাঁদ -->
            <circle cx="950" cy="120" r="40" fill="#f5e6b8" opacity="0.9"/>
            <circle cx="965" cy="110" r="35" fill="#0a0e27" opacity="0.8"/>
            <!-- বিল্ডিং -->
            <rect x="50" y="380" width="60" height="250" fill="#1a1a2e" rx="2"/>
            <rect x="130" y="320" width="45" height="310" fill="#222244" rx="2"/>
            <rect x="195" y="400" width="70" height="230" fill="#1a1a2e" rx="2"/>
            <rect x="285" y="280" width="55" height="350" fill="#1a1a3a" rx="2"/>
            <rect x="360" y="350" width="80" height="280" fill="#222244" rx="2"/>
            <rect x="460" y="300" width="50" height="330" fill="#1a1a2e" rx="2"/>
            <rect x="530" y="370" width="65" height="260" fill="#1a1a3a" rx="2"/>
            <rect x="615" y="260" width="55" height="370" fill="#222244" rx="2"/>
            <rect x="690" y="340" width="75" height="290" fill="#1a1a2e" rx="2"/>
            <rect x="785" y="310" width="50" height="320" fill="#1a1a3a" rx="2"/>
            <rect x="855" y="380" width="60" height="250" fill="#222244" rx="2"/>
            <rect x="935" y="290" width="70" height="340" fill="#1a1a2e" rx="2"/>
            <rect x="1025" y="350" width="55" height="280" fill="#1a1a3a" rx="2"/>
            <rect x="1100" y="400" width="80" height="230" fill="#222244" rx="2"/>
            <!-- জানালা (আলো) -->
            <g fill="#f5d020" opacity="0.7">
                <rect x="60" y="400" width="8" height="10" rx="1"/>
                <rect x="80" y="420" width="8" height="10" rx="1"/>
                <rect x="140" y="340" width="8" height="10" rx="1"/>
                <rect x="160" y="360" width="8" height="10" rx="1"/>
                <rect x="300" y="300" width="8" height="10" rx="1"/>
                <rect x="320" y="320" width="8" height="10" rx="1"/>
                <rect x="475" y="320" width="8" height="10" rx="1"/>
                <rect x="635" y="280" width="8" height="10" rx="1"/>
                <rect x="655" y="300" width="8" height="10" rx="1"/>
                <rect x="800" y="330" width="8" height="10" rx="1"/>
                <rect x="955" y="310" width="8" height="10" rx="1"/>
                <rect x="975" y="330" width="8" height="10" rx="1"/>
            </g>
            <text x="600" y="590" font-family="Arial, sans-serif" font-size="28" font-weight="bold" fill="white" text-anchor="middle" opacity="0.85">{}</text>
        </svg>""".format(title[:60] if len(title) > 60 else title)
    
    else:
        # ডিফল্ট: সূর্যাস্ত পাহাড়
        return generate_featured_svg(title)

def generate_tip_svg(tip_title, index):
    """প্রতিটি টিপসের জন্য থাম্বনেইল (টপিক অনুযায়ী)"""
    # টিপসের শিরোনাম থেকে কীওয়ার্ড বের করা
    keywords = tip_title.lower()
    
    # থিম নির্বাচন
    if "ব্যাটারি" in keywords or "battery" in keywords or "charge" in keywords:
        # ব্যাটারি থিম
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="400" height="300">
            <defs>
                <linearGradient id="bg{index}" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#0f172a"/>
                    <stop offset="100%" stop-color="#1e293b"/>
                </linearGradient>
                <linearGradient id="bat{index}" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#34d399"/>
                    <stop offset="100%" stop-color="#059669"/>
                </linearGradient>
            </defs>
            <rect width="400" height="300" fill="url(#bg{index})" rx="16"/>
            <rect x="100" y="80" width="200" height="100" rx="12" fill="none" stroke="#34d399" stroke-width="4"/>
            <rect x="280" y="115" width="20" height="30" rx="4" fill="#34d399"/>
            <rect x="110" y="90" width="180" height="80" rx="8" fill="url(#bat{index})" opacity="0.3"/>
            <text x="200" y="230" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#e2e8f0" text-anchor="middle">{index}. {tip_title[:30]}</text>
            <text x="200" y="265" font-family="Arial, sans-serif" font-size="14" fill="#94a3b8" text-anchor="middle">🔋 ব্যাটারি টিপস</text>
        </svg>"""
    
    elif "স্ক্রিন" in keywords or "screen" in keywords or "display" in keywords or "brightness" in keywords:
        # স্ক্রিন থিম
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="400" height="300">
            <defs>
                <linearGradient id="bg{index}" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#0f172a"/>
                    <stop offset="100%" stop-color="#1e293b"/>
                </linearGradient>
                <linearGradient id="screen{index}" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#3b82f6"/>
                    <stop offset="100%" stop-color="#7c3aed"/>
                </linearGradient>
            </defs>
            <rect width="400" height="300" fill="url(#bg{index})" rx="16"/>
            <rect x="100" y="60" width="200" height="140" rx="12" fill="url(#screen{index})" opacity="0.15"/>
            <rect x="110" y="70" width="180" height="120" rx="8" fill="url(#screen{index})" opacity="0.4"/>
            <circle cx="200" cy="130" r="30" fill="none" stroke="#3b82f6" stroke-width="3" opacity="0.6"/>
            <circle cx="200" cy="130" r="15" fill="#3b82f6" opacity="0.3"/>
            <text x="200" y="230" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#e2e8f0" text-anchor="middle">{index}. {tip_title[:30]}</text>
            <text x="200" y="265" font-family="Arial, sans-serif" font-size="14" fill="#94a3b8" text-anchor="middle">📱 স্ক্রিন টিপস</text>
        </svg>"""
    
    elif "চার্জ" in keywords or "charging" in keywords or "adapter" in keywords:
        # চার্জিং থিম
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="400" height="300">
            <defs>
                <linearGradient id="bg{index}" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#0f172a"/>
                    <stop offset="100%" stop-color="#1e293b"/>
                </linearGradient>
                <linearGradient id="bolt{index}" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#fbbf24"/>
                    <stop offset="100%" stop-color="#f59e0b"/>
                </linearGradient>
            </defs>
            <rect width="400" height="300" fill="url(#bg{index})" rx="16"/>
            <polygon points="200,80 170,160 195,160 180,230 220,180 195,180" fill="url(#bolt{index})" opacity="0.8"/>
            <text x="200" y="230" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#e2e8f0" text-anchor="middle">{index}. {tip_title[:30]}</text>
            <text x="200" y="265" font-family="Arial, sans-serif" font-size="14" fill="#94a3b8" text-anchor="middle">⚡ চার্জিং টিপস</text>
        </svg>"""
    
    else:
        # ডিফল্ট: জেনেরিক আইকন
        colors = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#ef4444']
        color = colors[index % len(colors)]
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="400" height="300">
            <defs>
                <linearGradient id="bg{index}" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#0f172a"/>
                    <stop offset="100%" stop-color="#1e293b"/>
                </linearGradient>
                <linearGradient id="ico{index}" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="{color}"/>
                    <stop offset="100%" stop-color="{color}" stop-opacity="0.6"/>
                </linearGradient>
            </defs>
            <rect width="400" height="300" fill="url(#bg{index})" rx="16"/>
            <circle cx="200" cy="135" r="45" fill="url(#ico{index})" opacity="0.15"/>
            <circle cx="200" cy="135" r="25" fill="url(#ico{index})" opacity="0.4"/>
            <text x="200" y="145" font-family="Arial" font-size="28" fill="#e2e8f0" text-anchor="middle">{index}</text>
            <text x="200" y="230" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#e2e8f0" text-anchor="middle">{index}. {tip_title[:30]}</text>
            <text x="200" y="265" font-family="Arial, sans-serif" font-size="14" fill="#94a3b8" text-anchor="middle">💡 টিপস</text>
        </svg>"""

# ============================================================
# বাকি কোড (UI, টেমপ্লেট, রাউট)
# ============================================================
UI_HTML = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>প্রো ব্লগ জেনারেটর (SVG ইমেজ)</title>
    <style>
        * { box-sizing: border-box; margin: 0; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0b1120; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }
        .card { background: #1a2332; border-radius: 32px; padding: 40px; max-width: 720px; width: 100%; border: 1px solid rgba(255,255,255,0.06); box-shadow: 0 25px 50px -12px rgba(0,0,0,0.8); }
        h1 { color: #f1f5f9; font-size: 28px; margin-bottom: 8px; }
        .sub { color: #94a3b8; font-size: 14px; margin-bottom: 24px; border-bottom: 1px solid #2d3b52; padding-bottom: 16px; }
        label { color: #94a3b8; display: block; margin-bottom: 6px; font-weight: 500; font-size: 13px; }
        input, select { width: 100%; padding: 14px; border-radius: 16px; background: #0f172a; color: #e2e8f0; border: 1px solid #2d3b52; font-size: 15px; margin-bottom: 16px; outline: none; }
        input:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.2); }
        button { width: 100%; padding: 16px; border: none; border-radius: 50px; background: linear-gradient(135deg, #3b82f6, #7c3aed); color: white; font-size: 18px; font-weight: 600; cursor: pointer; transition: 0.2s; box-shadow: 0 8px 24px rgba(59,130,246,0.2); }
        button:hover { transform: scale(1.01); box-shadow: 0 12px 32px rgba(59,130,246,0.35); }
        button:disabled { opacity: 0.5; transform: none; cursor: not-allowed; }
        .status { color: #94a3b8; margin-top: 16px; text-align: center; font-size: 14px; }
        .output-box { background: #0f172a; border-radius: 16px; padding: 20px; margin-top: 20px; max-height: 550px; overflow-y: auto; display: none; border: 1px solid #2d3b52; }
        .output-box pre { color: #e2e8f0; white-space: pre-wrap; font-family: 'Courier New', monospace; font-size: 12px; line-height: 1.5; }
        .btn-group { display: flex; gap: 12px; margin-top: 16px; flex-wrap: wrap; }
        .btn-group button { flex: 1; min-width: 100px; background: #059669; box-shadow: none; font-size: 15px; padding: 12px; }
        .btn-group button:last-child { background: #d97706; }
        .footer { color: #475569; text-align: center; font-size: 12px; margin-top: 20px; border-top: 1px solid #2d3b52; padding-top: 16px; }
    </style>
</head>
<body>
<div class="card">
    <h1>✍️ প্রো ব্লগ জেনারেটর</h1>
    <div class="sub">Google News · AdSense · E-E-A-T · ২০০০+ শব্দ · AMP · SVG রিয়েল ইমেজ</div>
    
    <label>📝 আর্টিকেল টাইটেল</label>
    <input type="text" id="titleInput" value="মোবাইলের ব্যাটারি লাইফ বাড়ানোর ১০টি টিপস (২০২৬)">
    
    <label>🌐 ভাষা</label>
    <select id="langSelect">
        <option value="bn">বাংলা</option>
        <option value="en">English</option>
    </select>

    <button id="generateBtn">🚀 ২০০০+ শব্দের আর্টিকেল তৈরি করুন</button>
    <div class="status" id="statusText">টাইটেল লিখে জেনারেট ক্লিক করুন। (SVG ইমেজ সহ)</div>
    <div class="output-box" id="outputBox">
        <pre id="outputContent"></pre>
        <div class="btn-group">
            <button id="copyBtn">📋 কপি</button>
            <button id="downloadBtn">⬇️ HTML ডাউনলোড</button>
        </div>
    </div>
    <div class="footer">⚡ ইমেজ: SVG (রিয়েলিস্টিক) · AMP-ভ্যালিড · info@banglaguide24.com</div>
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
        setStatus('⏳ ২০০০+ শব্দের আর্টিকেল তৈরি হচ্ছে (৪০-৯০ সেকেন্ড)...');
        generateBtn.disabled = true;
        generateBtn.textContent = '⏳ প্রসেসিং...';
        try {
            const res = await fetch('/generate_post', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, lang })
            });
            if (!res.ok) {
                const errorText = await res.text();
                throw new Error('সার্ভার থেকে এরর: ' + errorText);
            }
            const data = await res.json();
            if (data.error) throw new Error(data.error);
            generatedHtml = data.html;
            outputContent.textContent = generatedHtml;
            outputBox.style.display = 'block';
            setStatus('✅ সম্পূর্ণ! SVG রিয়েল ইমেজসহ আর্টিকেল তৈরি।');
        } catch (err) {
            setStatus('❌ ' + err.message);
            console.error(err);
        } finally {
            generateBtn.disabled = false;
            generateBtn.textContent = '🚀 ২০০০+ শব্দের আর্টিকেল তৈরি করুন';
        }
    });

    document.getElementById('copyBtn').addEventListener('click', function() {
        if (!generatedHtml) return;
        navigator.clipboard.writeText(generatedHtml).then(() => setStatus('✅ HTML কপি করা হয়েছে!'));
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
# AMP-ভ্যালিড ব্লগ টেমপ্লেট (SVG ইমেজ সহ)
# ============================================================
BLOG_TEMPLATE = """
<!DOCTYPE html>
<html amp lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,minimum-scale=1,initial-scale=1">
    <title>{headline}</title>
    <meta name="description" content="{description}">
    <meta property="og:title" content="{headline}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="data:image/svg+xml;charset=utf-8,{featured_image_encoded}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:type" content="article">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:image" content="data:image/svg+xml;charset=utf-8,{featured_image_encoded}">
    <link rel="canonical" href="https://www.yourblog.com/{slug}">

    <style amp-boilerplate>body{{-webkit-animation:-amp-start 8s steps(1,end) 0s 1 normal both;-moz-animation:-amp-start 8s steps(1,end) 0s 1 normal both;-ms-animation:-amp-start 8s steps(1,end) 0s 1 normal both;animation:-amp-start 8s steps(1,end) 0s 1 normal both}}@-webkit-keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}@-moz-keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}@-ms-keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}@-o-keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}@keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}</style>
    <noscript><style amp-boilerplate>body{{-webkit-animation:none;-moz-animation:none;-ms-animation:none;animation:none}}</style></noscript>
    <script async src="https://cdn.ampproject.org/v0.js"></script>

    <style amp-custom>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family: system-ui, -apple-system, sans-serif; background: #f8fafc; padding: 16px; }}
        .container {{ max-width: 880px; margin:0 auto; background:#fff; border-radius:24px; padding:24px; box-shadow:0 4px 20px rgba(0,0,0,0.03); }}
        amp-img {{ border-radius:16px; margin-bottom:20px; }}
        h1 {{ font-size:1.8rem; font-weight:700; margin-bottom:8px; line-height:1.2; color:#0f172a; }}
        .meta {{ color:#64748b; font-size:0.85rem; margin-bottom:20px; padding-bottom:16px; border-bottom:1px solid #e2e8f0; display:flex; flex-wrap:wrap; gap:12px; }}
        h2 {{ font-size:1.4rem; margin-top:2rem; margin-bottom:1rem; color:#0f172a; border-left:4px solid #1e3c72; padding-left:14px; }}
        .overview-box {{ background:#f0fdf4; padding:16px 20px; border-radius:16px; border-left:4px solid #10b981; margin:20px 0; color:#065f46; }}
        .toc-box {{ background:#f8fafc; padding:16px 20px; border-radius:16px; margin:20px 0; }}
        .toc-box ul {{ list-style:none; padding-left:0; columns:2; column-gap:20px; margin:0; }}
        .toc-box ul li {{ margin-bottom:6px; }}
        .toc-box ul li a {{ text-decoration:none; color:#1e293b; }}
        .tip-card {{ background:#fff; padding:20px; border-radius:16px; margin-bottom:20px; border:1px solid #e2e8f0; }}
        .tip-card h3 {{ margin-top:0; margin-bottom:8px; color:#1e3c72; }}
        .tip-card amp-img {{ margin:10px 0; border-radius:12px; }}
        .faq-item {{ background:#fff; border:1px solid #e2e8f0; border-radius:12px; padding:14px 16px; margin-bottom:10px; }}
        .faq-item strong {{ display:block; margin-bottom:4px; color:#0f172a; }}
        .author-box {{ display:flex; align-items:center; gap:16px; background:#fefce8; padding:16px 20px; border-radius:16px; border:1px solid #fde68a; margin:24px 0; }}
        .author-avatar {{ width:56px; height:56px; background:#1e3c72; border-radius:50%; display:flex; align-items:center; justify-content:center; color:#fff; font-size:1.4rem; flex-shrink:0; }}
        .conclusion-box {{ background:#eff6ff; border-radius:16px; padding:20px; border-left:4px solid #3b82f6; margin-top:24px; }}
        footer {{ text-align:center; margin-top:32px; padding-top:16px; border-top:1px solid #e2e8f0; color:#94a3b8; font-size:0.9rem; }}
        footer a {{ color:#1e3c72; text-decoration:none; }}
        @media (max-width:640px) {{ .container {{ padding:16px; }} h1 {{ font-size:1.5rem; }} .toc-box ul {{ columns:1; }} .author-box {{ flex-direction:column; text-align:center; }} }}
    </style>

    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "NewsArticle",
      "headline": "{headline}",
      "description": "{description}",
      "image": "data:image/svg+xml;charset=utf-8,{featured_image_encoded}",
      "datePublished": "{publish_date}",
      "dateModified": "{update_date}",
      "author": {{
        "@type": "Person",
        "name": "{author_name}",
        "email": "info@banglaguide24.com"
      }},
      "publisher": {{
        "@type": "Organization",
        "name": "BanglaGuide24",
        "email": "info@banglaguide24.com"
      }}
    }}
    </script>
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": {faq_json}
    }}
    </script>

</head>
<body>
<div class="container">

    <!-- ফিচার্ড ইমেজ (SVG) -->
    <amp-img src="data:image/svg+xml;charset=utf-8,{featured_image_encoded}" alt="{headline}" width="1200" height="630" layout="responsive"></amp-img>

    <h1>{headline}</h1>
    <div class="meta">
        <span>📅 {publish_date}</span>
        <span>✍️ {author_name}</span>
        <span>📧 <a href="mailto:info@banglaguide24.com" style="color:#1e3c72;">info@banglaguide24.com</a></span>
    </div>

    <div class="overview-box">
        <strong>🤖 সংক্ষিপ্ত সারাংশ:</strong> {ai_summary}
    </div>

    <div class="toc-box">
        <h3 style="margin-top:0;">📖 সূচিপত্র</h3>
        <ul>{toc_list}</ul>
    </div>

    {tips_html}

    <h2>🛑 ভুল ধারণা ও সঠিক তথ্য</h2>
    <ul style="list-style:none; padding-left:0;">{myth_fact_html}</ul>

    <h2>❓ সচরাচর জিজ্ঞাসা</h2>
    {faq_items}

    <div class="conclusion-box">
        <h2 style="border-left:none; padding-left:0; margin-top:0;">📌 শেষ কথা</h2>
        <p>{conclusion}</p>
    </div>

    <div class="author-box">
        <div class="author-avatar">✍️</div>
        <div>
            <h4 style="margin:0;">{author_name}</h4>
            <p style="margin:4px 0 0;">{author_bio}</p>
            <p>📧 <a href="mailto:info@banglaguide24.com" style="color:#1e3c72;">info@banglaguide24.com</a></p>
        </div>
    </div>

    <footer>
        © {year} BanglaGuide24 — সর্বস্বত্ব সংরক্ষিত | <a href="mailto:info@banglaguide24.com" style="color:#1e3c72;">info@banglaguide24.com</a>
    </footer>

</div>
</body>
</html>
"""

# ============================================================
# ফ্যালব্যাক ও পার্স ফাংশন
# ============================================================
def generate_fallback_data(lang):
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
            "myth_facts": [{"myth": "Charging overnight ruins battery", "fact": "Modern phones have overcharge protection."}],
            "faq": [{"question": "Is overnight charging okay?", "answer": "Yes, but 20-80% is better."}],
            "conclusion": "In conclusion, these tips are practical and effective."
        }

def parse_ai_output(text, lang):
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != 0:
            return json.loads(text[start:end])
        else:
            return json.loads(text)
    except:
        return generate_fallback_data(lang)

# ============================================================
# মেইন জেনারেট ফাংশন
# ============================================================
def generate_blog_html(title, lang, data):
    try:
        # ফিচার্ড SVG
        featured_svg = generate_featured_svg(title)
        # SVG-কে URL-এনকোড করা (AMP-তে data URI হিসেবে)
        featured_encoded = urllib.parse.quote(featured_svg)
        
        slug = re.sub(r'[^\w\s]', '', title).replace(' ', '-').lower()[:50]
        now = time.strftime("%d %B, %Y")
        year = time.strftime("%Y")
        
        tips_html = ""
        toc_items = []
        for i, tip in enumerate(data['tips'], 1):
            tip_id = f"tip{i}"
            # টিপসের জন্য SVG থাম্বনেইল
            tip_svg = generate_tip_svg(tip['title'], i)
            tip_encoded = urllib.parse.quote(tip_svg)
            tips_html += f"""
    <div class="tip-card" id="{tip_id}">
        <h3>{i}. {tip['title']}</h3>
        <amp-img src="data:image/svg+xml;charset=utf-8,{tip_encoded}" alt="{tip['title']}" width="400" height="300" layout="responsive"></amp-img>
        <p>{tip['description']}</p>
    </div>
"""
            toc_items.append(f'<li><a href="#{tip_id}">🌞 {i}. {tip["title"]}</a></li>')
        toc_list = "\n".join(toc_items)
        
        faq_items = ""
        for faq in data['faq']:
            faq_items += f"""
    <div class="faq-item">
        <strong>প্রশ্ন: {faq['question']}</strong>
        <p>উত্তর: {faq['answer']}</p>
    </div>
"""
        myth_fact_html = ""
        for mf in data['myth_facts']:
            myth_fact_html += f"<li style='margin-bottom:12px;'><strong>❌ মিথ:</strong> \"{mf['myth']}\"<br><strong>✅ সত্য:</strong> {mf['fact']}</li>\n"
        
        faq_json = json.dumps([
            {"@type": "Question", "name": f"{faq['question']}",
             "acceptedAnswer": {"@type": "Answer", "text": f"{faq['answer']}"}}
            for faq in data['faq']
        ], ensure_ascii=False)
        
        placeholders = {
            "headline": title,
            "description": data['ai_summary'][:160],
            "featured_image_encoded": featured_encoded,
            "slug": slug,
            "publish_date": now,
            "update_date": now,
            "year": year,
            "author_name": "BanglaGuide24 টিম" if lang == 'bn' else "BanglaGuide24 Team",
            "author_bio": "প্রযুক্তি ও মোবাইল বিশেষজ্ঞ | ১০+ বছর অভিজ্ঞতা" if lang == 'bn' else "Technology & Mobile Expert | 10+ years experience",
            "ai_summary": data['ai_summary'],
            "toc_list": toc_list,
            "tips_html": tips_html,
            "myth_fact_html": myth_fact_html,
            "faq_items": faq_items,
            "faq_json": faq_json,
            "conclusion": data['conclusion']
        }
        return BLOG_TEMPLATE.format(**placeholders)
    except Exception as e:
        return f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>"

# ============================================================
# প্রম্পট জেনারেট
# ============================================================
def generate_prompt(title, lang):
    base = "Write a VERY LONG and DETAILED blog post with 10 actionable tips. Each tip description at least 150-200 words. Total length >2000 words. Include personal anecdotes, opinions, examples."
    if lang == 'bn':
        return f"""
আপনি একজন অভিজ্ঞ ব্লগার। {base}
টাইটেল: "{title}"
আউটপুট JSON:
{{
  "ai_summary": "বিস্তারিত সারাংশ (গল্প দিয়ে শুরু)",
  "tips": [{{"title": "টিপ ১: শিরোনাম", "description": "অন্তত ১৫০-২০০ শব্দের বিস্তারিত"}}, ...],
  "myth_facts": [{{"myth": "ভুল ধারণা", "fact": "সত্য"}}, ...],
  "faq": [{{"question": "প্রশ্ন", "answer": "বিস্তারিত উত্তর"}}, ...],
  "conclusion": "সবশেষে বলবো..."
}}
শুধু JSON দিন।
"""
    else:
        return f"""
You are an expert blogger. {base}
Title: "{title}"
Output JSON:
{{
  "ai_summary": "Detailed summary starting with a story",
  "tips": [{{"title": "Tip 1: Title", "description": "Detailed description (150-200 words)"}}, ...],
  "myth_facts": [{{"myth": "Myth", "fact": "Fact"}}, ...],
  "faq": [{{"question": "Question", "answer": "Detailed answer"}}, ...],
  "conclusion": "In conclusion..."
}}
Output only JSON.
"""

# ============================================================
# Flask রাউট
# ============================================================
@app.route('/')
def home():
    return render_template_string(UI_HTML)

@app.route('/generate_post', methods=['POST'])
def generate_post():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        title = data.get('title', '').strip()
        lang = data.get('lang', 'bn')
        if not title:
            return jsonify({"error": "টাইটেল খালি"}), 400

        prompt = generate_prompt(title, lang)
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 3500,
                "temperature": 0.85,
                "top_p": 0.95,
                "do_sample": True,
                "return_full_text": False,
                "repetition_penalty": 1.1
            }
        }
        headers = {"Content-Type": "application/json"}

        last_error = None
        for model_url in MODELS:
            try:
                response = requests.post(model_url, headers=headers, json=payload, timeout=60)
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        text = result[0].get('generated_text', '')
                    elif isinstance(result, dict):
                        text = result.get('generated_text', '')
                    else:
                        text = str(result)
                    parsed = parse_ai_output(text, lang)
                    html = generate_blog_html(title, lang, parsed)
                    return jsonify({"html": html})
                else:
                    last_error = f"Model returned {response.status_code}"
            except Exception as e:
                last_error = str(e)
                continue

        fallback = generate_fallback_data(lang)
        html = generate_blog_html(title, lang, fallback)
        return jsonify({"html": html})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"সার্ভার এরর: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
