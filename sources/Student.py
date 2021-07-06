from dataclasses import dataclass
import time
from .AeriesScraper import Period
from typing import List

class Student:
    email: str
    password: str
    grades: List[Period]
    lastUpdated = time.time()

    def __init__(self, email: str, password: str, grades: List[Period], lastUpdated: float=time.time()) -> None:
        self.email = email
        self.password = password
        self.grades = grades
        self.lastUpdated = lastUpdated
    