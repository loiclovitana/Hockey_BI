from threading import Thread
from os import getenv

from hmtracker.constants import HM_DATABASE_URL_ENV_NAME, HM_USER_ENV_NAME, HM_PASSWORD_ENV_NAME
import hmtracker.loader.main as loader

_current_operation:Thread = None

class ServerBusyException(Exception):
    def __init__(self, message):            
        
        super().__init__(message)


def is_running_operation() -> bool:
    global _current_operation
    return _current_operation is not None and _current_operation.is_alive()


def check_operation():
    global _current_operation
    if is_running_operation():
        raise ServerBusyException(f"Server is currently busy with operation: {_current_operation.getName()}")
    del _current_operation
    _current_operation = None


def get_current_operation()->str:
    global _current_operation
    if not is_running_operation():
        return None
    return _current_operation.getName()


def _Operation(name : str):
    def decorator(method):
        def wrapper():
            global _current_operation
            check_operation()
            thread = Thread(target=method, name=name)
            _current_operation = thread
            thread.start()

        return wrapper
    return decorator
    
@_Operation("Load HM stats")
def start_loading():
    database_url = getenv(HM_DATABASE_URL_ENV_NAME)
    hm_user = getenv(HM_USER_ENV_NAME)
    hm_password = getenv(HM_PASSWORD_ENV_NAME)

    loader.import_playerstats_from_ajax(database_url,hm_user,hm_password)

