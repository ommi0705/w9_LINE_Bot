import yfinance as yf

def get_stock_price(stock_id: str) -> str:
    """
    爬取台股報價。會嘗試上市(.TW) 與 上櫃(.TWO)。
    回傳一段描述該股票目前價格的文字。
    """
    try:
        # 嘗試上市
        ticker_tw = f"{stock_id}.TW"
        stock = yf.Ticker(ticker_tw)
        hist = stock.history(period="1d")
        
        if hist.empty:
            # 嘗試上櫃
            ticker_two = f"{stock_id}.TWO"
            stock = yf.Ticker(ticker_two)
            hist = stock.history(period="1d")
            
        if hist.empty:
            return f"查無代碼 {stock_id} 的股票資訊，請確認代碼是否正確（目前支援四碼台股）。"
            
        # 取得最新一筆資料
        latest = hist.iloc[-1]
        close_price = latest['Close']
        open_price = latest['Open']
        high_price = latest['High']
        low_price = latest['Low']
        
        info = stock.info
        name = info.get("longName", stock_id)
        
        reply = (
            f"📊 【{name} ({stock_id})】 即時報價\n"
            f"💰 最新成交價：{close_price:.2f}\n"
            f"📈 開盤價：{open_price:.2f}\n"
            f"🔺 最高價：{high_price:.2f}\n"
            f"🔻 最低價：{low_price:.2f}\n"
            f"(資料來源：Yahoo Finance)"
        )
        return reply
    except Exception as e:
        print(f"取得股價時發生錯誤: {e}")
        return "取得股價失敗，請稍後再試。"
