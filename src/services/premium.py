\
from datetime import datetime, timedelta
from ..core.db import execute

async def grant_server_premium(server_id: str, days: int|None):
    if days is None:
        await execute("update servers set premium=true, premium_until=null where id=$1", server_id)
    else:
        until = datetime.utcnow() + timedelta(days=days)
        await execute("update servers set premium=false, premium_until=$2 where id=$1", server_id, until)

async def revoke_server_premium(server_id: str):
    await execute("update servers set premium=false, premium_until=null where id=$1", server_id)

async def grant_user_premium(user_id: str, days: int|None):
    if days is None:
        await execute("update users set premium=true, premium_until=null where id=$1", user_id)
    else:
        until = datetime.utcnow() + timedelta(days=days)
        await execute("update users set premium=false, premium_until=$2 where id=$1", user_id, until)

async def revoke_user_premium(user_id: str):
    await execute("update users set premium=false, premium_until=null where id=$1", user_id)
