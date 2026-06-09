from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import time
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 🧠 كاش متطور مقسم حسب التاريخ لتوفير الباقة وسرعة الاستجابة
global_cache = {}
CACHE_DURATION = 20  # تحديث كل 20 ثانية

API_TOKEN = os.getenv("FOOTBALL_API_TOKEN")
URL = "https://api.football-data.org/v4/matches"

@app.route('/api/live-scores', methods=['GET'])
def get_live_scores():
    # استقبال التاريخ المطلق من الواجهة (مثال: 2026-06-10)
    # إذا لم يرسل المستخدم تاريخاً، السيرفر سيجلب تاريخ اليوم تلقائياً
    target_date = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))
    current_time = time.time()
    
    # التحقق من الكاش الخاص بهذا التاريخ تحديداً
    if target_date not in global_cache or (current_time - global_cache[target_date]["last_updated"]) > CACHE_DURATION:
        try:
            headers = {"X-Auth-Token": API_TOKEN}
            # الفلترة الذكية بالتواريخ لجلب المباريات السابقة والقادمة والحالية بدقة
            params = {
                "dateFrom": target_date,
                "dateTo": target_date
            } 
            response = requests.get(URL, headers=headers, params=params, timeout=5)
            
            if response.status_code == 200:
                if target_date not in global_cache:
                    global_cache[target_date] = {}
                global_cache[target_date]["data"] = response.json().get("matches", [])
                global_cache[target_date]["last_updated"] = current_time
                print(f"🔄 [Global Cache] تم تحديث داتا المباريات للتاريخ: {target_date}")
        except Exception as e:
            print(f"⚠️ خطأ في السيرفر: {e}")
            
    return jsonify({"global_matches": global_cache.get(target_date, {}).get("data", [])})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
