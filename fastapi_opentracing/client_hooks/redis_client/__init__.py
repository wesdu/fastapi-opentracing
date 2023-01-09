import aioredis


def install_patch():
    if "aioredis" not in globals():
        raise Exception("aioredis import fail")
    if aioredis.__version__.startswith("1"):
        from . import aioredis_low_level
        aioredis_low_level.install_patch()
    elif aioredis.__version__.startswith("2"):
        from . import aioredis_high_level
        aioredis_high_level.install_patch()
    else:
        raise Exception("unsupported version of aioredis")
