\
from ..core.db import fetchrow, execute
import datetime

async def ensure_schema():
    await execute("""\
    create table if not exists streaks(
      user_id text primary key,
      last date,
      count int default 0
    );""")

async def bump(uid: str) -> int:
    await ensure_schema()
    today = datetime.date.today()
    row = await fetchrow("select last,count from streaks where user_id=$1", uid)
    if not row:
        await execute("insert into streaks(user_id,last,count) values($1,$2,1)", uid, today)
        return 1
    last, count = row["last"], row["count"]
    if last == today:
        return count or 1
    expected = last + datetime.timedelta(days=1) if last else None
    if expected and today == expected:
        c = (count or 0) + 1
        await execute("update streaks set last=$2,count=$3 where user_id=$1", uid, today, c)
        return c
    await execute("update streaks set last=$2,count=1 where user_id=$1", uid, today)
    return 1
