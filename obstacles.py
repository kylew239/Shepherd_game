import dataclasses
from typing import List

@dataclasses.dataclass()
class Line:
    start: List[float]
    end: List[float]

@dataclasses.dataclass()
class Circle:
    center: List[float]
    radius: float

lines: List[Line] = [
    Line(start=[20, 20], end=[70, 40]),
    Line(start=[30, 120], end=[100, 120]),
]

circles: List[Circle] = [
    Circle(center=(60, 60), radius=10),
]