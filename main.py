import os
import requests
from datetime import datetime, timedelta, timezone  
from zoneinfo import ZoneInfo                        

SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
SUMMARY_CHANNEL = "#gunluk-ozet"

ALLOWED_CHANNELS = [
    "social-media-team",
    "brainy-team",
    "marketing-team",
    "software-team",
    "aylik-rapor",
    "link-grubu" 
]
TR = ZoneInfo("Europe/Istanbul")

def get_start_ts():
    
    hrs = os.getenv("TEST_WINDOW_HOURS")
    if hrs:
        return (datetime.now(timezone.utc) - timedelta(hours=int(hrs))).timestamp()
    # Gün başlangıcı (TR) → UTC timestamp
    now_tr = datetime.now(TR)
    start_tr = now_tr.replace(hour=0, minute=0, second=0, microsecond=0)
    return start_tr.astimezone(timezone.utc).timestamp()

def get_today_messages():
    headers = {"Authorization": f"Bearer {SLACK_TOKEN}"}

    resp = requests.get("https://slack.com/api/conversations.list",
                        headers=headers,
                        params={"limit": 1000}).json()
    if not resp.get("ok"):
        raise RuntimeError(f"Slack conversations.list error: {resp}")

    channels = resp.get("channels", [])
    start_ts = get_start_ts()
    all_messages = []

    for ch in channels:
        if ALLOWED_CHANNELS and ch["name"] not in ALLOWED_CHANNELS:
            continue

        hist = requests.get("https://slack.com/api/conversations.history",
                            headers=headers,
                            params={"channel": ch["id"], "oldest": start_ts, "limit": 200}).json()
        if not hist.get("ok"):
            continue

        for msg in hist.get("messages", []):
            text = msg.get("text", "")
            user = msg.get("user", "")
            all_messages.append(f"[{ch['name']}] {user}: {text}")

    return "\n".join(all_messages)

def summarize_with_claude(text):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "content-type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    payload = {
        "model": "claude-3-opus-20240229",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": f"Bugünkü Slack mesajlarını analiz et, detaylı ve kategorilere ayrılmış bir özet çıkar, emoji ekle:\n\n{text}"
            }
        ]
    }
    resp = requests.post(url, headers=headers, json=payload).json()
    # Basit koruma
    if "content" in resp and resp["content"]:
        return resp["content"][0].get("text", "Özet üretilemedi.")
    return "Özet üretilemedi."

def post_to_slack(message):
    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": f"Bearer {SLACK_TOKEN}", "Content-Type": "application/json"}
    payload = {"channel": SUMMARY_CHANNEL, "text": message}
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    messages = get_today_messages()
    if messages.strip():
        summary = summarize_with_claude(messages)
        post_to_slack(summary)
    else:
        post_to_slack("Bugün hiç mesaj bulunamadı ")









