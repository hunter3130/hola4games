from flask import Flask, redirect, url_for
from flask_socketio import SocketIO

app = Flask(__name__)
app.secret_key = 'secret123'
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app)

# استيراد ملفات المسارات و Socket.IO handlers
from routes import *
from sockets import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
    socketio.run(app, debug=True)
