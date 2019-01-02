"""
This module exists to make os.path and shutil more readable.
Has lots of helper functions to deal with path normalization, directory structures, files on disk, etc.
"""
# python
import os
import shutil
import stat
import tempfile
import time
import contextlib
from filecmp import dircmp

# internal
import shared.python.utils as pyutils

# external
import lockfile

rmtree = shutil.rmtree
normalize = os.path.normpath
dirname = os.path.dirname


# """ ------------------------------------------------------------ """
# """ ------------------------------------------------------------ """
# """ --------------------------- PATH --------------------------- """
# """ ------------------------------------------------------------ """
# """ ------------------------------------------------------------ """

def expandnorm(path):
    return normalize(expand(path))


def join(*args):
    """
    similar to os.path.join but can take lists and it normalizes the results
    """
    flatten_list = []
    for a in args:
        if isinstance(a, (list, tuple)):
            flatten_list.extend(a)
        else:
            flatten_list.append(normalize(a))
    
    modified = flatten_list[:1]
    for a in flatten_list[1:]:
        modified.append(a.strip("\\").strip("/"))
    
    return normalize(os.path.join(*modified))


def humanize(path, max_char=40, include_drive=False):
    split = splitall(path)
    split.reverse()
    file_name = split.pop(0)
    pieces = [file_name]
    max_char -= len(file_name)
    
    for p in split:
        max_char -= len(p)
        if max_char < 0:
            if include_drive:
                pieces.append(split[-1] + r"...")
            else:
                pieces.append("...")
            break
        
        pieces.append(p)
    
    pieces.reverse()
    return os.path.join(*pieces)


def expand(file_path):
    return os.path.expandvars(file_path)


def shell_normalize(file_path, ignore_spaces=False):
    prepend = ""
    if file_path.startswith(r"\\"):
        file_path = file_path[2:]
        prepend = r"\\"
    
    if ignore_spaces:
        file_path = file_path.replace("\\", "/").replace("//", "/")
    else:
        file_path = file_path.replace("\\", "/").replace(" ", "\\ ").replace("//", "/")
    
    file_path = prepend + file_path
    
    return file_path


def name(file_path, include_ext=False):
    """
    gets file name without path or extension
    
    Args:
        file_path:
            (str) file path
        include_ext:
            (bool) have or not have the extension as part of the result

    Returns:
        (str) the name of the file

    """
    
    file_name = os.path.basename(os.path.splitext(file_path)[0])
    if include_ext:
        return file_name + ext(file_path)
    
    return file_name


def change_ext(file_path, new_ext):
    if not new_ext.startswith("."):
        new_ext = "." + new_ext
    
    return os.path.splitext(file_path)[0] + new_ext


def ext(file_path):
    """ returns the extension (with a '.')"""
    return os.path.splitext(file_path)[1]


def remove_ext(file_path):
    split = splitall(file_path)
    if split[-1].find(".") > -1:
        return file_path.rpartition(".")[0]
    
    return file_path


def splitall(path):
    all_parts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            all_parts.insert(0, parts[0])
            break
        elif parts[1] == path:  # sentinel for relative paths
            all_parts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            all_parts.insert(0, parts[1])
    return all_parts


def get_path(file_path):
    '''returns the path from a given file_path, this works even if the file is not currently on disk'''
    
    if is_file(file_path):
        return os.path.dirname(file_path)
    
    else:
        
        try:
            f_name = name(file_path, include_ext=True)
            return_path = file_path.replace(f_name, "")
            return return_path
        
        except OSError:
            raise Exception(file_path, "given file path is not a valid path location.")


def upper_letter_drive(file_path):
    """ makes the letter drive upper case"""
    
    if file_path[1] == ":":
        return file_path[0].upper() + file_path[1:]
    
    return file_path


def get_disk_size(start_path='.'):
    """
    returns the total size on disk of a given folder
    """
    folder_size = 0
    for dir_path, dir_names, file_names in os.walk(start_path):
        for f in file_names:
            fp = os.path.join(dir_path, f)
            folder_size += os.path.getsize(fp)
    return folder_size


def get_tree_differences(path1, path2):
    dcmp = dircmp(path1, path2)
    diffs = _gather_differences_in_paths(dcmp)
    return diffs


def _gather_differences_in_paths(dcmp):
    for name in dcmp.diff_files:
        return name
    for sub_dcmp in dcmp.subdirs.values():
        _gather_differences_in_paths(sub_dcmp)


def are_dir_trees_equal(dir1, dir2, check_file_contents=False):
    """
    Compare two directories recursively. Files in each directory are
    assumed to be equal if their names (ONLY) are equal.
    """
    
    # compare the file names and the contents of the files
    if check_file_contents:
        if not get_tree_differences(dir1, dir2):
            return True
        return False
    
    # compare only that the files are there
    src_files = []
    for root, dirnames, filenames in os.walk(dir1):
        for filename in filenames:
            if ".reaperdata" not in filename:
                src_files.append(os.path.join(root, filename))
    
    dst_files = []
    for root, dirnames, filenames in os.walk(dir2):
        for filename in filenames:
            if ".reaperdata" not in filename:
                dst_files.append(os.path.join(root, filename))
    
    src_files = sorted(src_files)
    dst_files = sorted(dst_files)
    
    if sorted(src_files) == sorted(dst_files):
        return True
    return False


# """ ------------------------------------------------------------ """
# """ ------------------------------------------------------------ """
# """ --------------------------- FILE --------------------------- """
# """ ------------------------------------------------------------ """
# """ ------------------------------------------------------------ """


def remove(path, force=False):
    path = expand(path)
    if force:
        os.chmod(path, stat.S_IWRITE)
    
    os.remove(path)


def exists(path):
    itexists = os.path.exists(expand(path))
    if itexists:
        return True
    
    itexists = os.path.isfile(path)
    if itexists:
        return True
    
    return False


def delete(path, force=False):
    path = pyutils.make_list(path)
    for p in path:
        if is_file(p) or is_dir(p):
            if force:
                os.chmod(p, stat.S_IWRITE)
                os.chmod(p, 0777)
                os.unlink(p)
            else:
                os.remove(expand(p))


def copy(src, dst):
    """
    If the source is a folder, it will copy the contentes of the folder.
    Otherwise, Windows will error out due to permissions problems.
    """
    dst = expand(dst)
    mkdir(dirname(dst))
    
    if is_dir(src):
        src = list_files(src)
    else:
        src = [src]
    
    for s in src:
        shutil.copyfile(expand(s), dst)


def move(src, dst):
    dst = expand(dst)
    mkdir(dirname(dst))
    shutil.move(expand(src), dst)
    return dst


def rename(src, dst):
    dst = expand(dst)
    mkdir(dirname(dst))
    shutil.copyfile(expand(src), dst)
    delete(src)


def is_file(path):
    if not path:
        return False
    try:
        isfile = os.path.isfile(expand(path))
        return isfile
    except:
        return False


def is_dir(path):
    if not path:
        return False
    return os.path.isdir(expand(path))


def is_abs(path):
    if not path:
        return False
    return os.path.isabs(path)


def walk(dir_, ext=None):
    expanded_dir = expand(dir_)
    found = []
    for root, dirs, files in os.walk(expanded_dir):
        for file in files:
            if ext:
                if file.endswith(ext):
                    found.append(os.path.join(root, file))
            else:
                found.append(os.path.join(root, file))
    
    return found


def initialize_path(path):
    """
    Makes the path specified if it doesn't exist
    """
    
    if path and not exists(path):
        mkdir(path)
    
    return path


def modified_recently(fullpath, buffer_=60):
    """
    return True if the file has been modified in the last "buffer" seconds
    """
    stamp_time = os.path.getmtime(fullpath)
    epoch_time = time.time()
    elapsed = epoch_time - stamp_time
    if elapsed > buffer_:
        return False
    return True


def get_time(fullpath, type_="modified"):
    if type_ == "creation":
        return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(os.path.getctime(fullpath)))
    
    elif type_ == "access":
        return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(os.path.getatime(fullpath)))
    
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(os.path.getmtime(fullpath)))


def list_folders(dir_, fullpath=True, recursive=False):
    dir_ = expand(dir_)
    f = []
    for (dirpath, dirnames, filenames) in os.walk(dir_):
        f.extend([os.path.join(dirpath, x) for x in dirnames])
        if not recursive:
            break
    
    if not fullpath:
        for i, entry in enumerate(f):
            f[i] = entry.split("/")[-1]
    
    return f


def list_files(dir_, extension=None, recursive=False):
    """
    will return a list of files in a folder.
    By default its NOT recursive and will only return the file contents of the base dir_
    
    extension can be a list (example: ["ma","mb"])
    return example: ["M:\\shared_metadata\\pickertest.ma", "M:\\shared_metadata\\pickertest2.mb"]
    
    """
    
    files = list()
    
    paths = pyutils.make_list(dir_)
    for path in paths:
        path = expand(path)
    
        for (dirpath, dirnames, filenames) in os.walk(path):
            files.extend([os.path.join(dirpath, x) for x in filenames])
            if not recursive:
                break
        
        if extension:
            
            filtered = list()
            extenstions = pyutils.make_list(extension)
            
            for e in extenstions:
                e = "." + e.replace(".", "")
            
            for i, file_name in enumerate(files):
                add = False
                for e in extenstions:
                    if file_name.endswith(e):
                        add = True
                        break
                if add:
                    filtered.append(file_name)
            
            files = filtered
    
    files = pyutils.remove_duplicates(files)
    
    return files


def is_writable(path):
    real_path = expand(path)
    if exists(real_path):
        return os.access(real_path, os.W_OK)
    else:
        raise RuntimeError("'{0}' does not exist".format(real_path))


def is_readonly(path):
    return not is_writable(path)


def mkdir(dirnames):
    for dirname in pyutils.make_list(dirnames):
        dirname = os.path.expandvars(dirname)
        if not os.path.exists(dirname):
            os.makedirs(dirname)


def temp_file_path(ext="tmp", name="temp", folder=None, dir_=None):
    """
    Returns a path to a temporary file that you can use for whatever.
    the temp file defaults to %TEMP% directiory.
    
    ext(str) - the extension of the temp file
    name(str) - the base name of the file
    folder(str) - a subfolder to put the temp file in
    dir_(str) - if this is set, the temp file goes here rather than %TEMP%
    """
    base_dir = os.environ['TEMP']
    if dir_:
        base_dir = expand(dir_)
    
    if not folder:
        temp_dir = os.path.join(base_dir)
    else:
        temp_dir = os.path.join(base_dir, folder)
    
    mkdir(temp_dir)
    fid, path = tempfile.mkstemp(suffix=ext, prefix=(name + '_'), dir=temp_dir)
    os.close(fid)
    return path


def is_file_type(file, extension=["psd", "tga"]):
    """
    Returns True if the file has a given extension.
    
    Args:
        file (str): File name or full path.
        extension (list, optional):
            example: [ "PSD", "MB", "MAX", "TGA", "BMP", "GIF", "JPEG", "MNG", "PBM", "PGM", "PNG", "PPM", "XBM", "XPM" ]
    
    
    Returns:
        Bool
    """
    for ext in extension:
        if file.lower().endswith(ext.lower()):
            return True
    return False


def nuke_dir(dir):
    """
    Deletes entire folder.
    Will work even if files or folders are write protected.
    """
    
    if dir[-1] == os.sep: dir = dir[:-1]
    files = os.listdir(dir)
    
    for file in files:
        
        if file == '.' or file == '..': continue
        path = dir + os.sep + file
        
        if os.path.isdir(path):
            nuke_dir(path)
        else:
            os.chmod(path, stat.S_IWRITE)
            os.chmod(path, 0777)
            os.unlink(path)
    
    os.rmdir(dir)


LockTimeout = lockfile.LockTimeout


@contextlib.contextmanager
def open_exclusive(file_path, mode, timeout=10):
    """
    opens a file and locks it so other processes can't open it.
    WARNING, the other processes must also use 'open_exclusive' for exclusivity to work
    """
    
    lock = lockfile.LockFile(file_path)
    # Try to acquire the lock a few times if there is a LockFailed Error.
    # LockFailed error is raised when the lockfile is unable to be created, which
    # can happen frequently over network drives.
    for i in range(5):
        try:
            lock.acquire(timeout=timeout)
        except lockfile.LockFailed:
            time.sleep(.5)
    
    try:
        f = open(file_path, mode=mode)
        yield f
    finally:
        f.close()
        lock.release()


@contextlib.contextmanager
def locked(file_path, timeout=10):
    """
    opens a file and locks it so other processes can't open it.
    WARNING, the other processes must also use 'open_exclusive' for exclusivity to work
    """
    
    lock = lockfile.LockFile(file_path)
    # Try to acquire the lock a few times if there is a LockFailed Error.
    # LockFailed error is raised when the lockfile is unable to be created, which
    # can happen frequently over network drives.
    for i in range(5):
        try:
            lock.acquire(timeout=timeout)
        except lockfile.LockFailed:
            time.sleep(.5)
    
    try:
        yield
    finally:
        lock.release()


def break_lock(file_path):
    """
    Remove a lock.  Useful when using "open_exclusive" and the process fails to clean up a lock
    """
    lock = lockfile.LockFile(file_path)
    lock.break_lock()
