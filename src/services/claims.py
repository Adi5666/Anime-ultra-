\
import random, json, pathlib
from ..core.db import fetchrow, execute
from ..core.entitlements import has_server_premium

def load_catalog():
    p = pathlib.Path("src/content/catalog.json")
    data = json.loads(p.read_text(encoding="utf-8"))
    return data.get("families", {}) or {}

def lookup(fams, name, fallback_family):
    for fam, arr in fams.items():
        for c in arr:
            if c.get("name","").lower() == name.lower():
                base = c.get("base") or {"atk":12,"def":11,"spd":12}
                return fam, base, c.get("rarity","UNCOMMON"), c.get("ability","Signature Technique"), c.get("shiny_ability")
    return fallback_family, {"atk":12,"def":11,"spd":12}, "UNCOMMON", "Signature Technique", None

def roll_iv(): return random.randint(0,31)
def ivp(a,b,c): return round(((a+b+c)/(31*3))*100, 1)

async def complete_claim_for_spawn(spawn_row, user_id: str, premium_user: bool=False):
    fams = load_catalog()
    name = spawn_row["template_name"]
    fam, base, rarity, ability, shiny_ability = lookup(fams, name, spawn_row.get("family") or "misc")
    a,b,c = roll_iv(), roll_iv(), roll_iv()
    atk = base["atk"] + int(a/5)
    df  = base["def"] + int(b/5)
    spd = base["spd"] + int(c/5)
    iv_percent = ivp(a,b,c)
    shiny_chance = 0.006
    try:
        if await has_server_premium(spawn_row["server_id"]):
            shiny_chance *= 1.8
    except:
        pass
    if premium_user: shiny_chance *= 1.5
    shiny = (random.random() < shiny_chance)
    ability_text = f"**Ability Unlocked:** {shiny_ability}" if shiny and shiny_ability else f"**Ability Unlocked:** {ability}"
    creature = await fetchrow("""\
        insert into creatures(owner_id,server_id,name,family,rarity,shiny,atk,def,spd)
        values($1,$2,$3,$4,$5,$6,$7,$8,$9)
        returning id,name,rarity,shiny,atk,def,spd
    """, user_id, spawn_row["server_id"], name, fam, rarity, shiny, atk, df, spd)
    gain = (25 if (shiny or rarity=="MYTHIC") else 15 if rarity=="EPIC" else 8 if rarity=="RARE" else 3 if rarity=="UNCOMMON" else 1)
    gain += int(iv_percent/20)
    await execute("update users set claims=coalesce(claims,0)+1, power=coalesce(power,0)+$2 where id=$1", user_id, gain)
    await execute("delete from spawns where id=$1", spawn_row["id"])
    return { "id": creature["id"], "name": creature["name"], "rarity": creature["rarity"], "shiny": creature["shiny"],
             "atk": creature["atk"], "def": creature["def"], "spd": creature["spd"], "iv_percent": iv_percent,
             "ability_text": ability_text }
