import time
import os
import json # 匯入 json 模組
from flask import Flask, Response

# --- 設定 ---
# 播放速度：每幀之間的延遲時間（秒）。
FRAME_DELAY = 0.2
# *** 這裡改成你檔案內的分隔符號 ***
# 因為你的幀本身已經包含了清除畫面的控制碼，所以我們將它設為分隔符號。
FRAME_DELIMITER = "---FRAME---" 


# --- 自動讀取動畫幀 ---
try:
    with open("blig.txt", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 使用分隔符號將整個檔案內容切分成幀
    FRAMES = content.split(FRAME_DELIMITER)
    
    # 清理掉空的元素（例如檔案結尾多餘的分隔符號）
    # 因為你的每一幀都包含了定位符號 ([H)，所以我們會將多餘的空白移除
    FRAMES = [frame.strip() for frame in FRAMES if frame.strip()]
    
except FileNotFoundError:
    print("錯誤：找不到 blig.txt 檔案！")
    FRAMES = ["ERROR: blig.txt not found."]
except Exception as e:
    print(f"讀取 blig.txt 時發生錯誤: {e}")
    FRAMES = ["ERROR: Failed to load animation."]

# 如果動畫幀為空，提供一個錯誤提示
if not FRAMES:
    FRAMES = ["ERROR: No frames found in blig.txt."]

# --- 動畫播放函式 ---

def generate_animation():
    """生成並持續輸出動畫幀到 HTTP 串流"""
    
    # 這是 Web 服務的標頭，確保內容被立即輸出
    yield "Content-Type: text/plain; charset=utf-8\r\n\r\n"
    
    # 無限循環播放動畫
    while True:
        for frame in FRAMES:
            # 1. 輸出動畫幀 (包含 [H)
            yield frame
            
            # 2. 延遲
            time.sleep(FRAME_DELAY)

# --- 伺服器設定 (使用 Flask) ---
app = Flask(__name__)

# 路由 1: 專供瀏覽器或非 cURL 工具訪問的根路徑
@app.route('/')
def web_error_message():
    """處理根路徑請求，輸出 JSON 錯誤訊息"""
    
    # 建立您想要的錯誤訊息字典
    error_data = {"error": "You almost ruined a good surprise. Come on, curl it in terminal."}
    
    # 將字典轉換為 JSON 格式的字串
    json_output = json.dumps(error_data)
    
    # 返回 Response 物件，設定 Content-Type 為 application/json
    return Response(
        json_output,
        mimetype='application/json',
        status=404 # 可選：設定 HTTP 狀態碼為 404 Not Found 或 400 Bad Request
    )


# 路由 2: 專供終端機 cURL 訪問的動畫串流路徑
@app.route('/curl')
def stream_animation():
    """處理 /curl 路徑請求，將動畫串流出去"""
    # 注意：這裡我們將動畫移動到 /curl 路徑
    return Response(generate_animation(), mimetype='text/plain')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
