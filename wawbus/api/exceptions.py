from requests.exceptions import RequestException


class ZtmApiException(Exception):
    msg: str

    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(self.msg)


class ZtmHttpException(ZtmApiException):

    def __init__(self, error: RequestException):
        super().__init__(str(error))
