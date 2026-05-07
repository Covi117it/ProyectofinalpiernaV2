import struct
import numpy as np

def load_stl(file_path):
    """
    Loads a binary STL file and returns a NumPy array of vertices.
    Each face has 3 vertices, so the shape is (N, 3, 3).
    We flatten this to (N*3, 3) for the engine.
    """
    try:
        with open(file_path, 'rb') as f:
            f.seek(80)
            num_triangles = struct.unpack('<I', f.read(4))[0]
            vertices = np.zeros((num_triangles * 3, 3), dtype=np.float32)
            
            for i in range(num_triangles):
                f.seek(12, 1) # Normal
                v_data = f.read(36)
                verts = struct.unpack('<9f', v_data)
                vertices[i*3 : i*3+3] = np.array(verts).reshape(3, 3)
                f.seek(2, 1) # Attribute
                
        return vertices
    except Exception as e:
        print(f"Error loading STL {file_path}: {e}")
        return None

def load_assembly(directory):
    """
    Loads all .stl files in a directory and returns a dictionary
    mapping filename to vertex array.
    """
    import os
    parts = {}
    for filename in os.listdir(directory):
        if filename.lower().endswith('.stl'):
            path = os.path.join(directory, filename)
            print(f"Loading part: {filename}...")
            verts = load_stl(path)
            if verts is not None:
                parts[filename] = verts
    return parts

def get_bounding_box(vertices):
    if len(vertices) == 0:
        return np.zeros(3), np.zeros(3)
    min_coords = vertices.min(axis=0)
    max_coords = vertices.max(axis=0)
    return min_coords, max_coords
