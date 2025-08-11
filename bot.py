import os
import discord
from discord import app_commands
from datetime import datetime, timezone

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")  # Optional: speeds up slash command registration for one server

class TimeBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Faster per-guild sync if GUILD_ID is set; otherwise global sync (can take ~1 minute the first time)
        if GUILD_ID:
            try:
                gid = int(GUILD_ID)
                await self.tree.sync(guild=discord.Object(id=gid))
                print(f"Slash commands synced to guild {gid}")
            except ValueError:
                print("Invalid GUILD_ID; doing global sync instead.")
                await self.tree.sync()
        else:
            await self.tree.sync()
            print("Slash commands globally synced.")

bot = TimeBot()

@bot.tree.command(
    name="utc",
    description="Convert a UTC time to a Discord timestamp that renders in everyone's local time."
)
@app_commands.describe(when="Time in 'HH:MM' or 'YYYY-MM-DD HH:MM' (UTC)")
async def utc(interaction: discord.Interaction, when: str):
    """Examples:
      /utc 15:30
      /utc 2025-08-11 09:00
    """
    try:
        if " " in when:
            # Format: YYYY-MM-DD HH:MM interpreted as UTC
            dt = datetime.strptime(when, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        else:
            # Format: HH:MM (UTC) -> assume today's date in UTC
            t = datetime.strptime(when, "%H:%M").time()
            today_utc = datetime.now(timezone.utc).date()
            dt = datetime.combine(today_utc, t).replace(tzinfo=timezone.utc)

        unix_ts = int(dt.timestamp())
        content = (
            f"Here’s the time for everyone: <t:{unix_ts}:F>  •  Relative: <t:{unix_ts}:R>\n"
            f"(Input interpreted as **UTC**)"
        )
        await interaction.response.send_message(content)

    except ValueError:
        await interaction.response.send_message(
            "Invalid format. Use **HH:MM** or **YYYY-MM-DD HH:MM** (UTC).", ephemeral=True
        )

if not TOKEN:
    raise SystemExit(
        "Set your token first: export DISCORD_TOKEN=... (macOS/Linux) or $env:DISCORD_TOKEN='...' (PowerShell)"
    )

bot.run(TOKEN)
