import pathlib

def write(path, content):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

# --- Consent buttons cog ---
write("src/cogs/consent_buttons.py", r'''\
import discord
from discord import app_commands
from discord.ext import commands
from ..ui.factory import theme_embed
from ..core.db import execute
from ..core.consent import requires_consent_prefix

class ConsentButtonsCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="approve", description="Accept Terms & Privacy and begin playing.")
    async def approve(self, inter: discord.Interaction):
        uid = str(inter.user.id)
        await execute("update users set registered=true, accepted_terms=true where id=$1", uid)
        await inter.response.send_message(embed=theme_embed("✅ Approved", "You may now begin your journey!", "success"), ephemeral=True)

    @app_commands.command(name="reject", description="Decline Terms & Privacy and disable gameplay.")
    async def reject(self, inter: discord.Interaction):
        uid = str(inter.user.id)
        await execute("update users set registered=false, accepted_terms=false where id=$1", uid)
        await inter.response.send_message(embed=theme_embed("❌ Rejected", "You will not be able to play until you approve.", "warn"), ephemeral=True)

async def setup(bot): await bot.add_cog(ConsentButtonsCog(bot))
''')

print("bootstrap_y Part 4 applied: consent_buttons.py written.")
