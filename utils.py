import random
import string
import json
import os


# ---------- مسارات الملفات ----------
TEAMS_FILE = "data/teams_data.json"

# ---------- توليد كود عشوائي للفريق ----------
def generate_team_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


# ---------- انشاء لعبة جديدة ومسح جميع البيانات السابقة ----------
def reset_full_game():
    red_code = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))
    blue_code = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))
    letters = random.sample(list("أبجدھوزحطيكلمنسعفصقرشتثخذضظغ"), 25)

    data = {
        "red": {
            "code": red_code,
            "buzzer_pressed": False,
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
            "buzzer_pressed": False,
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
        json.dump(data, f, ensure_ascii=False, indent=4)

    return red_code, blue_code, letters, {"red": False, "blue": False}, {}


# ---------- إنشاء ملف الجيسون لأول مرة ----------
def initialize_hex_game():
    red_code = generate_team_code()
    blue_code = generate_team_code()
    letters = random.sample(list("أبجدھوزحطيكلمنسعفصقرشتثخذضظغ"), 25)

    game_data = {
        "red": {
            "code": red_code,
            "buzzer_pressed": False,
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
            "buzzer_pressed": False,
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

    return red_code, blue_code, letters, {"red": False, "blue": False}, {}


# ---------- تحميل بيانات الفرق ----------
def load_teams_data():
    if not os.path.exists(TEAMS_FILE):
        initialize_hex_game()

    with open(TEAMS_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            else:
                print("❌ تحذير: ملف data/teams_data.json لا يحتوي على قاموس!")
                return {}
        except json.JSONDecodeError:
            print("❌ تحذير: فشل قراءة ملف JSON!")
            return {}


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
