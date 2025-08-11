# UTC2LOCAL-bot
Bot for discord to convert utc to local time


# UTC Time Helper (Discord Bot)

A tiny Discord bot that turns a **UTC time** into a Discord **dynamic timestamp** (`<t:...>`) so **every viewer** sees it in their **own local timezone**.

Example reply:
```
Here’s the time for everyone: <t:1707657600:F>  •  Relative: <t:1707657600:R>
```
Discord renders that as a full local date/time and a relative time.

---

## Commands

- `/utc when:`  
  Accepts `HH:MM` (assumes today, UTC) or `YYYY-MM-DD HH:MM` (UTC).  
  Examples:
  - `/utc 15:30`
  - `/utc 2025-08-11 09:00`

---

## Local Development

### 1) Create a Discord application and bot
1. Go to **Discord Developer Portal** → **New Application** → name it.
2. In **Bot** tab → **Add Bot** → copy the **token** (keep it secret).
3. In **OAuth2 → URL Generator**:
   - Scopes: **bot**, **applications.commands**
   - Bot Permissions: **View Channels**, **Send Messages**, **Read Message History**
   - Use the generated URL to invite the bot to your server.

### 2) Run locally
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt

# set your token (never commit it)
# macOS/Linux:
export DISCORD_TOKEN="PASTE_YOUR_TOKEN"
# Windows PowerShell:
$env:DISCORD_TOKEN="PASTE_YOUR_TOKEN"

# (optional) faster slash-command registration to one server
# export GUILD_ID=123456789012345678

python bot.py
```

Open Discord and type `/utc 15:30` in a channel where the bot can speak.

> **Tip:** Global slash commands can take ~1 minute the first time. Set `GUILD_ID` during development for near‑instant registration in one server.

---

## Deploy to Railway (Free)

You can host this bot online for free using **Railway**.

### Option A: Click-to-deploy from GitHub
1. Push this folder to a **new GitHub repo**.
2. Go to **https://railway.app** → **New Project** → **Deploy from GitHub repo** → select your repo.
3. After it builds, open the service → **Variables** → add:
   - `DISCORD_TOKEN` = *your bot token*
   - (optional) `GUILD_ID` = *your server ID for faster command sync*
4. Set the **Start Command** to:
   ```
   python bot.py
   ```
5. Deploy. Once it shows **Running**, your bot should appear **online** in your Discord server.

### Option B: Railway CLI (advanced)
```bash
# Install the Railway CLI
npm i -g @railway/cli

# In the project folder:
railway init
railway up

# Set environment variables in Railway's UI or via CLI
railway variables set DISCORD_TOKEN=YOUR_TOKEN
railway variables set GUILD_ID=YOUR_GUILD_ID   # optional
```

> Railway uses Nixpacks to auto-detect Python. The included `Procfile` (worker) is compatible, but you can just set the Start Command as shown above.

---

## Notes & Troubleshooting

- **Slash command not visible?**  
  Wait ~1 minute for global sync, or set `GUILD_ID` for instant per-guild sync while developing.

- **Bot online but silent?**  
  Check channel permissions: it needs **View Channels**, **Read Message History**, **Send Messages**.

- **Token errors?**  
  Ensure `DISCORD_TOKEN` is configured in Railway **Variables** or your local shell **before** running the bot.

- **Free tier limits**  
  If the Railway free hours are exhausted for the month, the service pauses until the reset.

---

## Security

- Never commit your real token. Use `.env.example` as a template and environment variables at runtime.
- Rotate your token in the Developer Portal if it leaks.

---
