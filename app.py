from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

clients = {}

@app.route('/')
def admin():
    return render_template('admin.html')

@app.route('/target')
def target():
    return render_template('target.html')

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in clients:
        del clients[request.sid]
    emit('update-clients', clients, broadcast=True)
    print(f'Client disconnected: {request.sid}')

@socketio.on('client-data')
def handle_client_data(data):
    # Merge data with existing or create new
    if request.sid not in clients:
        clients[request.sid] = {}
    clients[request.sid].update(data)
    clients[request.sid]['id'] = request.sid
    # Broadcast to all (admin will receive it)
    emit('update-clients', clients, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
