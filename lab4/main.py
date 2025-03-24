import pygame
import tkinter as tk
from tkinter import ttk
from transformations import *

# Настройки окна
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Камера
distance = 5  # Расстояние до проекции

# Доступные файлы
OBJECT_FILES = {
    "Куб": "cube.txt",
    "Пирамида": "pyramid.txt",
    "Тетраэдр": "tetrahedron.txt",
    "Призма": "prism.txt"
}

# Ребра для разных фигур
EDGES_MAP = {
    "cube.txt": [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)],
    "pyramid.txt": [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 3), (3, 4), (4, 1)],
    "tetrahedron.txt": [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)],
    "prism.txt": [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
}


def load_object(filename):
    """Загружает координаты 3D объекта из файла"""
    points = []
    with open(filename, 'r') as f:
        for line in f:
            x, y, z = map(float, line.split())
            points.append([x, y, z, 1])  # Однородные координаты
    return np.array(points)


def project(points):
    """Проецирует 3D точки на 2D"""
    projected = apply_transformation(points, perspective_matrix(distance))
    projected[:, :2] /= projected[:, 3].reshape(-1, 1)  # Деление на w
    return projected[:, :2]  # Возвращаем только x, y


def draw_edges(screen, projected, edges):
    """Рисует ребра объекта"""
    for edge in edges:
        p1 = projected[edge[0]]
        p2 = projected[edge[1]]
        pygame.draw.line(screen, WHITE, (p1[0] + WIDTH // 2, -p1[1] + HEIGHT // 2),
                         (p2[0] + WIDTH // 2, -p2[1] + HEIGHT // 2), 2)


def choose_object():
    """Создает графический интерфейс для выбора фигуры"""
    root = tk.Tk()
    root.title("Выбор 3D-фигуры")
    root.geometry("300x150")

    selected_figure = tk.StringVar(value="Куб")

    label = tk.Label(root, text="Выберите 3D-фигуру:", font=("Arial", 12))
    label.pack(pady=10)

    combo = ttk.Combobox(root, values=list(OBJECT_FILES.keys()), textvariable=selected_figure, font=("Arial", 12))
    combo.pack()

    def on_select():
        root.selected_file = OBJECT_FILES[selected_figure.get()]
        root.destroy()

    button = tk.Button(root, text="Выбрать", command=on_select, font=("Arial", 12))
    button.pack(pady=10)

    root.mainloop()
    return root.selected_file


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Выбор фигуры через GUI
    obj_file = choose_object()
    points = load_object(obj_file)
    edges = EDGES_MAP[obj_file]

    transform = np.eye(4)  # Начальная матрица преобразований
    mirror_delay = 300
    last_mirror_time = pygame.time.get_ticks()

    running = True
    while running:
        screen.fill(BLACK)

        # Применяем трансформацию
        transformed_points = apply_transformation(points, transform)
        projected_points = project(transformed_points)

        # Рисуем объект
        draw_edges(screen, projected_points, edges)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

        if keys[pygame.K_LEFT]:  # Поворот вокруг Y
            transform = transform @ rotation_matrix_y(0.05)
        if keys[pygame.K_RIGHT]:
            transform = transform @ rotation_matrix_y(-0.05)
        if keys[pygame.K_UP]:  # Поворот вокруг X
            transform = transform @ rotation_matrix_x(0.05)
        if keys[pygame.K_DOWN]:
            transform = transform @ rotation_matrix_x(-0.05)
        if keys[pygame.K_w]:  # Перемещение вперед
            transform = transform @ translation_matrix(0, 0, 0.1)
        if keys[pygame.K_s]:  # Назад
            transform = transform @ translation_matrix(0, 0, -0.1)
        if keys[pygame.K_a]:  # Влево
            transform = transform @ translation_matrix(-0.1, 0, 0)
        if keys[pygame.K_d]:  # Вправо
            transform = transform @ translation_matrix(0.1, 0, 0)
        if keys[pygame.K_q]:  # Увеличение
            transform = transform @ scale_matrix(1.05, 1.05, 1.05)
        if keys[pygame.K_e]:  # Уменьшение
            transform = transform @ scale_matrix(0.95, 0.95, 0.95)

        # Отражение с задержкой
        if keys[pygame.K_x] and current_time - last_mirror_time > mirror_delay:
            transform = transform @ mirror_x()
            last_mirror_time = current_time

        if keys[pygame.K_y] and current_time - last_mirror_time > mirror_delay:
            transform = transform @ mirror_y()
            last_mirror_time = current_time

        if keys[pygame.K_z] and current_time - last_mirror_time > mirror_delay:
            transform = transform @ mirror_z()
            last_mirror_time = current_time

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
