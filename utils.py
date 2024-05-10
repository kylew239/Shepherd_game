import numpy as np



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