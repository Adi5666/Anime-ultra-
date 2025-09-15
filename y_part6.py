import pathlib

def write(path, content):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

# --- Utility cog ---
write("src/cogs/utility.py", r'''\
import discord
from discord import app_commands
from discord.ext import commands
from ..ui.factory import theme_embed
from ..core.db import execute
from ..core.rbac import is_owner
from ..services.prefixes import get_prefix

class UtilityCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="announce", description="Send an embed announcement.")
    async def announce(self, inter: discord.Interaction, channel: discord.TextChannel, message: str):
        if not is_owner(str(inter.user.id)):
            return await inter.response.send_message(embed=theme_embed("Announce", "Only the owner can use this.", "warn"), ephemeral=True)
        await channel.send(embed=theme_embed("📢 Announcement", message, "info"))
        await inter.response.send_message(embed=theme_embed("Announce", "Sent.", "success"), ephemeral=True)

    @app_commands.command(name="setprefix", description="Change the bot prefix for this server.")
    async def setprefix(self, inter: discord.Interaction, prefix: str):
        await execute("insert into prefixes(server_id,prefix) values($1,$2) on conflict(server_id) do update set prefix=$2", str(inter.guild_id), prefix)
        await inter.response.send_message(embed=theme_embed("Prefix", f"Prefix set to `{prefix}`", "success"), ephemeral=True)

    @app_commands.command(name="toggle_spawns", description="Enable or disable wild spawns.")
    async def toggle_spawns(self, inter: discord.Interaction, enabled: bool):
        await execute("update servers set disabled=$2 where id=$1", str(inter.guild_id), not enabled)
        await inter.response.send_message(embed=theme_embed("Spawns", f"Wild spawns {'enabled' if enabled else 'disabled'}", "success"), ephemeral=True)

    @app_commands.command(name="dev_sync", description="Owner: sync slash commands.")
    async def dev_sync(self, inter: discord.Interaction):
        if not is_owner(str(inter.user.id)):
            return await inter.response.send_message(embed=theme_embed("Sync", "Only the owner can sync.", "warn"), ephemeral=True)
        await self.bot.tree.sync()
        await inter.response.send_message(embed=theme_embed("Sync", "Commands synced.", "success"), ephemeral=True)

async def setup(bot): await bot.add_cog(UtilityCog(bot))
''')

print("bootstrap_y Part 6 applied: utility.py written.")
