# 
# Below code inspired from https://github.com/podhmo/dictknife
# 
# podhmo/dictknife
# https://github.com/podhmo/dictknife/blob/master/dictknife/deepmerge.py
# 

import copy
from functools import partial
from typing import Any, Dict, List, Tuple, Union


def _extend(left, right, *, deduplicate=False):
    if isinstance(left, (list, tuple)):
        merged = None
        restore_tuple = False
        if isinstance(left, tuple):
            restore_tuple = True
            merged = list(left[:])
        else:
            merged = left[:]
        if isinstance(right, (list, tuple)):
            for val in right:
                if not (deduplicate and val in merged):
                    merged.append(val)
        else:
            if not (deduplicate and right in merged):
                merged.append(right)
        return tuple(merged) if restore_tuple else merged
    elif hasattr(left, 'get'):
        if hasattr(right, 'get'):
            merged = left.copy()
            for key in right.keys():
                if key in left:
                    merged[key] = _extend(merged[key], right[key], deduplicate=deduplicate)
                else:
                    merged[key] = right[key]
            return merged
        elif right is None:
            return left
        else:
            raise ValueError('cannot merge dict and non-dict: left=%s, right=%s', left, right)
    else:
        return right


def _replace(left, right):
    if hasattr(right, 'keys'):
        for key, val in right.items():
            if key in left:
                left[key] = _replace(left[key], val)
            else:
                left[key] = copy.deepcopy(val)
        return left
    elif isinstance(right, (list, tuple)):
        return right[:]
    else:
        return right


def mergedata(
    *data: Union[Dict[Any, Any], List[Any], Tuple[Any, ...]],
    override: bool = False
) -> Union[Dict[Any, Any], List[Any], Tuple[Any, ...]]:

    if len(data) == 0:
        return {}

    merge = partial(_extend, deduplicate=True)

    if override:
        merge = _replace

    left = data[0].__class__()

    for right in data:
        if not right:
            continue
        left = merge(left, right)
    return left
