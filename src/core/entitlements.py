\
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
