from typing import Optional, Dict


class RRHFOEM04Result:
    def __init__(self, success: bool, message: str, data: Optional[Dict] = None):
        self.success = success
        self.message = message
        self.data = data
    
    def __str__(self) -> str:
        return f"RRHFOEM04Result(success={self.success}, message='{self.message}', data={self.data})"