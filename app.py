import os
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

# 載入環境變數
load_dotenv()

# 初始化 FastAPI
app = FastAPI(title="Stock LINE Bot")

# Jinja2 樣板設定 (用於前端網頁展示)
templates = Jinja2Templates(directory="templates")

# 從環境變數讀取 LINE Bot 憑證
channel_secret = os.getenv('LINE_CHANNEL_SECRET', '')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')

# 初始化 LINE SDK v3 的 Configuration 與 WebhookHandler
configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(channel_secret)

# ---------------------------------------------------------
# API 路由區塊
# ---------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首頁或管理介面"""
    try:
        return templates.TemplateResponse(request=request, name="index.html")
    except Exception:
        return HTMLResponse("<h1>Stock LINE Bot 伺服器運作中！</h1><p>請確認 templates/index.html 檔案存在。</p>")

@app.get("/api/health")
async def health_check():
    """系統健康檢查"""
    return {"status": "ok"}

@app.post("/api/webhook")
async def webhook_callback(request: Request, background_tasks: BackgroundTasks):
    """LINE Webhook 接收端點"""
    # 取得 X-Line-Signature 標頭
    signature = request.headers.get('X-Line-Signature')
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature.")

    body = await request.body()
    body_str = body.decode('utf-8')

    try:
        # 必須在 1 秒內回傳 HTTP 200 給 LINE，因此將事件處理交由背景任務 (BackgroundTasks) 執行
        background_tasks.add_task(handler.handle, body_str, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        raise HTTPException(status_code=400, detail="Invalid signature.")
    except Exception as e:
        print(f"Error handling webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")

    return JSONResponse(content={"status": "ok"})

# ---------------------------------------------------------
# LINE Bot 訊息處理邏輯區塊
# ---------------------------------------------------------

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    """處理接收到的文字訊息"""
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        user_text = event.message.text
        
        # TODO: 整合 stock_service (股價查詢) 與 ai_service (新聞摘要/問答)
        # 這裡先做基本的 Echo 測試
        reply_text = f"您輸入了：{user_text}\n(這是一個測試回覆，更多功能建構中...)"
        
        # 呼叫 Reply API 回覆使用者
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )
