\
import time
_dual_hint = {}

def set_dual_hint(user_id: str, seconds: int=600):
    _dual_hint[user_id] = time.time() + seconds

def has_dual_hint(user_id: str) -> bool:
    import time as _t
    return _dual_hint.get(user_id, 0) > _t.time()
