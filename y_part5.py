import pathlib

def write(path, content):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

# --- Global checks cog ---
write("src/cogs/error_handler.py", r'''\
import discord, datetime
from discord.ext import commands
from ..core.db import fetchrow
from ..ui.factory import theme_embed

class ErrorHandlerCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        uid = str(ctx.author.id)
        row = await fetchrow("select banned, ban_reason, suspended_until, suspend_reason from users where id=$1", uid)
        if row and row["banned"]:
            raise commands.CheckFailure(f"Banned: {row['ban_reason']}")
        if row and row["suspended_until"]:
            until = row["suspended_until"]
            if until > datetime.datetime.utcnow():
                raise commands.CheckFailure(f"Suspended until {until} — {row['suspend_reason']}")
        return True

async def setup(bot): await bot.add_cog(ErrorHandlerCog(bot))
''')

print("bootstrap_y Part 5 applied: error_handler.py written.")
