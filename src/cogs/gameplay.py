\
import discord, datetime
from discord import app_commands
from discord.ext import commands
from ..ui.factory import theme_embed
from ..core.db import fetchrow, fetch, execute
from ..core.consent import ensure_user, consent_block_embed, requires_consent
from ..services.inventory import get_inventory
from ..core.entitlements import has_user_premium
from ..services.daily_streak import bump

class GameplayCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="daily", description="Claim your daily reward.")
    @requires_consent()
    async def daily(self, inter: discord.Interaction):
        uid = str(inter.user.id)
        up = await has_user_premium(uid)
        reward = 20 if up else 10
        await execute("update users set power=coalesce(power,0)+$2 where id=$1", uid, reward)
        streak = await bump(uid)
        await inter.response.send_message(embed=theme_embed("🎁 Daily Reward", f"You gained **{reward}** power!\nStreak: {streak} days", "success"), ephemeral=True)

async def setup(bot): await bot.add_cog(GameplayCog(bot))
