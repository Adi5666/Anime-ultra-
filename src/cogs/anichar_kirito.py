\
import discord
from discord import app_commands
from discord.ext import commands
from ..ui.factory import theme_embed

class AniCharKiritoCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="anichar_kirito", description="Summon the Black Swordsman.")
    async def anichar_kirito(self, inter: discord.Interaction):
        desc = (
            "From the shadows of Aincrad, a dual blade gleams.\n"
            "Kirito, the Black Swordsman, stands ready."
        )
        emb = theme_embed("⚔️ Kirito Appears", desc, "purple")
        emb.set_image(url="https://static.wikia.nocookie.net/swordartonline/images/4/4b/Kirito_Alicization.png")
        await inter.response.send_message(embed=emb)

async def setup(bot): await bot.add_cog(AniCharKiritoCog(bot))
