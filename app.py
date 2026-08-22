from flask import Flask, request, render_template_string, jsonify
import requests
import json
import time
import re
import urllib.parse
import traceback
import random

app = Flask(__name__)

MODELS = [
    "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
    "https://api-inference.huggingface.co/models/google/flan-t5-large"
]

# ============================================================
# স্মার্ট থিম ডিটেক্টর (কন্টেন্ট অ্যানালাইসিস)
# ============================================================
def detect_theme(text):
    """টেক্সট অ্যানালাইসিস করে থিম ডিটেক্ট করে"""
    text_lower = text.lower()
    
    themes = {
        'health': ['ডেঙ্গু', 'জ্বর', 'covid', 'করোনা', 'হাসপাতাল', 'চিকিৎসা', 'ওষুধ', 'সুস্থ', 'রোগ', 'প্রতিরোধ', 'টিকা', 'vaccine', 'doctor', 'health', 'fever', 'dengue', 'malaria', 'সর্দি', 'কাশি', 'মাথাব্যথা', 'পেটব্যথা', 'অসুস্থ'],
        'tech': ['মোবাইল', 'ফোন', 'ব্যাটারি', 'চার্জ', 'অ্যাপ', 'সফটওয়্যার', 'গ্যাজেট', 'কম্পিউটার', 'ল্যাপটপ', 'ডেটা', 'নেটওয়ার্ক', 'ওয়াইফাই', 'ব্লুটুথ', 'স্ক্রিন', 'ডিসপ্লে', 'র্যাম', 'স্টোরেজ', 'সিকিউরিটি', 'পাসওয়ার্ড', 'টেকনোলজি', 'স্মার্টফোন', 'ট্যাব', 'আইফোন', 'অ্যান্ড্রয়েড', 'সফটওয়্যার', 'হার্ডওয়্যার'],
        'food': ['রেসিপি', 'রান্না', 'খাবার', 'চিকেন', 'মাংস', 'তরকারি', 'ভর্তা', 'সালাদ', 'মিষ্টি', 'পিঠা', 'বিরিয়ানি', 'পোলাও', 'ভাজা', 'সুপ', 'নুডলস', 'পাস্তা', 'পিজা', 'বার্গার', 'স্যান্ডউইচ', 'ডেজার্ট', 'কেক', 'বেক', 'সস', 'মসলা', 'তেল', 'রান্নার', 'শাক', 'সবজি', 'ফল', 'ডিম', 'মাছ'],
        'education': ['শিক্ষা', 'পড়াশোনা', 'বিদ্যালয়', 'কলেজ', 'বিশ্ববিদ্যালয়', 'পাঠ্য', 'পাঠ', 'পরীক্ষা', 'ফলাফল', 'গ্রেড', 'ক্লাস', 'লেকচার', 'টিউটর', 'শিক্ষক', 'শিক্ষার্থী', 'বিজ্ঞান', 'গণিত', 'ইংরেজি', 'বাংলা', 'ইতিহাস', 'ভূগোল', 'রসায়ন', 'পদার্থবিজ্ঞান', 'জীববিজ্ঞান'],
        'business': ['ব্যবসা', 'মার্কেটিং', 'বিপণন', 'বিনিয়োগ', 'স্টার্টআপ', 'উদ্যোক্তা', 'কোম্পানি', 'ফ্রিল্যান্স', 'অনলাইন', 'ই-কমার্স', 'শপ', 'দোকান', 'পণ্য', 'সেবা', 'ক্রয়-বিক্রয়', 'লাভ', 'ক্ষতি', 'ঋণ', 'সঞ্চয়', 'টাকা', 'অর্থ', 'ব্যাংক', 'ইনভেস্ট', 'ফান্ড', 'ক্যাপিটাল'],
        'travel': ['ভ্রমণ', 'ট্রাভেল', 'পর্যটন', 'হোটেল', 'রিসোর্ট', 'বিমান', 'ট্রেন', 'বাস', 'নৌকা', 'সমুদ্র', 'পাহাড়', 'জঙ্গল', 'দ্বীপ', 'বিচ', 'সাফারি', 'এডভেঞ্চার', 'ক্যাম্পিং', 'হাইকিং', 'বুকিং', 'গাইড', 'স্যুটকেস', 'পাসপোর্ট', 'ভিসা'],
        'fashion': ['ফ্যাশন', 'পোশাক', 'শাড়ি', 'পাঞ্জাবি', 'জামা', 'প্যান্ট', 'শার্ট', 'টিশার্ট', 'জুতা', 'স্যান্ডেল', 'ব্যাগ', 'গহনা', 'মেকআপ', 'কসমেটিক্স', 'সাজগোজ', 'স্টাইল', 'ট্রেন্ড', 'র্যাম্প', 'ডিজাইনার', 'ব্র্যান্ড', 'লুক'],
        'sports': ['খেলা', 'ক্রিকেট', 'ফুটবল', 'টেনিস', 'ব্যাডমিন্টন', 'ভলিবল', 'বাস্কেটবল', 'অ্যাথলেটিক্স', 'অলিম্পিক', 'ওয়ার্ল্ডকাপ', 'প্রিমিয়ার', 'লিগ', 'ম্যাচ', 'দল', 'খেলোয়াড়', 'কোচ', 'স্টেডিয়াম', 'গোল', 'রান', 'উইকেট', 'সার্ভিস']
    }
    
    for theme_key, keywords in themes.items():
        for kw in keywords:
            if kw in text_lower:
                return theme_key
    return 'general'

def get_theme_palette(theme):
    """থিম অনুযায়ী কালার প্যালেট ও আইকন রিটার্ন করে"""
    palettes = {
        'health': {
            'bg': '#0f172a',
            'grad1': '#ef4444',
            'grad2': '#dc2626',
            'icon': '🏥',
            'label': 'স্বাস্থ্য',
            'featured': 'medical'
        },
        'tech': {
            'bg': '#0f172a',
            'grad1': '#3b82f6',
            'grad2': '#7c3aed',
            'icon': '💻',
            'label': 'প্রযুক্তি',
            'featured': 'tech'
        },
        'food': {
            'bg': '#0f172a',
            'grad1': '#f59e0b',
            'grad2': '#ef4444',
            'icon': '🍳',
            'label': 'রান্না',
            'featured': 'food'
        },
        'education': {
            'bg': '#0f172a',
            'grad1': '#10b981',
            'grad2': '#14b8a6',
            'icon': '📚',
            'label': 'শিক্ষা',
            'featured': 'education'
        },
        'business': {
            'bg': '#0f172a',
            'grad1': '#8b5cf6',
            'grad2': '#d946ef',
            'icon': '💼',
            'label': 'ব্যবসা',
            'featured': 'business'
        },
        'travel': {
            'bg': '#0f172a',
            'grad1': '#06b6d4',
            'grad2': '#3b82f6',
            'icon': '✈️',
            'label': 'ভ্রমণ',
            'featured': 'travel'
        },
        'fashion': {
            'bg': '#0f172a',
            'grad1': '#ec4899',
            'grad2': '#f43f5e',
            'icon': '👗',
            'label': 'ফ্যাশন',
            'featured': 'fashion'
        },
        'sports': {
            'bg': '#0f172a',
            'grad1': '#f97316',
            'grad2': '#ef4444',
            'icon': '⚽',
            'label': 'খেলা',
            'featured': 'sports'
        },
        'general': {
            'bg': '#0f172a',
            'grad1': '#64748b',
            'grad2': '#94a3b8',
            'icon': '📝',
            'label': 'জেনারেল',
            'featured': 'general'
        }
    }
    return palettes.get(theme, palettes['general'])

# ============================================================
# থিম-বেসড SVG জেনারেটর
# ============================================================
def generate_featured_svg(title, theme):
    """ফিচার্ড ইমেজ (থিম অনুযায়ী)"""
    palette = get_theme_palette(theme)
    
    # থিম অনুযায়ী আলাদা ডিজাইন
    if theme == 'health':
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630">
            <defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#0f172a"/><stop offset="100%" stop-color="#1e293b"/></linearGradient>
            <linearGradient id="g2" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stop-color="{palette['grad1']}"/><stop offset="100%" stop-color="{palette['grad2']}"/></linearGradient>
            <linearGradient id="g3" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="{palette['grad2']}" stop-opacity="0.3"/><stop offset="100%" stop-color="{palette['grad1']}" stop-opacity="0.1"/></linearGradient></defs>
            <rect width="1200" height="630" fill="url(#g)"/>
            <rect width="1200" height="630" fill="url(#g3)"/>
            <circle cx="600" cy="315" r="200" fill="{palette['grad1']}" opacity="0.05"/>
            <circle cx="600" cy="315" r="120" fill="{palette['grad1']}" opacity="0.08"/>
            <text x="600" y="250" font-family="Arial" font-size="80" text-anchor="middle" fill="white" opacity="0.9">{palette['icon']}</text>
            <text x="600" y="380" font-family="Arial, sans-serif" font-size="36" font-weight="bold" fill="white" text-anchor="middle" letter-spacing="1">{title[:80]}</text>
            <text x="600" y="440" font-family="Arial, sans-serif" font-size="18" fill="#94a3b8" text-anchor="middle">BanglaGuide24 · {palette['label']} বিষয়ক</text>
            <line x1="500" y1="470" x2="700" y2="470" stroke="{palette['grad1']}" stroke-width="3" opacity="0.6"/>
        </svg>"""
    else:
        # জেনেরিক সুন্দর ডিজাইন
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630">
            <defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#0f172a"/><stop offset="100%" stop-color="#1e293b"/></linearGradient>
            <linearGradient id="g2" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="{palette['grad1']}"/><stop offset="100%" stop-color="{palette['grad2']}"/></linearGradient>
            <linearGradient id="g3" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="{palette['grad2']}" stop-opacity="0.2"/><stop offset="100%" stop-color="{palette['grad1']}" stop-opacity="0.05"/></linearGradient></defs>
            <rect width="1200" height="630" fill="url(#g)"/>
            <circle cx="150" cy="150" r="300" fill="{palette['grad1']}" opacity="0.04"/>
            <circle cx="1050" cy="480" r="350" fill="{palette['grad2']}" opacity="0.04"/>
            <rect x="0" y="0" width="1200" height="630" fill="url(#g3)"/>
            <text x="600" y="250" font-family="Arial" font-size="70" text-anchor="middle" fill="white" opacity="0.8">{palette['icon']}</text>
            <text x="600" y="370" font-family="Arial, sans-serif" font-size="38" font-weight="bold" fill="white" text-anchor="middle" letter-spacing="1">{title[:80]}</text>
            <text x="600" y="430" font-family="Arial, sans-serif" font-size="18" fill="#94a3b8" text-anchor="middle">BanglaGuide24 · {palette['label']} গাইড</text>
            <rect x="520" y="460" width="160" height="4" rx="2" fill="{palette['grad1']}" opacity="0.6"/>
        </svg>"""
    return svg

def generate_tip_svg(tip_title, index, theme):
    """টিপসের জন্য থিম-বেসড থাম্বনেইল"""
    palette = get_theme_palette(theme)
    
    # থিম অনুযায়ী আইকন
    if theme == 'health':
        icon = '🩺'
        label = 'স্বাস্থ্য টিপস'
    elif theme == 'tech':
        icon = '💻'
        label = 'প্রযুক্তি টিপস'
    elif theme == 'food':
        icon = '🍳'
        label = 'রান্না টিপস'
    elif theme == 'education':
        icon = '📚'
        label = 'শিক্ষা টিপস'
    elif theme == 'business':
        icon = '💼'
        label = 'ব্যবসা টিপস'
    elif theme == 'travel':
        icon = '✈️'
        label = 'ভ্রমণ টিপস'
    elif theme == 'fashion':
        icon = '👗'
        label = 'ফ্যাশন টিপস'
    elif theme == 'sports':
        icon = '⚽'
        label = 'খেলা টিপস'
    else:
        icon = '📝'
        label = 'টিপস'
    
    # টিপসের শিরোনাম থেকে কীওয়ার্ড এক্সট্র্যাক্ট করে আরও কাস্টমাইজেশন
    title_lower = tip_title.lower()
    if 'ব্যাটারি' in title_lower or 'battery' in title_lower:
        icon = '🔋'
    elif 'স্ক্রিন' in title_lower or 'screen' in title_lower:
        icon = '☀️'
    elif 'অ্যাপ' in title_lower or 'app' in title_lower:
        icon = '📱'
    elif 'ওয়াইফাই' in title_lower or 'wifi' in title_lower:
        icon = '📶'
    elif 'চার্জ' in title_lower or 'charge' in title_lower:
        icon = '⚡'
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="400" height="300">
        <defs><linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#0f172a"/><stop offset="100%" stop-color="#1e293b"/></linearGradient>
        <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="{palette['grad1']}"/><stop offset="100%" stop-color="{palette['grad2']}"/></linearGradient></defs>
        <rect width="400" height="300" fill="url(#bg)" rx="16"/>
        <circle cx="200" cy="120" r="50" fill="url(#g)" opacity="0.12"/>
        <circle cx="200" cy="120" r="30" fill="url(#g)" opacity="0.25"/>
        <text x="200" y="135" font-family="Arial" font-size="40" text-anchor="middle" fill="white" opacity="0.9">{icon}</text>
        <text x="200" y="215" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="#e2e8f0" text-anchor="middle">{index}. {tip_title[:40]}</text>
        <text x="200" y="250" font-family="Arial, sans-serif" font-size="13" fill="#94a3b8" text-anchor="middle">{label}</text>
        <line x1="120" y1="270" x2="280" y2="270" stroke="{palette['grad1']}" stroke-width="2" opacity="0.4"/>
    </svg>"""
    return svg

# ============================================================
# ইউজার ইন্টারফেস (UI) — আগের মতোই
# ============================================================
UI_HTML = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>প্রো ব্লগ জেনারেটর (স্মার্ট থিম)</title>
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
    <div class="sub">Google News · AdSense · ২০০০+ শব্দ · স্মার্ট থিম-বেসড ইমেজ</div>
    
    <label>📝 আর্টিকেল টাইটেল</label>
    <input type="text" id="titleInput" value="ডেঙ্গু জ্বরের লক্ষণ ও প্রতিকার ২০২৬">
    
    <label>🌐 ভাষা</label>
    <select id="langSelect">
        <option value="bn">বাংলা</option>
        <option value="en">English</option>
    </select>

    <button id="generateBtn">🚀 ২০০০+ শব্দের আর্টিকেল তৈরি করুন</button>
    <div class="status" id="statusText">টাইটেল লিখে জেনারেট ক্লিক করুন। (কন্টেন্ট অনুযায়ী স্মার্ট থিম)</div>
    <div class="output-box" id="outputBox">
        <pre id="outputContent"></pre>
        <div class="btn-group">
            <button id="copyBtn">📋 কপি</button>
            <button id="downloadBtn">⬇️ HTML ডাউনলোড</button>
        </div>
    </div>
    <div class="footer">⚡ ইমেজ: কন্টেন্ট-ম্যাচিং স্মার্ট থিম · AMP-ভ্যালিড</div>
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
            setStatus('✅ সম্পূর্ণ! স্মার্ট থিম-বেসড ইমেজসহ আর্টিকেল তৈরি।');
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
# AMP-ভ্যালিড ব্লগ টেমপ্লেট
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
# মেইন জেনারেট ফাংশন (স্মার্ট থিম)
# ============================================================
def generate_blog_html(title, lang, data):
    try:
        # স্মার্ট থিম ডিটেক্ট
        theme = detect_theme(title)
        
        featured_svg = generate_featured_svg(title, theme)
        featured_encoded = urllib.parse.quote(featured_svg)
        
        slug = re.sub(r'[^\w\s]', '', title).replace(' ', '-').lower()[:50]
        now = time.strftime("%d %B, %Y")
        year = time.strftime("%Y")
        
        tips_html = ""
        toc_items = []
        for i, tip in enumerate(data['tips'], 1):
            tip_id = f"tip{i}"
            tip_svg = generate_tip_svg(tip['title'], i, theme)
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
            "author_bio": "প্রযুক্তি ও কনটেন্ট বিশেষজ্ঞ" if lang == 'bn' else "Tech & Content Expert",
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
            except Exception as e:
                continue

        fallback = generate_fallback_data(lang)
        html = generate_blog_html(title, lang, fallback)
        return jsonify({"html": html})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"সার্ভার এরর: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
