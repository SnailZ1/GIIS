import tkinter as tk
from tkinter import ttk
import numpy as np
from tkinter import messagebox


class PolygonEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Графический редактор полигонов")
        self.root.geometry("800x600")

        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.pack(side=tk.TOP, fill=tk.X)

        self.polygon = []
        self.convex_hull = []
        self.line_start = None
        self.selected_algorithm = tk.StringVar(value="ЦДА")

        self.add_buttons()

        # События мыши
        self.canvas.bind("<Button-1>", self.add_point)  # ЛКМ - добавление вершины
        self.canvas.bind("<Button-3>", self.check_point_inside)  # ПКМ - проверка принадлежности

    def add_buttons(self):
        """Создание кнопок интерфейса"""
        btn_graham = tk.Button(self.buttons_frame, text="Метод Грэхема", command=self.run_graham)
        btn_graham.pack(side=tk.LEFT)

        btn_jarvis = tk.Button(self.buttons_frame, text="Метод Джарвиса", command=self.run_jarvis)
        btn_jarvis.pack(side=tk.LEFT)

        btn_clear = tk.Button(self.buttons_frame, text="Очистить", command=self.clear_canvas)
        btn_clear.pack(side=tk.LEFT)

        btn_check_convex = tk.Button(self.buttons_frame, text="Проверить выпуклость", command=self.check_convex)
        btn_check_convex.pack(side=tk.LEFT)

        btn_draw_line = tk.Button(self.buttons_frame, text="Рисовать линию с пересечениями", command=self.find_intersection)
        btn_draw_line.pack(side=tk.LEFT)

        # Выбор алгоритма рисования
        ttk.Label(self.buttons_frame, text="Алгоритм:").pack(side=tk.LEFT, padx=5)
        algo_menu = ttk.Combobox(self.buttons_frame, textvariable=self.selected_algorithm,
                                 values=["ЦДА", "Брезенхем", "Ву"], state="readonly", width=10)
        algo_menu.pack(side=tk.LEFT)

    def add_point(self, event):
        """Добавление точки в полигон"""
        self.polygon.append((event.x, event.y))
        self.canvas.create_oval(event.x - 2, event.y - 2, event.x + 2, event.y + 2, fill="black")
        if len(self.polygon) > 1:
            self.canvas.create_line(self.polygon[-2], self.polygon[-1], fill="black")

    def check_point_inside(self, event):
        """Проверка принадлежности точки полигону"""
        if not self.polygon:
            return

        point = (event.x, event.y)
        if self.point_in_polygon(point, self.polygon):
            color = "green"
        else:
            color = "red"

        self.canvas.create_oval(event.x - 3, event.y - 3, event.x + 3, event.y + 3, fill=color)

    def run_graham(self):
        """Построение выпуклой оболочки методом Грэхема"""
        if len(self.polygon) < 3:
            return

        self.convex_hull = self.graham_scan(self.polygon)
        self.draw_hull(color="blue")

    def run_jarvis(self):
        """Построение выпуклой оболочки методом Джарвиса"""
        if len(self.polygon) < 3:
            return

        self.convex_hull = self.jarvis_march(self.polygon)
        self.draw_hull(color="purple")

    def draw_hull(self, color):
        """Отрисовка выпуклой оболочки"""
        if len(self.convex_hull) < 2:
            return

        self.canvas.create_line(self.convex_hull, fill=color, width=2)
        self.canvas.create_line(self.convex_hull[-1], self.convex_hull[0], fill=color, width=2)

    def clear_canvas(self):
        """Очистка холста"""
        self.canvas.delete("all")
        self.polygon.clear()
        self.convex_hull.clear()

    @staticmethod
    def draw_dda(x1, y1, x2, y2):
        """Алгоритм ЦДА (DDA)"""
        points = []
        dx, dy = x2 - x1, y2 - y1
        steps = max(abs(dx), abs(dy))
        x_inc, y_inc = dx / steps, dy / steps
        x, y = x1, y1

        for _ in range(steps):
            points.append((round(x), round(y)))
            x += x_inc
            y += y_inc
        return points

    @staticmethod
    def draw_bresenham(x1, y1, x2, y2):
        """Алгоритм Брезенхема"""
        points = []
        dx, dy = abs(x2 - x1), abs(y2 - y1)
        sx, sy = (1 if x1 < x2 else -1), (1 if y1 < y2 else -1)
        err = dx - dy

        while True:
            points.append((x1, y1))
            if x1 == x2 and y1 == y2:
                break
            e2 = err * 2
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
        return points

    @staticmethod
    def draw_wu(x1, y1, x2, y2):
        """Алгоритм Ву"""
        points = []
        dx, dy = x2 - x1, y2 - y1
        steep = abs(dy) > abs(dx)

        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2

        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1

        dx, dy = x2 - x1, y2 - y1
        gradient = dy / dx if dx != 0 else 1
        y = y1 + 0.5

        for x in range(x1, x2 + 1):
            y_int = int(y)
            points.append((y_int, x) if steep else (x, y_int))
            y += gradient
        return points

    def graham_scan(self, points):
        """Алгоритм Грэхема для построения выпуклой оболочки"""
        points = sorted(points, key=lambda p: (p[1], p[0]))
        p0 = points[0]
        def polar_angle(p):
            return np.arctan2(p[1] - p0[1], p[0] - p0[0])

        sorted_points = sorted(points[1:], key=polar_angle)
        stack = [p0, sorted_points[0]]

        for p in sorted_points[1:]:
            while len(stack) > 1 and self.orientation(stack[-2], stack[-1], p) != -1:
                stack.pop()
            stack.append(p)

        return stack

    def jarvis_march(self, points):
        """Алгоритм Джарвиса"""
        if len(points) < 3:
            return points

        hull = []
        leftmost = min(points, key=lambda p: p[0])
        point = leftmost

        while True:
            hull.append(point)
            next_point = points[0]
            for candidate in points[1:]:
                if candidate == point:
                    continue
                o = self.orientation(point, next_point, candidate)
                if o == -1 or (o == 0 and np.linalg.norm(np.array(candidate) - np.array(point)) > np.linalg.norm(np.array(next_point) - np.array(point))):
                    next_point = candidate

            point = next_point
            if point == leftmost:
                break

        return hull

    @staticmethod
    def orientation(p, q, r):
        """Определяет поворот трех точек"""
        val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
        return 0 if val == 0 else (1 if val > 0 else -1)

    def point_in_polygon(self, point, polygon):
        """Метод луча для проверки принадлежности точки полигону"""
        x, y = point
        inside = False
        x0, y0 = polygon[-1]

        for x1, y1 in polygon:
            if min(y0, y1) < y <= max(y0, y1) and x <= max(x0, x1):
                x_intersect = (y - y0) * (x1 - x0) / (y1 - y0) + x0 if y0 != y1 else x0
                if x <= x_intersect:
                    inside = not inside
            x0, y0 = x1, y1
        return inside

    def is_convex(self, polygon):
        """Проверяет, является ли полигон выпуклым"""
        if len(polygon) < 3:
            return False  # Меньше 3 точек – не полигон

        direction = None  # Определяем направление первого поворота

        for i in range(len(polygon)):
            p1, p2, p3 = polygon[i], polygon[(i + 1) % len(polygon)], polygon[(i + 2) % len(polygon)]
            turn = self.orientation(p1, p2, p3)

            if turn != 0:  # Если точки не на одной прямой
                if direction is None:
                    direction = turn  # Запоминаем первое направление
                elif turn != direction:
                    return False  # Если поменялось направление, полигон невыпуклый

        return True  # Если направление одно – полигон выпуклый

    def check_convex(self):
        """Проверяет выпуклость полигона и выводит результат во всплывающем окне"""
        if not self.polygon:
            messagebox.showwarning("Ошибка", "Полигон не задан!")
            return

        if self.is_convex(self.polygon):
            messagebox.showinfo("Результат", "Полигон выпуклый ✅")
        else:
            messagebox.showwarning("Результат", "Полигон НЕ выпуклый ❌")

    def find_intersection(self):
        """Запускает процесс рисования линии с проверкой пересечений с полигоном"""
        if len(self.polygon) < 3:
            messagebox.showerror("Ошибка", "Недостаточно точек для полигона")
            return

        def on_first_click(event):
            """Обработчик для первой точки отрезка"""
            self.intersect_point = (event.x, event.y)
            self.canvas.unbind("<Button-1>")  # Отвязываем старый обработчик
            self.canvas.bind("<Button-1>", on_second_click)  # Привязываем второй обработчик

        def on_second_click(event):
            """Обработчик для второй точки отрезка"""
            x1, y1 = self.intersect_point
            x2, y2 = event.x, event.y

            # Рисуем отрезок с выбранным алгоритмом
            if self.selected_algorithm == "ЦДА":
                self.draw_dda(x1, y1, x2, y2, "blue")
            elif self.selected_algorithm == "Брезенхем":
                self.draw_bresenham(x1, y1, x2, y2, "blue")
            elif self.selected_algorithm == "Ву":
                self.draw_wu(x1, y1, x2, y2, "blue")

            self.canvas.unbind("<Button-1>")  # Отвязываем второй обработчик
            self.canvas.bind("<Button-1>", self.add_point)  # Возвращаем обработчик для добавления точки

            # Рисуем отрезок
            self.intersect_line = self.canvas.create_line(x1, y1, x2, y2, fill="blue")

            # Находим пересечения линии с полигоном
            intersections = self.calculate_intersection((x1, y1), (x2, y2), self.polygon)
            if intersections:
                for intersection in intersections:
                    x, y = intersection
                    self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="red", tags="intersect")
                messagebox.showinfo("Результат",
                                    f"Точки пересечения: {[f'({x:.2f}, {y:.2f})' for x, y in intersections]}")
            else:
                messagebox.showinfo("Результат", "Пересечение не найдено")

        # Привязываем обработчик для первой точки
        self.canvas.bind("<Button-1>", on_first_click)

    def calculate_intersection(self, p1, p2, poly):
        """Находит точки пересечения отрезка с полигоном"""
        intersection_points = []
        x1, y1 = p1
        x2, y2 = p2
        for i in range(len(poly)):
            x3, y3 = poly[i]
            x4, y4 = poly[(i + 1) % len(poly)]  # Следующая вершина, с учетом замкнутости

            # Вычисляем детерминант
            d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            if d == 0:
                continue  # Параллельные линии

            # Вычисляем параметры t и u
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
            u = ((x1 - x3) * (y1 - y2) - (y1 - y3) * (x1 - x2)) / d

            # Проверяем, лежит ли точка пересечения на отрезках
            if 0 <= t <= 1 and 0 <= u <= 1:
                # Вычисляем координаты пересечения
                intersect_x = x1 + t * (x2 - x1)
                intersect_y = y1 + t * (y2 - y1)
                intersection_points.append((intersect_x, intersect_y))

        return intersection_points


if __name__ == "__main__":
    root = tk.Tk()
    editor = PolygonEditor(root)
    root.mainloop()
