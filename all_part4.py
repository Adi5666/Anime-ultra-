import pathlib

def write(path, content):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

# --- RBAC (roles & permissions) ---
write("src/core/rbac.py", r'''\
from ..config.settings import OWNER_IDS

OWNER_IDS_CLEAN = {x for x in OWNER_IDS if x}

def is_owner(uid: str) -> bool:
    return uid in OWNER_IDS_CLEAN

async def has_role(uid: str, role: str, fetchrow=None) -> bool:
    if is_owner(uid): return True
    if not fetchrow: return False
    row = await fetchrow("select role_name from bot_roles where user_id=$1", uid)
    return bool(row and row["role_name"] == role)

async def can_ban(uid: str, fetchrow=None) -> bool:
    if is_owner(uid): return True
    if not fetchrow: return False
    row = await fetchrow("select role_name from bot_roles where user_id=$1", uid)
    return bool(row and row["role_name"] in ("bot_admin","bot_moderator"))

async def can_unban(uid: str, fetchrow=None) -> bool:
    if is_owner(uid): return True
    if not fetchrow: return False
    row = await fetchrow("select role_name from bot_roles where user_id=$1", uid)
    return bool(row and row["role_name"] in ("bot_admin",))

async def can_suspend(uid: str, fetchrow=None) -> bool:
    return await can_ban(uid, fetchrow)

async def can_grant_premium(uid: str, fetchrow=None) -> bool:
    if is_owner(uid): return True
    if not fetchrow: return False
    row = await fetchrow("select role_name from bot_roles where user_id=$1", uid)
    return bool(row and row["role_name"] in ("bot_admin",))
''')

# --- Spawn service (basic) ---
write("src/services/spawns.py", r'''\
import random, json, pathlib
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
    emb = Embed(
        title="A shadowed figure appears…",
        description="A mysterious aura gathers. Identify this hero to claim them!",
        colour=rarity_color(rarity)
    )
    if img: emb.set_image(url=img)
    emb.set_footer(text=f"Rarity: {rarity} • Use /hint then /guess <name>")
    await execute(
        "insert into spawns(server_id,channel_id,code,template_name,family,safe_image,authentic_image,rarity) values($1,$2,$3,$4,$5,$6,$7,$8)",
        gid, str(channel.id), "", name, fam, ch.get("safe_image"), ch.get("authentic_image"), rarity
    )
    await channel.send(embed=emb)
''')

print("bootstrap_all Part 4 applied: rbac.py and spawns.py written.")
