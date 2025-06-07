from typing import Dict, Any, Set


def find_map_key_intersect(map1: Dict[str, Any], map2: Dict[str, Any]) -> Set[str]:
    if not map1 or not map2:
        return set()
    map1_keys = set(map1.keys())
    map2_keys = set(map2.keys())
    return set.intersection(map1_keys, map2_keys)
