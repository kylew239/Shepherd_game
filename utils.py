import numpy as np

X = 0
Y = 1

def dist(a, b=np.array([0, 0])):
    """
    Calculate the distance between two points.

    Args:
        a (List): Point 1
        b (List, optional): Point 2. Defaults to np.array([0, 0]).

    Returns:
        float: Distance between the two points
    """
    return np.linalg.norm(a-b)


def unit_vect(head, tail=np.array([0, 0])):
    """
    Create a unit vector.

    Args:
        head (List): Head of the vector
        tail (List, optional): Tail of the vector. Defaults to np.array([0, 0]).

    Returns:
        List: Unit Vector
    """
    if dist(head, tail) == 0:
        return np.array([0, 0])
    return (head-tail)/dist(head, tail)


def rand_unit():
    """Return a random unit vector."""
    return unit_vect([np.random.rand()-.5, np.random.rand()-.5])


def on_segment(p, q, r):
    """Check if point q lies on line segment 'pr'."""
    return (np.all(q <= np.maximum(p, r)) and np.all(q >= np.minimum(p, r)))


def orientation(p, q, r):
    """
    Find orientation of ordered triplet (p, q, r).

    0 -> p, q and r are collinear
    1 -> Clockwise
    2 -> Counterclockwise
    """
    val = (q[Y] - p[Y]) * (r[X] - q[X]) - (q[X] - p[X]) * (r[Y] - q[Y])
    if val == 0:
        return 0  # collinear
    return 1 if val > 0 else 2  # clockwise or counterclockwise


def line_intersects(start1: np.ndarray,
                    end1: np.ndarray,
                    start2: np.ndarray,
                    end2: np.ndarray):
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


def circle_intersects(start, end, circle_center, radius):
    """Check if a line segment intersects with a circle."""
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
            close_point =  start + t * segment  

    # Compare the distance to the closest point on the segment vs the radius
    return np.sum((close_point - circle_center) ** 2) <= radius ** 2
