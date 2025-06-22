
# 💰 HG Crypto Assistant

A Streamlit-based AI-powered assistant that provides real-time cryptocurrency prices using **Binance API** and interprets user queries with **Gemini (Google's GenAI)**.

![HG Crypto Assistant Screenshot](3cdd22ae-b0fc-48c0-96bb-ee57c696c80c.png)

---

## 📌 Features

- 🧠 Understands natural language queries like _“What’s the price of Bitcoin?”_
- 🔎 Extracts trading pair using Google Gemini
- 💹 Fetches live prices from Binance API
- 🛡️ Error handling for invalid queries or network issues
- 📦 Powered by `.env` for API security

---

## 🧪 Tech Stack

- `Streamlit` – Web UI
- `Python` – Backend logic
- `Binance API` – Real-time crypto prices
- `Google Gemini` – Natural language query interpretation
- `dotenv` – API key management

---

## 🔐 Environment Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/hg-crypto-agent.git
   cd hg-crypto-agent
````

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root with the following:

   ```env
   GEMINI_API_KEY=your_gemini_api_key
   BINANCE_API_KEY=your_binance_api_key
   BINANCE_API_SECRET=your_binance_api_secret
   ```

---

## 🚀 Run Locally

```bash
streamlit run crypto_app.py
```

---

## ⚠️ Note

* ✅ Works **perfectly on localhost**
* ❌ May face **HTTP 451 error** on [Streamlit Cloud](https://share.streamlit.io) due to **Binance region-based API restrictions**
* ✅ Recommended: Use CoinGecko as an alternative API for deployment (no auth required)

---

## 👩‍💻 Developer

**Hadiqa Gohar**
🔗 Powered by Gemini & Binance APIs
💻 Made with ❤️ and Streamlit

---
