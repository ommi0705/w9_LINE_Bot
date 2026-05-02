---
name: linebot-dev
description: 指導 AI 撰寫 LINE Bot 程式碼的最佳實踐與規範
---

# LINE Bot Development Skill

本指南提供使用 `line-bot-sdk-python` v3 開發 LINE Bot 的標準規範與最佳實踐。AI 在生成或修改 LINE Bot 相關程式碼時，必須嚴格遵守以下準則。

## 1. LINE Bot SDK Python v3 規範

強烈建議使用 `line-bot-sdk-python` v3。請確保專案依賴項中包含 `line-bot-sdk>=3.0.0`。

### v2 與 v3 差異對照表

| 功能 | v2 舊版寫法 | v3 新版寫法 | 說明 |
| --- | --- | --- | --- |
| **API Client 初始化** | `LineBotApi(access_token)` | `Configuration(access_token)`<br>`ApiClient(configuration)`<br>`MessagingApi(api_client)` | v3 採用 OpenAPI Generator 生成，需透過 `Configuration` 與 `ApiClient` 初始化各個 API 服務。 |
| **回覆訊息 API** | `line_bot_api.reply_message(reply_token, TextSendMessage(text='...'))` | `messaging_api.reply_message(ReplyMessageRequest(replyToken=..., messages=[TextMessage(text='...')]))` | 請求參數封裝進 `Request` 類別中，訊息模型也簡化為 `TextMessage` 等。 |
| **訊息模型命名** | `TextSendMessage` | `TextMessage` | 新版去除了 `Send` 字眼，直接使用訊息類型名稱（例如 `ImageMessage`, `FlexMessage`）。 |
| **例外處理** | `LineBotApiError` | `ApiException` | API 錯誤統一由 `linebot.v3.exceptions.ApiException` 處理。 |

## 2. Webhook + Handler 標準寫法範例

以下是使用 FastAPI 與 SDK v3 的標準 Webhook 結構：

```python
import os
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
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

app = FastAPI()

# 從環境變數讀取憑證
channel_secret = os.getenv('LINE_CHANNEL_SECRET', '')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')

configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(channel_secret)

@app.post("/callback")
async def callback(request: Request, background_tasks: BackgroundTasks):
    # 取得 X-Line-Signature 標頭
    signature = request.headers.get('X-Line-Signature')
    body = await request.body()
    body_str = body.decode('utf-8')

    try:
        # 將事件處理交由背景執行，以加速回傳 HTTP 200 給 LINE
        background_tasks.add_task(handler.handle, body_str, signature)
        
        # 若為非耗時任務，也可選擇直接處理：
        # handler.handle(body_str, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature.")
    except Exception as e:
        print(f"Error handling webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    # 建立 ApiClient 與 MessagingApi 實例
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        user_text = event.message.text
        
        # 呼叫 API 進行回覆
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=f"你說了：{user_text}")]
            )
        )
```

## 3. 常見地雷與注意事項

*   **Reply Token 限制：** 
    *   每個 `reply_token` **只能使用一次**。
    *   `reply_token` 有時間限制，通常為數十秒。若處理時間過長將會失效，遇到會超時的情境建議改用 Push Message（但需注意 Push Message 有計費限制）。
*   **環境變數與安全：** 
    *   **絕對不要**將 `CHANNEL_SECRET` 或 `CHANNEL_ACCESS_TOKEN` 寫死在程式碼中。必須透過 `.env` 檔案或系統環境變數讀取。
*   **耗時操作處理：** 
    *   LINE Platform 對 Webhook 的逾時限制非常嚴格（通常期望 1 秒內回傳 200 OK）。
    *   如果需要呼叫 LLM (如 Gemini/OpenAI)、查詢資料庫、處理圖片等耗時操作，**必須**使用背景任務 (如 FastAPI 的 `BackgroundTasks` 或 Celery/RQ) 處理，確保立刻回傳 HTTP 200 OK 給 LINE 伺服器，隨後再於背景利用 Reply 或 Push API 發送回應。

## 4. 所有事件與訊息類型列表

### Webhook Event Types
*   `MessageEvent`: 收到任何訊息時觸發。
*   `FollowEvent`: 使用者加好友 / 重新解除封鎖時觸發。
*   `UnfollowEvent`: 使用者封鎖帳號時觸發。
*   `JoinEvent`: Bot 被加入群組或聊天室時觸發。
*   `LeaveEvent`: Bot 離開群組或聊天室時觸發。
*   `PostbackEvent`: 使用者點擊 Postback 類型的選單或按鈕時觸發。
*   `BeaconEvent`: 使用者進入 LINE Beacon 範圍時觸發。
*   `MemberJoinedEvent` / `MemberLeftEvent`: 有其他使用者加入 / 離開群組或聊天室時觸發。

### Message Content Types (對應 MessageEvent)
*   `TextMessageContent`: 文字訊息
*   `ImageMessageContent`: 圖片訊息
*   `VideoMessageContent`: 影片訊息
*   `AudioMessageContent`: 語音訊息
*   `LocationMessageContent`: 位置訊息
*   `StickerMessageContent`: 貼圖訊息
*   `FileMessageContent`: 檔案訊息

## 5. 開發前 Checklist

- [ ] 確認專案 `requirements.txt` 中已加入 `line-bot-sdk>=3.0.0`。
- [ ] 檢查 `.env` 中是否已正確配置 `LINE_CHANNEL_SECRET` 與 `LINE_CHANNEL_ACCESS_TOKEN`，且 `.env` 檔案已加入 `.gitignore`。
- [ ] 確認 Webhook 架構能夠正常接收 POST 請求並在時限內回傳 HTTP 200 OK。
- [ ] 確認架構上針對 LLM 呼叫等耗時操作，已規劃好背景處理 (BackgroundTasks / 異步 worker) 方案。
- [ ] 若需部署，確認 Webhook 網址具備 HTTPS，並已在 LINE Developers Console 進行 Webhook URL 設定與 Verify。
- [ ] 確認對 `Configuration` 與 `ApiClient` 的實例化方式已轉換至 v3 語法。
