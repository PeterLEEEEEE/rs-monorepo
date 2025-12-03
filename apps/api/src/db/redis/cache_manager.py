
from fastapi_cache import FastAPICache

def key_builder(func, *args, **kwargs):
    """Generate a cache key based on the function name and its arguments."""
    user = kwargs.get('user')
    prefix = FastAPICache.get_prefix()
    return f"{prefix}:{func.__module__}:{func.__name__}"
    # return f"{func.__name__}::{user['email']}"

# class CacheManager:
    
#     def __init__(self, key_builder):
        