from flask import Flask, jsonify
from flask_cors import CORS
import requests
import time
import os  # المكتبة المسؤولة عن قراءة متغيرات البيئة بأمان

app = Flask(__name__)
CORS(app)

# 🧠 كاش الذاكرة المؤقتة للبطولات العالمية
global_cache = {
    "data": None,
    "last_updated": 0
}

CACHE_DURATION = 20  # تحديث كل 20 ثانية لتوفير الباقة

# 🔐 قراءة المفتاح سرياً من خوادم Render مباشرة بناءً على الاسم الذي اخترته
API_TOKEN = os.getenv("FOOTBALL_API_TOKEN")
URL = "https://api.football-data.org/v4/matches"

@app.route('/api/live-scores', methods=['GET'])
def get_live_scores():
    current_time = time.time()
    
    if global_cache["data"] is None or (current_time - global_cache["last_updated"]) > CACHE_DURATION:
        try:
            headers = {"X-Auth-Token": API_TOKEN}
            
            # ✨ التعديل السحري هنا: قمنا بإزالة {"status": "LIVE"} لجلب كل مباريات اليوم (القادمة، الجارية، والمنتهية)
            params = {} 
            
            response = requests.get(URL, headers=headers, params=params, timeout=5)
            
            if response.status_code == 200:
                global_cache["data"] = response.json().get("matches", [])
                global_cache["last_updated"] = current_time
                print("🔄 [Global Cache] تم تحديث داتا جميع مباريات اليوم الأوروبية والعالمية!")
        except Exception as e:
            print(f"⚠️ خطأ: {e}")
            
    return jsonify({"global_matches": global_cache["data"] or []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
