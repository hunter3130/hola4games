from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_socketio import SocketIO, emit
import random
import string
import json
import os

app = Flask(__name__)

app.secret_key = 'secret123'
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

first_buzzer = None

def generate_team_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def initialize_hex_game():
    red_code = generate_team_code()
    blue_code = generate_team_code()

    game_data = {
        "game": "hex_game",
        "red_code": red_code,
        "blue_code": blue_code,
        "started": False
    }

    with open('game_codes.json', 'w') as f:
        json.dump(game_data, f)

    return red_code, blue_code

@app.route('/', methods=['GET', 'POST'])
def index():
    # if request.method == 'POST':
        # code = request.form.get('code').strip()
        # game = games.get(code)
        # if game and game['active']:
        #     return redirect(url_for('participant', code=code))
        # else:
        #     flash('الكود غير صحيح أو اللعبة غير شغالة حالياً.')
        #     return render_template('index.html')
     return render_template('index.html')

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
           flash("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
           return render_template('login.html')
    return render_template('login.html')

@app.route('/admin', endpoint='admin_page')
def admin_page():
    if 'admin' not in session:
        return redirect(url_for('login'))
    else:
        # توليد الأكواد فقط إذا ما تم توليدها من قبل
        if 'red_code' not in session or 'blue_code' not in session:
            session['red_code'] = generate_team_code()
            session['blue_code'] = generate_team_code()

        return render_template('admin.html', red_code=session['red_code'], blue_code=session['blue_code'])

@app.route('/admin/start_game')
def start_game():
    if 'username' not in session:
        return redirect(url_for('login'))

    red_code, blue_code = initialize_hex_game()

    return render_template('hex_game.html', red_code=red_code, blue_code=blue_code)

@app.route('/contestant')
def contestant():
    return render_template('participant.html', team=session.get('team'))

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

    # نداء دالة البداية لتوليد الأكواد
    red_code, blue_code = initialize_hex_game()

    return render_template('hex_game.html',
                           letters=selected_letters,
                           red_code=red_code,
                           blue_code=blue_code)

@app.route('/four-in-row')
def four_in_row():
    return render_template('four_in_row.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/participant/<code>')
def participant(code):
    try:
        with open('game_codes.json') as f:
            game_data = json.load(f)
    except FileNotFoundError:
        flash('لا توجد لعبة حالياً.')
        return redirect(url_for('index'))

    if code not in [game_data['red_code'], game_data['blue_code']]:
        flash('الكود غير صحيح أو اللعبة غير شغالة.')
        return redirect(url_for('index'))

    # تحديد الفريق من الكود
    team = 'red' if code == game_data['red_code'] else 'blue'
    session['team'] = team

    return render_template('participant.html', code=code, team=team)

@app.route('/join', methods=['GET', 'POST'])
def join_game():
    error = None
    if request.method == 'POST':
        code = request.form['code'].strip()
        try:
            with open('game_codes.json') as f:
                game_data = json.load(f)
        except FileNotFoundError:
            error = 'لا توجد لعبة حالياً.'
            return render_template('index.html', error=error)

        if code == game_data.get('red_code'):
            session['team'] = 'red'
            return redirect(url_for('participant', code=code))
        elif code == game_data.get('blue_code'):
            session['team'] = 'blue'
            return redirect(url_for('participant', code=code))
        else:
            error = '❌ كود غير صحيح'

    return render_template('index.html', error=error)

if __name__ == '__main__':
    socketio.run(app, debug=True)
