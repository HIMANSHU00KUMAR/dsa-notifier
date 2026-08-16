# 🔥 DSA Daily Notifier (WhatsApp)

An automated daily Data Structures & Algorithms (DSA) trainer that selects an unsolved problem tailored to your rating and topic preferences, and sends a styled WhatsApp message directly to your phone every morning using **GitHub Actions (100% Free, no server required)**.

---

## ✨ Features

- 👤 **Personalized Problem Selection:** Checks your Codeforces handle to avoid recommending problems you have already solved (`VERDICT: OK`).
- 🎯 **Skill-Adaptive Difficulty:** Dynamically recommends problems around your current rating (e.g. `+100` to `+300`) or within your customized range (e.g. `1200` to `1600`).
- 🏷️ **Topic Targeting:** Filter by DSA topics like `dp`, `greedy`, `graphs`, `trees`, `math`, `binary search`, `data structures`, `bitmasks`, etc.
- 📱 **Clean WhatsApp Alerts:** Includes problem title, rating badge (🟢 Easy, 🟡 Medium, 🔴 Hard), topics, direct solve link, and daily DSA tips.
- 📜 **History Tracking:** Remembers previously recommended problems in `history/sent_problems.json` so you never get repeat problems.
- ⚡ **Zero Cost / 100% Free:** Runs completely free in the cloud on GitHub Actions.

---

## 📲 WhatsApp Message Preview

```text
🔥 *DAILY DSA NOTIFIER* 🔥
📅 _Sunday, 16 August 2026_

👤 *Coder:* @tourist (Rating: 1600)
🎯 *Target Rating:* 1600-1800
📌 *Problem:* 1872E - *Data Structures Fan*
⭐ *Level:* 🟡 Medium (1500)
🏷️ *DSA Topics:* bitmasks, data structures, divide and conquer

🔗 *Solve Link:*
https://codeforces.com/problemset/problem/1872/E

💡 *DSA Tip of the Day:*
_Look for monotonic properties — if increasing a threshold preserves validity, Binary Search on Answer will work!_

🚀 _Keep up the streak and build your problem-solving muscle!_ ✨
```

---

## 🚀 Quick Setup Guide (Takes ~2 Minutes)

### Step 1: Get Your Free WhatsApp API Key (CallMeBot)

1. Add the CallMeBot phone number **`+34 644 44 20 86`** (or current active bot number from [callmebot.com](https://www.callmebot.com/blog/free-api-whatsapp-messages/)) to your phone contacts as "CallMeBot".
2. Open WhatsApp and send this exact message to that contact:
   ```text
   I allow callmebot to send me messages
   ```
3. Within a few seconds, CallMeBot will reply with your personal **API Key**:
   > *"CallMeBot API: Your APIkey is 123456"*
4. Note down:
   - Your **Phone Number** with country code, NO `+` sign, NO spaces (e.g., `919876543210` for India, `14155552671` for US).
   - Your **API Key** (e.g., `123456`).

---

### Step 2: Push this Repository to GitHub

1. Create a new repository on [GitHub](https://github.com/new) named **`dsa-notifier`** (Public or Private).
2. Push your project files:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: DSA Daily WhatsApp Notifier"
   git branch -M main
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/dsa-notifier.git
   git push -u origin main
   ```

---

### Step 3: Add GitHub Secrets

1. In your GitHub repository, go to **Settings** → **Secrets and variables** → **Actions**.
2. Click **New repository secret** and add the following:

| Secret Name | Description | Example |
| :--- | :--- | :--- |
| `CF_HANDLE` | Your Codeforces username | `tourist` |
| `WHATSAPP_PHONE` | Phone number with country code (no `+`) | `919876543210` |
| `CALLMEBOT_API_KEY` | Your CallMeBot API key | `123456` |
| `MIN_RATING` *(Optional)* | Minimum problem rating | `1200` |
| `MAX_RATING` *(Optional)* | Maximum problem rating | `1600` |
| `PREFERRED_TAGS` *(Optional)* | Comma-separated DSA topics | `dp,graphs,binary search` |

> 💡 *Note: If `MIN_RATING` and `MAX_RATING` are omitted, the bot will automatically calculate your target rating based on your profile.*

---

### Step 4: Test & Verify

1. Go to the **Actions** tab in your GitHub repository.
2. Select **Daily DSA Notifier (WhatsApp)** on the left.
3. Click **Run workflow** → **Run workflow**.
4. Check your WhatsApp — your daily DSA problem will arrive directly on your phone! 🎉

---

## ⏰ Changing the Notification Time

The daily notification schedule is configured in [`.github/workflows/daily_dsa.yml`](.github/workflows/daily_dsa.yml):

```yaml
on:
  schedule:
    # 09:30 UTC = 3:00 PM IST (Indian Standard Time)
    - cron: '30 9 * * *'
```

To adjust the time:
- **8:00 AM IST:** `'30 2 * * *'` (02:30 UTC)
- **3:00 PM IST:** `'30 9 * * *'` (09:30 UTC)
- **9:00 AM IST:** `'30 3 * * *'` (03:30 UTC)
- **8:00 AM EST:** `'0 13 * * *'` (13:00 UTC)
- **8:00 AM PST:** `'0 16 * * *'` (16:00 UTC)

---

## 🛠️ Local Usage & Testing

If you want to run or test locally:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in your details:
   ```bash
   cp .env.example .env
   ```
3. Run the diagnostic tool:
   ```bash
   python test_notifier.py
   ```
4. Run the full daily job:
   ```bash
   python main.py
   ```

---

## 📁 Project Structure

```
dsa-notifier/
├── .github/
│   └── workflows/
│       └── daily_dsa.yml        # GitHub Actions cron scheduler
├── src/
│   ├── __init__.py
│   ├── config.py                # Environment & configuration parser
│   ├── codeforces_client.py     # Codeforces API query & problem selector
│   ├── notifier.py              # WhatsApp dispatch (CallMeBot / Twilio)
│   ├── formatter.py             # WhatsApp message builder with badges & DSA tips
│   └── history_manager.py       # History tracker for non-repeating problems
├── history/
│   └── sent_problems.json       # Log of past recommendations
├── tests/
│   └── test_suite.py            # Unit tests
├── main.py                      # Main entrypoint
├── test_notifier.py             # Interactive diagnostic script
├── requirements.txt             # Project dependencies
├── .env.example                 # Environment variable template
└── README.md                    # Documentation & Setup guide
```
