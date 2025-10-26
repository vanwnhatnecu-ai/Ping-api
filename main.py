import os
import requests
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import datetime

# Cấu hình logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Danh sách các API cần treo
APIS = [
    {
        'name': 'HitClub ChatGPT',
        'url': 'https://hitclub-chat-gpt-binn-new.onrender.com/api/history',
        'status': '❌ Chưa kiểm tra'
    },
    {
        'name': 'B52 Chaoconnha',
        'url': 'https://b52-chaoconnha-bobinn.onrender.com/api/history', 
        'status': '❌ Chưa kiểm tra'
    },
    {
        'name': 'Lau Cua Gay Sex MD5',
        'url': 'https://laucuagaysex-md5-phantichai.onrender.com/api/predict',
        'status': '❌ Chưa kiểm tra'
    }
]

# Hàm ping API
async def ping_api(api_info):
    """Ping một API và cập nhật trạng thái"""
    try:
        start_time = datetime.datetime.now()
        response = requests.get(api_info['url'], timeout=30)
        end_time = datetime.datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        if response.status_code == 200:
            api_info['status'] = f'✅ Online ({response_time:.2f}s)'
            api_info['last_success'] = datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')
            logger.info(f"✅ {api_info['name']} - Thành công trong {response_time:.2f}s")
        else:
            api_info['status'] = f'❌ Lỗi {response.status_code} ({response_time:.2f}s)'
            logger.warning(f"❌ {api_info['name']} - Lỗi {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        api_info['status'] = f'❌ Lỗi kết nối: {str(e)}'
        logger.error(f"❌ {api_info['name']} - Lỗi kết nối: {e}")

# Hàm ping tất cả API
async def ping_all_apis():
    """Ping tất cả các API cùng lúc"""
    logger.info("🔄 Bắt đầu ping tất cả API...")
    
    # Tạo tasks để ping đồng thời
    tasks = [ping_api(api) for api in APIS]
    await asyncio.gather(*tasks)
    
    logger.info("✅ Đã hoàn thành ping tất cả API")

# Hàm lên lịch ping
def setup_scheduler():
    """Thiết lập lịch ping tự động 5 phút/lần"""
    scheduler = AsyncIOScheduler()
    
    # Lên lịch ping mỗi 5 phút
    scheduler.add_job(
        ping_all_apis,
        trigger=IntervalTrigger(minutes=5),
        id='ping_apis',
        name='Ping APIs mỗi 5 phút',
        replace_existing=True
    )
    
    return scheduler

# Lệnh start cho bot Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gửi tin nhắn chào mừng khi người dùng bắt đầu"""
    user = update.effective_user
    welcome_text = f"""
🤖 Chào {user.mention_html()}!

Đây là bot treo API tự động. Bot sẽ tự động ping các API sau mỗi 5 phút:

📋 Danh sách API được theo dõi:
• HitClub ChatGPT
• B52 Chaoconnha  
• Lau Cua Gay Sex MD5

🛠 Các lệnh có sẵn:
/start - Hiển thị thông tin này
/status - Kiểm tra trạng thái API ngay lập tức
/ping - Ping tất cả API ngay lập tức

⏰ Bot đang chạy tự động!
    """
    await update.message.reply_html(welcome_text)

# Lệnh kiểm tra trạng thái
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hiển thị trạng thái hiện tại của tất cả API"""
    status_text = "📊 **TRẠNG THÁI API HIỆN TẠI**\n\n"
    
    for api in APIS:
        last_success = api.get('last_success', 'Chưa có dữ liệu')
        status_text += f"**{api['name']}**\n"
        status_text += f"🔗 {api['url']}\n"
        status_text += f"📊 {api['status']}\n"
        status_text += f"⏰ Thành công lúc: {last_success}\n\n"
    
    status_text += f"🕒 Cập nhật lúc: {datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')}"
    
    await update.message.reply_text(status_text, parse_mode='Markdown')

# Lệnh ping ngay lập tức
async def ping_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ping tất cả API ngay lập tức"""
    await update.message.reply_text("🔄 Đang ping tất cả API...")
    await ping_all_apis()
    await status(update, context)

# Hàm chính
def main():
    """Hàm chính để khởi chạy bot"""
    
    # Lấy token từ environment variable
    TELEGRAM_TOKEN = os.getenv('8318094060:AAGXPli-P7R2Fu4GvGwEi3NrpXaR9AlgbFM')
    if not TELEGRAM_TOKEN:
        logger.error("❌ Không tìm thấy TELEGRAM_TOKEN trong environment variables!")
        return
    
    # Khởi tạo ứng dụng Telegram
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Thêm các handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("ping", ping_now))
    
    # Thiết lập scheduler
    scheduler = setup_scheduler()
    scheduler.start()
    
    logger.info("🚀 Bot đang khởi động...")
    logger.info("⏰ Đã lên lịch ping tự động mỗi 5 phút")
    
    # Ping lần đầu khi khởi động
    asyncio.get_event_loop().run_until_complete(ping_all_apis())
    
    # Chạy bot
    application.run_polling()

if __name__ == '__main__':
    main()
