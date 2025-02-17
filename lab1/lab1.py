import tkinter as tk
import time


def dda_line(x1, y1, x2, y2, canvas, delay=0.05):
    if x1 == x2 and y1 == y2:  # Проверка на одинаковые точки
        canvas.create_oval(x1, y1, x1 + 1, y1 + 1, fill="black")
        return

    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))
    x_inc = dx / float(steps)
    y_inc = dy / float(steps)

    x, y = x1, y1
    for _ in range(int(steps) + 1):
        print(f"DDA Point: ({x:.2f}, {y:.2f})")
        canvas.create_oval(x, y, x + 1, y + 1, fill="black")
        x += x_inc
        y += y_inc
        canvas.update()
        if delay > 0:
            time.sleep(delay)


# Алгоритм Брезенхама
def bresenham_line(x1, y1, x2, y2, canvas, delay=0.05):
    if x1 == x2 and y1 == y2:  # Проверка на одинаковые точки
        canvas.create_oval(x1, y1, x1 + 1, y1 + 1, fill="black")
        return

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        normalized_err = min(max(err / max(dx, dy), -1), 1)
        print(f"Bresenham Point: ({x1}, {y1}), Error: {normalized_err:.2f}")
        canvas.create_oval(x1, y1, x1 + 1, y1 + 1, fill="black")
        if x1 == x2 and y1 == y2:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
        canvas.update()
        if delay > 0:
            time.sleep(delay)


# Алгоритм Ву
def wu_line(x1, y1, x2, y2, canvas, delay=0.05):
    if x1 == x2 and y1 == y2:  # Проверка на одинаковые точки
        canvas.create_oval(x1, y1, x1 + 1, y1 + 1, fill="black")
        return

    def plot(x, y, intensity):
        color = get_color(intensity)
        canvas.create_oval(x, y, x + 1, y + 1, fill=color)

    dx = x2 - x1
    dy = y2 - y1
    steep = abs(dy) > abs(dx)

    if steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1

    dx = x2 - x1
    dy = y2 - y1
    gradient = dy / dx if dx != 0 else 0

    y = y1

    for x in range(int(x1), int(x2) + 1):
        intensity = y - int(y)
        print(f"Wu Point: ({int(x)}, {int(y)}), Intensity: {intensity:.2f}")
        if steep:
            plot(int(y), x, intensity)
            plot(int(y) + 1, x, 1 - intensity)
        else:
            plot(x, y, intensity)
            plot(x, int(y) + 1, 1 - intensity)
        y += gradient
        canvas.update()
        if delay > 0:
            time.sleep(delay)


def get_color(intensity):
    intensity = max(0, min(intensity, 1))
    gray_value = int((1 - intensity) * 255)
    return f"#{gray_value:02x}{gray_value:02x}{gray_value:02x}"


# Главное окно приложения
class LineDrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Line Drawing Algorithms")

        self.canvas = tk.Canvas(self.root, bg='white', width=800, height=600)
        self.canvas.pack()

        self.button_dda = tk.Button(self.root, text="DDA", command=self.dda)
        self.button_dda.pack(side="left")

        self.button_bresenham = tk.Button(self.root, text="Bresenham", command=self.bresenham)
        self.button_bresenham.pack(side="left")

        self.button_wu = tk.Button(self.root, text="Wu", command=self.wu)
        self.button_wu.pack(side="left")

        self.debug_button = tk.Button(self.root, text="Debug Mode", command=self.toggle_debug)
        self.debug_button.pack(side="left")

        self.is_debug_mode = False
        self.selected_algorithm = "DDA"

        self.start_x, self.start_y, self.end_x, self.end_y = None, None, None, None

        self.canvas.bind("<Button-1>", self.on_click)

    def toggle_debug(self):
        self.is_debug_mode = not self.is_debug_mode

    def on_click(self, event):
        if self.start_x is None and self.start_y is None:
            self.start_x, self.start_y = event.x, event.y
        else:
            self.end_x, self.end_y = event.x, event.y
            self.draw_line()
            self.start_x, self.start_y, self.end_x, self.end_y = None, None, None, None

    def draw_line(self):
        delay = 0.2 if self.is_debug_mode else 0
        if self.selected_algorithm == "DDA":
            dda_line(self.start_x, self.start_y, self.end_x, self.end_y, self.canvas, delay)
        elif self.selected_algorithm == "Bresenham":
            bresenham_line(self.start_x, self.start_y, self.end_x, self.end_y, self.canvas, delay)
        elif self.selected_algorithm == "Wu":
            wu_line(self.start_x, self.start_y, self.end_x, self.end_y, self.canvas, delay)

    def dda(self):
        self.selected_algorithm = "DDA"

    def bresenham(self):
        self.selected_algorithm = "Bresenham"

    def wu(self):
        self.selected_algorithm = "Wu"


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = LineDrawingApp(root)
    root.mainloop()
