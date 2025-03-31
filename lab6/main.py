import tkinter as tk
from tkinter import ttk, BooleanVar

class PolygonEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Графический редактор")

        # Холст для рисования
        self.canvas = tk.Canvas(root, width=600, height=400, bg="white")
        self.canvas.pack()

        # Подложка для работы с пикселями (PhotoImage)
        self.image = tk.PhotoImage(width=600, height=400)
        self.canvas.create_image((0, 0), image=self.image, anchor="nw")

        # Панель управления
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Кнопки управления
        self.clear_button = tk.Button(self.control_frame, text="Очистить", command=self.clear_canvas)
        self.clear_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.close_button = tk.Button(self.control_frame, text="Завершить", command=self.close_polygon)
        self.close_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Чекбокс режима отладки
        self.debug_mode = BooleanVar(value=False)
        self.debug_check = tk.Checkbutton(self.control_frame, text="Режим отладки", variable=self.debug_mode)
        self.debug_check.pack(side=tk.LEFT, padx=5, pady=5)

        # Выпадающий список выбора алгоритма заливки
        self.fill_method = tk.StringVar(value="Упорядоченный список рёбер")
        self.fill_menu = ttk.Combobox(self.control_frame, textvariable=self.fill_method,
                                      values=["Упорядоченный список рёбер",
                                              "Активный список рёбер",
                                              "Затравочный алгоритм (пиксельный)",
                                              "Затравочный алгоритм (построчный)"])
        self.fill_menu.pack(side=tk.LEFT, padx=5, pady=5)

        # Кнопка заливки
        self.fill_button = tk.Button(self.control_frame, text="Заливка", command=self.fill_polygon)
        self.fill_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Список вершин
        self.vertices = []
        self.polygon_closed = False

        # Обработчик кликов по холсту
        self.canvas.bind("<Button-1>", self.add_vertex)
        self.canvas.bind("<Button-3>", self.start_flood_fill)  # Запуск затравочного алгоритма правым кликом

    def add_vertex(self, event):
        """Добавление вершины полигона."""
        if self.polygon_closed:
            return

        x, y = event.x, event.y
        self.vertices.append((x, y))
        self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="black")

        if len(self.vertices) > 1:
            self.canvas.create_line(self.vertices[-2], self.vertices[-1], fill="black")

    def close_polygon(self):
        """Замыкает полигон, соединяя последнюю точку с первой."""
        if len(self.vertices) > 2 and not self.polygon_closed:
            self.polygon_closed = True
            self.canvas.create_line(self.vertices[-1], self.vertices[0], fill="black")

    def clear_canvas(self):
        """Очистка холста."""
        self.canvas.delete("all")
        self.vertices = []
        self.polygon_closed = False

    def fill_polygon(self):
        """Вызывает соответствующий алгоритм заливки в зависимости от выбора пользователя."""
        if not self.polygon_closed:
            print("Сначала завершите полигон!")
            return

        if self.fill_method.get() == "Упорядоченный список рёбер":
            edges = self.get_edges()
            self.scanline_fill_ordered(edges)
        elif self.fill_method.get() == "Активный список рёбер":
            edges = self.get_edges()
            self.scanline_fill_active(edges)
        elif self.fill_method.get() == "Затравочный алгоритм (пиксельный)" or "Затравочный алгоритм (построчный)":
            print("Для затравочной заливки кликните ПРАВОЙ кнопкой внутри полигона!")

    def get_edges(self):
        """Создаёт список рёбер полигона."""
        edges = []
        for i in range(len(self.vertices)):
            x1, y1 = self.vertices[i]
            x2, y2 = self.vertices[(i + 1) % len(self.vertices)]

            if y1 != y2:  # Игнорируем горизонтальные рёбра
                if y1 > y2:
                    x1, y1, x2, y2 = x2, y2, x1, y1  # Упорядочиваем по y

                edge = {
                    "y_min": y1,
                    "y_max": y2,
                    "x": x1,
                    "inv_slope": (x2 - x1) / (y2 - y1)
                }
                edges.append(edge)

        edges.sort(key=lambda e: e["y_min"])  # Сортируем по y_min
        return edges

    def scanline_fill_ordered(self, edges):
        """Заполнение полигона алгоритмом растровой развертки с упорядоченным списком рёбер."""
        if not edges:
            return

        y = edges[0]["y_min"]
        active_edges = []

        def fill_step():
            """Один шаг заливки (для отладки)."""
            nonlocal y
            active_edges.extend([e for e in edges if e["y_min"] == y])
            edges[:] = [e for e in edges if e["y_min"] != y]
            active_edges[:] = [e for e in active_edges if e["y_max"] > y]

            if not active_edges:
                return

            active_edges.sort(key=lambda e: e["x"])

            for i in range(0, len(active_edges), 2):
                if i + 1 < len(active_edges):
                    x1, x2 = int(active_edges[i]["x"]), int(active_edges[i + 1]["x"])
                    self.canvas.create_line(x1, y, x2, y, fill="red")
                    if self.debug_mode.get():
                        print(f"Рисуем линию от ({x1}, {y}) до ({x2}, {y})")

            y += 1
            for edge in active_edges:
                edge["x"] += edge["inv_slope"]

            if self.debug_mode.get():
                self.root.after(50, fill_step)
            else:
                fill_step()

        fill_step()

    def scanline_fill_active(self, edges):
        """Заполнение полигона с использованием активного списка рёбер (AET)."""
        if not edges:
            return

        y = edges[0]["y_min"]
        active_edges = []

        def fill_step():
            """Один шаг заливки (для отладки)."""
            nonlocal y
            active_edges.extend([e for e in edges if e["y_min"] == y])
            edges[:] = [e for e in edges if e["y_min"] != y]
            active_edges[:] = [e for e in active_edges if e["y_max"] > y]

            if not active_edges:
                return

            active_edges.sort(key=lambda e: e["x"])

            for i in range(0, len(active_edges), 2):
                if i + 1 < len(active_edges):
                    x1, x2 = int(active_edges[i]["x"]), int(active_edges[i + 1]["x"])
                    self.canvas.create_line(x1, y, x2, y, fill="blue")
                    if self.debug_mode.get():
                        print(f"Рисуем линию от ({x1}, {y}) до ({x2}, {y})")

            y += 1
            for edge in active_edges:
                edge["x"] += edge["inv_slope"]

            if self.debug_mode.get():
                self.root.after(50, fill_step)
            else:
                fill_step()

        fill_step()

    def start_flood_fill(self, event):
        """Запуск затравочной заливки по клику правой кнопкой."""
        if self.fill_method.get() == "Затравочный алгоритм (пиксельный)":
            self.flood_fill(event.x, event.y)
        elif self.fill_method.get() == "Затравочный алгоритм (построчный)":
            self.scanline_flood_fill(event.x, event.y)

    def point_inside_polygon(self, x, y):
        """Проверяет, находится ли точка (x, y) внутри полигона."""
        n = len(self.vertices)
        inside = False
        p1x, p1y = self.vertices[0]

        for i in range(n + 1):
            p2x, p2y = self.vertices[i % n]
            if min(p1y, p2y) < y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        x_intersect = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= x_intersect:
                        inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def flood_fill(self, x, y):
        """Затравочная заливка с проверкой внутри полигона."""
        if not self.point_inside_polygon(x, y):
            print("Точка вне полигона! Выберите другую.")
            return

        fill_color = "green"
        stack = [(x, y)]
        visited = set()  # Храним уже проверенные точки

        while stack:
            px, py = stack.pop()

            if (px, py) in visited:
                continue
            visited.add((px, py))

            if self.point_inside_polygon(px, py):
                self.image.put(fill_color, (px, py))

                stack.append((px+1, py))
                stack.append((px-1, py))
                stack.append((px, py+1))
                stack.append((px, py-1))

                if self.debug_mode.get():
                    print(f"Заполняем точку ({px}, {py})")

                self.root.update()

    def scanline_flood_fill(self, x, y):
        if not self.point_inside_polygon(x, y):
            print("Точка вне полигона!")
            return

        fill_color = "purple"
        stack = [(x, y)]
        visited = set()

        while stack:
            x, y = stack.pop()

            if (x, y) in visited or not self.point_inside_polygon(x, y):
                continue
            visited.add((x, y))

            # Найти границы строки (левая и правая границы)
            left, right = x, x
            while left > 0 and self.point_inside_polygon(left - 1, y) and (left - 1, y) not in visited:
                left -= 1
            while right < 599 and self.point_inside_polygon(right + 1, y) and (right + 1, y) not in visited:
                right += 1

            # Закрашиваем строку
            for i in range(left, right + 1):
                self.image.put(fill_color, (i, y))
                visited.add((i, y))  # Добавляем в посещённые точки

            if self.debug_mode.get():
                print(f"Заполняем строку {y} от {left} до {right}")

            # Добавляем верхнюю строку, если там есть незакрашенные пиксели
            if y > 0:
                for i in range(left, right + 1):
                    if (i, y - 1) not in visited and self.point_inside_polygon(i, y - 1):
                        stack.append((i, y - 1))
                        break  # Гарантированно добавляем строку только 1 раз

            # Добавляем нижнюю строку, если там есть незакрашенные пиксели
            if y < 399:
                for i in range(left, right + 1):
                    if (i, y + 1) not in visited and self.point_inside_polygon(i, y + 1):
                        stack.append((i, y + 1))
                        break  # Гарантированно добавляем строку только 1 раз

            self.root.update()

# Запуск
if __name__ == "__main__":
    root = tk.Tk()
    app = PolygonEditor(root)
    root.mainloop()
