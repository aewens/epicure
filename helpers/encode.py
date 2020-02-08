from helpers.general import eprint
from json import dump, dumps, loads

# JSON encoder, converts a python object to a string
def jots(data, readable=False, dest=None):
    kwargs = dict()

    # If readable is set, it pretty prints the JSON to be more human-readable
    if readable:
        # kwargs["sort_keys"] = True
        kwargs["indent"] = 4 
        kwargs["separators"] = (",", ":")

    try:
        if dest:
            return dump(data, dest, ensure_ascii=False, **kwargs)

        return dumps(data, ensure_ascii=False, **kwargs)

    except ValueError as e:
        return None

# JSON decoder, converts a string to a python object
def jsto(data):
    try:
        return loads(data)

    except ValueError as e:
        eprint(e)
        return None
