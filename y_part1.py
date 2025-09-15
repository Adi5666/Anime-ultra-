import pathlib

def write(path, content):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

# --- Consent service + cinematic policy embeds ---
write("src/core/consent.py", r'''\
from ..core.db import fetchrow, execute
from ..ui.factory import theme_embed
from ..config.settings import PRIVACY_URL, TERMS_URL
from discord import Interaction
from discord.ext import commands
from discord import app_commands

async def ensure_user(uid: str, name: str):
    await execute("insert into users(id,name) values($1,$2) on conflict do nothing", uid, name)

async def has_registration(uid: str):
    row = await fetchrow("select registered, accepted_terms from users where id=$1", uid)
    return bool(row and row["registered"] and row["accepted_terms"])

def consent_block_embed():
    return theme_embed(
        "📜 Terms & Privacy",
        f"Before playing, you must accept our Policies.\n\n"
        f"• Privacy Policy: {PRIVACY_URL}\n"
        f"• Terms of Use: {TERMS_URL}\n\n"
        "Choose: Approve to continue, or Reject to decline.",
        "purple"
    )

def requires_consent():
    async def check(inter: Interaction):
        uid = str(inter.user.id)
        row = await fetchrow("select registered, accepted_terms from users where id=$1", uid)
        if not row or not row["registered"] or not row["accepted_terms"]:
            try:
                await inter.response.send_message(embed=consent_block_embed(), ephemeral=True)
            except:
                pass
            raise app_commands.CheckFailure("Consent required")
        return True
    return app_commands.check(check)

def requires_consent_prefix():
    def predicate(ctx: commands.Context):
        return True
    return commands.check(predicate)
''')

print("bootstrap_y Part 1 applied: consent.py written.")
