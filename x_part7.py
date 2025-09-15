import pathlib

def write(path, content):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

# --- Help cog (cinematic categories) ---
write("src/cogs/help.py", r'''\
import discord
from discord import app_commands
from discord.ext import commands
from ..ui.factory import theme_embed

CATEGORIES = {
  "Gameplay": [
    ("register", "Join the adventure", "/register"),
    ("profile", "View your stats", "/profile"),
    ("card", "Show a hero card", "/card <id>"),
    ("daily", "Claim daily power", "/daily"),
    ("rename_character", "Premium: rename a hero", "/rename_character <id> <new_name>"),
    ("dex", "Unique captures", "/dex")
  ],
  "Spawns": [
    ("hint", "Masked name + lore clue", "/hint"),
    ("guess", "Guess to claim", "/guess <name>"),
    ("buy_incense", "Timed spawns here", "/buy_incense [count] [interval]"),
    ("stop_incense", "Stop incense", "/stop_incense"),
    ("incense_status", "Active incenses", "/incense_status")
  ],
  "Leaderboards": [
    ("leaderboard", "Top 10 players", "/leaderboard <captures|shinies|power> [page]")
  ],
  "Battles": [
    ("battle", "Duel scaffold", "/battle @user <your_id> <their_id>")
  ],
  "Quests": [
    ("quest", "View progress", "/quest"),
    ("quest_claim", "Claim rewards", "/quest_claim")
  ],
  "Shop": [
    ("shop", "Browse items", "/shop"),
    ("buy", "Purchase item", "/buy <item_id>")
  ],
  "Premium": [
    ("premium_status", "See perks", "/premium_status"),
    ("set_spawn_mode", "Admin: safe/authentic", "/set_spawn_mode <safe|authentic>"),
    ("summon", "Premium: instant spawn", "/summon"),
    ("event_spawn", "Premium: Mythic spawn", "/event_spawn"),
    ("grant_server_premium", "Owner/Admin: timed/permanent", "/grant_server_premium [days]"),
    ("revoke_server_premium", "Owner/Admin: revoke", "/revoke_server_premium"),
    ("grant_user_premium", "Owner/Admin: timed/permanent", "/grant_user_premium @user [days]"),
    ("revoke_user_premium", "Owner/Admin: revoke", "/revoke_user_premium @user")
  ],
  "Admin & Roles": [
    ("admin_ban", "Ban via bot", "/admin_ban @user <reason>"),
    ("admin_unban", "Unban", "/admin_unban @user [reason]"),
    ("admin_suspend", "Timed suspend", "/admin_suspend @user <minutes> <reason>"),
    ("botadmin_add", "Owner: add Bot Admin", "/botadmin_add @user"),
    ("botadmin_remove", "Owner: remove Bot Admin", "/botadmin_remove @user"),
    ("botmod_add", "Owner: add Bot Moderator", "/botmod_add @user"),
    ("botmod_remove", "Owner: remove Bot Moderator", "/botmod_remove @user")
  ],
  "Utility": [
    ("setprefix", "Change prefix", "/setprefix <prefix>"),
    ("toggle_spawns", "Enable/disable wild", "/toggle_spawns <true|false>"),
    ("announce", "Embed announcement", "/announce #channel <message>"),
    ("dev_sync", "Owner: sync commands", "/dev_sync")
  ],
  "Packs": [
    ("packs_list", "Available packs", "/packs_list"),
    ("packs_enable", "Enable pack", "/packs_enable <pack>"),
    ("packs_disable", "Disable pack", "/packs_disable <pack>")
  ],
  "Trading": [
    ("trade_start", "Start trade", "/trade_start @user"),
    ("trade_add", "Add item", "/trade_add <trade_id> <creature_id>"),
    ("trade_ready", "Mark ready", "/trade_ready <trade_id>"),
    ("trade_confirm", "Confirm trade", "/trade_confirm <trade_id>")
  ],
  "Capital & Events": [
    ("capital_add", "Add Capital channel", "/capital_add"),
    ("capital_remove", "Remove Capital channel", "/capital_remove"),
    ("capital_list", "List Capital channels", "/capital_list"),
    ("event_rotation", "Seasonal boosts", "/event_rotation")
  ]
}

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.remove_command("help")

    @app_commands.command(name="help", description="Cinematic help with categories and usage.")
    async def help_slash(self, inter: discord.Interaction, category: str=None):
        if category:
            cat = category.title()
            items = CATEGORIES.get(cat)
            if not items:
                return await inter.response.send_message(embed=theme_embed("❓ Help","No such category.","warn"), ephemeral=True)
            emb = theme_embed(f"📖 Help — {cat}", "", "info")
            for name, desc, usage in items:
                emb.add_field(name=f"/{name}", value=f"{desc}\n`{usage}`", inline=False)
            return await inter.response.send_message(embed=emb, ephemeral=True)
        emb = theme_embed("📖 Help — Index", "Choose a category or use `/help <Category>`", "info")
        for cat in CATEGORIES.keys():
            emb.add_field(name=cat, value="—", inline=True)
        await inter.response.send_message(embed=emb, ephemeral=True)

    @commands.command(name="help")
    async def help_prefix(self, ctx: commands.Context, *, category: str=None):
        if category:
            await self.help_slash(ctx, category)
        else:
            emb = theme_embed("📖 Help", "Use `/help` for interactive help or `/help <Category>` for detail.", "info")
            await ctx.reply(embed=emb, mention_author=False)

async def setup(bot): await bot.add_cog(HelpCog(bot))
''')

print("bootstrap_x Part 7 applied: help.py written.")
