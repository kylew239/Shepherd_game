import math
from typing import List

import numpy as np

X = 0
Y = 1


def dist(a, b=np.array([0, 0])) -> float:
    """
    Calculate the distance between two points.

    Args:
        a (np.ndarray): Point 1
        b (np.ndarray, optional): Point 2. Defaults to np.array([0, 0]).

    Returns:
        float: Distance between the two points
    """
    return np.linalg.norm(a-b)


def unit_vect(head, tail=np.array([0, 0])) -> np.ndarray:
    """
    Create a unit vector.

    Args:
        head (np.ndarray): Head of the vector
        tail (np.ndarray, optional): Tail of the vector. Defaults to np.array([0, 0]).

    Returns:
        np.ndarray: Unit Vector
    """
    if dist(head, tail) == 0:
        return np.array([0, 0])
    return (head-tail)/dist(head, tail)


def rand_unit() -> np.ndarray:
    """Return a random unit vector."""
    return unit_vect([np.random.rand()-.5, np.random.rand()-.5])


def on_segment(p: np.ndarray, q: np.ndarray, r: np.ndarray) -> bool:
    """
    Check if point q lies on line segment 'pr'.

    Args:
        p (np.ndarray): Point 1
        q (np.ndarray): Point 2
        r (np.ndarray): Point 3

    Returns:
        bool: True if the 3 points are collinear
    """
    return (np.all(q <= np.maximum(p, r)) and np.all(q >= np.minimum(p, r)))


def orientation(p: np.ndarray, q: np.ndarray, r: np.ndarray) -> int:
    """
    Find orientation of ordered triplet (p, q, r).

    0 -> p, q and r are collinear
    1 -> Clockwise
    2 -> Counterclockwise

    Args:
        p (np.ndarray): Point 1
        q (np.ndarray): Point 2
        r (np.ndarray): Point 3

    Returns:
        int: Representation of the orientation
    """
    val = (q[Y] - p[Y]) * (r[X] - q[X]) - (q[X] - p[X]) * (r[Y] - q[Y])
    if val == 0:
        return 0  # collinear
    return 1 if val > 0 else 2  # clockwise or counterclockwise


def line_intersects(start1: np.ndarray,
                    end1: np.ndarray,
                    start2: np.ndarray,
                    end2: np.ndarray) -> bool:
    """
    Check if two line segments intersect.

    Args:
        start1 (np.ndarray): Start of line segment 1
        end1 (np.ndarray): End of line segment 1
        start2 (np.ndarray): Start of line segment 2
        end2 (np.ndarray): End of line segment 2

    Returns:
        bool: True if the line segments intersect
    """
    o1 = orientation(start1, end1, start2)
    o2 = orientation(start1, end1, end2)
    o3 = orientation(start2, end2, start1)
    o4 = orientation(start2, end2, end1)

    if o1 != o2 and o3 != o4:
        return True

    return False


def circle_intersects(start: np.ndarray,
                      end: np.ndarray,
                      circle_center: np.ndarray,
                      radius: int) -> bool:
    """
    Check if a line segment intersects with a circle.

    Args:
        start (np.ndarray): Start of line segment
        end (np.ndarray): End of line segment
        circle_center (np.ndarray): Center of the circle
        radius (int): radius of the circle

    Returns:
        bool: True if the line segment intersects the circle
    """
    # Find the point on the line segment that is closest to the circle center
    segment = end - start
    mag = np.dot(segment, segment)

    if mag == 0:
        # check if line segment has 0 length
        close_point = start
    else:
        t = np.dot(circle_center - start, segment) / mag

        if t < 0:
            # Start of segment
            close_point = start
        elif t > 1:
            # End of segment
            close_point = end
        else:
            # Closest point on the segment
            close_point = start + t * segment

    # Compare the distance to the closest point on the segment vs the radius
    return np.sum((close_point - circle_center) ** 2) <= radius ** 2


def triangle(point: np.ndarray,
             direction: np.ndarray,
             size: float) -> List:
    """
    Generate a triangle using a direction for the center.

    Args:
        point (np.ndarray): Origin of the triangle
        direction (np.ndarray): Point of the triangle
        size (float, optional): Size of the triangle

    Returns:
        List: 3 points representing the triangle
    """
    angle = math.atan2(direction[Y] - point[Y],
                       direction[X] - point[X])

    head = point + unit_vect(direction, point) * size * 2
    base1 = np.array([
        point[X] + math.cos(angle + math.pi/4) * size,
        point[Y] + math.sin(angle + math.pi/4) * size
    ])
    base2 = np.array([
        point[X] + math.cos(angle - math.pi/4) * size,
        point[Y] + math.sin(angle - math.pi/4) * size
    ])

    return [head, base1, base2]
