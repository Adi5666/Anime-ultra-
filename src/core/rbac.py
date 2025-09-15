\
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
