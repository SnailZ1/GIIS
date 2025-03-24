import numpy as np

def translation_matrix(dx, dy, dz):
    """Создает матрицу перемещения"""
    return np.array([
        [1, 0, 0, dx],
        [0, 1, 0, dy],
        [0, 0, 1, dz],
        [0, 0, 0,  1]
    ])

def scale_matrix(sx, sy, sz):
    """Создает матрицу масштабирования"""
    return np.array([
        [sx, 0,  0, 0],
        [0, sy,  0, 0],
        [0, 0,  sz, 0],
        [0, 0,  0,  1]
    ])

def rotation_matrix_x(angle):
    """Создает матрицу поворота вокруг оси X"""
    c, s = np.cos(angle), np.sin(angle)
    return np.array([
        [1,  0,  0, 0],
        [0,  c, -s, 0],
        [0,  s,  c, 0],
        [0,  0,  0, 1]
    ])

def rotation_matrix_y(angle):
    """Создает матрицу поворота вокруг оси Y"""
    c, s = np.cos(angle), np.sin(angle)
    return np.array([
        [ c, 0,  s, 0],
        [ 0, 1,  0, 0],
        [-s, 0,  c, 0],
        [ 0, 0,  0, 1]
    ])

def rotation_matrix_z(angle):
    """Создает матрицу поворота вокруг оси Z"""
    c, s = np.cos(angle), np.sin(angle)
    return np.array([
        [c, -s, 0, 0],
        [s,  c, 0, 0],
        [0,  0, 1, 0],
        [0,  0, 0, 1]
    ])

def perspective_matrix(d):
    """Создает матрицу перспективы"""
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 1/d],
        [0, 0, 0, 1]
    ])

def apply_transformation(points, matrix):
    """Применяет матрицу к набору точек"""
    return np.dot(points, matrix.T)

def mirror_x():
    """Отражение относительно плоскости YZ (меняет знак X)"""
    return np.array([
        [-1, 0,  0, 0],
        [ 0, 1,  0, 0],
        [ 0, 0,  1, 0],
        [ 0, 0,  0, 1]
    ])

def mirror_y():
    """Отражение относительно плоскости XZ (меняет знак Y)"""
    return np.array([
        [ 1,  0, 0, 0],
        [ 0, -1, 0, 0],
        [ 0,  0, 1, 0],
        [ 0,  0, 0, 1]
    ])

def mirror_z():
    """Отражение относительно плоскости XY (меняет знак Z)"""
    return np.array([
        [ 1, 0,  0, 0],
        [ 0, 1,  0, 0],
        [ 0, 0, -1, 0],
        [ 0, 0,  0, 1]
    ])