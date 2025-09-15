\
import datetime, discord
from discord import app_commands
from discord.ext import commands
from ..ui.factory import theme_embed
from ..core.db import fetchrow, execute
from ..services.economy import add_power
from ..core.consent import requires_consent

QUESTS = {
    "daily": "Catch 3 heroes today",
    "weekly": "Gain 150 power this week"
}

class QuestsCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    async def _ensure(self, uid):
        await execute("""\
        create table if not exists user_quests(
          user_id text primary key,
          daily_count int default 0,
          daily_date date,
          weekly_power int default 0,
          week_iso text
        );""")
        await execute("insert into user_quests(user_id) values($1) on conflict do nothing", uid)

    @app_commands.command(name="quest", description="View and claim quest rewards.")
    @requires_consent()
    async def quest(self, inter: discord.Interaction):
        uid = str(inter.user.id)
        await self._ensure(uid)
        today = datetime.date.today()
        week = f"{today.isocalendar().year}-W{today.isocalendar().week}"
        row = await fetchrow("select * from user_quests where user_id=$1", uid)
        daily_done = (row["daily_date"] == today) and (row["daily_count"] >= 3)
        weekly_done = (row["week_iso"] == week) and (row["weekly_power"] >= 150)
        lines = []
        lines.append(f"Daily: {QUESTS['daily']} — {'✅' if daily_done else f'{row['daily_count'] or 0}/3'}")
        lines.append(f"Weekly: {QUESTS['weekly']} — {'✅' if weekly_done else f'{row['weekly_power'] or 0}/150'}")
        await inter.response.send_message(embed=theme_embed("📜 Quests", "\n".join(lines), "info"))

    @app_commands.command(name="quest_claim", description="Claim quest rewards, if complete.")
    @requires_consent()
    async def quest_claim(self, inter: discord.Interaction):
        uid = str(inter.user.id)
        await self._ensure(uid)
        today = datetime.date.today()
        week = f"{today.isocalendar().year}-W{today.isocalendar().week}"
        row = await fetchrow("select * from user_quests where user_id=$1", uid)
        reward = 0
        if (row["daily_date"] == today) and (row["daily_count"] >= 3):
            reward += 15
            await execute("update user_quests set daily_count=0, daily_date=null where user_id=$1", uid)
        if (row["week_iso"] == week) and (row["weekly_power"] >= 150):
            reward += 60
            await execute("update user_quests set weekly_power=0, week_iso=null where user_id=$1", uid)
        if reward == 0:
            return await inter.response.send_message(embed=theme_embed("📜 Quests", "Nothing to claim yet.", "warn"), ephemeral=True)
        await add_power(uid, reward)
        await inter.response.send_message(embed=theme_embed("🎁 Quest Rewards", f"You gained **{reward}** power!", "success"))

async def setup(bot): await bot.add_cog(QuestsCog(bot))
