import pathlib

def write(path, content):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

# --- Prefix service ---
write("src/services/prefixes.py", r'''\
from ..core.db import fetchrow, execute
from ..config.settings import DEFAULT_PREFIX

async def get_prefix(gid: str) -> str:
    row = await fetchrow("select prefix from prefixes where server_id=$1", gid)
    return row["prefix"] if row and row["prefix"] else DEFAULT_PREFIX
''')

# --- Security settings ---
write("src/core/security.py", r'''\
def should_hide_names() -> bool:
    return True

def guess_cooldown_sec() -> int:
    return 2
''')

# --- Entitlements (Premium checks) ---
write("src/core/entitlements.py", r'''\
from datetime import datetime
from .db import fetchrow

async def _active(ts):
    if not ts: return False
    return datetime.utcnow() < ts

async def has_server_premium(server_id: str) -> bool:
    row = await fetchrow("select premium, premium_until from servers where id=$1", server_id)
    if not row: return False
    if row["premium"]: return True
    return await _active(row["premium_until"])

async def has_user_premium(user_id: str) -> bool:
    row = await fetchrow("select premium, premium_until from users where id=$1", user_id)
    if not row: return False
    if row["premium"]: return True
    return await _active(row["premium_until"])

async def get_server_spawn_mode(server_id: str) -> str:
    row = await fetchrow("select spawn_mode from servers where id=$1", server_id)
    return row["spawn_mode"] if row and row["spawn_mode"] in ("safe","authentic") else "safe"
''')

print("bootstrap_all Part 3 applied: prefixes.py, security.py, entitlements.py written.")
