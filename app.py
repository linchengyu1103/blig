import time
import os
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
    print("錯誤：找不到 frames.txt 檔案！")
    FRAMES = ["ERROR: frames.txt not found."]
except Exception as e:
    print(f"讀取 frames.txt 時發生錯誤: {e}")
    FRAMES = ["ERROR: Failed to load animation."]

# 如果動畫幀為空，提供一個錯誤提示
if not FRAMES:
    FRAMES = ["ERROR: No frames found in frames.txt."]

# --- 動畫播放函式 ---

def generate_animation():
    """生成並持續輸出動畫幀到 HTTP 串流"""
    
    # 這是 Web 服務的標頭，確保內容被立即輸出
    yield "Content-Type: text/plain; charset=utf-8\r\n\r\n"
    
    # 無限循環播放動畫
    while True:
        for frame in FRAMES:
            # *** 注意：這裡我們不再發送清除畫面的指令 ***
            # 因為你的 'frame' 內容開頭已經包含了 '[H'，
            # 它會自行將游標移到頂部，實現「清除」的效果。
            
            # 1. 輸出動畫幀 (包含 [H)
            yield frame
            
            # 2. 延遲
            time.sleep(FRAME_DELAY)

# --- 伺服器設定 (使用 Flask) ---
app = Flask(__name__)

@app.route('/')
def stream_animation():
    """處理根路徑請求，將動畫串流出去"""
    return Response(generate_animation(), mimetype='text/plain')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
