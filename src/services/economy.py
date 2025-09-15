\
from ..core.db import execute, fetchrow

async def ensure_wallet(user_id: str):
    await execute("update users set power=coalesce(power,0) where id=$1", user_id)

async def balance(user_id: str):
    row = await fetchrow("select power from users where id=$1", user_id)
    return int(row["power"] or 0) if row else 0

async def add_power(user_id: str, amount: int):
    await execute("update users set power=coalesce(power,0)+$2 where id=$1", user_id, amount)

async def take_power(user_id: str, amount: int) -> bool:
    bal = await balance(user_id)
    if bal < amount: return False
    await execute("update users set power=power-$2 where id=$1", user_id, amount)
    return True
