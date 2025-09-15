import pathlib

def write(path, content):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

# --- Config settings ---
write("src/config/settings.py", r'''\
import os

OWNER_IDS = {os.environ.get("OWNER_ID","")}
OFFICIAL_SERVER_ID = os.environ.get("OFFICIAL_SERVER_ID","")
CAPITAL_SERVER_ID = os.environ.get("CAPITAL_SERVER_ID","")

DEFAULT_PREFIX = "!"
''')

# --- Logger ---
write("src/core/logger.py", r'''\
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("anime_ultra")
''')

# --- DB core (part 1) ---
write("src/core/db.py", r'''\
import os, asyncpg
from .logger import log

_pool = None

async def init_db():
    global _pool
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL missing")
    _pool = await asyncpg.create_pool(dsn=db_url, max_size=10)
    await bootstrap_schema()
    log.info("DB pool ready.")

async def fetch(query, *args):
    async with _pool.acquire() as con:
        return await con.fetch(query, *args)

async def fetchrow(query, *args):
    async with _pool.acquire() as con:
        return await con.fetchrow(query, *args)

async def execute(query, *args):
    async with _pool.acquire() as con:
        return await con.execute(query, *args)
''')

print("bootstrap_all Part 1 applied: settings.py, logger.py, db.py base written.")
