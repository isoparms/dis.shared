import collections
import timeit
import warnings
import os
from functools import wraps


def make_list(obj, type_=list):
    """

    :param obj: any python object. if its iterable, it will return it as is.
    :param type_: type of return object

    makes sure that obj is an iterable, if its not, it will be put into an
    iterable (default list)

    """
    
    if obj is None:
        return type_()
    
    # WIP: does not function like the rest of fns in here, but works for dicts now.
    # before it exploded, since this is called make_list,
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


def join_lists(*args):
    """
    This replaces the += operator for lists. It gracefully deals with adding False as a list ( [item] += False )
    :param args: any number of lists
    :return: a new list that contains all the elements of the other lists.

    """
    new_list = list()
    for arg in args:
        arg = make_list(arg)
        new_list += arg

    return new_list


def env_var_to_list(env_var, separator=";"):
    """
    Converts an environment variable like PATH, that has paths separated by a ";" into a list of paths
    :param : (str) name of environment variable. Such as PATH or PYTHONPATH
    :return: (list)
    """
    
    if env_var not in os.environ.keys():
        message = "environment variable does not exist: {}".format(env_var)
        raise Exception(message)
        
    long_word = os.getenv(env_var)
    word_list = list()
    if separator in long_word:
        word_list = long_word.split(separator)
    else:
        word_list = make_list(long_word)
    
    return word_list
    

def deep_compare(objA, objB, depth=0, max_depth=10000):
    # NOTE: leaf objects are still compared with equality,
    # objects that are not iterable will be compared by reference, not value
    if depth > max_depth:
        warnings.warn('Max depth of {} reached in deep_compare'.format(max_depth), RuntimeWarning)
        return objA == objB
    # is the object iterable? if not, just compare
    if not hasattr(objA, '__iter__') or not hasattr(objB, '__iter__'):
        return objA == objB
    # does our iterable object have matching lengths?
    if len(objA) != len(objB) or type(objA) != type(objB):
        return False

    if isinstance(objA, dict):
        for item in objA:
            if item not in objB:
                return False
            if not deep_compare(objA[item], objB[item], depth=depth + 1):
                return False
    else:
        i = 0
        for item in objA:
            if not deep_compare(item, objB[i], depth=depth + 1):
                return False
            i += 1
    return True


def get_sorted_by_most_common(data, alphabetize=False, remove_singles=False):
    """
    Will take the list you fed it and sort it by number of times each item appears in the list.
    
    example:
        
        data = get_sorted_by_most_common(
            ["Mouth","Corner","Up","Mouth","Up","Mouth","Up","Mouth","Up","Mouth","Corner","Up"]
        )
        
        data == ["Mouth", "Up", "Corner"]
    
    :param data: (list). a list of strings
    :param alphabetize: (bool) return the list sorted by number of occurrences AND alphabetically
    :param remove_singles: (bool) remove entries that only appear once in the list
    :return: (list) sorted by number of occurrences.
    """
    by_max = list()
    initial_data = data
    while data:

        cur_max = max(set(data), key=data.count)
        by_max.append(cur_max)

        cur_data = list()
        for d in data:
            if d != cur_max:
                cur_data.append(d)
        data = cur_data

    if remove_singles:
        repeating = [k for k, v in collections.Counter(initial_data).items() if v > 1]
        new_data = list()
        for entry in by_max:
            if entry in repeating:
                new_data.append(entry)
        by_max = new_data

    if alphabetize:
        return by_max

    test_data = list()
    used = list()
    for s, s_word in enumerate(by_max):
        for u, u_word in enumerate(initial_data):
            if s_word == u_word and s_word not in used:
                test_data.append([u, s_word])
                used.append(s_word)

    test_data = sorted(test_data)
    new_data = list()
    for t in test_data:
        new_data.append(t[1])

    return new_data


def dict_unicode_to_string(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(dict_unicode_to_string, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(dict_unicode_to_string, data))
    else:
        return data


def remove_duplicates(objects, sort=False):
    if isinstance(objects, list):
        if sort:
            return sorted(list(set(objects)))
        else:
            return list(set(objects))


def merge_dicts(dicts):
    """
    
    Given multiple dicts, merge them into a new dict as a shallow copy.
    Conflicts will overwrite
    
    when I figure out how unit testing in tech art works here it is
    bob = {}
    bob['name'] = "bob"
    bob['job'] = "test dummy"
    
    jim = {}
    jim['name'] = "jim"
    jim['shoes'] = 'hiking'
    
    jim_bob = putils.merge_dicts([bob,jim])
    creates:{'job': 'test dummy', 'name': 'jim', 'shoes': 'hiking'}
    
    :param dicts: any number of dictionary objects.
    :return: a merged dictionary object.
    
    """

    dicts = make_list(dicts)
    new_dict = {}
    for dict_ in dicts:
        new_dict.update(dict_)

    return new_dict


def get_object_from_path(path):
    """
    :param path:
        dot seperated path. Assumes last item is the object and first part is module
    
    path(str) -
    example:
        cls = get_object_from_path("a.module.somewhere.MyClass")
    
    you can create a path like this:
        class_path = "{0}.{1}".format(MyClass.__module__, MyClass.__name__)
    """

    module_path, _, obj_name = path.rpartition(".")
    module = __import__(module_path, globals(), locals(), [obj_name], -1)
    obj = getattr(module, obj_name, None)
    return obj


def time_it(func):
    """
    Helper decorator to time how long a function takes and prints the result
    :param fn: function to be timed
    """

    @wraps(func)
    def timed(*args, **kwargs):
        timeStart = timeit.default_timer()
        result = func(*args, **kwargs)
        timeEnd = timeit.default_timer()
        print('Timed func : %r' % (func.__name__))
        print('Timed result : {0:.20f} sec'.format(timeEnd - timeStart))
        return result

    return timed


def count_it(fn):
    """
    Helper decorator to count the times a specified function is called
    :param fn: function to be counted
    """

    @wraps(fn)
    def counter(*args, **kwargs):
        counter.calls += 1
        print '%s was called %i times' % (fn.__name__, counter.calls)
        return fn(*args, **kwargs)

    counter.calls = 0
    return counter


def are_items_in_list(items, full_list):
    """

    Will return true if any of the given items are in the given list

    :param items: (list) Items to check against a bigger list.
    :param full_list: (list)
    :return: (bool)

    """
    item_list = make_list(items)

    its = set(item_list)
    fts = set(full_list)

    if len(fts.intersection(its)):
        return True

    return False


def empty_list(number_of_items=0, default_item=None):
    """
    Convenience fn to make a list with a pre-determined number of items.
    Its more readable than:
        var = [None] * number_of_items
    
    :param number_of_items: (int)
        how many items in the list
    :param default_item:
        the list will come pre filled with that this in every item
        example:
            default_item = "foo"
            return = ["foo", "foo", "foo"...]
    :return:
        (list)
    """
    
    list_ = [default_item] * number_of_items
    return list_

#
# def get_item_index(target, object_list):
#     """
#     list.index() is pretty slow. This function speeds it up quite a bit.
#
#     :param target:
#         item in to find in the list:
#     :param object_list:
#         a list of items
#     :return:
#     """
#     for i in range(len(object_list)):
#         if object_list[i] == target:
#             yield i
