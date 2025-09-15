\
import discord
from discord import app_commands
from discord.ext import commands
from ..ui.factory import theme_embed
from ..core.db import fetch, fetchrow

async def _page_rows(rows, page, size):
    start = (page-1)*size; end = start+size
    return rows[start:end]

class LeaderboardsCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="leaderboard", description="View top players.")
    async def leaderboard(self, inter: discord.Interaction, lb_type: str="captures", page: int=1):
        lb_type = lb_type.lower()
        if lb_type not in ("captures","shinies","power"):
            return await inter.response.send_message(embed=theme_embed("❓ Leaderboard", "Type must be captures, shinies, or power.", "warn"), ephemeral=True)

        if lb_type == "captures":
            rows = await fetch("select id as user_id, coalesce(claims,0) as score from users order by score desc nulls last")
            title = "🏆 Leaderboard — Captures"
        elif lb_type == "shinies":
            rows = await fetch("select owner_id as user_id, count(*) as score from creatures where shiny=true group by owner_id order by score desc")
            title = "✨ Leaderboard — Shinies"
        else:
            rows = await fetch("select id as user_id, coalesce(power,0) as score from users order by score desc nulls last")
            title = "⚡ Leaderboard — Power"

        page_rows = await _page_rows(rows, page, 10)
        if not page_rows:
            return await inter.response.send_message(embed=theme_embed("Leaderboard", "No entries on this page.", "info"), ephemeral=True)

        lines = []
        for i, r in enumerate(page_rows, start=1+(page-1)*10):
            lines.append(f"**#{i}** <@{r['user_id']}> — {r['score']}")

        my_id = str(inter.user.id)
        my_score = 0
        for r in rows:
            if r["user_id"] == my_id:
                my_score = r["score"]; break
        my_rank = next((i+1 for i, r in enumerate(rows) if r["user_id"] == my_id), None)
        me = f"Your rank: **#{my_rank}** — {my_score}" if my_rank else "You are not ranked yet."

        emb = theme_embed(title, "\n".join(lines) + f"\n\n{me}\nPage {page}", "gold")
        await inter.response.send_message(embed=emb)

async def setup(bot): await bot.add_cog(LeaderboardsCog(bot))
