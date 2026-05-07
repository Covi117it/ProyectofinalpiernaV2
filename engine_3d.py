import numpy as np
from numba import njit, prange

@njit(cache=True)
def apply_transformations(vertices, matrix):
    """
    Applies a 4x4 transformation matrix to a set of 3D vertices.
    """
    # Homogeneous coordinates
    n = vertices.shape[0]
    output = np.zeros_like(vertices)
    
    for i in prange(n):
        x = vertices[i, 0]
        y = vertices[i, 1]
        z = vertices[i, 2]
        
        nx = x * matrix[0, 0] + y * matrix[0, 1] + z * matrix[0, 2] + matrix[0, 3]
        ny = x * matrix[1, 0] + y * matrix[1, 1] + z * matrix[1, 2] + matrix[1, 3]
        nz = x * matrix[2, 0] + y * matrix[2, 1] + z * matrix[2, 2] + matrix[2, 3]
        nw = x * matrix[3, 0] + y * matrix[3, 1] + z * matrix[3, 2] + matrix[3, 3]
        
        output[i, 0] = nx / nw
        output[i, 1] = ny / nw
        output[i, 2] = nz / nw
        
    return output

@njit(cache=True)
def project_vertices(vertices, width, height, fov, viewer_distance):
    """
    Simple perspective projection.
    """
    n = vertices.shape[0]
    projected = np.zeros((n, 2), dtype=np.float32)
    aspect_ratio = height / width
    
    # Pre-calculate projection factor
    f = 1.0 / np.tan(np.radians(fov) / 2.0)
    
    for i in prange(n):
        z = vertices[i, 2] + viewer_distance
        # Clip Z to avoid division by zero or negative projection
        if z < 0.1: z = 0.1
        
        px = (vertices[i, 0] * f * aspect_ratio) / z
        py = (vertices[i, 1] * f) / z
        
        # Screen space conversion
        projected[i, 0] = (px + 1.0) * (width / 2.0)
        projected[i, 1] = (1.0 - py) * (height / 2.0)
        
    return projected

def get_rotation_matrix_x(angle_deg):
    a = np.radians(angle_deg)
    return np.array([
        [1, 0, 0, 0],
        [0, np.cos(a), -np.sin(a), 0],
        [0, np.sin(a), np.cos(a), 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)

def get_rotation_matrix_y(angle_deg):
    a = np.radians(angle_deg)
    return np.array([
        [np.cos(a), 0, np.sin(a), 0],
        [0, 1, 0, 0],
        [-np.sin(a), 0, np.cos(a), 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)

def get_rotation_matrix_z(angle_deg):
    a = np.radians(angle_deg)
    return np.array([
        [np.cos(a), -np.sin(a), 0, 0],
        [np.sin(a), np.cos(a), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)

def get_translation_matrix(dx, dy, dz):
    return np.array([
        [1, 0, 0, dx],
        [0, 1, 0, dy],
        [0, 0, 1, dz],
        [0, 0, 0, 1]
    ], dtype=np.float32)

class Engine3D:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.fov = 60
        self.viewer_distance = 5.0
        
    def render(self, vertices, rx, ry, rz, tx, ty, tz, return_triangles=False):
        # Combine transformations
        m = get_rotation_matrix_x(rx) @ get_rotation_matrix_y(ry) @ get_rotation_matrix_z(rz)
        m = get_translation_matrix(tx, ty, tz) @ m
        
        transformed = apply_transformations(vertices, m)
        projected = project_vertices(transformed, self.width, self.height, self.fov, self.viewer_distance)
        
        if return_triangles:
            # Group into triangles (3 vertices each)
            n_tri = len(projected) // 3
            return projected.reshape(n_tri, 3, 2)
            
        return projected

@njit(cache=True)
def apply_part_kinematics(vertices, knee_angle, extension, abduction, group_id, y_pivot_knee, y_pivot_hip):
    """
    group_id:
    0: Static (Hip/Base)
    1: Thigh (Abduction)
    2: Lower (Knee + Extension + Abduction)
    """
    n = vertices.shape[0]
    output = np.empty_like(vertices)
    
    rad_knee = np.radians(knee_angle)
    rad_abd = np.radians(abduction)
    
    cos_k, sin_k = np.cos(rad_knee), np.sin(rad_knee)
    cos_a, sin_a = np.cos(rad_abd), np.sin(rad_abd)
    
    for i in prange(n):
        x, y, z = vertices[i, 0], vertices[i, 1], vertices[i, 2]
        
        # Group 2: Rod/Foot -> Apply Extension AND Knee Rotation
        if group_id == 2:
            y = y - extension
            # Rotate around Knee Pivot (X axis)
            dy = y - y_pivot_knee
            new_y = y_pivot_knee + dy * cos_k - z * sin_k
            new_z = dy * sin_k + z * cos_k
            x, y, z = x, new_y, new_z
            
        # Group 1 and 2: Apply Abduction (rotate around Hip)
        if group_id >= 1:
            dy = y - y_pivot_hip
            new_x = x * cos_a - dy * sin_a
            new_y = y_pivot_hip + x * sin_a + dy * cos_a
            x, y, z = new_x, new_y, z
            
        output[i, 0] = x
        output[i, 1] = y
        output[i, 2] = z
        
    return output
