from dataclasses import dataclass
from .AeriesScraper import Period
from typing import List
@dataclass
class User:
    email: str
    password: str
    grades: List[Period]
