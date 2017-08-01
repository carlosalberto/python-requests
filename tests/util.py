from mock import MagicMock

import requests

class PatchedSessionSend(MagicMock):
    def __init__(self, *args, **kwargs):
        super(PatchedSessionSend, self).__init__(*args, **kwargs)
        self.exception = None
        self.__name__ = 'send' # Work properly with @wraps

    def __call__(self, *args, **kwargs):
        if self.exception is not None:
            raise self.exception

        res = requests.Response()
        res.status_code = 200
        res.reason = 'OK'

        return res
