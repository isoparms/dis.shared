import json as json_
import shared.python.file as pyfile


def json(path_or_file, obj=None, default=None, indent=4, sort_keys=True):
    """
    Convenient to serialize and deserialize.
    IF you pass a value to arg 'obj', it will be serialize to 'path_or_file'.
    If arg 'obj' is None, the 'path_or_file' will be deserialized and returned.
    
    Args:
        path_or_file:
            (str or file object)
            Path to the json file on disk
        obj:
            the object to serialize. If not None, the object will be written to
            disk. If it is None, the function will read whats on disk.
        default:
            value to return if file not found or if file is empty.
        indent:
            (int)
             Format spacing for json output
        sort_keys:
            (bool)
            Save with keys sorted.
            
    Returns:
        None or data - depending on weather obj is set or not

    """
    
    file_object = None
    path = ""
    if isinstance(path_or_file, file):
        file_object = path_or_file
    else:
        path = pyfile.expand(path_or_file)
    
    if not obj is None:
        
        if path:
            try:
                pyfile.mkdir(path)
            except:
                raise Exception("invalid path: \"{0}\"".format(path))
                
        if file_object:
            json_.dump(obj, file_object, indent=indent, sort_keys=sort_keys)
        else:
            with open(path, mode="w") as f:
                json_.dump(obj, f, indent=indent, sort_keys=sort_keys)
        
        return True
    
    elif pyfile.exists(path) or file_object:
        if file_object:
            # json fails if the file is empty
            try:
                data = json_.load(file_object)
            except ValueError:
                data = default
        else:
            with open(path, mode="r") as f:
                try:
                    data = json_.load(f)
                except ValueError:
                    data = default
        
        return data
    
    else:
        return default


def load(path_or_file, default=None, indent=4, sort_keys=True):
    """
    Convenient way to load a JSON file to a dict()

    Args:
        path_or_file:
            (str or file object)
            the path to the json file on disk
        default:
            the value or object to return if file not found or if file is empty
        indent:
            (int)
            for formatting json output
        sort_keys:
            (bool)
            save with keys sorted or unsorted.

    Returns:
        (dict)
        the contents of the file.

    """
    return json(path_or_file, obj=None, default=default, indent=indent, sort_keys=sort_keys)


def save(path_or_file, obj, default=None, indent=4, sort_keys=True):
    """

    Args:
        path_or_file:
            (str or file object)
            the path to the json file on disk
        obj:
            (list, dict)
            The object that will be written to disk.
        default:
            the value or object to return if file not found or if file is empty
        indent:
            (int)
            for formatting json output
        sort_keys:
            (bool)
            save with keys sorted or unsorted.

    Returns:
        (bool)
        If file was successfully written or not.

    """
    return json(path_or_file, obj=obj, default=default, indent=indent, sort_keys=sort_keys)
