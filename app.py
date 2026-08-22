from flask import Flask, request, render_template_string, jsonify
import random

app = Flask(__name__)

# ============================================================
# ডেমো ডেটাবেস (মেডএক্সের সমস্ত কন্টেন্ট)
# ============================================================

# ওষুধের ডেটা
drugs = [
    {"brand": "Napa", "generic": "Paracetamol", "company": "Beximco Pharma", "indication": "জ্বর, ব্যথা", "class": "Analgesic", "form": "ট্যাবলেট"},
    {"brand": "Seclo", "generic": "Omeprazole", "company": "Healthcare Pharma", "indication": "গ্যাস্ট্রিক", "class": "Proton Pump Inhibitor", "form": "ক্যাপসুল"},
    {"brand": "Xenical", "generic": "Orlistat", "company": "Roche", "indication": "ওজন কমানো", "class": "Lipase Inhibitor", "form": "ক্যাপসুল"},
    {"brand": "Ventolin", "generic": "Salbutamol", "company": "GSK", "indication": "হাঁপানি", "class": "Bronchodilator", "form": "ইনহেলার"},
    {"brand": "Augmentin", "generic": "Co-amoxiclav", "company": "GSK", "indication": "ব্যাকটেরিয়া সংক্রমণ", "class": "Antibiotic", "form": "ট্যাবলেট"},
    {"brand": "Losartan", "generic": "Losartan Potassium", "company": "Square Pharma", "indication": "উচ্চ রক্তচাপ", "class": "ARB", "form": "ট্যাবলেট"},
    {"brand": "Metformin", "generic": "Metformin HCl", "company": "Beximco Pharma", "indication": "ডায়াবেটিস", "class": "Biguanide", "form": "ট্যাবলেট"},
    {"brand": "Insulin", "generic": "Insulin Human", "company": "Novo Nordisk", "indication": "ডায়াবেটিস", "class": "Hormone", "form": "ইনজেকশন"},
    {"brand": "Claritin", "generic": "Loratadine", "company": "Bayer", "indication": "এলার্জি", "class": "Antihistamine", "form": "ট্যাবলেট"},
    {"brand": "Vitamin D3", "generic": "Cholecalciferol", "company": "Square Pharma", "indication": "ভিটামিন ডি ঘাটতি", "class": "Vitamin", "form": "ক্যাপসুল"},
]

# ফার্মাসিউটিক্যাল কোম্পানি
companies = [
    {"name": "Beximco Pharma", "location": "ঢাকা", "products": 120},
    {"name": "Square Pharma", "location": "ঢাকা", "products": 150},
    {"name": "GSK Bangladesh", "location": "ঢাকা", "products": 80},
    {"name": "Healthcare Pharma", "location": "চট্টগ্রাম", "products": 60},
    {"name": "Roche Bangladesh", "location": "ঢাকা", "products": 40},
    {"name": "Novo Nordisk", "location": "ঢাকা", "products": 30},
    {"name": "Bayer Bangladesh", "location": "ঢাকা", "products": 50},
]

# নিউজ ডেটা
news = [
    {"title": "ওষুধ কোম্পানির আপত্তিতে ফিরল পুরোনো নিয়ম", "summary": "দাম নিয়ন্ত্রণে নজরদারি দুর্বল হলে রোগীর ওপর চাপ বাড়বে।", "tag": "ফার্মা", "date": "৩ দিন আগে"},
    {"title": "দেশে যে ৮ টুথপেস্টে কোনো মাইক্রোপ্লাস্টিক পাওয়া যায়নি", "summary": "নিয়মিত ওষুধ খেয়েও ফল না পাওয়ার ঘটনা বাড়ছে।", "tag": "স্বাস্থ্য", "date": "৪ দিন আগে"},
    {"title": "মার্কিন বাণিজ্যচুক্তি: বাংলাদেশের ওষুধশিল্পের সামনে অশনিসংকেত", "summary": "ইরান যুদ্ধের কারণে আকাশছোঁয়া ওষুধের দাম, বেশি ক্ষতিগ্রস্ত হবে যেসব দেশ।", "tag": "বাণিজ্য", "date": "৫ দিন আগে"},
    {"title": "অতি প্রয়োজনীয় ওষুধের তালিকা বাতিল বেইমানি", "summary": "বন্ধ হয়ে যাচ্ছে রূপপুর? মার্কিন শর্তের বেড়াজালে।", "tag": "ফার্মা", "date": "২ দিন আগে"},
]

# ভিডিও ডেটা
videos = [
    {"title": "অতি প্রয়োজনীয় ওষুধের তালিকা বাতিল বেইমানি", "views": "১২৩", "date": "২ দিন আগে"},
    {"title": "বন্ধ হয়ে যাচ্ছে রূপপুর? মার্কিন শর্তের বেড়াজালে", "views": "৯৮", "date": "৩ দিন আগে"},
    {"title": "কফি খেলে শরীরে কী হয়? কফি নিয়ে অজানা সব গল্প", "views": "২১৫", "date": "৪ দিন আগে"},
    {"title": "গাড়ির এসি চালু রেখে ঘুমিয়ে পড়া ওমান প্রবাসীদের মৃত্যু", "views": "১৬৭", "date": "৫ দিন আগে"},
]

# ড্রাগ ক্লাস
drug_classes = ["Analgesic", "Antibiotic", "Antihistamine", "ARB", "Biguanide", "Bronchodilator", "Hormone", "Lipase Inhibitor", "Proton Pump Inhibitor", "Vitamin"]

# ডোজ ফর্ম
dose_forms = ["ট্যাবলেট", "ক্যাপসুল", "ইনজেকশন", "সিরাপ", "ইনহেলার", "ক্রিম", "ড্রপস"]

# স্বাস্থ্য দিবস
health_days = [
    "৯ সেপ্টেম্বর — ফিটাল অ্যালকোহল সিন্ড্রোম দিবস",
    "১০ সেপ্টেম্বর — ইন্টারন্যাশনাল গাইনোকোলজিক্যাল হেলথ ডে",
    "১৭ সেপ্টেম্বর — বিশ্ব রোগী নিরাপত্তা দিবস",
    "২১ সেপ্টেম্বর — বিশ্ব আলঝেইমার দিবস",
    "২৫ সেপ্টেম্বর — বিশ্ব ফার্মাসিস্ট দিবস",
    "২৬ সেপ্টেম্বর — বিশ্ব গর্ভনিরোধক দিবস",
    "২৮ সেপ্টেম্বর — বিশ্ব রেবিজ দিবস",
    "২৯ সেপ্টেম্বর — বিশ্ব হৃদয় দিবস",
]

# ============================================================
# HTML টেমপ্লেট (পূর্ণাঙ্গ সাইট)
# ============================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedEx | লিডিং মেডিসিন ইনডেক্স</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family:'Inter',sans-serif; background:#f4f7fc; color:#1a2a3a; }
        a { text-decoration:none; color:inherit; }
        ul { list-style:none; }
        .container { max-width:1200px; margin:0 auto; padding:0 15px; }
        .flex { display:flex; align-items:center; flex-wrap:wrap; }
        .flex-between { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; }
        .grid-3 { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:20px; }
        .grid-4 { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:20px; }

        /* হেডার */
        .header-top { background:#0a1a2b; padding:8px 0; color:#aab8c5; font-size:13px; }
        .header-top .container { justify-content:flex-end; }
        .header-top a { color:#aab8c5; margin-left:18px; transition:0.3s; }
        .header-top a:hover { color:#fff; }
        .header-main { background:#fff; box-shadow:0 2px 10px rgba(0,0,0,0.05); padding:12px 0; position:sticky; top:0; z-index:100; }
        .logo span { font-size:22px; font-weight:700; color:#0a1a2b; }
        .logo span i { color:#1a8c6e; }
        .nav-menu { display:flex; gap:4px; flex-wrap:wrap; }
        .nav-menu > li { position:relative; }
        .nav-menu > li > a { display:block; padding:8px 14px; font-size:14px; font-weight:500; color:#1a2a3a; border-radius:6px; transition:0.3s; }
        .nav-menu > li > a:hover { background:#eef3f9; }
        .nav-menu .dropdown { display:none; position:absolute; top:100%; left:0; background:#fff; min-width:200px; box-shadow:0 10px 30px rgba(0,0,0,0.1); border-radius:8px; padding:8px 0; z-index:10; }
        .nav-menu li:hover .dropdown { display:block; }
        .dropdown li a { display:block; padding:8px 18px; font-size:13px; color:#1a2a3a; transition:0.2s; }
        .dropdown li a:hover { background:#f0f4fa; }
        .dropdown .divider { height:1px; background:#e5ecf3; margin:6px 12px; }

        /* সার্চ */
        .search-wrap { display:flex; align-items:center; background:#f0f4fa; border-radius:30px; padding:4px 4px 4px 18px; border:1px solid #dce4ed; max-width:420px; width:100%; }
        .search-wrap:focus-within { border-color:#1a8c6e; box-shadow:0 0 0 3px rgba(26,140,110,0.15); }
        .search-wrap select { border:none; background:transparent; font-size:13px; padding:8px 4px 8px 0; outline:none; cursor:pointer; font-weight:500; }
        .search-wrap input { flex:1; border:none; background:transparent; padding:10px 12px; font-size:14px; outline:none; color:#1a2a3a; min-width:100px; }
        .search-wrap input::placeholder { color:#8899aa; }
        .search-wrap button { background:#1a8c6e; border:none; color:#fff; width:42px; height:42px; border-radius:50%; font-size:16px; cursor:pointer; transition:0.3s; }
        .search-wrap button:hover { background:#147a5f; }

        /* হিরো স্ট্যাটস */
        .hero-stats { background:linear-gradient(135deg,#0a1a2b 0%,#1a3a4a 100%); color:#fff; padding:30px 0 40px; border-radius:0 0 30px 30px; }
        .hero-stats .stat-item { text-align:center; }
        .hero-stats .stat-item h2 { font-size:32px; font-weight:700; color:#5cd4a8; }
        .hero-stats .stat-item p { font-size:14px; color:#b0c8dd; margin-top:4px; }

        /* সেকশন */
        .section { padding:40px 0; }
        .section-title { font-size:22px; font-weight:700; color:#0a1a2b; margin-bottom:20px; display:flex; align-items:center; gap:12px; }
        .section-title .line { flex:1; height:2px; background:linear-gradient(to right,#dce4ed,transparent); }

        /* ভিডিও কার্ড */
        .video-card { background:#fff; border-radius:16px; overflow:hidden; box-shadow:0 4px 16px rgba(0,0,0,0.04); border:1px solid #eef3f9; transition:0.3s; }
        .video-card:hover { transform:translateY(-4px); box-shadow:0 12px 32px rgba(0,0,0,0.08); }
        .video-card .thumb { background:linear-gradient(135deg,#0a1a2b,#1a3a4a); height:140px; display:flex; align-items:center; justify-content:center; color:#fff; font-size:32px; }
        .video-card .thumb .play { width:50px; height:50px; background:rgba(255,255,255,0.2); border-radius:50%; display:flex; align-items:center; justify-content:center; backdrop-filter:blur(4px); }
        .video-card .body { padding:14px 16px; }
        .video-card .body h4 { font-size:14px; font-weight:600; color:#0a1a2b; }
        .video-card .body p { font-size:12px; color:#8899aa; margin-top:4px; }

        /* নিউজ কার্ড */
        .news-card { background:#fff; border-radius:16px; padding:18px 20px; border:1px solid #eef3f9; transition:0.3s; }
        .news-card:hover { border-color:#c8d6e4; }
        .news-card h4 { font-size:15px; font-weight:600; color:#0a1a2b; }
        .news-card p { font-size:13px; color:#667a8a; margin-top:6px; }
        .news-card .tag { display:inline-block; margin-top:10px; font-size:11px; font-weight:600; color:#1a8c6e; background:#e8f5f0; padding:2px 12px; border-radius:20px; }

        /* ড্রাগ টেবিল */
        .drug-table { width:100%; background:#fff; border-radius:16px; overflow:hidden; border:1px solid #eef3f9; }
        .drug-table th { background:#0a1a2b; color:#fff; padding:12px 16px; text-align:left; font-size:13px; }
        .drug-table td { padding:12px 16px; border-bottom:1px solid #eef3f9; font-size:14px; }
        .drug-table tr:hover td { background:#f8fafc; }

        /* ফুটার */
        .footer { background:#0a1a2b; color:#aab8c5; padding:40px 0 20px; margin-top:30px; border-radius:30px 30px 0 0; }
        .footer h4 { color:#fff; font-size:16px; margin-bottom:12px; }
        .footer p, .footer li { font-size:13px; line-height:2; }
        .footer a:hover { color:#fff; }
        .footer-bottom { border-top:1px solid #1a3a4a; padding-top:16px; margin-top:24px; text-align:center; font-size:13px; }

        /* ব্যাজ */
        .badge { background:#065f46; color:#34d399; padding:2px 12px; border-radius:30px; font-size:11px; }

        /* রেস্পন্সিভ */
        .menu-toggle { display:none; font-size:24px; cursor:pointer; color:#0a1a2b; padding:4px 10px; }
        @media (max-width:992px) {
            .nav-menu { display:none; flex-direction:column; width:100%; background:#fff; padding:16px; border-radius:12px; box-shadow:0 10px 30px rgba(0,0,0,0.08); margin-top:12px; }
            .nav-menu.open { display:flex; }
            .nav-menu .dropdown { position:static; box-shadow:none; padding-left:16px; }
            .menu-toggle { display:block; }
            .search-wrap { max-width:100%; margin-top:12px; }
        }
        @media (max-width:576px) {
            .hero-stats .grid-3 { grid-template-columns:1fr 1fr; }
        }
    </style>
</head>
<body>

<!-- টপ বার -->
<div class="header-top">
    <div class="container flex" style="justify-content:flex-end;">
        <a href="#"><i class="fa fa-newspaper-o"></i> নিউজ</a>
        <a href="#"><i class="fa fa-briefcase"></i> ফার্মা জবস</a>
        <a href="#"><i class="fa fa-file-text"></i> ডকুমেন্টস</a>
        <a href="#"><i class="fa fa-envelope"></i> কন্ট্যাক্ট</a>
    </div>
</div>

<!-- হেডার -->
<header class="header-main">
    <div class="container flex-between">
        <div class="logo flex" style="gap:6px;">
            <span>Med<i>Ex</i></span>
        </div>
        <div class="menu-toggle" onclick="toggleMenu()"><i class="fa fa-bars"></i></div>
        <ul class="nav-menu" id="navMenu">
            <li>
                <a href="#">Browse <i class="fa fa-angle-down"></i></a>
                <ul class="dropdown">
                    <li><a href="#drugs">ব্র্যান্ড (অ্যালোপ্যাথিক)</a></li>
                    <li><a href="#drugs">জেনেরিক</a></li>
                    <li class="divider"></li>
                    <li><a href="#companies">ফার্মাসিউটিক্যালস</a></li>
                    <li><a href="#classes">ড্রাগ ক্লাস</a></li>
                    <li><a href="#forms">ডোজ ফর্ম</a></li>
                </ul>
            </li>
            <li><a href="#drugs">ওষুধের তালিকা</a></li>
            <li><a href="#news">নিউজ</a></li>
            <li><a href="#">কন্ট্যাক্ট</a></li>
        </ul>
        <form class="search-wrap" action="/search" method="GET">
            <select name="type">
                <option value="brand">ব্র্যান্ড</option>
                <option value="generic">জেনেরিক</option>
                <option value="company">কোম্পানি</option>
            </select>
            <input type="text" name="q" placeholder="ওষুধের নাম লিখুন...">
            <button type="submit"><i class="fa fa-search"></i></button>
        </form>
    </div>
</header>

<!-- স্ট্যাটস -->
<section class="hero-stats">
    <div class="container">
        <div class="grid-3">
            <div class="stat-item"><h2>{{ drugs|length }}+</h2><p>ওষুধের তথ্য</p></div>
            <div class="stat-item"><h2>{{ companies|length }}+</h2><p>ফার্মাসিউটিক্যাল কোম্পানি</p></div>
            <div class="stat-item"><h2>{{ drug_classes|length }}</h2><p>ড্রাগ ক্লাস</p></div>
        </div>
    </div>
</section>

<!-- ওষুধের তালিকা -->
<section class="section" id="drugs">
    <div class="container">
        <div class="section-title">
            <i class="fa fa-medkit" style="color:#1a8c6e;"></i> ওষুধের সম্পূর্ণ তালিকা
            <span class="line"></span>
        </div>
        <div style="overflow-x:auto;">
            <table class="drug-table">
                <thead><tr><th>ব্র্যান্ড নাম</th><th>জেনেরিক</th><th>কোম্পানি</th><th>ইন্ডিকেশন</th><th>ক্লাস</th><th>ফর্ম</th></tr></thead>
                <tbody>
                    {% for drug in drugs %}
                    <tr>
                        <td><strong>{{ drug.brand }}</strong></td>
                        <td>{{ drug.generic }}</td>
                        <td>{{ drug.company }}</td>
                        <td>{{ drug.indication }}</td>
                        <td>{{ drug.class }}</td>
                        <td>{{ drug.form }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</section>

<!-- ফার্মাসিউটিক্যাল কোম্পানি -->
<section class="section" id="companies" style="padding-top:0;">
    <div class="container">
        <div class="section-title">
            <i class="fa fa-building" style="color:#1a8c6e;"></i> ফার্মাসিউটিক্যাল কোম্পানি
            <span class="line"></span>
        </div>
        <div class="grid-3">
            {% for company in companies %}
            <div class="news-card">
                <h4>{{ company.name }}</h4>
                <p><i class="fa fa-map-marker"></i> {{ company.location }}</p>
                <p><i class="fa fa-cube"></i> {{ company.products }}+ পণ্য</p>
            </div>
            {% endfor %}
        </div>
    </div>
</section>

<!-- ড্রাগ ক্লাস ও ডোজ ফর্ম -->
<section class="section" id="classes" style="padding-top:0;">
    <div class="container">
        <div class="grid-4">
            <div>
                <h4 style="color:#0a1a2b; margin-bottom:12px;"><i class="fa fa-tags"></i> ড্রাগ ক্লাস</h4>
                <ul style="font-size:14px; line-height:2.2; color:#1a2a3a;">
                    {% for cls in drug_classes %}
                    <li>• {{ cls }}</li>
                    {% endfor %}
                </ul>
            </div>
            <div>
                <h4 style="color:#0a1a2b; margin-bottom:12px;"><i class="fa fa-capsules"></i> ডোজ ফর্ম</h4>
                <ul style="font-size:14px; line-height:2.2; color:#1a2a3a;">
                    {% for form in dose_forms %}
                    <li>• {{ form }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </div>
</section>

<!-- ভিডিও -->
<section class="section" style="padding-top:0;">
    <div class="container">
        <div class="section-title">
            <i class="fa fa-play-circle" style="color:#1a8c6e;"></i> ফিচার্ড ভিডিও
            <span class="line"></span>
        </div>
        <div class="grid-3">
            {% for video in videos %}
            <div class="video-card">
                <div class="thumb"><div class="play"><i class="fa fa-play"></i></div></div>
                <div class="body">
                    <h4>{{ video.title }}</h4>
                    <p>{{ video.date }} · {{ video.views }} ভিউ</p>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</section>

<!-- নিউজ -->
<section class="section" id="news" style="padding-top:0;">
    <div class="container">
        <div class="section-title">
            <i class="fa fa-newspaper-o" style="color:#1a8c6e;"></i> সর্বশেষ নিউজ
            <span class="line"></span>
        </div>
        <div class="grid-3">
            {% for item in news %}
            <div class="news-card">
                <h4>{{ item.title }}</h4>
                <p>{{ item.summary }}</p>
                <div class="tag">{{ item.tag }}</div>
                <span style="font-size:11px; color:#8899aa; display:block; margin-top:6px;">{{ item.date }}</span>
            </div>
            {% endfor %}
        </div>
    </div>
</section>

<!-- স্বাস্থ্য দিবস -->
<section class="section" style="padding-top:0;">
    <div class="container">
        <div class="section-title">
            <i class="fa fa-calendar" style="color:#1a8c6e;"></i> আন্তর্জাতিক স্বাস্থ্য দিবস
            <span class="line"></span>
        </div>
        <div style="display:flex; flex-wrap:wrap; gap:10px; background:#fff; border-radius:16px; padding:20px; border:1px solid #eef3f9;">
            {% for day in health_days %}
            <span style="background:#e8f5f0; padding:6px 16px; border-radius:30px; font-size:13px; color:#0a1a2b;">📅 {{ day }}</span>
            {% endfor %}
        </div>
    </div>
</section>

<!-- ফুটার -->
<footer class="footer">
    <div class="container">
        <div class="grid-3">
            <div>
                <h4>মেডএক্স সম্পর্কে</h4>
                <p>বাংলাদেশের সবচেয়ে বড় অনলাইন মেডিসিন ইনডেক্স ও হেলথকেয়ার পোর্টাল। প্রেসক্রিপশনের যেকোনো ওষুধ সম্পর্কে বিস্তারিত তথ্য পান।</p>
            </div>
            <div>
                <h4>দ্রুত লিংক</h4>
                <ul>
                    <li><a href="#drugs">ব্র্যান্ড নাম</a></li>
                    <li><a href="#drugs">জেনেরিক নাম</a></li>
                    <li><a href="#companies">ফার্মাসিউটিক্যালস</a></li>
                    <li><a href="#classes">ড্রাগ ক্লাস</a></li>
                    <li><a href="#forms">ডোজ ফর্ম</a></li>
                </ul>
            </div>
            <div>
                <h4>যোগাযোগ</h4>
                <ul>
                    <li><i class="fa fa-envelope" style="width:20px;"></i> info@medex.com.bd</li>
                    <li><i class="fa fa-phone" style="width:20px;"></i> +৮৮০ ১৭০০-০০০০০০</li>
                    <li><i class="fa fa-map-marker" style="width:20px;"></i> ঢাকা, বাংলাদেশ</li>
                </ul>
            </div>
        </div>
        <div class="footer-bottom">&copy; ২০২৬ MedEx — সর্বস্বত্ব সংরক্ষিত</div>
    </div>
</footer>

<script>
    function toggleMenu() {
        document.getElementById('navMenu').classList.toggle('open');
    }
    document.querySelectorAll('.nav-menu > li').forEach(item => {
        item.addEventListener('click', function(e) {
            if (window.innerWidth <= 992) {
                const dropdown = this.querySelector('.dropdown');
                if (dropdown) { e.preventDefault(); dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block'; }
            }
        });
    });
</script>
</body>
</html>
"""

# ============================================================
# রাউটসমূহ
# ============================================================
@app.route('/')
def home():
    return render_template_string(
        HTML_TEMPLATE,
        drugs=drugs,
        companies=companies,
        news=news,
        videos=videos,
        drug_classes=drug_classes,
        dose_forms=dose_forms,
        health_days=health_days
    )

@app.route('/search')
def search():
    q = request.args.get('q', '').strip().lower()
    search_type = request.args.get('type', 'brand')
    results = []
    for drug in drugs:
        if search_type == 'brand' and q in drug['brand'].lower():
            results.append(drug)
        elif search_type == 'generic' and q in drug['generic'].lower():
            results.append(drug)
        elif search_type == 'company' and q in drug['company'].lower():
            results.append(drug)
    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head><title>সার্চ ফলাফল - MedEx</title>
        <style>
            body { font-family:Inter,sans-serif; background:#f4f7fc; padding:30px; }
            .container { max-width:1000px; margin:auto; background:#fff; padding:30px; border-radius:20px; }
            h2 { color:#0a1a2b; }
            table { width:100%; border-collapse:collapse; margin-top:20px; }
            th { background:#0a1a2b; color:#fff; padding:10px; text-align:left; }
            td { padding:10px; border-bottom:1px solid #eef3f9; }
            .back { display:inline-block; margin-top:20px; color:#1a8c6e; text-decoration:none; }
        </style>
        </head>
        <body>
        <div class="container">
            <h2>🔍 সার্চ ফলাফল: "{{ q }}" ({{ results|length }})</h2>
            <a href="/" class="back">← হোমে ফিরুন</a>
            <table>
                <tr><th>ব্র্যান্ড</th><th>জেনেরিক</th><th>কোম্পানি</th><th>ইন্ডিকেশন</th></tr>
                {% for drug in results %}
                <tr><td>{{ drug.brand }}</td><td>{{ drug.generic }}</td><td>{{ drug.company }}</td><td>{{ drug.indication }}</td></tr>
                {% endfor %}
            </table>
            {% if not results %}<p>কোনো ফলাফল পাওয়া যায়নি।</p>{% endif %}
        </div>
        </body>
        </html>
    """, q=q, results=results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
