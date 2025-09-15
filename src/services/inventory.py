\
from ..core.db import fetchrow, fetch, execute

async def add_item(user_id: str, key: str, qty: int=1):
    await execute("insert into inventory(user_id,item_key,qty) values($1,$2,$3) on conflict(user_id,item_key) do update set qty=inventory.qty+$3", user_id, key, qty)

async def take_item(user_id: str, key: str, qty: int=1) -> bool:
    row = await fetchrow("select qty from inventory where user_id=$1 and item_key=$2", user_id, key)
    have = (row["qty"] if row else 0)
    if have < qty: return False
    await execute("update inventory set qty=qty-$3 where user_id=$1 and item_key=$2", user_id, key, qty)
    return True

async def get_inventory(user_id: str):
    return await fetch("select item_key, qty from inventory where user_id=$1 order by item_key", user_id)
