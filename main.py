import os
import requests
from datetime import datetime, timedelta, timezone

SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
SUMMARY_CHANNEL = "#gunluk-ozet"

def get_today_messages():
    url = "https://slack.com/api/conversations.list"
    headers = {"Authorization": f"Bearer {SLACK_TOKEN}"}
    channels = requests.get(url, headers=headers).json()["channels"]

    all_messages = []
    start_ts = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()

    for ch in channels:
        ch_id = ch["id"]
        hist_url = "https://slack.com/api/conversations.history"
        params = {"channel": ch_id, "oldest": start_ts}
        resp = requests.get(hist_url, headers=headers, params=params).json()
        for msg in resp.get("messages", []):
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
    return resp["content"][0]["text"]

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

