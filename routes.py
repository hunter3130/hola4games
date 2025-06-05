from flask import render_template, redirect, url_for, flash, request, session
import random
import string
import json
import os
from app import app, socketio
from utils import generate_team_code, initialize_hex_game, reset_full_game

@app.route('/', methods=['GET', 'POST'])
def index():
      session.clear()
      return render_template('index.html')

# ----------توليد لعبة جديدة---------------
@app.route('/start_new_game', methods=['GET', 'POST'])
def start_new_game():
    
    red_code, blue_code, letters, buzzer_pressed, helpers = initialize_hex_game()
    session['red_code'] = red_code
    session['blue_code'] = blue_code
    flash("✅ تم إنشاء لعبة جديدة بنجاح")
    return redirect(url_for('hex_game'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "adminpass":
            session['username'] = username
            session['logged_in'] = True
            session['admin'] = True
            session['logged_in'] = True
            session.pop('in_game', None)
            return redirect(url_for('dashboard'))
        elif username == "user" and password == "user":
            session['username'] = username
            session['logged_in'] = True
            session.pop('in_game', None)
            return redirect(url_for('contestant'))
        else:
            flash("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
            # return redirect(url_for('login'))
            return "✅ تم تسجيل الدخول كأدمن"

    return render_template('login.html')

@app.route('/admin', endpoint='admin_page')
def admin_page():
    if not session.get('admin'):
        return "✅ تم تسجيل الدخول كأدمن"

        # return redirect(url_for('login'))
    if 'red_code' not in session or 'blue_code' not in session:
        session['red_code'] = generate_team_code()
        session['blue_code'] = generate_team_code()
    return render_template('admin.html', red_code=session['red_code'], blue_code=session['blue_code'])

@app.route('/admin/start_game')
def start_game():
    if 'username' not in session:
        return redirect(url_for('login'))

    red_code, blue_code, letters, buzzer_pressed, helpers = initialize_hex_game()
    return render_template('hex_game.html', red_code=red_code, blue_code=blue_code)

@app.route('/contestant')
def contestant():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('participant.html', team=session.get('team'))

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/hex-game')
def hex_game():
    try:
        if not os.path.exists("data/teams_data.json"):
            initialize_hex_game()

        with open('data/teams_data.json', 'r', encoding='utf-8') as f:
            game_data = json.load(f)
            red_code = game_data.get('red', {}).get('code', '')
            blue_code = game_data.get('blue', {}).get('code', '')
            buzzer_pressed = {
                "red": game_data.get('red', {}).get('buzzer_pressed', False),
                "blue": game_data.get('blue', {}).get('buzzer_pressed', False)
            }
            helpers = {
                "red": game_data.get('red', {}).get('helpers', {}),
                "blue": game_data.get('blue', {}).get('helpers', {})
            }
            selected_letters = game_data.get('letters', [])

            if not selected_letters:
                selected_letters = random.sample(list("أبجدھوزحطيكلمنسعفصقرشتثخذضظغ"), 25)
                game_data["letters"] = selected_letters
                with open('data/teams_data.json', 'w', encoding='utf-8') as f2:
                    json.dump(game_data, f2, ensure_ascii=False, indent=4)

    except FileNotFoundError:
        red_code, blue_code, selected_letters, buzzer_pressed, helpers = initialize_hex_game()

    return render_template('hex_game.html',
                           letters=selected_letters,
                           red_code=red_code,
                           blue_code=blue_code,
                           buzzer_pressed=buzzer_pressed,
                           helpers=helpers)

@app.route('/four-in-row')
def four_in_row():
    return render_template('four_in_row.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/participant/<code>')
def participant(code):
    try:
        with open('data/teams_data.json', encoding='utf-8') as f:
            game_data = json.load(f)
    except FileNotFoundError:
        flash('لا توجد لعبة حالياً.')
        return redirect(url_for('index'))

    red_code = game_data.get('red', {}).get('code')
    blue_code = game_data.get('blue', {}).get('code')

    if code not in [red_code, blue_code]:
        flash('الكود غير صحيح أو اللعبة غير شغالة.')
        return redirect(url_for('index'))

    team = 'red' if code == red_code else 'blue'
    session['team'] = team
    session['is_participant'] = True

    # قراءة حالة الفريق من ملف الحالة
    state_file = 'data/teams_data.json'
    team_state = {"buzzed": False, "helpers": []}

    if os.path.exists(state_file):
        with open(state_file, encoding='utf-8') as f:
            state_data = json.load(f)
            if team in state_data:
                team_state = state_data[team]

    return render_template('participant.html', code=code, team=team, game_data=game_data, team_state=team_state)

@app.route('/join', methods=['GET', 'POST'])
def join_game():
    error = None
    session.clear()
    session['in_game'] = True
    if request.method == 'POST':
        code = request.form['code'].strip()
        try:
            with open('data/teams_data.json', encoding='utf-8') as f:
                game_data = json.load(f)
        except FileNotFoundError:
            error = 'لا توجد لعبة حالياً.'
            return render_template('index.html', error=error)

        red_code = game_data.get('red', {}).get('code')
        blue_code = game_data.get('blue', {}).get('code')

        if code == red_code:
            session['team'] = 'red'
            session['is_participant'] = True
            return redirect(url_for('participant', code=code))

        elif code == blue_code:
            session['team'] = 'blue'
            session['is_participant'] = True
            return redirect(url_for('participant', code=code))

        else:
            error = '❌ كود غير صحيح'

    return render_template('index.html', error=error)
