

class VkError(Exception):
    def __init__(self, error_code: int, error_message: str, request_params: list = None):
        self.code = error_code
        self.message = error_message
        self.request_params = request_params
