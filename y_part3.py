import pathlib

def write(path, content):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

# --- Gameplay cog (consent-gated profile, card, daily, dex) ---
write("src/cogs/gameplay.py", r'''\
import discord, datetime
from discord import app_commands
from discord.ext import commands
from ..ui.factory import theme_embed
from ..core.db import fetchrow, fetch, execute
from ..core.consent import ensure_user, consent_block_embed, requires_consent
from ..services.inventory import get_inventory
from ..core.entitlements import has_user_premium

class GameplayCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="register", description="Register and accept Terms & Privacy to start.")
    async def register(self, inter: discord.Interaction):
        await ensure_user(str(inter.user.id), inter.user.name)
        await inter.response.send_message(embed=consent_block_embed(), ephemeral=True)

    @app_commands.command(name="terms", description="Review and accept Terms & Privacy again.")
    async def terms(self, inter: discord.Interaction):
        await ensure_user(str(inter.user.id), inter.user.name)
        await inter.response.send_message(embed=consent_block_embed(), ephemeral=True)

    @app_commands.command(name="profile", description="View your hero profile and stats.")
    @requires_consent()
    async def profile(self, inter: discord.Interaction):
        uid = str(inter.user.id)
        await ensure_user(uid, inter.user.name)
        total = (await fetchrow("select count(*) as c from creatures where owner_id=$1", uid))["c"] or 0
        unique = (await fetchrow("select count(distinct name) as c from creatures where owner_id=$1", uid))["c"] or 0
        shiny = (await fetchrow("select count(*) as c from creatures where owner_id=$1 and shiny=true", uid))["c"] or 0
        power = (await fetchrow("select power from users where id=$1", uid))["power"] or 0
        up = await has_user_premium(uid)
        inv = await get_inventory(uid)
        inv_line = ", ".join(f"{r['item_key']}×{r['qty']}" for r in inv) if inv else "Empty"
        lines = [
            f"Total Captures: **{total}**",
            f"Unique Heroes: **{unique}**",
            f"Shiny Found: **{shiny}**",
            f"Power Level: **{power}**",
            f"Inventory: {inv_line}",
            "",
            f"Premium Status: {'✅ Premium' if up else '❌ No Premium'}"
        ]
        await inter.response.send_message(embed=theme_embed(f"🦸 Profile — {inter.user.name}", "\n".join(lines), "info"))

    @app_commands.command(name="card", description="View a captured hero's card.")
    @requires_consent()
    async def card(self, inter: discord.Interaction, creature_id: str):
        uid = str(inter.user.id)
        row = await fetchrow("select * from creatures where id=$1 and owner_id=$2", creature_id, uid)
        if not row:
            return await inter.response.send_message(embed=theme_embed("Card", "Creature not found or not owned by you.", "warn"), ephemeral=True)
        title = f"{'🌟 ' if row['shiny'] else ''}{row['name']} [{row['rarity']}]"
        desc = f"ATK {row['atk']} • DEF {row['def']} • SPD {row['spd']}\nCaught: {row['caught_at'].strftime('%Y-%m-%d %H:%M UTC')}"
        emb = theme_embed(f"🎴 {title}", desc, "info")
        await inter.response.send_message(embed=emb)

    @app_commands.command(name="daily", description="Claim your daily reward.")
    @requires_consent()
    async def daily(self, inter: discord.Interaction):
        uid = str(inter.user.id)
        up = await has_user_premium(uid)
        reward = 20 if up else 10
        await execute("update users set power=coalesce(power,0)+$2 where id=$1", uid, reward)
        await inter.response.send_message(embed=theme_embed("🎁 Daily Reward", f"You gained **{reward}** power!", "success"), ephemeral=True)

    @app_commands.command(name="dex", description="Show your unique collection.")
    @requires_consent()
    async def dex(self, inter: discord.Interaction):
        uid = str(inter.user.id)
        rows = await fetch("select name, count(*) as c from creatures where owner_id=$1 group by name order by c desc", uid)
        if not rows:
            return await inter.response.send_message(embed=theme_embed("Dex", "You haven’t caught any heroes yet.", "info"), ephemeral=True)
        lines = [f"**{r['name']}** — {r['c']}" for r in rows[:25]]
        await inter.response.send_message(embed=theme_embed("📜 Your Dex", "\n".join(lines), "info"))

async def setup(bot): await bot.add_cog(GameplayCog(bot))
''')

print("bootstrap_y Part 3 applied: gameplay.py written.")
