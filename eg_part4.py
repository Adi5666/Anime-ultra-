import pathlib

def write(path, content):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

# --- Kirito command cog ---
write("src/cogs/anichar_kirito.py", r'''\
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
''')

# --- Patch shop.py to add streak refund ---
write("src/cogs/shop.py", r'''\
import discord
from discord import app_commands
from discord.ext import commands
from ..ui.factory import theme_embed
from ..services.economy import balance, take_power
from ..services.incenses import buy_incense, _incense_loop
from ..services.daily_streak import bump
from ..core.consent import requires_consent
import asyncio

SHOP = [
  {"id":"incense_small", "name":"Incense (60x / 20s)", "price":50, "count":60, "interval":20},
  {"id":"incense_large", "name":"Incense (300x / 15s)", "price":180, "count":300, "interval":15}
]

class ShopCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="shop", description="Browse the in-game shop.")
    @requires_consent()
    async def shop(self, inter: discord.Interaction):
        lines = [f"• {it['name']} — {it['price']} power" for it in SHOP]
        await inter.response.send_message(embed=theme_embed("🛒 Shop", "\n".join(lines), "info"))

    @app_commands.command(name="buy", description="Purchase an item from the shop.")
    @requires_consent()
    async def buy(self, inter: discord.Interaction, item_id: str):
        uid = str(inter.user.id)
        it = next((x for x in SHOP if x["id"]==item_id), None)
        if not it:
            return await inter.response.send_message(embed=theme_embed("🛒 Shop", "Unknown item.", "warn"), ephemeral=True)
        streak = await bump(uid)
        if streak >= 7:
            await inter.response.send_message(embed=theme_embed("🔥 Streak Bonus", "7‑day streak! Incense refunded.", "gold"), ephemeral=True)
            return
        if not await take_power(uid, it["price"]):
            return await inter.response.send_message(embed=theme_embed("🛒 Shop", "Not enough power.", "warn"), ephemeral=True)
        await buy_incense(str(inter.guild_id), str(inter.channel.id), uid, it["count"], it["interval"], is_owner_call=False)
        asyncio.create_task(_incense_loop(self.bot, str(inter.channel.id)))
        await inter.response.send_message(embed=theme_embed("🕯️ Incense", f"{it['name']} activated in this channel.", "success"))

async def setup(bot): await bot.add_cog(ShopCog(bot))
''')

# --- Patch daily in gameplay.py to bump streak ---
write("src/cogs/gameplay.py", r'''\
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
''')

print("Easter Eggs Patch Part 4 applied: Kirito command, streak refund in shop, streak bump in daily.")
