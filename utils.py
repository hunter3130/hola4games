import random
import string
import json
import os
import threading

# Lock for thread-safe team data access
team_data_lock = threading.Lock()

# ---------- مسارات الملفات ----------
TEAMS_FILE = "data/teams_data.json"
CELL_STATE_FILE = 'data/cell_states.json'

# ---------- توليد كود عشوائي للفريق ----------
def generate_team_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# ---------- إنشاء ملف الجيسون لأول مرة ----------
def initialize_hex_game():
    red_code = generate_team_code()
    blue_code = generate_team_code()
       # تهيئة الخلايا
    cell_states = {}
    for i in range(25):
        cell_id = f"cell_{i+1}"
        cell_states[cell_id] = {}

    write_cell_states(cell_states)
    
    letters = random.sample(list("أبجدھوزحطيكلمنسعفصقرشتثخذضظغ"), 25)

    game_data = {
        "red": {
            "code": red_code,
            "buzzer_pressed": False,
            "helpers": default_helpers()
        },
        "blue": {
            "code": blue_code,
            "buzzer_pressed": False,
            "helpers": default_helpers()
        }
    }

    save_teams_data(game_data)
    return red_code, blue_code, letters, {"red": False, "blue": False}, {}

# ---------- إنشاء مساعدات افتراضية ----------
def default_helpers():
    return {
        "تحدي القرصان": False,
        "تحدي البالون": False,
        "تغيير السؤال": False,
        "طلب خيارات": False,
        "تلميح على الإجابة": False,
        "كرت أحمر": False
    }

# ---------- انشاء لعبة جديدة ومسح جميع البيانات السابقة ----------
def reset_full_game():
    red_code = generate_team_code()
    blue_code = generate_team_code()
    letters = random.sample(list("أبجدھوزحطيكلمنسعفصقرشتثخذضظغ"), 25)

    data = {
        "red": {
            "code": red_code,
            "buzzer_pressed": False,
            "helpers": default_helpers()
        },
        "blue": {
            "code": blue_code,
            "buzzer_pressed": False,
            "helpers": default_helpers()
        }
    }

    save_teams_data(data)
    return red_code, blue_code, letters, {"red": False, "blue": False}, {}

def read_team_data():
    with team_data_lock:
        try:
            with open(TEAMS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # التأكد من وجود الهيكل الأساسي إذا كان الملف فارغاً
                if "red" not in data:
                    data["red"] = {"helpers": default_helpers()}
                if "blue" not in data:
                    data["blue"] = {"helpers": default_helpers()}
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {"red": {"helpers": default_helpers()}, "blue": {"helpers": default_helpers()}}
        

        
# ---------- تحميل بيانات الفرق ----------
def load_teams_data():
    if not os.path.exists(TEAMS_FILE):
        initialize_hex_game()

    try:
        with open(TEAMS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            else:
                print("❌ تحذير: ملف JSON لا يحتوي على قاموس!")
                return {}
    except json.JSONDecodeError:
        print("❌ تحذير: فشل قراءة ملف JSON!")
        return {}
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return {}

# ---------- حفظ البيانات ----------
def save_teams_data(data):
    try:
        with open(TEAMS_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"❌ خطأ أثناء الحفظ: {e}")

# ---------- استخدام بطاقة مساعدة ----------
def use_helper(team_name, helper_name):
    data = load_teams_data()
    if team_name in data and helper_name in data[team_name].get("helpers", {}):
        data[team_name]["helpers"][helper_name] = True
        save_teams_data(data)

# ---------- إعادة تعيين كل المساعدات ----------
def reset_helpers():
    data = load_teams_data()
    for team in data:
        for helper in data[team].get("helpers", {}):
            data[team]["helpers"][helper] = False
    save_teams_data(data)

# ---------- التحقق إذا المساعدة استُخدمت ----------
def is_helper_used(team_name, helper_name):
    data = load_teams_data()
    return data.get(team_name, {}).get("helpers", {}).get(helper_name, False)

# ---------- ضبط حالة البازر لفريق معين ----------
def set_buzzer(team_name, pressed=True):
    data = load_teams_data()
    if team_name in data:
        data[team_name]["buzzer_pressed"] = pressed
        save_teams_data(data)

# ---------- إعادة تعيين البازر لجميع الفرق ----------
def reset_buzzer():
    data = load_teams_data()
    for team in data:
        if isinstance(data[team], dict):
            data[team]["buzzer_pressed"] = False
    save_teams_data(data)

# ---------- التحقق إذا فريق محدد ضغط البازر ----------
def is_buzzer_pressed(team_name):
    data = load_teams_data()
    return data.get(team_name, {}).get("buzzer_pressed", False)

# ---------- التحقق إذا أي فريق ضغط البازر ----------
def any_buzzer_pressed():
    data = load_teams_data()
    return any(
        isinstance(data[team], dict) and data[team].get("buzzer_pressed", False)
        for team in data
    )
#--------  دالة قراءة الخلايا ------------
def read_cell_states():
    try:
        with open(CELL_STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
#-------- دالة الكتابة للخلايا
def write_cell_states(data):
    try:
        with open(CELL_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error writing cell states: {e}")


def check_win_from_json():
    cell_states = read_cell_states()
    board_size = 5
    
    # تحويل بيانات الخلايا إلى مصفوفة ثنائية الأبعاد
    board_state = [[None for _ in range(board_size)] for _ in range(board_size)]
    
    for cell_id, state in cell_states.items():
        try:
            row, col = map(int, cell_id.split('-'))
            if 0 <= row < board_size and 0 <= col < board_size:
                board_state[row][col] = state.get('team')
        except (ValueError, AttributeError):
            continue
    
    # دالة DFS للتحقق من الاتصال
    def dfs(row, col, team, visited):
        if (row < 0 or row >= board_size or 
            col < 0 or col >= board_size or 
            visited[row][col] or 
            board_state[row][col] != team):
            return False
        
        visited[row][col] = True
        
        # الفوز للفريق الأحمر (من اليسار إلى اليمين)
        if team == "red" and col == board_size - 1:
            return True
        
        # الفوز للفريق الأزرق (من الأعلى إلى الأسفل)
        if team == "blue" and row == board_size - 1:
            return True
        
        # اتجاهات الحركة في شبكة سداسية
        directions = [
            [-1, 0], [-1, 1],
            [0, -1], [0, 1],
            [1, 0], [1, 1]
        ] if row % 2 == 0 else [
            [-1, -1], [-1, 0],
            [0, -1], [0, 1],
            [1, -1], [1, 0]
        ]
        
        for dr, dc in directions:
            if dfs(row + dr, col + dc, team, visited):
                return True
        return False
    
    # التحقق من فوز الفريق الأحمر
    visited = [[False for _ in range(board_size)] for _ in range(board_size)]
    for row in range(board_size):
        if board_state[row][0] == "red" and dfs(row, 0, "red", visited):
            return "red"
    
    # التحقق من فوز الفريق الأزرق
    visited = [[False for _ in range(board_size)] for _ in range(board_size)]
    for col in range(board_size):
        if board_state[0][col] == "blue" and dfs(0, col, "blue", visited):
            return "blue"
    
    return None