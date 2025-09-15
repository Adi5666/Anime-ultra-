\
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
