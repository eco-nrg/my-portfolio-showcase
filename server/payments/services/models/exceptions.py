class PaymentError(Exception):
    def __init__(self, msg) -> None:
        super().__init__()
        self.msg = msg


class PaymentWebhookError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__()
        self.msg = msg
