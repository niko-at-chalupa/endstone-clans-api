# This was Rust code I wrote translated to Python through an LLM.
# https://github.com/niko-at-chalupa/endstone-elytra-core/blob/main/crates/elytra-core/src/id.rs

import xxhash

# In Python, we convert the 8-byte string directly into an integer.
HASH_SEED = int.from_bytes(b"clansapi\0", byteorder="big")

def compute_plugin_id(kebab_name: str) -> int:
    """
    Generates a plugin ID that derives from the kebab-case name of plugins.
    Returns an unsigned 64-bit integer.
    """
    # xxhash.xxh64 takes an integer seed and returns a 64-bit hash object
    hasher = xxhash.xxh64(seed=HASH_SEED)
    hasher.update(kebab_name.encode('utf-8'))
    return hasher.intdigest()

def kebabify(name: str) -> str:
    """
    Converts a display name into a kebabbed name.
    """
    slug = []
    last_was_hyphen = False

    for c in name:
        if c.isalnum():
            # handles multi-character lowercase conversions (like German 'ß' -> 'ss')
            slug.append(c.lower())
            last_was_hyphen = False
        elif c.isspace() or c == '-' or c == '_':
            if slug and not last_was_hyphen:
                slug.append('-')
                last_was_hyphen = True

    # Join the characters together
    result = "".join(slug)
    
    # Strip trailing hyphen if it exists
    if result.endswith('-'):
        result = result[:-1]
        
    return result