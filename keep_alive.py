from flask import Flask
from threading import Thread
import logging

app = Flask('')

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Monitoring Bot</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 40px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: rgba(255,255,255,0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }
            h1 { text-align: center; }
            .status { 
                background: rgba(255,255,255,0.2); 
                padding: 15px; 
                margin: 10px 0; 
                border-radius: 8px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 API Monitoring Bot</h1>
            <p>Bot đang hoạt động và tự động ping các API:</p>
            <div class="status">
                <strong>📋 Danh sách API:</strong><br>
                • HitClub ChatGPT<br>
                • B52 Chaoconnha<br>
                • Lau Cua Gay Sex MD5
            </div>
            <div class="status">
                <strong>⏰ Tần suất:</strong> 5 phút/lần<br>
                <strong>🔄 Tự động:</strong> Đang chạy
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return {"status": "healthy", "message": "Bot is running"}

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    server = Thread(target=run)
    server.daemon = True
    server.start()
    logging.info("🌐 Keep-alive server đã khởi động trên port 8080")
