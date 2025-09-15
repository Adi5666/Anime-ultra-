\
import discord
from discord.ext import commands
from ..core.db import fetchrow
from ..services.claims import complete_claim_for_spawn
from ..ui.factory import theme_embed
from ..services.secrets_state import set_dual_hint, has_dual_hint

class SpawnListenerCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        content = message.content.strip().lower()

        # Easter Egg: Dracarys trigger
        if content == "dracarys":
            await message.channel.send(embed=theme_embed("🔥 Dracarys!", "The dragon’s flames roar to life!", "danger"))
            return

        # Example: guess command simulation
        if content.startswith("!guess "):
            guess_name = content[7:].strip()
            spawn_row = await fetchrow("select * from spawns where channel_id=$1 limit 1", str(message.channel.id))
            if not spawn_row:
                return
            if guess_name.lower() == spawn_row["template_name"].lower():
                result = await complete_claim_for_spawn(spawn_row, str(message.author.id))
                await message.channel.send(embed=theme_embed("✅ Captured!", f"You caught **{result['name']}**!", "success"))
                # Easter Egg: Dual-Wield hint grant
                if "dual" in result["name"].lower():
                    set_dual_hint(str(message.author.id))
            else:
                await message.channel.send(embed=theme_embed("❌ Wrong Guess", "Try again!", "warn"))

async def setup(bot): await bot.add_cog(SpawnListenerCog(bot))
