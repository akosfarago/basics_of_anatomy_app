import math


def get_actor_center(actor):
    """
    Returns the 3D geometric center of a VTK actor based on its bounds.
    """
    mapper = actor.GetMapper()
    if not mapper or not mapper.GetInput():
        return [0.0, 0.0, 0.0]

    bounds = mapper.GetInput().GetBounds()
    center = [
        (bounds[0] + bounds[1]) / 2.0,
        (bounds[2] + bounds[3]) / 2.0,
        (bounds[4] + bounds[5]) / 2.0
    ]
    return center


def vector_sub(v1, v2):
    """Subtract v2 from v1: v1 - v2"""
    return [v1[i] - v2[i] for i in range(3)]


def vector_add(v1, v2):
    """Add two vectors: v1 + v2"""
    return [v1[i] + v2[i] for i in range(3)]


def vector_scale(v, scalar):
    """Scale vector by scalar: v * scalar"""
    return [v[i] * scalar for i in range(3)]


def vector_magnitude(v):
    """Length of a vector"""
    return math.sqrt(sum(v[i] * v[i] for i in range(3)))


def vector_normalize(v):
    """Normalize vector to unit length"""
    mag = vector_magnitude(v)
    return [v[i] / mag for i in range(3)] if mag != 0 else v


def lerp(v_start, v_end, t):
    """
    Linear interpolation between v_start and v_end:
    result = v_start + t * (v_end - v_start)
    """
    return [
        v_start[i] + t * (v_end[i] - v_start[i]) for i in range(3)
    ]
