# ===== নতুন ফাংশন: কন্টেন্ট আইডিয়া জেনারেটর =====
def generate_content_ideas(topic):
    ideas = [
        f"📌 {topic} এর ৫টি সিক্রেট যা কেউ জানে না",
        f"📌 {topic} দিয়ে মাসে ৫০,০০০ টাকা আয়ের উপায়",
        f"📌 {topic} শেখার সেরা ৩টি ফ্রি রিসোর্স",
        f"📌 {topic} এ নতুনদের করা ৭টি ভুল",
        f"📌 {topic} এর ভবিষ্যৎ: ২০২৭ সালে কী হবে?"
    ]
    hooks = [
        f"🔥 'আমি {topic} নিয়ে ১০ বছর ধরে কাজ করছি, এবং এই একটি জিনিস আমি কাউকে বলিনি...'",
        f"💡 '{topic} এ সফল হওয়ার চাবিকাঠি হলো...'",
        f"⚡ '{topic} নিয়ে সবাই যে ভুলটা করে, সেটা হলো...'"
    ]
    thumbnails = [
        f"🎨 কালার: নীল + সোনালি | টেক্সট: 'বড় চমক!' | ইমেজ: একটি চাবি",
        f"🎨 কালার: লাল + সাদা | টেক্সট: 'ভুল করবেন না!' | ইমেজ: একটি বিস্ময় চিহ্ন"
    ]
    return {
        "ideas": "\n".join(ideas),
        "hooks": "\n".join(hooks),
        "thumbnails": "\n".join(thumbnails)
    }

# ===== নতুন API রাউট =====
@app.route('/api/ideas', methods=['POST'])
def api_ideas():
    topic = request.get_json().get('topic', 'এই টপিক')
    result = generate_content_ideas(topic)
    return jsonify({
        "result": f"📌 **কন্টেন্ট আইডিয়াস:**\n{result['ideas']}\n\n🎯 **হুক:**\n{result['hooks']}\n\n🖼️ **থাম্বনেইল আইডিয়া:**\n{result['thumbnails']}"
    })
