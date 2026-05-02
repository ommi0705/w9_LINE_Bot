import os
import google.generativeai as genai

def get_ai_response(user_message: str) -> str:
    """
    呼叫 Gemini API 根據使用者的輸入產生回覆
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return "系統提示：目前尚未設定 GEMINI_API_KEY，請先在 .env 中填寫您的 API 金鑰以便啟用 AI 功能。"
        
    try:
        genai.configure(api_key=api_key)
        # 使用 Gemini Flash 模型，適合快速問答
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # 設定 System Prompt 讓它扮演財經小幫手
        prompt = f"""
你是一個專業且友善的「股票投資小幫手」。
請用白話文且容易理解的方式回答使用者的財經問題。如果使用者詢問非財經的問題，你可以友善地回答，但請引導回投資理財相關話題。

使用者的問題：
{user_message}
"""
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API 發生錯誤: {e}")
        return "抱歉，目前 AI 系統繁忙或發生錯誤，請稍後再試。"
