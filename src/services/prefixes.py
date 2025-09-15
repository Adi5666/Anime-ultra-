\
from ..core.db import fetchrow, execute
from ..config.settings import DEFAULT_PREFIX

async def get_prefix(gid: str) -> str:
    row = await fetchrow("select prefix from prefixes where server_id=$1", gid)
    return row["prefix"] if row and row["prefix"] else DEFAULT_PREFIX
