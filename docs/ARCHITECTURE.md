# 股票投資小幫手 LINE Bot - 系統架構設計 (ARCHITECTURE)

## 1. 系統架構概覽 (Architecture Overview)

系統採用輕量級的前後端分離架構設計，主體為一個基於 FastAPI 構建的後端服務。使用者透過 LINE App 發送訊息，訊息經由 LINE 平台轉發至 FastAPI 所提供的 Webhook 進行處理。

- **LINE Webhook**: 接收並解析使用者發送的文字、指令或 Flex Message 互動。
- **核心業務邏輯**:
  - **股價查詢**: 解析股票代碼後，呼叫外部金融 API (例如 Yahoo Finance 或 TWSE API) 取得即時報價，並組裝為 LINE Flex Message 回傳。
  - **AI 財經問答**: 使用者輸入新聞網址或財經問題時，將內容傳送至 Google Gemini API，並將生成的摘要或解釋回傳給使用者。
  - **到價提醒**: 使用者透過指令設定提醒條件後，系統會將條件存入資料庫。背景排程任務會定期輪詢最新股價，若達成條件即主動透過 LINE Push API 通知使用者。
- **Web 介面 (網頁端)**: 提供 HTML 樣板渲染的網頁介面，可用於簡單的系統狀態監控、管理或是未來的 LIFF (LINE Front-end Framework) 整合。

## 2. 技術選型 (Tech Stack)

- **後端框架 (Backend Framework)**: `FastAPI` (Python 3)
  - 選擇原因：高效能、支援非同步 (AsyncIO)，適合處理需要高併發且大量等待 I/O (例如呼叫外部 API 及 LINE 平台) 的 Chatbot 應用。
- **LINE 整合**: `line-bot-sdk-python`
  - 選擇原因：官方提供的 SDK，能穩定處理 Webhook 驗證與各類型訊息的收發。
- **資料庫 (Database)**: `SQLite` + `SQLAlchemy` (ORM)
  - 選擇原因：輕量級關聯式資料庫，無須額外架設資料庫伺服器，適合第一階段 MVP 的快速開發與部署。SQLAlchemy 提供易於維護的資料模型操作。
- **AI 整合**: `google-generativeai` (Gemini API)
  - 選擇原因：Google 的強大 LLM，適合進行長文本的新聞摘要與複雜名詞解釋。
- **前端網頁 (Frontend)**: `HTML` + `CSS` + `JS` (搭配 `Jinja2` Templates)
  - 選擇原因：FastAPI 原生支援 Jinja2 樣板，能快速建構 SSR (Server-Side Rendering) 的網頁管理與展示介面。
- **排程系統 (Task Scheduling)**: `APScheduler` 或 FastAPI 內建的 `BackgroundTasks`
  - 選擇原因：用於處理到價提醒的背景輪詢機制。

## 3. 目錄結構規劃 (Directory Structure)

專案結構採用模組化的設計，將路由、業務邏輯與資料模型拆分，提升可維護性。

```text
.
├── app.py                 # FastAPI 應用程式主程式與掛載點
├── config.py              # 環境變數 (.env) 載入與設定中心
├── database.py            # 資料庫連線與 SQLAlchemy Session 管理
├── routers/               # API 路由與控制器
│   ├── line_bot.py        # 專門處理 LINE Webhook (/api/webhook) 的路由
│   ├── web.py             # 處理網頁前端視圖 (HTML) 的路由
│   └── api.py             # 其他內部 API 路由
├── services/              # 核心商業邏輯 (Service Layer)
│   ├── stock_service.py   # 股價爬取與金融 API 串接邏輯
│   ├── ai_service.py      # Gemini AI 呼叫與提示詞 (Prompt) 封裝
│   ├── line_service.py    # LINE 訊息格式組裝 (如 Flex Message) 與發送邏輯
│   └── alert_service.py   # 到價提醒的背景輪詢與觸發邏輯
├── models/                # SQLAlchemy 資料表模型與 Pydantic Schema
│   ├── user.py            # 使用者資訊與綁定狀態
│   ├── alert.py           # 儲存到價提醒條件 (目標價格、大於/小於)
│   └── history.py         # 對話歷史紀錄 (可選，作為 AI 上下文)
├── templates/             # Jinja2 前端 HTML 樣板
│   └── index.html         # 首頁 / 管理介面
├── static/                # 靜態資源檔案
│   ├── css/
│   ├── js/
│   └── images/
├── .env                   # 環境變數 (API Keys, Channel Secret 等機密資訊)
├── requirements.txt       # Python 依賴套件清單
└── docs/                  # 開發與產品文件
    ├── PRD.md
    └── ARCHITECTURE.md
```

## 4. 核心 API 路由 (Endpoints)

1. **LINE Webhook 端點**
   - **路由**: `POST /api/webhook`
   - **用途**: 提供給 LINE 平台呼叫，接收使用者訊息、追蹤 (Follow) 事件、Postback 行為。系統須在 1 秒內回覆 HTTP 200 OK，後續再透過非同步任務或 Reply API 處理業務。

2. **前端網頁端點**
   - **路由**: `GET /`
   - **用途**: 渲染 `templates/index.html`，展示服務介紹或系統狀態。

3. **系統健康檢查**
   - **路由**: `GET /api/health`
   - **用途**: 回傳系統狀態 (例如 `{"status": "ok"}`)，用於雲端平台 (如 Render, Heroku) 判斷應用程式是否正常啟動與運作。
