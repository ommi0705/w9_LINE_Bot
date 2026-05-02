# W11 作業：股票 LINE Bot

> **繳交方式**：將你的 GitHub repo 網址貼到作業繳交區
> **作業性質**：個人作業

---

## 作業目標

利用上週設計的 Skill，開發一個股票相關的 LINE Bot。
重點不是功能多寡，而是你設計的 **Skill 品質**——Skill 寫得越具體，AI 產出的程式碼就越接近可以直接執行。

---

## 功能要求（擇一實作）

| 功能 | 說明 |
| --- | --- |
| AI 分析股票 | 使用者說股票名稱，Gemini 給出分析 |
| 追蹤清單 | 儲存使用者的自選股清單到 SQLite |
| 查詢即時價格 | 整合 yfinance 或 twstock 取得股價 |

> 以「可以執行、能回覆訊息」為目標，不需要複雜

---

## 繳交項目

你的 GitHub repo 需要包含：

| 項目 | 說明 |
| --- | --- |
| `app.py` | LINE Webhook + Gemini + SQLite 後端 |
| `requirements.txt` | 所有套件 |
| `.env.example` | 環境變數範本（不含真實 token） |
| `.agents/skills/` | 至少包含 `/linebot-implement` Skill |
| `README.md` | 本檔案（含心得報告） |
| `screenshots/chat.png` | LINE Bot 對話截圖（至少一輪完整對話） |

### Skill 要求

`.agents/skills/` 至少需要包含：

- `/linebot-implement`：產出 LINE Bot 主程式（必要）
- `/prd` 或 `/architecture`：延用上週的
- `/commit`：延用上週的

---

## 專案結構

```
your-repo/
├── .agents/
│   └── skills/
│       ├── prd/SKILL.md
│       ├── linebot-implement/SKILL.md
│       └── commit/SKILL.md
├── docs/
│   └── PRD.md
├── screenshots/
│   └── chat.png
├── app.py
├── requirements.txt
├── .env.example
└── README.md
```

> `.env` 和 `users.db` 不要 commit（加入 `.gitignore`）

---

## 啟動方式

```bash
# 1. 建立虛擬環境
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. 安裝套件
pip install -r requirements.txt

# 3. 設定環境變數
cp .env.example .env
# 編輯 .env，填入三個 token

# 4. 啟動 FastAPI
uvicorn app:app --reload

# 5. 另開終端機啟動 ngrok
ngrok http 8000
# 複製 https 網址，填入 LINE Developers Console 的 Webhook URL（加上 /callback）
# 點「Verify」確認連線正常後，掃 QR Code 加好友開始測試
```

---

## 心得報告

**姓名**：姚谷伝
**學號**：D1109866

**Q1. 你在 `/linebot-implement` Skill 的「注意事項」寫了哪些規則？為什麼這樣寫？**

> 1. **強制使用 LINE Bot SDK v3**：因為 v2 與 v3 在 `ApiClient` 與 `MessagingApi` 的寫法差異極大，若不特別規定，AI 容易混用舊語法導致報錯。
> 2. **要求使用 FastAPI `BackgroundTasks` 處理耗時任務**：因為 LINE 官方嚴格要求 Webhook 必須在 1 秒內回覆 HTTP 200 OK，如果直接在請求中等待呼叫 Gemini AI 完成，一定會發生逾時 (Timeout) 並引發不斷重試的問題。
> 3. **敏感資訊與環境變數隔離**：要求絕對不能把 Token 寫死在程式碼中，養成安全良好的開發習慣。

---

**Q2. 你的 Skill 第一次執行後，AI 產出的程式直接能跑嗎？需要修改哪些地方？修改後有沒有更新 Skill？**

> 大致上直接能跑，API 結構與 SDK 呼叫都完全正確，但「業務邏輯的細節」還是出了點狀況。
> 例如：在判斷使用者是不是要查股票時，AI 寫的正則表達式 `\b\d{4}\b` 在英文環境沒問題，但在中文環境下，因為中文字（如「詢」）也被算作 `\w`，導致輸入「查詢2330」會因為中間沒有空格而判定失敗。後來手動請 AI 改成 `(?<!\d)\d{4}(?!\d)` 才解決。
> 這個經驗讓我學到，後續可以在 Skill 中特別加上：「處理中文 NLP 或是正規表達式時，請特別注意中文詞彙邊界（Word Boundary）的問題」。

---

**Q3. 你遇到什麼問題是 AI 沒辦法自己解決、需要你介入處理的？**

> 最大的問題是「舊有環境遺留物造成的衝突」。因為先前的專案遺留了一個舊的 `chatbot.db` 檔案，當這次換成 LINE Bot 新架構要建立新的 `users` 資料表（需要 `line_user_id` 欄位）時，SQLAlchemy 發生了衝突與報錯。AI 可以分析出錯誤原因，但這種「砍掉重練舊檔案」的行為，還是需要人類介入判斷並下達指令把舊的檔案刪除，才能讓伺服器順利重建資料庫。

---

**Q4. 如果你要把這個 LINE Bot 讓朋友使用，你還需要做什麼？**

> 1. **雲端部署**：目前是透過本機 + ngrok 執行，我需要把專案部署到 Render、Heroku 或 GCP 等雲端主機，讓它 24 小時都能運作。
> 2. **錯誤處理與 Rate Limit**：需要加入 API 的流量控制與更好的 Try-Catch 錯誤提示。如果朋友瘋狂打字，可能會把 Gemini API 的免費額度用完。
> 3. **LINE 官方帳號設定**：目前可能是開發者模式，需要到 LINE Official Account Manager 將帳號狀態設為公開（或將朋友加入測試群組）。