import pathlib

def write(path, content):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

# --- Patch spawns.py to add Easter Egg variants ---
write("src/services/spawns.py", r'''\
import random, json, pathlib, datetime
from discord import Embed, Colour, TextChannel
from ..core.db import execute, fetchrow
from ..core.entitlements import get_server_spawn_mode

def load_catalog():
    p = pathlib.Path("src/content/catalog.json")
    if not p.exists():
        return {"families":{}}, {}
    data = json.loads(p.read_text(encoding="utf-8"))
    return data, data.get("families", {}) or {}

def rarity_color(r):
    return {
        "COMMON": Colour.light_grey(),
        "UNCOMMON": Colour.teal(),
        "RARE": Colour.blue(),
        "EPIC": Colour.purple(),
        "MYTHIC": Colour.gold()
    }.get(r, Colour.dark_grey())

async def has_active_spawn(channel_id: str):
    row = await fetchrow("select 1 from spawns where channel_id=$1 limit 1", channel_id)
    return bool(row)

def pick(fams):
    families = [k for k,v in fams.items() if v]
    if not families:
        raise RuntimeError("No families in catalog.json")
    fam = random.choice(families)
    ch = random.choice(fams[fam])
    return fam, ch

async def spawn_once(gid: str, channel: TextChannel):
    if await has_active_spawn(str(channel.id)):
        return
    _, fams = load_catalog()
    fam, ch = pick(fams)
    name = ch["name"]
    rarity = ch.get("rarity","UNCOMMON")
    mode = await get_server_spawn_mode(gid)
    img = ch.get("authentic_image") if mode == "authentic" else ch.get("safe_image")

    # Easter Egg variants
    boosted = False
    hour = datetime.datetime.utcnow().hour
    if 18 <= hour or hour < 6:
        if random.random() < 0.15:
            rarity = "MYTHIC"
            boosted = True
            name = f"Night Shiny {name}"
    if random.random() < 0.05:
        boosted = True
        name = f"Archivist {name}"
    if random.random() < 0.03:
        boosted = True
        name = f"MemeMaster {name}"

    emb = Embed(
        title="A shadowed figure appears…",
        description="A mysterious aura gathers. Identify this hero to claim them!",
        colour=rarity_color(rarity)
    )
    if img: emb.set_image(url=img)
    footer = f"Rarity: {rarity} • Use /hint then /guess <name>"
    if boosted: footer += " • BOOSTED"
    emb.set_footer(text=footer)

    await execute(
        "insert into spawns(server_id,channel_id,code,template_name,family,safe_image,authentic_image,rarity) values($1,$2,$3,$4,$5,$6,$7,$8)",
        gid, str(channel.id), "", name, fam, ch.get("safe_image"), ch.get("authentic_image"), rarity
    )
    await channel.send(embed=emb)
''')

print("Easter Eggs Patch Part 2 applied: spawns.py upgraded with Night Shiny, Archivist, MemeMaster, boosted flag.")
