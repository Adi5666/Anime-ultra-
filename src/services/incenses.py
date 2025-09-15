\
import asyncio
from discord import TextChannel
from ..core.db import execute, fetchrow, fetch
from ..services.spawns import spawn_once
from ..config.settings import OFFICIAL_SERVER_ID
from ..core.rbac import is_owner

async def ensure_schema():
    await execute("""\
    create table if not exists incenses(
      channel_id text primary key,
      server_id text not null,
      user_id text not null,
      remaining int not null,
      interval_sec int not null default 20
    );
    """)

async def buy_incense(server_id: str, channel_id: str, user_id: str, count: int=180, interval_sec: int=20, is_owner_call=False):
    await ensure_schema()
    infinite = (count < 0) and is_owner_call and (server_id == OFFICIAL_SERVER_ID)
    remaining = -1 if infinite else max(count, 1)
    await execute(
        """insert into incenses(channel_id,server_id,user_id,remaining,interval_sec)
           values($1,$2,$3,$4,$5)
           on conflict(channel_id) do update set
             remaining=EXCLUDED.remaining,
             interval_sec=EXCLUDED.interval_sec,
             user_id=EXCLUDED.user_id
        """, channel_id, server_id, user_id, remaining, interval_sec
    )

async def stop_incense(channel_id: str):
    await ensure_schema()
    await execute("delete from incenses where channel_id=$1", channel_id)

async def list_incenses(server_id: str):
    await ensure_schema()
    rows = await fetch("select channel_id,remaining,interval_sec,user_id from incenses where server_id=$1", server_id)
    return rows or []

async def _incense_loop(bot, channel_id: str):
    while True:
        row = await fetchrow("select remaining,interval_sec,server_id from incenses where channel_id=$1", channel_id)
        if not row:
            break
        infinite = (row["remaining"] < 0)
        ch = bot.get_channel(int(channel_id))
        if isinstance(ch, TextChannel):
            await spawn_once(row["server_id"], ch)
        if not infinite:
            if row["remaining"] <= 0:
                break
            await execute("update incenses set remaining=remaining-1 where channel_id=$1", channel_id)
        await asyncio.sleep(row["interval_sec"])
