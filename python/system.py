import subprocess
import getpass
import socket


def get_windows_user():
    """
    Helper function to get the windows user name
    :return: (str)
    """
    return getpass.getuser()


def run_application_async(path):
    """
    Helper function to run Popen. Its more readable.
    :param path: Popen arg
    """
    subprocess.Popen(path)


def get_computer_name():
    """
    Helper function to get the local computer name
    :return:
        ( str )
        the name of the computer that ran this code.
    """
    return socket.gethostname()


def get_local_ip():
    """
    Helper function to get the local IP address of the computer.
    :return:
        ( str )
        IP address of the computer running this function.
    """
    return socket.gethostbyname(get_computer_name())
