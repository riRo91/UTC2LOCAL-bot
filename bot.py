import os
import discord
from discord import app_commands
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")  # Optional: speeds up slash command registration for one server

# -----------------------------
# Event Catalog (from your data)
# -----------------------------
# Each event may define multiple "days". For each day:
#   - "name": display name for the day/stage
#   - "scoring": list[tuple[str, int]] or [] if not applicable
#   - "tasks": list[tuple[str, str]] -> (Task, Reward string)
# Top-level event also supports "duration_days", "repeats", and "notes" fields (optional).

EVENTS: Dict[str, Dict[str, Any]] = {
    "The Greatest Leader": {
        "description": "Do your best to prove that you are the greatest leader!",
        "duration_days": 5,
        "repeats": "Every 2 weeks",
        "notes": (
            "First 7 times are single-server; afterward becomes cross-server. "
            "Hero shards rotate among Aang, Amon, Korra, Kyoshi, Yangchen, Roku."
        ),
        "days": [
            {
                "name": "Day 1 — Resource Gathering & Research",
                "scoring": [
                    ("Per gathering 100 Food on the field", 3),
                    ("Per gathering 100 Wood on the field", 3),
                    ("Per gathering 100 Stone on the field", 3),
                    ("Per gathering 50 Gold on the field", 3),
                    ("Increase Power by 1 with research", 25),
                    ("Per 1 Lucky Ticket", 150_000),
                ],
                "tasks": [
                    ("Gather 100,000 resources from the field",
                     "1x Rare Spirit Shard, 1x Silver Scroll, 1x 50,000 Food, 1x 50,000 Wood"),
                    ("Gather 300,000 resources from the field",
                     "1x Rare Spirit Shard, 1x Golden Scroll, 2x 50,000 Food, 2x 50,000 Wood"),
                    ("Gather 500,000 resources from the field",
                     "1x Epic Spirit Shard, 1x Golden Scroll, 3x 50,000 Food, 3x 50,000 Wood"),
                    ("Increase Power by 30,000 with Research",
                     "50x Gem, 1x Rare Spirit Badge, 1x Silver Scroll, 5x Speedup 5m"),
                    ("Increase Power by 60,000 with Research",
                     "100x Gem, 1x Rare Spirit Badge, 1x Golden Scroll, 1x Speedup 60m"),
                    ("Increase Power by 90,000 with Research",
                     "200x Gem, 1x Legendary Spirit Badge, 1x Golden Scroll, 2x Speedup 60m"),
                ],
            },
            {
                "name": "Day 2 — Bender Recruitment",
                "scoring": [
                    ("Per recruiting 1 bender (Tier 1)", 25),
                    ("Per recruiting 1 bender (Tier 2)", 50),
                    ("Per recruiting 1 bender (Tier 3)", 75),
                    ("Per recruiting 1 bender (Tier 4)", 100),
                    ("Per recruiting 1 bender (Tier 5)", 150),
                    ("Per recruiting 1 bender (Tier 6)", 350),
                    ("Per 1 Lucky Ticket", 150_000),
                ],
                "tasks": [
                    ("Recruit 1,000 Tier 2 or Higher Benders",
                     "30x Gem, 1x Rare Spirit Badge, 1x Silver Scroll, 5x Speedup 5m"),
                    ("Recruit 3,000 Tier 2 or Higher Benders",
                     "60x Gem, 1x Rare Spirit Badge, 1x Silver Scroll, 10x Speedup 5m"),
                    ("Recruit 6,000 Tier 2 or Higher Benders",
                     "90x Gem, 1x Epic Spirit Badge, 1x Silver Scroll, 15x Speedup 5m"),
                    ("Recruit 12,000 Tier 2 or Higher Benders",
                     "120x Gem, 1x Epic Spirit Badge, 1x Golden Scroll, 2x Speedup 60m"),
                    ("Recruit 18,000 Tier 2 or Higher Benders",
                     "150x Gem, 1x Legendary Spirit Badge, 1x Golden Scroll, 3x Speedup 60m"),
                    ("Recruit 25,000 Tier 2 or Higher Benders",
                     "200x Gem, 1x Legendary Spirit Shard, 1x Golden Scroll, 5x Speedup 60m"),
                ],
            },
            {
                "name": "Day 3 — Hero Growth",
                "scoring": [
                    ("Use a Silver Scroll", 750),
                    ("Use a Golden Scroll", 1_500),
                    ("Use a Rare Hero Spirit Shard", 250),
                    ("Use an Epic Hero Spirit Shard", 1_250),
                    ("Use a Legendary Hero Spirit Shard", 50_000),
                    ("Use a Rare Hero Spirit Badge", 250),
                    ("Use an Epic Hero Spirit Badge", 1_250),
                    ("Use a Legendary Hero Spirit Badge", 50_000),
                    ("Per 1 Lucky Ticket", 150_000),
                ],
                "tasks": [
                    ("Use Silver Scrolls 10 time(s)",
                     "1x Rare Spirit Shard, 5x Silver Scroll, 1x Book of Experience (1,000), 1x Research Speedup 60m"),
                    ("Use Golden Scrolls 10 time(s)",
                     "1x Epic Spirit Shard, 5x Golden Scroll, 1x Book of Experience (5,000), 2x Research Speedup 60m"),
                    ("Skill up any hero 1 time(s)",
                     "3x Rare Spirit Badge, 1x Silver Scroll, 1x Book of Experience (1,000), 1x Research Speedup 60m"),
                    ("Skill up any hero 3 time(s)",
                     "1x Epic Spirit Badge, 1x Golden Scroll, 1x Book of Experience (5,000), 2x Research Speedup 60m"),
                    ("Rank up any hero 1 time(s)",
                     "3x Rare Spirit Shard, 1x Silver Scroll, 1x Book of Experience (1,000), 1x Research Speedup 60m"),
                    ("Rank up any hero 3 time(s)",
                     "3x Rare Spirit Shard, 1x Golden Scroll, 1x Book of Experience (5,000), 2x Research Speedup 60m"),
                ],
            },
            {
                "name": "Day 4 — Shattered Skulls & Construction",
                "scoring": [
                    ("Shattered Skull Levels 1 ~ 5", 1_500),
                    ("Shattered Skull Levels 6 ~ 10", 1_800),
                    ("Shattered Skull Levels 11 ~ 15", 2_100),
                    ("Shattered Skull Levels 16 ~ 20", 2_400),
                    ("Shattered Skull Levels 21 ~ 25", 2_700),
                    ("Shattered Skull Levels 26 ~ 30", 3_000),
                    ("Shattered Skulls’ Fortress 1", 10_000),
                    ("Shattered Skulls’ Fortress 2", 12_000),
                    ("Shattered Skulls’ Fortress 3", 14_000),
                    ("Shattered Skulls’ Fortress 4", 16_000),
                    ("Increase construction Power by 1", 25),
                ],
                "tasks": [
                    ("Defeat Shattered Skulls 10 time(s)",
                     "1x Rare Spirit Shard, 1x Silver Scroll, 1x Book of Experience (1,000), 1x Seal of Solidarity"),
                    ("Defeat Shattered Skulls 20 time(s)",
                     "1x Epic Spirit Shard, 1x Golden Scroll, 1x Book of Experience (5,000), 3x Seal of Solidarity"),
                    ("Destroy Shattered Skulls’ Fortress 2 time(s)",
                     "1x Rare Spirit Badge, 1x Silver Scroll, 1x Book of Experience (1,000), 2x Seal of Solidarity"),
                    ("Destroy Shattered Skulls’ Fortress 4 time(s)",
                     "1x Epic Spirit Badge, 1x Golden Scroll, 1x Book of Experience (5,000), 5x Seal of Solidarity"),
                    ("Increase Power by 30,000 with Construction",
                     "30x Gem, 3x Epic Spirit Shard, 1x Silver Scroll, 1x Speedup 60m"),
                    ("Increase Power by 60,000 with Construction",
                     "100x Gem, 1x Legendary Spirit Shard, 1x Golden Scroll, 2x Speedup 60m"),
                ],
            },
            {
                "name": "Day 5 — Increase Power (Hero Power excluded)",
                "scoring": [
                    ("Increase Power by 1 (Hero Power excluded)", 20),
                ],
                "tasks": [
                    ("Increase Power by 40,000",
                     "50x Gem, 1x Rare Spirit Badge, 1x Silver Scroll, 5x Speedup 5m"),
                    ("Increase Power by 80,000",
                     "100x Gem, 1x Rare Spirit Shard, 1x Silver Scroll, 10x Speedup 5m"),
                    ("Increase Power by 120,000",
                     "150x Gem, 1x Epic Spirit Shard, 1x Golden Scroll, 15x Speedup 5m"),
                    ("Increase Power by 180,000",
                     "200x Gem, 1x Epic Spirit Shard, 1x Golden Scroll, 2x Speedup 60m"),
                    ("Increase Power by 240,000",
                     "250x Gem, 1x Legendary Spirit Badge, 1x Golden Scroll, 3x Speedup 60m"),
                    ("Increase Power by 300,000",
                     "300x Gem, 1x Legendary Spirit Shard, 1x Golden Scroll, 5x Speedup 60m"),
                ],
            },
        ],
    },

    "Avatar Day Festival": {
        "description": "Exchange Aang Cookies for rewards.",
        "duration_days": 7,  # Shop on last day
        "days": [
            {
                "name": "Day 1",
                "scoring": [],
                "tasks": [
                    ("Login 1 Day(s)", "1x Aang Cookie, 1x Book of Experience (1,000), 1x 10,000 Food, 1x 10,000 Wood, 1x 10,000 Stone"),
                    ("Login 2 Day(s)", "2x Aang Cookie, 2x Book of Experience (1,000), 2x 10,000 Food, 2x 10,000 Wood, 2x 10,000 Stone"),
                    ("Login 3 Day(s)", "3x Aang Cookie, 1x Book of Experience (5,000), 3x 10,000 Food, 3x 10,000 Wood, 3x 10,000 Stone"),
                    ("Login 4 Day(s)", "4x Aang Cookie, 1x Silver Scroll, 4x 10,000 Food, 4x 10,000 Wood, 4x 10,000 Stone"),
                    ("Login 5 Day(s)", "5x Aang Cookie, 1x Golden Scroll, 5x 10,000 Food, 5x 10,000 Wood, 5x 10,000 Stone"),
                    ("Recruit 3,000 Benders", "1x Aang Cookie, 1x Research Speedup 60m, 1x 50,000 Food, 1x 50,000 Wood, 1x 50,000 Stone"),
                    ("Recruit 6,000 Benders", "3x Aang Cookie, 2x Research Speedup 60m, 3x 50,000 Food, 3x 50,000 Wood, 3x 50,000 Stone"),
                    ("Recruit 12,000 Benders", "5x Aang Cookie, 1x Silver Scroll, 3x Research Speedup 60m, 5x 50,000 Food, 5x 50,000 Wood, 5x 50,000 Stone"),
                    ("Recruit 20,000 Benders", "5x Aang Cookie, 1x Golden Scroll, 5x Research Speedup 60m, 10x 50,000 Food, 10x 50,000 Wood, 10x 50,000 Stone"),
                ],
            },
            {
                "name": "Day 2",
                "scoring": [],
                "tasks": [
                    ("Use 500 AP", "1x Aang Cookie, 1x Book of Experience (5,000), 1x 50,000 Food, 1x 50,000 Wood, 1x 50,000 Stone"),
                    ("Use 1,000 AP", "3x Aang Cookie, 1x Silver Scroll, 3x 50,000 Food, 3x 50,000 Wood, 3x 50,000 Stone"),
                    ("Use 2,000 AP", "5x Aang Cookie, 1x Golden Scroll, 5x 50,000 Food, 5x 50,000 Wood, 5x 50,000 Stone"),
                    ("Gather 100,000 resources from the field", "1x Aang Cookie, 1x Book of Experience (5,000), 5x Construction Speedup 5m, 5x Recruitment Speedup 5m, 5x Research Speedup 5m"),
                    ("Gather 200,000 resources from the field", "2x Aang Cookie, 1x Silver Scroll, 10x Construction Speedup 5m, 10x Recruitment Speedup 5m, 10x Research Speedup 5m"),
                    ("Gather 400,000 resources from the field", "3x Aang Cookie, 1x Golden Scroll, 15x Construction Speedup 5m, 15x Recruitment Speedup 5m, 15x Research Speedup 5m"),
                    ("Gather 800,000 resources from the field", "5x Aang Cookie, 2x Golden Scroll, 2x Construction Speedup 60m, 2x Recruitment Speedup 60m, 2x Research Speedup 60m"),
                ],
            },
            {
                "name": "Day 3",
                "scoring": [],
                "tasks": [
                    ("Increase Power by 40,000 with Construction", "1x Aang Cookie, 1x Book of Experience (5,000), 5x Construction Speedup 5m, 5x Recruitment Speedup 5m, 5x Research Speedup 5m"),
                    ("Increase Power by 80,000 with Construction", "3x Aang Cookie, 1x Silver Scroll, 1x Construction Speedup 60m, 1x Recruitment Speedup 60m, 1x Research Speedup 60m"),
                    ("Increase Power by 120,000 with Construction", "5x Aang Cookie, 1x Golden Scroll, 2x Construction Speedup 60m, 2x Recruitment Speedup 60m, 2x Research Speedup 60m"),
                    ("Complete Expedition missions 10 time(s)", "1x Aang Cookie, 1x Book of Experience (5,000), 1x 50,000 Food, 1x 50,000 Wood, 1x 50,000 Stone"),
                    ("Complete Expedition missions 20 time(s)", "3x Aang Cookie, 1x Silver Scroll, 3x 50,000 Food, 3x 50,000 Wood, 3x 50,000 Stone"),
                    ("Complete Expedition missions 30 time(s)", "5x Aang Cookie, 1x Golden Scroll, 5x 10,000 Food, 5x 10,000 Wood, 5x 10,000 Stone"),
                ],
            },
            {
                "name": "Day 4",
                "scoring": [],
                "tasks": [
                    ("Harvest 10,000 resources in the city", "1x Aang Cookie, 2x Book of Experience (1,000), 1x 10,000 Food, 1x 10,000 Wood, 1x 10,000 Stone"),
                    ("Harvest 50,000 resources in the city", "2x Aang Cookie, 1x Book of Experience (5,000), 3x 10,000 Food, 3x 10,000 Wood, 3x 10,000 Stone"),
                    ("Harvest 100,000 resources in the city", "3x Aang Cookie, 1x Silver Scroll, 1x 50,000 Food, 1x 50,000 Wood, 1x 50,000 Stone"),
                    ("Harvest 150,000 resources in the city", "5x Aang Cookie, 1x Golden Scroll, 3x 50,000 Food, 3x 50,000 Wood, 3x 50,000 Stone"),
                    ("Increase Power by 20,000 with Research", "1x Aang Cookie, 1x Book of Experience (5,000), 1x Construction Speedup 5m, 1x Recruitment Speedup 5m, 1x Research Speedup 5m"),
                    ("Increase Power by 40,000 with Research", "3x Aang Cookie, 1x Silver Scroll, 1x Construction Speedup 60m, 1x Recruitment Speedup 60m, 1x Research Speedup 60m"),
                    ("Increase Power by 60,000 with Research", "5x Aang Cookie, 1x Golden Scroll, 2x Construction Speedup 60m, 2x Recruitment Speedup 60m, 2x Research Speedup 60m"),
                ],
            },
            {
                "name": "Day 5",
                "scoring": [],
                "tasks": [
                    ("Defeat Shattered Skulls 5 time(s)", "1x Aang Cookie, 1x Book of Experience (5,000), 2x 10,000 Food, 2x 10,000 Wood, 2x 10,000 Stone"),
                    ("Defeat Shattered Skulls 10 time(s)", "3x Aang Cookie, 2x Book of Experience (5,000), 1x 50,000 Food, 1x 50,000 Wood, 1x 50,000 Stone"),
                    ("Defeat Shattered Skulls 20 time(s)", "5x Aang Cookie, 1x Silver Scroll, 3x 50,000 Food, 3x 50,000 Wood, 3x 50,000 Stone"),
                    ("Defeat Shattered Skulls 30 time(s)", "7x Aang Cookie, 1x Golden Scroll, 5x 50,000 Food, 5x 50,000 Wood, 5x 50,000 Stone"),
                    ("Use any Scrolls 5 time(s)", "1x Aang Cookie, 1x Book of Experience (5,000), 2x Construction Speedup 5m, 2x Recruitment Speedup 5m, 2x Research Speedup 5m"),
                    ("Use any Scrolls 10 time(s)", "3x Aang Cookie, 1x Silver Scroll, 5x Construction Speedup 5m, 5x Recruitment Speedup 5m, 5x Research Speedup 5m"),
                    ("Use any Scrolls 15 time(s)", "5x Aang Cookie, 1x Golden Scroll, 1x Construction Speedup 60m, 1x Recruitment Speedup 60m, 1x Research Speedup 60m"),
                ],
            },
            {
                "name": "Exchange Shop (last day only)",
                "scoring": [],
                "tasks": [
                    ("1 Cookie → Speedup 60m", "Qty 10"),
                    ("1 Cookie → 50,000 Food", "Qty 10"),
                    ("1 Cookie → 50,000 Wood", "Qty 10"),
                    ("1 Cookie → 50,000 Stone", "Qty 10"),
                    ("1 Cookie → 25,000 Gold", "Qty 10"),
                    ("2 Cookies → Rare Spirit Shard", "Qty 10"),
                    ("2 Cookies → Rare Spirit Badge", "Qty 10"),
                    ("2 Cookies → Silver Scroll", "Qty 10"),
                    ("8 Cookies → Spirit Shard: Zuko", "Qty 10"),
                    ("8 Cookies → Spirit Shard: Katara", "Qty 10"),
                    ("8 Cookies → Spirit Shard: Toph", "Qty 10"),
                    ("8 Cookies → Spirit Shard: Tenzin", "Qty 10"),
                    ("10 Cookies → Golden Scroll", "Qty 10"),
                    ("10 Cookies → Reset Talents", "Qty 1"),
                    ("30 Cookies → Legendary Spirit Shard", "Qty 2"),
                    ("30 Cookies → Legendary Spirit Badge", "Qty 2"),
                ],
            },
        ],
    },

    "Journey of Us": {
        "description": "Let’s not forget our journey. Every step has been meaningful.",
        "duration_days": 2,
        "days": [
            {
                "name": "All Days",
                "scoring": [],
                "tasks": [
                    ("Use Silver Scroll 5 time(s)", "1x Silver Scroll, 1x Book of Experience (1,000), 1x 10,000 Food, 1x 10,000 Wood, 1x 10,000 Stone"),
                    ("Use Silver Scroll 20 time(s)", "3x Silver Scroll, 1x Book of Experience (5,000), 3x 10,000 Food, 3x 10,000 Wood, 3x 10,000 Stone"),
                    ("Use Golden Scroll 5 time(s)", "1x Golden Scroll, 1x Book of Experience (1,000), 1x 10,000 Food, 1x 10,000 Wood, 1x 10,000 Stone"),
                    ("Use Golden Scroll 20 time(s)", "3x Golden Scroll, 1x Book of Experience (1,000), 3x 10,000 Food, 3x 10,000 Wood, 3x 10,000 Stone"),
                    ("Send airship 4 time(s)", "1x Silver Scroll, 2x Book of Experience (1,000), 5x Construction Speedup 5m, 5x Recruitment Speedup 5m, 5x Research Speedup 5m"),
                    ("Successfully raid another airship 4 time(s)", "1x Golden Scroll, 1x Book of Experience (5,000), 1x Construction Speedup 60m, 1x Recruitment Speedup 60m, 1x Research Speedup 60m"),
                ],
            }
        ],
    },

    "Supply Quest": {
        "description": "Collect as many Supply Chests as possible. Resets daily at 00:00 UTC.",
        "duration_days": 2,
        "days": [
            {
                "name": "Daily",
                "scoring": [
                    ("Defeat Shattered Skulls (per Supply Chest)", 10),
                    ("Gather Resources (per 50,000 gathered → 1 Supply Chest)", 1),
                ],
                "tasks": [
                    ("Defeat Shattered Skulls", "Earn points via Supply Chests"),
                    ("Gather Resources on the field", "Earn points via Supply Chests (1 per 50,000)"),
                ],
            }
        ],
    },

    "Timeless": {
        "description": "Cherished values transcend the ages.",
        "duration_days": 1,
        "days": [
            {
                "name": "All Day",
                "scoring": [],
                "tasks": [
                    ("Use 200 Minutes of Speedup items", "100x Gem, 5x Speedup 5m, 1x 150K Food, 1x 150K Wood, 1x 150K Stone, 1x 75,000 Gold"),
                    ("Use 1,000 Minutes of Speedup items", "150x Gem, 10x Speedup 5m, 2x 150K Food, 2x 150K Wood, 2x 150K Stone, 2x 75,000 Gold"),
                    ("Use 3,000 Minutes of Speedup items", "200x Gem, 2x Speedup 60m, 3x 150K Food, 3x 150K Wood, 3x 150K Stone, 3x 75,000 Gold"),
                    ("Use 6,000 Minutes of Speedup items", "250x Gem, 3x Speedup 60m, 4x 150K Food, 4x 150K Wood, 4x 150K Stone, 4x 75,000 Gold"),
                    ("Use 12,000 Minutes of Speedup items", "400x Gem, 5x Speedup 60m, 5x 150K Food, 5x 150K Wood, 5x 150K Stone, 5x 75,000 Gold"),
                ],
            }
        ],
    },

    "Unbreakable Will": {
        "description": "What matters is an unyielding determination! Resets daily at 00:00 UTC.",
        "duration_days": 3,
        "days": [
            {
                "name": "Daily",
                "scoring": [],
                "tasks": [
                    ("Use 300 AP", "1x Construction Speedup 60m, 1x 10,000 Food, 1x 10,000 Wood, 1x 10,000 Stone"),
                    ("Use 1,000 AP", "5x Research Speedup 60m, 3x 10,000 Food, 3x 10,000 Wood, 3x 10,000 Stone"),
                    ("Recruit 1,000 Benders", "1x Book of Experience (5,000), 1x 10,000 Food, 1x 10,000 Wood, 1x 10,000 Stone"),
                    ("Recruit 2,000 Benders", "1x Rare Spirit Shard, 3x 10,000 Food, 3x 10,000 Wood, 3x 10,000 Stone"),
                    ("Recruit 6,000 Benders", "1x Epic Spirit Shard, 1x 50,000 Food, 1x 50,000 Wood, 1x 50,000 Stone"),
                    ("Harvest 20,000 resources in the city", "1x Silver Scroll, 1x Construction Speedup 5m, 1x Recruitment Speedup 5m, 1x Research Speedup 5m"),
                    ("Harvest 100,000 resources in the city", "1x Golden Scroll, 3x Construction Speedup 5m, 3x Recruitment Speedup 5m, 3x Research Speedup 5m"),
                ],
            }
        ],
    },

    "Harvest Season": {
        "description": "Gather abundant resources to build an outstanding city.",
        "duration_days": 2,
        "days": [
            {
                "name": "All Days",
                "scoring": [],
                "tasks": [
                    ("Gather 200,000 resources from the field", "1x Book of Experience (5,000), 1x 10,000 Food, 1x 10,000 Wood, 1x 10,000 Stone"),
                    ("Gather 500,000 resources from the field", "1x Silver Scroll, 3x 10,000 Food, 3x 10,000 Wood, 3x 10,000 Stone"),
                    ("Gather 1,000,000 resources from the field", "1x Golden Scroll, 1x 50,000 Food, 1x 50,000 Wood, 1x 50,000 Stone"),
                    ("Purchase items at the Trading Post 5 time(s)", "1x Book of Experience (5,000), 5x Research Speedup 5m, 1x AP Potion 100, 1x Seal of Solidarity"),
                    ("Purchase items at the Trading Post 15 time(s)", "1x Silver Scroll, 1x Research Speedup 60m, 3x AP Potion 100, 2x Seal of Solidarity"),
                    ("Purchase items at the Trading Post 30 time(s)", "1x Golden Scroll, 2x Research Speedup 60m, 5x AP Potion 100, 3x Seal of Solidarity"),
                ],
            }
        ],
    },
}

# -----------------------------
# Bot Implementation
# -----------------------------
class TimeBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
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

# -----------------------------
# Helpers for formatting
# -----------------------------
def _chunk_lines(lines: List[str], limit: int = 950) -> List[str]:
    """Split long lists of bullet lines into chunks under 'limit' characters (embed field value <= 1024)."""
    chunks = []
    cur = ""
    for line in lines:
        add = f"{line}\n"
        if len(cur) + len(add) > limit:
            if cur:
                chunks.append(cur.rstrip())
            cur = add
        else:
            cur += add
    if cur:
        chunks.append(cur.rstrip())
    return chunks

def _format_scoring(scoring: List[Tuple[str, int]]) -> List[str]:
    out = []
    for label, pts in scoring:
        # Display in "+X points — Label" form
        if isinstance(pts, int):
            if pts >= 1000:
                pts_str = f"{pts:,}"
            else:
                pts_str = str(pts)
        else:
            pts_str = str(pts)
        out.append(f"• **+{pts_str}** — {label}")
    return out if out else ["• *(No point scoring specified for this day)*"]

def _format_tasks(tasks: List[Tuple[str, str]]) -> List[str]:
    if not tasks:
        return ["• *(No tasks listed for this day)*"]
    return [f"• **{t}**\n  ↳ {r}" for t, r in tasks]

def build_event_embeds(event_name: str, day_name: str) -> List[discord.Embed]:
    ev = EVENTS[event_name]
    day = next((d for d in ev["days"] if d["name"] == day_name), None)
    if not day:
        raise ValueError("Day not found for event.")

    title = f"{event_name} • {day_name}"
    embed1 = discord.Embed(title=title, description=ev.get("description") or "", color=0x2B6CB0)

    # Optional meta
    meta_bits = []
    if ev.get("duration_days"): meta_bits.append(f"**Duration:** {ev['duration_days']} day(s)")
    if ev.get("repeats"): meta_bits.append(f"**Repeats:** {ev['repeats']}")
    if meta_bits:
        embed1.add_field(name="Info", value="\n".join(meta_bits), inline=False)

    # Scoring
    scoring_lines = _format_scoring(day.get("scoring", []))
    for i, chunk in enumerate(_chunk_lines(scoring_lines)):
        name = "Scoring" if i == 0 else "Scoring (cont.)"
        embed1.add_field(name=name, value=chunk, inline=False)

    # Tasks & Rewards (second embed to avoid hitting total field limits)
    embed2 = discord.Embed(color=0x2B6CB0)
    task_lines = _format_tasks(day.get("tasks", []))
    for i, chunk in enumerate(_chunk_lines(task_lines)):
        name = "Tasks & Rewards" if i == 0 else "Tasks & Rewards (cont.)"
        embed2.add_field(name=name, value=chunk, inline=False)

    if ev.get("notes"):
        embed2.set_footer(text=ev["notes"])

    return [embed1, embed2]

def get_event_names() -> List[str]:
    return list(EVENTS.keys())

def get_day_names(event_name: str) -> List[str]:
    ev = EVENTS.get(event_name)
    if not ev:
        return []
    return [d["name"] for d in ev["days"]]

# -----------------------------
# Interactive Day Picker View
# -----------------------------
class DayPickerView(discord.ui.View):
    def __init__(self, event_name: str, user_id: int):
        super().__init__(timeout=120)
        self.event_name = event_name
        self.user_id = user_id
        options = [discord.SelectOption(label=name) for name in get_day_names(event_name)]
        self.select = discord.ui.Select(placeholder="Select a day/stage…", options=options, min_values=1, max_values=1)
        self.select.callback = self._on_select
        self.add_item(self.select)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Ensure only the requesting user can use this selector
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This selector isn’t for you.", ephemeral=True)
            return False
        return True

    async def _on_select(self, interaction: discord.Interaction):
        day_name = self.select.values[0]
        embeds = build_event_embeds(self.event_name, day_name)
        # Replace the original ephemeral message with the result
        await interaction.response.edit_message(content=None, embeds=embeds, view=None)

# -----------------------------
# Slash Commands
# -----------------------------
@bot.tree.command(
    name="utc",
    description="Convert a UTC time to a Discord timestamp that renders in everyone's local time.",
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

# -----------------------------
# Autocomplete handlers (must be defined before they're used)
# -----------------------------
async def autocomplete_event(
    interaction: discord.Interaction,
    current: str
) -> List[app_commands.Choice[str]]:
    current_lower = (current or "").lower()
    names = get_event_names()
    if current_lower:
        names = [n for n in names if current_lower in n.lower()]
    return [app_commands.Choice(name=n, value=n) for n in names[:25]]

async def autocomplete_day(
    interaction: discord.Interaction,
    current: str
) -> List[app_commands.Choice[str]]:
    ns = interaction.namespace
    ev_name = getattr(ns, "event", None)
    if not ev_name or ev_name not in EVENTS:
        return []
    day_names = get_day_names(ev_name)
    current_lower = (current or "").lower()
    if current_lower:
        day_names = [n for n in day_names if current_lower in n.lower()]
    return [app_commands.Choice(name=n, value=n) for n in day_names[:25]]


# /event command with autocomplete + optional interactive day picker
@bot.tree.command(
    name="event",
    description="Show scoring and personal tasks + rewards for a game event/day.",
)
@app_commands.describe(
    event="Event name (start typing for suggestions)",
    day="Day/Stage (optional—picker appears if omitted and multiple days exist)",
    public="Check to post publicly; default is private (ephemeral)",
)

@app_commands.autocomplete(event=autocomplete_event, day=autocomplete_day)
async def event(
    interaction: discord.Interaction,
    event: str,
    day: Optional[str] = None,
    public: Optional[bool] = False,
):
    # Validate event
    if event not in EVENTS:
        suggestions = ", ".join(get_event_names())
        await interaction.response.send_message(
            f"Unknown event **{event}**. Try one of: {suggestions}",
            ephemeral=True,
        )
        return

    day_names = get_day_names(event)
    if not day_names:
        await interaction.response.send_message("No days found for that event.", ephemeral=True)
        return

    # If no day provided and multiple days exist, show interactive picker
    if day is None and len(day_names) > 1:
        view = DayPickerView(event_name=event, user_id=interaction.user.id)
        await interaction.response.send_message(
            f"**{event}** has multiple days. Pick one:",
            view=view,
            ephemeral=not public,
        )
        return

    # If day provided (or only one day exists), validate and render
    if day is None:
        day = day_names[0]
    elif day not in day_names:
        await interaction.response.send_message(
            f"**{event}** doesn’t have a day/stage named **{day}**.\n"
            f"Available: {', '.join(day_names)}",
            ephemeral=True,
        )
        return

    embeds = build_event_embeds(event, day)
    await interaction.response.send_message(embeds=embeds, ephemeral=not public)

# -----------------------------
# Autocomplete handlers
# -----------------------------
async def autocomplete_event(interaction: discord.Interaction, current: str):
    current_lower = (current or "").lower()
    names = get_event_names()
    if current_lower:
        names = [n for n in names if current_lower in n.lower()]
    # Discord allows up to 25 choices
    return [app_commands.Choice(name=n, value=n) for n in names[:25]]

async def autocomplete_day(interaction: discord.Interaction, current: str):
    # Attempt to get the value typed/selected for 'event'
    ns = interaction.namespace
    ev_name = getattr(ns, "event", None)
    if not ev_name or ev_name not in EVENTS:
        # If event isn't selected yet, show nothing for day
        return []
    day_names = get_day_names(ev_name)
    current_lower = (current or "").lower()
    if current_lower:
        day_names = [n for n in day_names if current_lower in n.lower()]
    return [app_commands.Choice(name=n, value=n) for n in day_names[:25]]

# -----------------------------
# Boot
# -----------------------------
if not TOKEN:
    raise SystemExit(
        "Set your token first: export DISCORD_TOKEN=... (macOS/Linux) or $env:DISCORD_TOKEN='...' (PowerShell)"
    )

bot.run(TOKEN)
