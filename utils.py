import random
import string
import json
import os

# ---------- مسارات الملفات ----------
TEAMS_FILE = "teams_data.json"

# ---------- توليد كود عشوائي للفريق ----------
def generate_team_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# ---------- انشاء لعبة جديدة ومسح جميع البيانات السابقة ---------
def reset_full_game():
    red_code = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))
    blue_code = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))
    letters = random.sample(list("أبجدھوزحطيكلمنسعفصقرشتثخذضظغ"), 25)

    data = {
        "red_code": red_code,
        "blue_code": blue_code,
        "letters": letters,
        "helpers": {
            "red": {"skip": False, "hint": False, "fifty": False},
            "blue": {"skip": False, "hint": False, "fifty": False}
        }
    }

    with open("teams_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return red_code, blue_code, letters

# ---------- إنشاء ملف الجيسون لأول مرة ----------
def initialize_hex_game():
    red_code = generate_team_code()
    blue_code = generate_team_code()

    game_data = {
        "red": {
            "code": red_code,
            "helpers": {
                "تحدي القرصان": False,
                "تحدي البالون": False,
                "تغيير السؤال": False,
                "طلب خيارات": False,
                "تلميح على الإجابة": False,
                "كرت أحمر": False
            }
        },
        "blue": {
            "code": blue_code,
            "helpers": {
                "تحدي القرصان": False,
                "تحدي البالون": False,
                "تغيير السؤال": False,
                "طلب خيارات": False,
                "تلميح على الإجابة": False,
                "كرت أحمر": False
            }
        }
    }

    with open(TEAMS_FILE, "w", encoding="utf-8") as f:
        json.dump(game_data, f, ensure_ascii=False, indent=4)

    return red_code, blue_code


# ---------- تحميل بيانات الفرق ----------
def load_teams_data():
    if not os.path.exists(TEAMS_FILE):
        initialize_hex_game()
    with open(TEAMS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# ---------- حفظ البيانات ----------
def save_teams_data(data):
    with open(TEAMS_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


# ---------- استخدام بطاقة مساعدة ----------
def use_helper(team_name, helper_name):
    data = load_teams_data()
    if team_name in data and helper_name in data[team_name]["helpers"]:
        data[team_name]["helpers"][helper_name] = True
        save_teams_data(data)


# ---------- إعادة تعيين كل المساعدات ----------
def reset_helpers():
    data = load_teams_data()
    for team in data:
        for helper in data[team]["helpers"]:
            data[team]["helpers"][helper] = False
    save_teams_data(data)


# ---------- التحقق إذا المساعدة استُخدمت ----------
def is_helper_used(team_name, helper_name):
    data = load_teams_data()
    return data.get(team_name, {}).get("helpers", {}).get(helper_name, False)

