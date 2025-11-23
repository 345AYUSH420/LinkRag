import re
import hashlib

def url_to_index_name(url: str) -> str:
    url = re.sub(r'^https?://', '', url)

    name = re.sub(r'[^a-zA-Z0-9-]', '-', url)
    name = name.lower()
    name = re.sub(r'-+', '-', name)
    if not name[0].isalpha():
        name = "idx-" + name
    if len(name) > 45:
        hash_part = hashlib.md5(url.encode()).hexdigest()[:10]
        name = name[:30] + "-" + hash_part

    return name