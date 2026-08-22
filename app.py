import os
import shutil

# ============================================================
# ফাইল ও ফোল্ডারের ডেটা
# ============================================================

FILES = {
    "app.py": '''from flask import Flask, request, render_template, redirect, url_for, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'medex-secret-key-2026'

DATABASE = 'medex.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            generic TEXT NOT NULL,
            company TEXT NOT NULL,
            indication TEXT,
            drug_class TEXT,
            dose_form TEXT,
            strength TEXT,
            price REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            location TEXT,
            website TEXT,
            established INTEGER,
            description TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drug_classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dose_forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            summary TEXT,
            content TEXT,
            tag TEXT,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            video_url TEXT,
            thumbnail_url TEXT,
            views INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_days (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    insert_demo_data()

def insert_demo_data():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM drugs")
    if cursor.fetchone()[0] == 0:
        demo_drugs = [
            ("Napa", "Paracetamol", "Beximco Pharma", "জ্বর, মাথাব্যথা, দাঁতের ব্যথা", "Analgesic", "ট্যাবলেট", "500mg", 1.50),
            ("Ace", "Paracetamol", "Square Pharma", "জ্বর, মাথাব্যথা", "Analgesic", "ট্যাবলেট", "500mg", 1.20),
            ("Augmentin", "Co-amoxiclav", "GSK", "ব্যাকটেরিয়া সংক্রমণ", "Antibiotic", "ট্যাবলেট", "625mg", 12.00),
            ("Amoxil", "Amoxicillin", "Beximco Pharma", "গলা সংক্রমণ", "Antibiotic", "ক্যাপসুল", "500mg", 4.50),
            ("Ciprocin", "Ciprofloxacin", "Square Pharma", "মূত্রনালির সংক্রমণ", "Antibiotic", "ট্যাবলেট", "500mg", 6.00),
            ("Azithro", "Azithromycin", "Healthcare Pharma", "শ্বাসনালির সংক্রমণ", "Antibiotic", "ট্যাবলেট", "500mg", 8.00),
            ("Seclo", "Omeprazole", "Healthcare Pharma", "গ্যাস্ট্রিক, অ্যাসিডিটি", "Proton Pump Inhibitor", "ক্যাপসুল", "20mg", 4.00),
            ("Losartan", "Losartan Potassium", "Square Pharma", "উচ্চ রক্তচাপ", "ARB", "ট্যাবলেট", "50mg", 3.50),
            ("Metformin", "Metformin HCl", "Beximco Pharma", "ডায়াবেটিস", "Biguanide", "ট্যাবলেট", "500mg", 2.00),
            ("Insulin", "Insulin Human", "Novo Nordisk", "ডায়াবেটিস (টাইপ ১)", "Hormone", "ইনজেকশন", "100IU", 120.00),
            ("Ventolin", "Salbutamol", "GSK", "হাঁপানি, শ্বাসকষ্ট", "Bronchodilator", "ইনহেলার", "100mcg", 45.00),
            ("Claritin", "Loratadine", "Bayer", "এলার্জি, চুলকানি", "Antihistamine", "ট্যাবলেট", "10mg", 3.00),
            ("Vitamin D3", "Cholecalciferol", "Square Pharma", "ভিটামিন ডি ঘাটতি", "Vitamin", "ক্যাপসুল", "2000IU", 5.00),
            ("Xenical", "Orlistat", "Roche", "ওজন কমানো", "Lipase Inhibitor", "ক্যাপসুল", "120mg", 25.00),
            ("Doxy", "Doxycycline", "ACI Pharma", "ম্যালেরিয়া, সিফিলিস", "Antibiotic", "ক্যাপসুল", "100mg", 7.00),
            ("Flagyl", "Metronidazole", "Beximco Pharma", "পেটের সংক্রমণ", "Antibiotic", "ট্যাবলেট", "400mg", 3.00),
            ("Omep", "Omeprazole", "Square Pharma", "গ্যাস্ট্রিক আলসার", "Proton Pump Inhibitor", "ক্যাপসুল", "20mg", 3.50),
            ("Naproxen", "Naproxen", "ACI Pharma", "বাতের ব্যথা", "NSAID", "ট্যাবলেট", "250mg", 4.00),
            ("Diclofenac", "Diclofenac Sodium", "Healthcare Pharma", "গাঁটের ব্যথা", "NSAID", "ট্যাবলেট", "50mg", 2.50),
            ("Amlodipine", "Amlodipine Besilate", "Beximco Pharma", "উচ্চ রক্তচাপ", "Calcium Channel Blocker", "ট্যাবলেট", "5mg", 2.00),
        ]
        cursor.executemany('''
            INSERT INTO drugs (brand, generic, company, indication, drug_class, dose_form, strength, price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', demo_drugs)
    
    cursor.execute("SELECT COUNT(*) FROM companies")
    if cursor.fetchone()[0] == 0:
        demo_companies = [
            ("Beximco Pharma", "ঢাকা", "https://beximcopharma.com", 1976, "বাংলাদেশের শীর্ষস্থানীয় ফার্মাসিউটিক্যাল কোম্পানি"),
            ("Square Pharma", "ঢাকা", "https://squarepharma.com", 1958, "বাংলাদেশের বৃহত্তম ফার্মাসিউটিক্যাল কোম্পানি"),
            ("GSK Bangladesh", "ঢাকা", "https://gsk.com.bd", 1948, "বহুজাতিক ফার্মাসিউটিক্যাল কোম্পানি"),
            ("Healthcare Pharma", "চট্টগ্রাম", "https://healthcarepharma.com", 1985, "বাংলাদেশের অন্যতম ফার্মাসিউটিক্যাল কোম্পানি"),
            ("Roche Bangladesh", "ঢাকা", "https://roche.com.bd", 1992, "বহুজাতিক ফার্মাসিউটিক্যাল কোম্পানি"),
            ("Novo Nordisk", "ঢাকা", "https://novonordisk.com.bd", 1995, "ডায়াবেটিস ও হরমোন বিশেষজ্ঞ"),
            ("Bayer Bangladesh", "ঢাকা", "https://bayer.com.bd", 1990, "বহুজাতিক ফার্মাসিউটিক্যাল কোম্পানি"),
            ("ACI Pharma", "ঢাকা", "https://aci-bd.com", 1970, "বাংলাদেশের অগ্রগামী ফার্মাসিউটিক্যাল কোম্পানি"),
            ("Opsonin Pharma", "ঢাকা", "https://opsonin.com", 1976, "বাংলাদেশের শীর্ষ ফার্মাসিউটিক্যাল কোম্পানি"),
            ("Renata Pharma", "ঢাকা", "https://renata.com", 1980, "বাংলাদেশের উন্নত ফার্মাসিউটিক্যাল কোম্পানি"),
        ]
        cursor.executemany('''
            INSERT INTO companies (name, location, website, established, description)
            VALUES (?, ?, ?, ?, ?)
        ''', demo_companies)
    
    cursor.execute("SELECT COUNT(*) FROM drug_classes")
    if cursor.fetchone()[0] == 0:
        demo_classes = [
            ("Analgesic", "ব্যথানাশক ও জ্বর কমানোর ওষুধ"),
            ("Antibiotic", "ব্যাকটেরিয়া সংক্রমণের ওষুধ"),
            ("Antihistamine", "এলার্জি ও চুলকানির ওষুধ"),
            ("ARB", "উচ্চ রক্তচাপের ওষুধ"),
            ("Biguanide", "ডায়াবেটিসের ওষুধ (মেটফর্মিন)"),
            ("Bronchodilator", "হাঁপানি ও শ্বাসকষ্টের ওষুধ"),
            ("Hormone", "হরমোনজাতীয় ওষুধ"),
            ("Lipase Inhibitor", "ওজন কমানোর ওষুধ"),
            ("Proton Pump Inhibitor", "গ্যাস্ট্রিক ও অ্যাসিডিটির ওষুধ"),
            ("Vitamin", "ভিটামিন সাপ্লিমেন্ট"),
            ("NSAID", "নন-স্টেরয়েডাল ব্যথানাশক"),
            ("Calcium Channel Blocker", "উচ্চ रक्तচাপের ওষুধ"),
        ]
        cursor.executemany('''
            INSERT INTO drug_classes (name, description)
            VALUES (?, ?)
        ''', demo_classes)
    
    cursor.execute("SELECT COUNT(*) FROM dose_forms")
    if cursor.fetchone()[0] == 0:
        demo_forms = [
            ("ট্যাবলেট", "মুখে খাওয়ার জন্য ট্যাবলেট"),
            ("ক্যাপসুল", "মুখে খাওয়ার জন্য ক্যাপসুল"),
            ("ইনজেকশন", "ইনজেকশনের মাধ্যমে প্রদান"),
            ("সিরাপ", "তরল আকারে খাওয়ার ওষুধ"),
            ("ইনহেলার", "শ্বাসের মাধ্যমে গ্রহণ"),
            ("ক্রিম", "ত্বকে লাগানোর ওষুধ"),
            ("ড্রপস", "চোখ বা কানের ড্রপ"),
            ("সাসপেনশন", "তরল সাসপেনশন"),
            ("পাউডার", "গুঁড়া আকারে"),
            ("অয়েন্টমেন্ট", "ত্বকে লাগানোর মলম"),
        ]
        cursor.executemany('''
            INSERT INTO dose_forms (name, description)
            VALUES (?, ?)
        ''', demo_forms)
    
    cursor.execute("SELECT COUNT(*) FROM news")
    if cursor.fetchone()[0] == 0:
        demo_news = [
            ("ওষুধ কোম্পানির আপত্তিতে ফিরল পুরোনো নিয়ম", "দাম নিয়ন্ত্রণে নজরদারি দুর্বল হলে রোগীর ওপর চাপ বাড়বে।", "বিস্তারিত...", "ফার্মা", "", "2026-08-20"),
            ("দেশে যে ৮ টুথপেস্টে কোনো মাইক্রোপ্লাস্টিক পাওয়া যায়নি", "নিয়মিত ওষুধ খেয়েও ফল না পাওয়ার ঘটনা বাড়ছে।", "বিস্তারিত...", "স্বাস্থ্য", "", "2026-08-19"),
            ("মার্কিন বাণিজ্যচুক্তি: বাংলাদেশের ওষুধশিল্পের সামনে অশনিসংকেত", "ইরান যুদ্ধের কারণে আকাশছোঁয়া ওষুধের দাম।", "বিস্তারিত...", "বাণিজ্য", "", "2026-08-18"),
            ("অতি প্রয়োজনীয় ওষুধের তালিকা বাতিল বেইমানি", "বন্ধ হয়ে যাচ্ছে রূপপুর? মার্কিন শর্তের বেড়াজালে।", "বিস্তারিত...", "ফার্মা", "", "2026-08-17"),
            ("বাংলাদেশে নতুন ৫টি ওষুধের লাইসেন্স অনুমোদন", "ডিজিটাল স্বাস্থ্যসেবা বাড়াতে নতুন উদ্যোগ", "বিস্তারিত...", "স্বাস্থ্য", "", "2026-08-16"),
        ]
        cursor.executemany('''
            INSERT INTO news (title, summary, content, tag, image_url, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', demo_news)
    
    cursor.execute("SELECT COUNT(*) FROM videos")
    if cursor.fetchone()[0] == 0:
        demo_videos = [
            ("অতি প্রয়োজনীয় ওষুধের তালিকা বাতিল বেইমানি", "ওষুধের দাম ও প্রাপ্যতা নিয়ে বিশ্লেষণ", "", "", 123, "2026-08-20"),
            ("বন্ধ হয়ে যাচ্ছে রূপপুর? মার্কিন শর্তের বেড়াজালে", "রূপপুর পারমাণবিক প্রকল্পের ওপর মার্কিন শর্ত", "", "", 98, "2026-08-19"),
            ("কফি খেলে শরীরে কী হয়? কফি নিয়ে অজানা সব গল্প", "কফির উপকারিতা ও অপকারিতা", "", "", 215, "2026-08-18"),
            ("গাড়ির এসি চালু রেখে ঘুমিয়ে পড়া ওমান প্রবাসীদের মৃত্যু", "ওমানে প্রবাসীদের জন্য সতর্কতা", "", "", 167, "2026-08-17"),
        ]
        cursor.executemany('''
            INSERT INTO videos (title, description, video_url, thumbnail_url, views, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', demo_videos)
    
    cursor.execute("SELECT COUNT(*) FROM health_days")
    if cursor.fetchone()[0] == 0:
        demo_days = [
            ("সেপ্টেম্বর ৯", "ফিটাল অ্যালকোহল সিন্ড্রোম দিবস", ""),
            ("সেপ্টেম্বর ১০", "ইন্টারন্যাশনাল গাইনোকোলজিক্যাল হেলথ ডে", ""),
            ("সেপ্টেম্বর ১৭", "বিশ্ব রোগী নিরাপত্তা দিবস", ""),
            ("সেপ্টেম্বর ২১", "বিশ্ব আলঝেইমার দিবস", ""),
            ("সেপ্টেম্বর ২৫", "বিশ্ব ফার্মাসিস্ট দিবস", ""),
            ("সেপ্টেম্বর ২৬", "বিশ্ব গর্ভনিরোধক দিবস", ""),
            ("সেপ্টেম্বর ২৮", "বিশ্ব রেবিজ দিবস", ""),
            ("সেপ্টেম্বর ২৯", "বিশ্ব হৃদয় দিবস", ""),
        ]
        cursor.executemany('''
            INSERT INTO health_days (date, title, description)
            VALUES (?, ?, ?)
        ''', demo_days)
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM drugs")
    drug_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM companies")
    company_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM drug_classes")
    class_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT * FROM drugs ORDER BY id DESC LIMIT 10")
    recent_drugs = cursor.fetchall()
    cursor.execute("SELECT * FROM news ORDER BY created_at DESC LIMIT 4")
    news_list = cursor.fetchall()
    cursor.execute("SELECT * FROM videos ORDER BY views DESC LIMIT 4")
    videos_list = cursor.fetchall()
    cursor.execute("SELECT * FROM health_days")
    health_days = cursor.fetchall()
    cursor.execute("SELECT * FROM companies LIMIT 6")
    companies = cursor.fetchall()
    conn.close()
    
    return render_template('index.html', 
        drug_count=drug_count,
        company_count=company_count,
        class_count=class_count,
        recent_drugs=recent_drugs,
        news_list=news_list,
        videos_list=videos_list,
        health_days=health_days,
        companies=companies
    )

@app.route('/drugs')
def drug_list():
    conn = get_db()
    cursor = conn.cursor()
    search = request.args.get('search', '')
    search_type = request.args.get('type', 'brand')
    
    if search:
        if search_type == 'brand':
            cursor.execute("SELECT * FROM drugs WHERE brand LIKE ? ORDER BY brand", (f'%{search}%',))
        elif search_type == 'generic':
            cursor.execute("SELECT * FROM drugs WHERE generic LIKE ? ORDER BY brand", (f'%{search}%',))
        elif search_type == 'company':
            cursor.execute("SELECT * FROM drugs WHERE company LIKE ? ORDER BY brand", (f'%{search}%',))
        else:
            cursor.execute("SELECT * FROM drugs WHERE brand LIKE ? OR generic LIKE ? ORDER BY brand", 
                          (f'%{search}%', f'%{search}%'))
    else:
        cursor.execute("SELECT * FROM drugs ORDER BY brand")
    
    drugs = cursor.fetchall()
    conn.close()
    return render_template('drugs.html', drugs=drugs, search=search, search_type=search_type)

@app.route('/drugs/add', methods=['GET', 'POST'])
def add_drug():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM companies ORDER BY name")
    companies = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT name FROM drug_classes ORDER BY name")
    classes = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT name FROM dose_forms ORDER BY name")
    forms = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    if request.method == 'POST':
        brand = request.form.get('brand')
        generic = request.form.get('generic')
        company = request.form.get('company')
        indication = request.form.get('indication')
        drug_class = request.form.get('drug_class')
        dose_form = request.form.get('dose_form')
        strength = request.form.get('strength')
        price = request.form.get('price', 0)
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO drugs (brand, generic, company, indication, drug_class, dose_form, strength, price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (brand, generic, company, indication, drug_class, dose_form, strength, price))
        conn.commit()
        conn.close()
        return redirect(url_for('drug_list'))
    
    return render_template('add_drug.html', companies=companies, classes=classes, forms=forms)

@app.route('/drugs/edit/<int:id>', methods=['GET', 'POST'])
def edit_drug(id):
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        brand = request.form.get('brand')
        generic = request.form.get('generic')
        company = request.form.get('company')
        indication = request.form.get('indication')
        drug_class = request.form.get('drug_class')
        dose_form = request.form.get('dose_form')
        strength = request.form.get('strength')
        price = request.form.get('price', 0)
        
        cursor.execute('''
            UPDATE drugs SET brand=?, generic=?, company=?, indication=?, drug_class=?, dose_form=?, strength=?, price=?
            WHERE id=?
        ''', (brand, generic, company, indication, drug_class, dose_form, strength, price, id))
        conn.commit()
        conn.close()
        return redirect(url_for('drug_list'))
    
    cursor.execute("SELECT * FROM drugs WHERE id=?", (id,))
    drug = cursor.fetchone()
    
    cursor.execute("SELECT name FROM companies ORDER BY name")
    companies = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT name FROM drug_classes ORDER BY name")
    classes = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT name FROM dose_forms ORDER BY name")
    forms = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return render_template('edit_drug.html', drug=drug, companies=companies, classes=classes, forms=forms)

@app.route('/drugs/delete/<int:id>')
def delete_drug(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM drugs WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('drug_list'))

@app.route('/companies')
def company_list():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companies ORDER BY name")
    companies = cursor.fetchall()
    conn.close()
    return render_template('companies.html', companies=companies)

@app.route('/companies/add', methods=['GET', 'POST'])
def add_company():
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        website = request.form.get('website')
        established = request.form.get('established', 0)
        description = request.form.get('description')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO companies (name, location, website, established, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, location, website, established, description))
        conn.commit()
        conn.close()
        return redirect(url_for('company_list'))
    
    return render_template('add_company.html')

@app.route('/companies/edit/<int:id>', methods=['GET', 'POST'])
def edit_company(id):
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        website = request.form.get('website')
        established = request.form.get('established', 0)
        description = request.form.get('description')
        
        cursor.execute('''
            UPDATE companies SET name=?, location=?, website=?, established=?, description=?
            WHERE id=?
        ''', (name, location, website, established, description, id))
        conn.commit()
        conn.close()
        return redirect(url_for('company_list'))
    
    cursor.execute("SELECT * FROM companies WHERE id=?", (id,))
    company = cursor.fetchone()
    conn.close()
    return render_template('edit_company.html', company=company)

@app.route('/companies/delete/<int:id>')
def delete_company(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM companies WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('company_list'))

@app.route('/api/drugs')
def api_drugs():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM drugs ORDER BY brand")
    drugs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(drugs)

@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
''',

    "requirements.txt": '''flask
gunicorn
''',

    "templates/index.html": '''<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedEx - সম্পূর্ণ মেডিসিন ইনডেক্স</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family: 'Segoe UI', sans-serif; background:#f4f7fc; color:#1a2a3a; }
        a { text-decoration:none; color:inherit; }
        ul { list-style:none; }
        .container { max-width:1200px; margin:0 auto; padding:0 15px; }
        .flex { display:flex; align-items:center; flex-wrap:wrap; }
        .flex-between { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; }
        .grid-3 { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:20px; }
        .grid-4 { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:20px; }

        .header-top { background:#0a1a2b; padding:8px 0; color:#aab8c5; font-size:13px; }
        .header-top .container { justify-content:flex-end; }
        .header-top a { color:#aab8c5; margin-left:18px; transition:0.3s; }
        .header-top a:hover { color:#fff; }
        .header-main { background:#fff; box-shadow:0 2px 10px rgba(0,0,0,0.05); padding:12px 0; position:sticky; top:0; z-index:100; }
        .logo span { font-size:22px; font-weight:700; color:#0a1a2b; }
        .logo span i { color:#1a8c6e; }
        .nav-menu { display:flex; gap:4px; flex-wrap:wrap; }
        .nav-menu > li > a { display:block; padding:8px 14px; font-size:14px; font-weight:500; color:#1a2a3a; border-radius:6px; transition:0.3s; }
        .nav-menu > li > a:hover { background:#eef3f9; }
        .search-wrap { display:flex; align-items:center; background:#f0f4fa; border-radius:30px; padding:4px; border:1px solid #dce4ed; max-width:380px; width:100%; }
        .search-wrap input { flex:1; border:none; background:transparent; padding:10px 16px; font-size:14px; outline:none; }
        .search-wrap button { background:#1a8c6e; border:none; color:#fff; width:42px; height:42px; border-radius:50%; font-size:16px; cursor:pointer; }
        .search-wrap button:hover { background:#147a5f; }

        .hero-stats { background:linear-gradient(135deg,#0a1a2b 0%,#1a3a4a 100%); color:#fff; padding:30px 0 40px; border-radius:0 0 30px 30px; }
        .hero-stats .stat-item { text-align:center; }
        .hero-stats .stat-item h2 { font-size:32px; font-weight:700; color:#5cd4a8; }
        .hero-stats .stat-item p { font-size:14px; color:#b0c8dd; }

        .section { padding:40px 0; }
        .section-title { font-size:22px; font-weight:700; color:#0a1a2b; margin-bottom:20px; display:flex; align-items:center; gap:12px; }
        .section-title .line { flex:1; height:2px; background:linear-gradient(to right,#dce4ed,transparent); }
        .section-title a { font-size:14px; color:#1a8c6e; }

        .drug-card, .video-card, .news-card { background:#fff; border-radius:16px; padding:16px; border:1px solid #eef3f9; transition:0.3s; }
        .drug-card:hover, .video-card:hover, .news-card:hover { transform:translateY(-3px); box-shadow:0 8px 24px rgba(0,0,0,0.06); }
        .drug-card h4, .video-card h4, .news-card h4 { font-size:15px; font-weight:600; color:#0a1a2b; }
        .drug-card p, .video-card p, .news-card p { font-size:13px; color:#667a8a; margin-top:4px; }
        .drug-card .badge, .news-card .tag { display:inline-block; margin-top:8px; font-size:11px; font-weight:600; color:#1a8c6e; background:#e8f5f0; padding:2px 12px; border-radius:20px; }
        .video-card .thumb { background:linear-gradient(135deg,#0a1a2b,#1a3a4a); height:140px; border-radius:12px; display:flex; align-items:center; justify-content:center; color:#fff; font-size:32px; margin-bottom:12px; }

        .footer { background:#0a1a2b; color:#aab8c5; padding:40px 0 20px; margin-top:30px; border-radius:30px 30px 0 0; }
        .footer h4 { color:#fff; font-size:16px; margin-bottom:12px; }
        .footer p, .footer li { font-size:13px; line-height:2; }
        .footer a:hover { color:#fff; }
        .footer-bottom { border-top:1px solid #1a3a4a; padding-top:16px; margin-top:24px; text-align:center; font-size:13px; }

        .health-day { background:#e8f5f0; padding:6px 16px; border-radius:30px; font-size:13px; color:#0a1a2b; }
        .menu-toggle { display:none; font-size:24px; cursor:pointer; color:#0a1a2b; }
        @media (max-width:992px) {
            .nav-menu { display:none; flex-direction:column; width:100%; background:#fff; padding:16px; border-radius:12px; margin-top:12px; }
            .nav-menu.open { display:flex; }
            .menu-toggle { display:block; }
            .search-wrap { max-width:100%; margin-top:12px; }
        }
        @media (max-width:576px) {
            .hero-stats .grid-3 { grid-template-columns:1fr 1fr; }
            .grid-3 { grid-template-columns:1fr; }
        }
    </style>
</head>
<body>

<div class="header-top">
    <div class="container flex" style="justify-content:flex-end;">
        <a href="/"><i class="fa fa-home"></i> হোম</a>
        <a href="/drugs"><i class="fa fa-medkit"></i> ওষুধ</a>
        <a href="/companies"><i class="fa fa-building"></i> কোম্পানি</a>
    </div>
</div>

<header class="header-main">
    <div class="container flex-between">
        <div class="logo"><span>Med<i>Ex</i></span></div>
        <div class="menu-toggle" onclick="document.getElementById('navMenu').classList.toggle('open')">
            <i class="fa fa-bars"></i>
        </div>
        <ul class="nav-menu" id="navMenu">
            <li><a href="/">হোম</a></li>
            <li><a href="/drugs">ওষুধের তালিকা</a></li>
            <li><a href="/companies">কোম্পানি</a></li>
            <li><a href="/drugs/add"><i class="fa fa-plus-circle"></i> যোগ করুন</a></li>
        </ul>
        <form class="search-wrap" action="/drugs" method="GET">
            <input type="text" name="search" placeholder="ওষুধের নাম লিখুন...">
            <button type="submit"><i class="fa fa-search"></i></button>
        </form>
    </div>
</header>

<section class="hero-stats">
    <div class="container">
        <div class="grid-3">
            <div class="stat-item"><h2>{{ drug_count }}+</h2><p>ওষুধ</p></div>
            <div class="stat-item"><h2>{{ company_count }}+</h2><p>ফার্মাসিউটিক্যাল কোম্পানি</p></div>
            <div class="stat-item"><h2>{{ class_count }}</h2><p>ড্রাগ ক্লাস</p></div>
        </div>
    </div>
</section>

<section class="section">
    <div class="container">
        <div class="section-title">
            <i class="fa fa-medkit" style="color:#1a8c6e;"></i> সাম্প্রতিক ওষুধ
            <span class="line"></span>
            <a href="/drugs">সব দেখুন →</a>
        </div>
        <div class="grid-3">
            {% for drug in recent_drugs %}
            <div class="drug-card">
                <h4>{{ drug.brand }}</h4>
                <p><strong>জেনেরিক:</strong> {{ drug.generic }}</p>
                <p><strong>কোম্পানি:</strong> {{ drug.company }}</p>
                <p><strong>ইন্ডিকেশন:</strong> {{ drug.indication or 'N/A' }}</p>
                <span class="badge">{{ drug.drug_class or 'N/A' }}</span>
            </div>
            {% endfor %}
        </div>
    </div>
</section>

<section class="section" style="padding-top:0;">
    <div class="container">
        <div class="section-title">
            <i class="fa fa-building" style="color:#1a8c6e;"></i> ফার্মাসিউটিক্যাল কোম্পানি
            <span class="line"></span>
            <a href="/companies">সব দেখুন →</a>
        </div>
        <div class="grid-4">
            {% for company in companies %}
            <div class="drug-card" style="text-align:center;">
                <h4>{{ company.name }}</h4>
                <p><i class="fa fa-map-marker"></i> {{ company.location or 'N/A' }}</p>
                <p><i class="fa fa-calendar"></i> {{ company.established or 'N/A' }}</p>
            </div>
            {% endfor %}
        </div>
    </div>
</section>

<section class="section" style="padding-top:0;">
    <div class="container">
        <div class="section-title">
            <i class="fa fa-calendar" style="color:#1a8c6e;"></i> আন্তর্জাতিক স্বাস্থ্য দিবস
            <span class="line"></span>
        </div>
        <div style="display:flex; flex-wrap:wrap; gap:10px; background:#fff; border-radius:16px; padding:20px; border:1px solid #eef3f9;">
            {% for day in health_days %}
            <span class="health-day">📅 {{ day.date }} — {{ day.title }}</span>
            {% endfor %}
        </div>
    </div>
</section>

<footer class="footer">
    <div class="container">
        <div class="grid-3">
            <div>
                <h4>মেডএক্স সম্পর্কে</h4>
                <p>বাংলাদেশের সবচেয়ে বড় অনলাইন মেডিসিন ইনডেক্স। প্রেসক্রিপশনের যেকোনো ওষুধ সম্পর্কে বিস্তারিত তথ্য পান।</p>
            </div>
            <div>
                <h4>দ্রুত লিংক</h4>
                <ul>
                    <li><a href="/drugs">ওষুধের তালিকা</a></li>
                    <li><a href="/companies">কোম্পানি</a></li>
                    <li><a href="/drugs/add">ওষুধ যোগ করুন</a></li>
                </ul>
            </div>
            <div>
                <h4>যোগাযোগ</h4>
                <ul>
                    <li><i class="fa fa-envelope"></i> info@medex.com.bd</li>
                    <li><i class="fa fa-phone"></i> +৮৮০ ১৭০০-০০০০০০</li>
                    <li><i class="fa fa-map-marker"></i> ঢাকা, বাংলাদেশ</li>
                </ul>
            </div>
        </div>
        <div class="footer-bottom">&copy; ২০২৬ MedEx — সর্বস্বত্ব সংরক্ষিত</div>
    </div>
</footer>

</body>
</html>
''',

    "templates/drugs.html": '''<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ওষুধের তালিকা - MedEx</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family:'Segoe UI',sans-serif; background:#f4f7fc; color:#1a2a3a; }
        a { text-decoration:none; color:inherit; }
        .container { max-width:1200px; margin:0 auto; padding:0 15px; }
        .header { background:#fff; padding:16px 0; box-shadow:0 2px 10px rgba(0,0,0,0.05); }
        .header .flex { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; }
        .logo span { font-size:22px; font-weight:700; color:#0a1a2b; }
        .logo span i { color:#1a8c6e; }
        .btn { display:inline-block; padding:10px 20px; border-radius:30px; border:none; cursor:pointer; font-weight:600; }
        .btn-primary { background:#1a8c6e; color:#fff; }
        .btn-primary:hover { background:#147a5f; }
        .btn-danger { background:#dc2626; color:#fff; }
        .btn-danger:hover { background:#b91c1c; }
        .btn-sm { padding:6px 14px; font-size:13px; }
        .search-form { display:flex; gap:8px; flex-wrap:wrap; }
        .search-form input, .search-form select { padding:10px 16px; border-radius:30px; border:1px solid #dce4ed; font-size:14px; background:#fff; }
        .search-form input { flex:1; min-width:180px; }
        table { width:100%; background:#fff; border-radius:16px; overflow:hidden; border:1px solid #eef3f9; margin-top:20px; }
        th { background:#0a1a2b; color:#fff; padding:12px 16px; text-align:left; font-size:13px; }
        td { padding:12px 16px; border-bottom:1px solid #eef3f9; font-size:14px; }
        tr:hover td { background:#f8fafc; }
        .badge { background:#e8f5f0; color:#1a8c6e; padding:2px 12px; border-radius:20px; font-size:11px; font-weight:600; }
        .footer { background:#0a1a2b; color:#aab8c5; padding:20px 0; text-align:center; margin-top:30px; }
        .action-links a { margin:0 6px; color:#1a8c6e; }
        .action-links a:hover { color:#147a5f; }
        @media (max-width:768px) { table { font-size:12px; } th, td { padding:8px; } }
    </style>
</head>
<body>

<div class="header">
    <div class="container">
        <div class="flex">
            <div class="logo"><a href="/"><span>Med<i>Ex</i></span></a></div>
            <div>
                <a href="/" style="margin-right:16px; color:#1a2a3a;">হোম</a>
                <a href="/drugs/add" class="btn btn-primary btn-sm"><i class="fa fa-plus"></i> নতুন ওষুধ</a>
            </div>
        </div>
    </div>
</div>

<div class="container" style="padding:20px 15px;">
    <h2 style="margin-bottom:16px;">💊 সমস্ত ওষুধ ({{ drugs|length }})</h2>
    
    <form class="search-form" method="GET">
        <select name="type">
            <option value="brand" {% if search_type=='brand' %}selected{% endif %}>ব্র্যান্ড</option>
            <option value="generic" {% if search_type=='generic' %}selected{% endif %}>জেনেরিক</option>
            <option value="company" {% if search_type=='company' %}selected{% endif %}>কোম্পানি</option>
        </select>
        <input type="text" name="search" placeholder="ওষুধের নাম লিখুন..." value="{{ search }}">
        <button type="submit" class="btn btn-primary btn-sm"><i class="fa fa-search"></i> খুঁজুন</button>
        {% if search %}<a href="/drugs" class="btn btn-sm" style="background:#e5ecf3;">ক্লিয়ার</a>{% endif %}
    </form>

    <div style="overflow-x:auto;">
        <table>
            <thead>
                <tr>
                    <th>ব্র্যান্ড</th>
                    <th>জেনেরিক</th>
                    <th>কোম্পানি</th>
                    <th>ইন্ডিকেশন</th>
                    <th>ক্লাস</th>
                    <th>ফর্ম</th>
                    <th>শক্তি</th>
                    <th>মূল্য</th>
                    <th>অ্যাকশন</th>
                </tr>
            </thead>
            <tbody>
                {% for drug in drugs %}
                <tr>
                    <td><strong>{{ drug.brand }}</strong></td>
                    <td>{{ drug.generic }}</td>
                    <td>{{ drug.company }}</td>
                    <td>{{ drug.indication or '—' }}</td>
                    <td><span class="badge">{{ drug.drug_class or '—' }}</span></td>
                    <td>{{ drug.dose_form or '—' }}</td>
                    <td>{{ drug.strength or '—' }}</td>
                    <td>৳{{ drug.price or '—' }}</td>
                    <td class="action-links">
                        <a href="/drugs/edit/{{ drug.id }}"><i class="fa fa-edit"></i></a>
                        <a href="/drugs/delete/{{ drug.id }}" onclick="return confirm('মুছতে চান?')"><i class="fa fa-trash" style="color:#dc2626;"></i></a>
                    </td>
                </tr>
                {% endfor %}
                {% if not drugs %}
                <tr><td colspan="9" style="text-align:center; padding:30px;">কোনো ওষুধ পাওয়া যায়নি। <a href="/drugs/add" style="color:#1a8c6e;">নতুন যোগ করুন</a></td></tr>
                {% endif %}
            </tbody>
        </table>
    </div>
</div>

<div class="footer">&copy; ২০২৬ MedEx — সর্বস্বত্ব সংরক্ষিত</div>

</body>
</html>
''',

    "templates/add_drug.html": '''<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>নতুন ওষুধ যোগ - MedEx</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family:'Segoe UI',sans-serif; background:#f4f7fc; color:#1a2a3a; padding:30px; }
        .container { max-width:700px; margin:auto; background:#fff; padding:30px; border-radius:20px; box-shadow:0 4px 20px rgba(0,0,0,0.06); }
        h2 { margin-bottom:20px; color:#0a1a2b; }
        label { display:block; font-weight:500; margin:12px 0 4px; font-size:14px; color:#1a2a3a; }
        input, select { width:100%; padding:12px 16px; border-radius:12px; border:1px solid #dce4ed; font-size:15px; }
        .btn { padding:12px 30px; border:none; border-radius:30px; cursor:pointer; font-weight:600; }
        .btn-primary { background:#1a8c6e; color:#fff; }
        .btn-primary:hover { background:#147a5f; }
        .btn-secondary { background:#e5ecf3; color:#1a2a3a; }
        .btn-secondary:hover { background:#c8d6e4; }
        .flex { display:flex; gap:12px; margin-top:20px; flex-wrap:wrap; }
    </style>
</head>
<body>
<div class="container">
    <h2><i class="fa fa-plus-circle"></i> নতুন ওষুধ যোগ</h2>
    <form method="POST">
        <label>ব্র্যান্ড নাম *</label>
        <input type="text" name="brand" required placeholder="যেমন: Napa">

        <label>জেনেরিক নাম *</label>
        <input type="text" name="generic" required placeholder="যেমন: Paracetamol">

        <label>কোম্পানি *</label>
        <select name="company" required>
            <option value="">— নির্বাচন করুন —</option>
            {% for c in companies %}
            <option value="{{ c }}">{{ c }}</option>
            {% endfor %}
        </select>

        <label>ইন্ডিকেশন</label>
        <input type="text" name="indication" placeholder="যেমন: জ্বর, মাথাব্যথা">

        <label>ড্রাগ ক্লাস</label>
        <select name="drug_class">
            <option value="">— নির্বাচন করুন —</option>
            {% for c in classes %}
            <option value="{{ c }}">{{ c }}</option>
            {% endfor %}
        </select>

        <label>ডোজ ফর্ম</label>
        <select name="dose_form">
            <option value="">— নির্বাচন করুন —</option>
            {% for f in forms %}
            <option value="{{ f }}">{{ f }}</option>
            {% endfor %}
        </select>

        <label>শক্তি</label>
        <input type="text" name="strength" placeholder="যেমন: 500mg">

        <label>মূল্য (৳)</label>
        <input type="number" name="price" step="0.01" placeholder="যেমন: 1.50">

        <div class="flex">
            <button type="submit" class="btn btn-primary"><i class="fa fa-save"></i> সংরক্ষণ</button>
            <a href="/drugs" class="btn btn-secondary">বাতিল</a>
        </div>
    </form>
</div>
</body>
</html>
''',

    "templates/edit_drug.html": '''<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ওষুধ সম্পাদনা - MedEx</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family:'Segoe UI',sans-serif; background:#f4f7fc; color:#1a2a3a; padding:30px; }
        .container { max-width:700px; margin:auto; background:#fff; padding:30px; border-radius:20px; box-shadow:0 4px 20px rgba(0,0,0,0.06); }
        h2 { margin-bottom:20px; color:#0a1a2b; }
        label { display:block; font-weight:500; margin:12px 0 4px; font-size:14px; }
        input, select { width:100%; padding:12px 16px; border-radius:12px; border:1px solid #dce4ed; font-size:15px; }
        .btn { padding:12px 30px; border:none; border-radius:30px; cursor:pointer; font-weight:600; }
        .btn-primary { background:#1a8c6e; color:#fff; }
        .btn-primary:hover { background:#147a5f; }
        .btn-secondary { background:#e5ecf3; color:#1a2a3a; }
        .btn-secondary:hover { background:#c8d6e4; }
        .flex { display:flex; gap:12px; margin-top:20px; flex-wrap:wrap; }
    </style>
</head>
<body>
<div class="container">
    <h2><i class="fa fa-edit"></i> ওষুধ সম্পাদনা</h2>
    <form method="POST">
        <label>ব্র্যান্ড নাম *</label>
        <input type="text" name="brand" required value="{{ drug.brand }}">

        <label>জেনেরিক নাম *</label>
        <input type="text" name="generic" required value="{{ drug.generic }}">

        <label>কোম্পানি *</label>
        <select name="company" required>
            {% for c in companies %}
            <option value="{{ c }}" {% if c==drug.company %}selected{% endif %}>{{ c }}</option>
            {% endfor %}
        </select>

        <label>ইন্ডিকেশন</label>
        <input type="text" name="indication" value="{{ drug.indication or '' }}">

        <label>ড্রাগ ক্লাস</label>
        <select name="drug_class">
            <option value="">— নির্বাচন করুন —</option>
            {% for c in classes %}
            <option value="{{ c }}" {% if c==drug.drug_class %}selected{% endif %}>{{ c }}</option>
            {% endfor %}
        </select>

        <label>ডোজ ফর্ম</label>
        <select name="dose_form">
            <option value="">— নির্বাচন করুন —</option>
            {% for f in forms %}
            <option value="{{ f }}" {% if f==drug.dose_form %}selected{% endif %}>{{ f }}</option>
            {% endfor %}
        </select>

        <label>শক্তি</label>
        <input type="text" name="strength" value="{{ drug.strength or '' }}">

        <label>মূল্য (৳)</label>
        <input type="number" name="price" step="0.01" value="{{ drug.price or '' }}">

        <div class="flex">
            <button type="submit" class="btn btn-primary"><i class="fa fa-save"></i> আপডেট</button>
            <a href="/drugs" class="btn btn-secondary">বাতিল</a>
        </div>
    </form>
</div>
</body>
</html>
''',

    "templates/companies.html": '''<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>কোম্পানি - MedEx</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family:'Segoe UI',sans-serif; background:#f4f7fc; color:#1a2a3a; }
        a { text-decoration:none; color:inherit; }
        .container { max-width:1200px; margin:0 auto; padding:0 15px; }
        .header { background:#fff; padding:16px 0; box-shadow:0 2px 10px rgba(0,0,0,0.05); }
        .header .flex { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; }
        .logo span { font-size:22px; font-weight:700; color:#0a1a2b; }
        .logo span i { color:#1a8c6e; }
        .btn { padding:10px 20px; border-radius:30px; border:none; cursor:pointer; font-weight:600; background:#1a8c6e; color:#fff; }
        .btn:hover { background:#147a5f; }
        .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:20px; padding:20px 0; }
        .card { background:#fff; border-radius:16px; padding:20px; border:1px solid #eef3f9; }
        .card h4 { color:#0a1a2b; margin-bottom:6px; }
        .card p { font-size:14px; color:#667a8a; margin:4px 0; }
        .action-links { margin-top:12px; }
        .action-links a { margin-right:12px; color:#1a8c6e; }
        .action-links a:hover { color:#147a5f; }
        .footer { background:#0a1a2b; color:#aab8c5; padding:20px 0; text-align:center; margin-top:30px; }
    </style>
</head>
<body>
<div class="header">
    <div class="container">
        <div class="flex">
            <div class="logo"><a href="/"><span>Med<i>Ex</i></span></a></div>
            <div>
                <a href="/" style="margin-right:16px;">হোম</a>
                <a href="/companies/add" class="btn">+ নতুন কোম্পানি</a>
            </div>
        </div>
    </div>
</div>

<div class="container">
    <h2 style="margin-top:20px;">🏢 ফার্মাসিউটিক্যাল কোম্পানি ({{ companies|length }})</h2>
    <div class="grid">
        {% for company in companies %}
        <div class="card">
            <h4>{{ company.name }}</h4>
            <p><i class="fa fa-map-marker"></i> {{ company.location or 'N/A' }}</p>
            <p><i class="fa fa-globe"></i> <a href="{{ company.website }}" target="_blank">{{ company.website or 'N/A' }}</a></p>
            <p><i class="fa fa-calendar"></i> প্রতিষ্ঠিত: {{ company.established or 'N/A' }}</p>
            <p style="font-size:13px; color:#8899aa;">{{ company.description or '' }}</p>
            <div class="action-links">
                <a href="/companies/edit/{{ company.id }}"><i class="fa fa-edit"></i> সম্পাদনা</a>
                <a href="/companies/delete/{{ company.id }}" onclick="return confirm('মুছতে চান?')" style="color:#dc2626;"><i class="fa fa-trash"></i> মুছুন</a>
            </div>
        </div>
        {% endfor %}
    </div>
</div>

<div class="footer">&copy; ২০২৬ MedEx — সর্বস্বত্ব সংরক্ষিত</div>
</body>
</html>
''',

    "templates/add_company.html": '''<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>নতুন কোম্পানি - MedEx</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family:'Segoe UI',sans-serif; background:#f4f7fc; color:#1a2a3a; padding:30px; }
        .container { max-width:700px; margin:auto; background:#fff; padding:30px; border-radius:20px; box-shadow:0 4px 20px rgba(0,0,0,0.06); }
        h2 { margin-bottom:20px; color:#0a1a2b; }
        label { display:block; font-weight:500; margin:12px 0 4px; font-size:14px; }
        input, textarea { width:100%; padding:12px 16px; border-radius:12px; border:1px solid #dce4ed; font-size:15px; }
        .btn { padding:12px 30px; border:none; border-radius:30px; cursor:pointer; font-weight:600; }
        .btn-primary { background:#1a8c6e; color:#fff; }
        .btn-primary:hover { background:#147a5f; }
        .btn-secondary { background:#e5ecf3; color:#1a2a3a; }
        .btn-secondary:hover { background:#c8d6e4; }
        .flex { display:flex; gap:12px; margin-top:20px; flex-wrap:wrap; }
    </style>
</head>
<body>
<div class="container">
    <h2><i class="fa fa-building"></i> নতুন কোম্পানি যোগ</h2>
    <form method="POST">
        <label>নাম *</label>
        <input type="text" name="name" required>

        <label>অবস্থান</label>
        <input type="text" name="location" placeholder="ঢাকা, চট্টগ্রাম">

        <label>ওয়েবসাইট</label>
        <input type="text" name="website" placeholder="https://example.com">

        <label>প্রতিষ্ঠিত সাল</label>
        <input type="number" name="established" placeholder="১৯৯০">

        <label>বর্ণনা</label>
        <textarea name="description" rows="4"></textarea>

        <div class="flex">
            <button type="submit" class="btn btn-primary">সংরক্ষণ</button>
            <a href="/companies" class="btn btn-secondary">বাতিল</a>
        </div>
    </form>
</div>
</body>
</html>
''',

    "templates/edit_company.html": '''<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>কোম্পানি সম্পাদনা - MedEx</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family:'Segoe UI',sans-serif; background:#f4f7fc; color:#1a2a3a; padding:30px; }
        .container { max-width:700px; margin:auto; background:#fff; padding:30px; border-radius:20px; box-shadow:0 4px 20px rgba(0,0,0,0.06); }
        h2 { margin-bottom:20px; color:#0a1a2b; }
        label { display:block; font-weight:500; margin:12px 0 4px; font-size:14px; }
        input, textarea { width:100%; padding:12px 16px; border-radius:12px; border:1px solid #dce4ed; font-size:15px; }
        .btn { padding:12px 30px; border:none; border-radius:30px; cursor:pointer; font-weight:600; }
        .btn-primary { background:#1a8c6e; color:#fff; }
        .btn-primary:hover { background:#147a5f; }
        .btn-secondary { background:#e5ecf3; color:#1a2a3a; }
        .btn-secondary:hover { background:#c8d6e4; }
        .flex { display:flex; gap:12px; margin-top:20px; flex-wrap:wrap; }
    </style>
</head>
<body>
<div class="container">
    <h2><i class="fa fa-edit"></i> কোম্পানি সম্পাদনা</h2>
    <form method="POST">
        <label>নাম *</label>
        <input type="text" name="name" required value="{{ company.name }}">

        <label>অবস্থান</label>
        <input type="text" name="location" value="{{ company.location or '' }}">

        <label>ওয়েবসাইট</label>
        <input type="text" name="website" value="{{ company.website or '' }}">

        <label>প্রতিষ্ঠিত সাল</label>
        <input type="number" name="established" value="{{ company.established or '' }}">

        <label>বর্ণনা</label>
        <textarea name="description" rows="4">{{ company.description or '' }}</textarea>

        <div class="flex">
            <button type="submit" class="btn btn-primary">আপডেট</button>
            <a href="/companies" class="btn btn-secondary">বাতিল</a>
        </div>
    </form>
</div>
</body>
</html>
'''
}

# ============================================================
# ফাইল তৈরি করা
# ============================================================
def create_project():
    # medex ফোল্ডার তৈরি
    if os.path.exists('medex'):
        shutil.rmtree('medex')
    os.makedirs('medex')
    os.makedirs('medex/templates')

    # সব ফাইল তৈরি
    for filename, content in FILES.items():
        if filename.startswith('templates/'):
            path = os.path.join('medex', filename)
        else:
            path = os.path.join('medex', filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'✅ তৈরি: {path}')

    print('\n🎉 সম্পূর্ণ MedEx প্রোজেক্ট তৈরি হয়েছে!')
    print('📁 লোকেশন: ./medex/')
    print('\n🚀 চালানোর জন্য:')
    print('  cd medex')
    print('  pip install -r requirements.txt')
    print('  python app.py')
    print('  👉 http://127.0.0.1:5000')

if __name__ == '__main__':
    create_project()
