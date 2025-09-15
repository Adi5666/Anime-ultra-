\
import discord
from discord import app_commands
from discord.ext import commands
from ..core.db import fetchrow
from ..ui.factory import theme_embed
from ..services.secrets_state import has_dual_hint

class HintCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="hint", description="Get a hint for the current spawn.")
    async def hint(self, inter: discord.Interaction):
        row = await fetchrow("select * from spawns where channel_id=$1 limit 1", str(inter.channel.id))
        if not row:
            return await inter.response.send_message(embed=theme_embed("Hint", "No active spawn here.", "info"), ephemeral=True)
        masked = "".join("_" if c.isalnum() else c for c in row["template_name"])
        desc = f"Name: {masked}\nFamily: {row['family'] or 'Unknown'}"
        if has_dual_hint(str(inter.user.id)):
            desc += "\n\n⚔️ You sense this hero can wield two blades at once..."
        await inter.response.send_message(embed=theme_embed("Hint", desc, "info"))

async def setup(bot): await bot.add_cog(HintCog(bot))
