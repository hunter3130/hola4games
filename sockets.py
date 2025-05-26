from flask_socketio import emit
from app import socketio
import json
from utils import read_cell_states, use_helper, set_buzzer, reset_buzzer, is_buzzer_pressed, any_buzzer_pressed, write_cell_states

TEAM_DATA_FILE = 'data/teams_data.json'  # <-- تم التعديل هنا

def read_team_data():
    try:
        with open(TEAM_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # لو الملف مش موجود أو فيه خطأ ارجع بيانات أولية
        return {
            "red": {"helpers": {}},
            "blue": {"helpers": {}}
        }

def write_team_data(data):
    try:
        with open(TEAM_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error writing team data: {e}")

@socketio.on("helper_used")
def handle_helper_used(data):
    team = data.get("team")  # 'red' أو 'blue'
    helper = data.get("helper")

    if not team or not helper:
        return

    team_data = read_team_data()

    if team not in team_data:
        return

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
#------ تحديث اختيار الخلايا --------
@socketio.on("update_cell")
def handle_update_cell(data):
    cell_id = data.get("cellId")
    state = data.get("state")  # مثلاً {"team": "red", "color": "#f00"}

    if not cell_id or not state:
        return

    cell_states = read_cell_states()
    cell_states[cell_id] = state
    write_cell_states(cell_states)

    emit("cell_updated", {"cellId": cell_id, "state": state}, broadcast=True)

#------- طلب الخلايا -----
@socketio.on("get_cells")
def handle_get_cells():
    cell_states = read_cell_states()
    emit("cell_states", cell_states)

@socketio.on('connect')
def handle_connect():
    with open("buzzer.json") as f:
        state = json.load(f)
    emit("initial_state", state)

