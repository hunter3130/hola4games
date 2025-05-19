from flask_socketio import emit
from app import socketio
import json
from utils import use_helper  # لازم تتأكد تستوردها من ملفك اللي فيه المساعدات

first_buzzer = None

@socketio.on("helper_used")
def handle_helper_used(data):
    team = data.get("team")
    helper = data.get("helper")

    if not team or not helper:
        return  # تحقق أساسي

    use_helper(team, helper)  # تحدث teams_data.json

    # نرسل إشعار للمستخدمين أن المساعدة تم استخدامها
    emit("helper_update", {"team": team, "helper": helper}, broadcast=True)

    # نرسل للمستخدمين لتعطيل الزر (على حسب المنطق في JS)
    emit("disable_helper", {"team": team, "helper": helper}, broadcast=True)


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
