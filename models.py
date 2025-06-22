from dataclasses import dataclass

@dataclass
class User:
    id: int
    username: str
    password: str
    email: str

@dataclass
class Transaction:
    id: int
    user_id: int
    type: str  # 'deposit' or 'withdraw'
    amount: float
    timestamp: str

