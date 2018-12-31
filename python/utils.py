"""

"""


def join_lists(*args):
    """
    Will take any number of lists and join them.
    If any arg is None, it will not fail, it will skip it.
    Args:
        *args: any number of lists

    Returns:
        list

    """
    new_list = list()
    for arg in args:
        arg = make_list(arg)
        new_list += arg

    return new_list


def make_list(obj, type_=list):
    """
    Makes sure that obj is an iterable, if its not, it will be put into an
    iterable (default list)

    Args:
        obj: Python object
        type_:

    Returns:
        Iterable object with obj as its data.
    """
    if not obj:
        return type_()

    # does not function like the rest of fns in here, but works for dicts now.
    # before it exploded, since this is called make list,
    # felt like it was ok to have this make a list and loose the type_ functionality only for dicts
    if isinstance(obj, dict):
        return [obj]

    if isinstance(obj, type_):
        return obj

    if isinstance(obj, basestring):
        return type_((obj,))

    if hasattr(obj, '__iter__'):
        return type_(obj)

    return type_((obj,))
