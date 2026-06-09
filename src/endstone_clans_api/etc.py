# Parts of this was Rust code I wrote translated to Python through an LLM.
# https://github.com/niko-at-chalupa/endstone-elytra-core/blob/main/crates/elytra-core/src/id.rs

from re import I
import re
import xxhash

# In Python, we convert the 8-byte string directly into an integer.
HASH_SEED = int.from_bytes(b"clansapi\0", byteorder="big")

def compute_id(kebab_name: str) -> int:
    """
    Generates a plugin ID that derives from the kebab-case name of plugins.
    Returns an unsigned 64-bit integer.
    """
    # xxhash.xxh64 takes an integer seed and returns a 64-bit hash object
    hasher = xxhash.xxh64(seed=HASH_SEED)
    hasher.update(kebab_name.encode('utf-8'))
    return hasher.intdigest()

def remove_minecraft_formatting(formatted_stuff: str) -> str:
    return re.sub(r'§.', '', formatted_stuff)