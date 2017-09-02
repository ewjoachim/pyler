import subprocess
import sys
import time


def user_input(*args, **kwargs):
    return input(*args, **kwargs)


def default_open(something_to_open):
    """
    Open given file with default user program.
    From https://github.com/carlos-jenkins/nested/blob/
        c38bf1d17bdf52c8f4051e044069327532c0ef88/src/lib/nested/utils.py#L68
    """
    if sys.platform.startswith('linux'):
        subprocess.Popen(['xdg-open', something_to_open])

    elif sys.platform.startswith('darwin'):
        subprocess.Popen(['open', something_to_open])

    elif sys.platform.startswith('win'):
        subprocess.Popen(['start', something_to_open], shell=True)

    time.sleep(0.3)
