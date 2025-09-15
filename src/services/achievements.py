\
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
