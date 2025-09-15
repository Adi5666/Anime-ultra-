import pathlib

def write(path, content):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

# --- Battle logic service ---
write("src/services/battles.py", r'''\
import random

def calc_damage(atk, df):
    base = max(1, atk - int(df*0.6))
    variance = random.randint(-2, 3)
    return max(1, base + variance)

def turn_order(a_spd, b_spd):
    return ("A","B") if a_spd >= b_spd else ("B","A")
''')

# --- Battles cog (cinematic scaffold) ---
write("src/cogs/battles.py", r'''\
import discord
from discord import app_commands
from discord.ext import commands
from ..ui.factory import theme_embed
from ..core.db import fetchrow
from ..services.battles import calc_damage, turn_order
from ..core.consent import requires_consent

class BattlesCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="battle", description="Challenge someone to a duel (scaffold).")
    @requires_consent()
    async def battle(self, inter: discord.Interaction, user: discord.User, your_creature_id: str, their_creature_id: str):
        if user.id == inter.user.id:
            return await inter.response.send_message(embed=theme_embed("Battle", "You cannot battle yourself.", "warn"), ephemeral=True)
        a = await fetchrow("select * from creatures where id=$1 and owner_id=$2", your_creature_id, str(inter.user.id))
        b = await fetchrow("select * from creatures where id=$1 and owner_id=$2", their_creature_id, str(user.id))
        if not a or not b:
            return await inter.response.send_message(embed=theme_embed("Battle", "Invalid creatures or ownership.", "warn"), ephemeral=True)

        order = turn_order(a["spd"], b["spd"])
        a_hp, b_hp = 30, 30
        log = []
        for _ in range(6):
            if order[0] == "A":
                dmg = calc_damage(a["atk"], b["def"]); b_hp -= dmg
                log.append(f"Your {a['name']} strikes for {dmg} → Opponent HP {max(0,b_hp)}")
                if b_hp <= 0: break
                dmg = calc_damage(b["atk"], a["def"]); a_hp -= dmg
                log.append(f"Their {b['name']} counters for {dmg} → Your HP {max(0,a_hp)}")
                if a_hp <= 0: break
            else:
                dmg = calc_damage(b["atk"], a["def"]); a_hp -= dmg
                log.append(f"Their {b['name']} opens for {dmg} → Your HP {max(0,a_hp)}")
                if a_hp <= 0: break
                dmg = calc_damage(a["atk"], b["def"]); b_hp -= dmg
                log.append(f"Your {a['name']} replies for {dmg} → Opponent HP {max(0,b_hp)}")
                if b_hp <= 0: break

        if a_hp == b_hp:
            result = "It’s a draw — legends are forged in stalemates."
        elif a_hp > b_hp:
            result = f"You win! {a['name']} stands triumphant."
        else:
            result = f"You fall this time. {b['name']} proves formidable."

        emb = theme_embed("⚔️ Duel Results", "\n".join(log) + f"\n\n{result}", "info")
        await inter.response.send_message(embed=emb)

async def setup(bot): await bot.add_cog(BattlesCog(bot))
''')

print("bootstrap_x Part 3 applied: battles.py written.")
