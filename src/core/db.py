\
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

async def bootstrap_schema():
    await execute("""\
    create table if not exists servers(
      id text primary key,
      name text,
      premium boolean default false,
      premium_until timestamp with time zone,
      disabled boolean default false,
      spawn_mode text default 'safe'
    );
    create table if not exists users(
      id text primary key,
      name text,
      premium boolean default false,
      premium_until timestamp with time zone,
      banned boolean default false,
      ban_reason text,
      suspend_reason text,
      suspended_until timestamp with time zone,
      power int default 0,
      claims int default 0
    );
    create table if not exists spawns(
      id bigserial primary key,
      server_id text not null,
      channel_id text not null,
      code text,
      template_name text not null,
      family text,
      safe_image text,
      authentic_image text,
      rarity text default 'UNCOMMON',
      created_at timestamp with time zone default now()
    );
    create table if not exists creatures(
      id bigserial primary key,
      owner_id text not null,
      server_id text not null,
      name text not null,
      family text,
      rarity text,
      shiny boolean default false,
      atk int default 10,
      def int default 10,
      spd int default 10,
      caught_at timestamp with time zone default now()
    );
    create table if not exists prefixes(
      server_id text primary key,
      prefix text not null
    );
    create table if not exists bot_roles(
      user_id text primary key,
      role_name text not null check (role_name in ('bot_admin','bot_moderator'))
    );
    """)
