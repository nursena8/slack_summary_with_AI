# Slack Message Summarizer with Claude 🤖

This project automatically collects messages from selected **Slack channels**, summarizes them using **Claude AI**, and posts the summary back into a designated Slack channel.  

It’s useful for **daily standups, team activity reports, or communication monitoring**.  

---

## 🚀 Features
- Collects messages from specified **Slack channels**  
- Filters messages from the **last 1 hour** (configurable)  
- Summarizes messages with **Claude AI (Anthropic)**  
- Posts the summary into a **summary channel** in Slack  
- Can also be scheduled to **run daily at specific times** (via cron jobs or task schedulers)  
- Provides informative error logs if something goes wrong  

---

## Setup
- Clone the repo
```bash
git clone https://github.com/username/slack-claude-summarizer.git
cd slack-claude-summarizer
```

- Create a virtual environment and install dependencies
```bash
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

pip install requests

```

- Go to Slack API page
[https://api.slack.com/apps](https://api.slack.com/apps)  

  - Click **"Create New App"** → **"From scratch"**.
  - Enter an **App Name**
  - Select your **Slack Workspace**
  - Click **Create App**
  - Select your app → **OAuth & Permissions**
  - Scroll down to **Scopes** → Add the following **Bot Token Scopes**:
    
      -  ```channels:read``` → Read information about public channels 

      -  ```groups:read```   → Read information about private channels  

      -  ```channels:history``` → Read message history in public channels  
  
      -  ```groups:history``` → Read message history in private channels  

      -  ```chat:write``` → Read message history in private channels
  - **OAuth & Permissions** → **Install App to Workspace**
  -This will generate your **Bot User OAuth Token** (starts with `xoxb-...`). Save this token as `SLACK_BOT_TOKEN`.  
  - Invite bot to channel  ``` /invite @your-bot-name```

- Set environment variables
You can use a .env file or export them directly in your terminal:
```bash
export SLACK_BOT_TOKEN="xoxb-xxxxxx"
export CLAUDE_API_KEY="sk-ant-xxxxxx"
```
-  Run ```python main.py```
-  You also can create scheduling to be able to post whenever you want.




