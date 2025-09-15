import pathlib

def write(path, content):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

# --- Economy service (power currency) ---
write("src/services/economy.py", r'''\
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
''')

# --- Achievements service ---
write("src/services/achievements.py", r'''\
from ..core.db import execute, fetch, fetchrow

async def ensure_schema():
    await execute("""\
    create table if not exists achievements(
      id bigserial primary key,
      user_id text not null,
      key text not null,
      title text not null,
      earned_at timestamp with time zone default now(),
      unique(user_id, key)
    );""")

async def grant(user_id: str, key: str, title: str):
    await ensure_schema()
    await execute("insert into achievements(user_id,key,title) values($1,$2,$3) on conflict do nothing", user_id, key, title)

async def list_for(user_id: str):
    await ensure_schema()
    return await fetch("select key,title,earned_at from achievements where user_id=$1 order by earned_at desc", user_id)

async def maybe_grant_milestones(user_id: str, creatures_count: int, shiny_count: int):
    if creatures_count >= 1: await grant(user_id, "first_catch", "First Catch!")
    if creatures_count >= 50: await grant(user_id, "collector_50", "Collector 50")
    if creatures_count >= 200: await grant(user_id, "collector_200", "Collector 200")
    if shiny_count >= 1: await grant(user_id, "first_shiny", "First Shiny")
''')

print("bootstrap_x Part 1 applied: economy.py and achievements.py written.")
