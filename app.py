from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.secret_key = 'secret123'  # 🔑 المفتاح السري (يكفي هذا السطر فقط)

socketio = SocketIO(app, cors_allowed_origins="*")  # ⚠️ أضف هذه للسماح بجميع المصادر (للتطوير فقط)

# استيراد ملفات المسارات و Socket.IO handlers
from routes import *
from sockets import *

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=3000, debug=True)  # ⚠️ استخدم socketio.run فقط