\
import random, discord
from discord import app_commands
from discord.ext import commands
from ..ui.factory import theme_embed
from ..core.consent import requires_consent

ROTATIONS = {
  "Spring": ["demon_slayer","jujutsu_kaisen"],
  "Summer": ["one_piece","bleach"],
  "Autumn": ["attack_on_titan","naruto"],
  "Winter": ["dragon_ball","my_hero_academia"]
}

class EventsRotationCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="event_rotation", description="Show current seasonal boosts.")
    @requires_consent()
    async def event_rotation(self, inter: discord.Interaction):
        season = random.choice(list(ROTATIONS.keys()))
        packs = ", ".join(ROTATIONS[season])
        await inter.response.send_message(embed=theme_embed("🎉 Seasonal Event", f"Season: **{season}**\nBoosted packs: {packs}", "gold"))

async def setup(bot): await bot.add_cog(EventsRotationCog(bot))
