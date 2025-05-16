from flask import Flask, render_template, redirect, url_for, request, session
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)

app.secret_key = 'secret123'
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

first_buzzer = None

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "adminpass":
            session['username'] = username
            return redirect(url_for('dashboard'))
        elif username == "user" and password == "user":
            session['username'] = username
            return redirect(url_for('contestant'))
        else:
            return "اسم المستخدم أو كلمة المرور غير صحيحة", 401
    return render_template('login.html')

@app.route('/admin', endpoint='admin_page')
def admin_page():
    return render_template('admin.html')

@app.route('/contestant')
def contestant():
    return render_template('contestant.html')

@socketio.on('start_question')
def handle_start_question(data):
    global first_buzzer
    first_buzzer = None
    question = "ما هو لون السماء؟"
    emit('show_question', {'question': question, 'team': 'لا أحد'}, broadcast=True)

@socketio.on('buzz')
def handle_buzz(data):
    global first_buzzer
    if not first_buzzer:
        first_buzzer = data['team']
        emit('buzzer_result', {'team': first_buzzer}, broadcast=True)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/hex-game')
def hex_game():
    arabic_letters = list("أبجدھوزحطيكلمنسعفصقرشتثخذضظغ")
    selected_letters = random.sample(arabic_letters, 25)
    print("الحروف المختارة:", selected_letters)  # تظهر في الكونسول السيرفر
    return render_template('hex_game.html', letters=selected_letters)

@app.route('/four-in-row')
def four_in_row():
    return render_template('four_in_row.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    socketio.run(app, debug=True)
