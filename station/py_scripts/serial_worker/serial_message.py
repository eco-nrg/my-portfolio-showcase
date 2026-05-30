from typing import List, Optional, Union


class SerialMessage:
    def __init__(
        self,
        message: Union[bytes, List[int]],
        destination: str,
        size: int,
        skip_bytes: Optional[int] = None,
    ):
        self.message = message
        self.destination = destination
        self.size = size
        self.skip_bytes = skip_bytes
