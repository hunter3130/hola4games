from flask_socketio import emit
from app import socketio
import json
from utils import use_helper, set_buzzer, reset_buzzer, is_buzzer_pressed, any_buzzer_pressed

TEAM_DATA_FILE = 'data/teams_data.json'  # <-- تم التعديل هنا

def read_team_data():
    with open(TEAM_DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_team_data(data):
    with open(TEAM_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@socketio.on("helper_used")
def handle_helper_used(data):
    team = data.get("team")  # 'red' أو 'blue'
    helper = data.get("helper")

    if not team or not helper:
        return

    team_data = read_team_data()

    # تحقق من أن المساعدة لم تُستخدم من قبل
    if team_data[team]["helpers"].get(helper, False):
        return

    # تحديث حالة المساعدة
    team_data[team]["helpers"][helper] = True
    write_team_data(team_data)

    emit("helper_update", {"team": team, "helper": helper}, broadcast=True)
    emit("disable_helper", {"team": team, "helper": helper}, broadcast=True)

@socketio.on('start_question')
def handle_start_question(data):
    question = data.get("question", "ما هو لون السماء؟")
    emit('show_question', {'question': question, 'team': 'لا أحد'}, broadcast=True)

@socketio.on("buzz")
def handle_buzz(data):
    team = data.get("team")
    if not team:
        return

    if not any_buzzer_pressed():
        set_buzzer(team, True)
        emit("buzz", {"team": team}, broadcast=True)

@socketio.on("reset_buzzer")
def handle_reset_buzzer():
    reset_buzzer()
    emit("buzzer_reset", broadcast=True)
