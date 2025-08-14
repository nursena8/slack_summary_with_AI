import os
import requests
from datetime import datetime, timezone

SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")  
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY") 
SUMMARY_CHANNEL = "#gunluk-ozet"  

TARGET_CHANNELS = ["social-media-team","brainy-team","marketing-team","software-team"]


def get_recent_messages():
 
    url = "https://slack.com/api/conversations.list"
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
    params = {"types": "public_channel,private_channel", "limit": 1000}
    channels_resp = requests.get(url, headers=headers, params=params).json()
    channels = channels_resp.get("channels", [])

    if not channels_resp.get("ok"):
        print(f"⚠️ Kanallar listelenemedi: {channels_resp.get('error')}")
        return []

    all_messages = []
    start_ts = (datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()  # 🔹 Son 1 saat

    for ch in channels:
        if TARGET_CHANNELS and ch["name"] not in TARGET_CHANNELS:
            continue  

        ch_id = ch["id"]
        hist_url = "https://slack.com/api/conversations.history"
        params = {"channel": ch_id, "oldest": start_ts}
        resp = requests.get(hist_url, headers=headers, params=params).json()

        if not resp.get("ok"):
            print(f"⚠️ Kanal {ch['name']} okunamadı: {resp}")
            continue

        for msg in resp.get("messages", []):
            text = msg.get("text", "")
            user = msg.get("user", "")
            ts = datetime.fromtimestamp(float(msg["ts"]), tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
            all_messages.append(f"[{ch['name']}] {user} @ {ts}: {text}")

    return all_messages


def summarize_with_claude(text):
    """Claude ile özetleme yapar"""
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "content-type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": f"Aşağıdaki Slack mesajlarını analiz et ve özetle:\n\n{text}"
            }
        ]
    }
    resp = requests.post(url, headers=headers, json=payload).json()
    return resp["content"][0]["text"]


def post_to_slack(message):
    """Özeti Slack kanalına gönderir"""
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"channel": SUMMARY_CHANNEL, "text": message}
    resp = requests.post(url, headers=headers, json=payload).json()

    if not resp.get("ok"):
        print(f"⚠️ Slack'e mesaj gönderilemedi: {resp}")


if __name__ == "__main__":
    messages = get_recent_messages()

    if messages:
        print("✅ Mesajlar çekildi, Claude'a gönderiliyor...")
        summary = summarize_with_claude("\n".join(messages))
        print("📢 Özet Slack'e gönderiliyor...")
        post_to_slack(summary)
        print("✅ Özet başarıyla gönderildi.")
    else:
        post_to_slack("Son 1 saatte mesaj bulunamadı.")










