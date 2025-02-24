import tkinter as tk
import time
import math

class GraphicalEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Графический редактор")

        # Полотно для рисования
        self.canvas = tk.Canvas(root, width=600, height=500, bg="white")
        self.canvas.pack()

        # Фрейм для управления
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(fill=tk.X, pady=5)

        # Поля ввода для размеров
        self.create_label_input("Радиус / a:", 100, "size1")
        self.create_label_input("Высота / b:", 50, "size2")

        # Кнопки выбора режима
        self.figure_type = "circle"  # По умолчанию окружность
        self.create_button("Окружность", lambda: self.set_figure("circle"))
        self.create_button("Эллипс", lambda: self.set_figure("ellipse"))
        self.create_button("Гипербола", lambda: self.set_figure("hyperbola"))
        self.create_button("Парабола", lambda: self.set_figure("parabola"))

        # Кнопка включения режима отладки
        self.debug_mode = False
        self.debug_button = tk.Button(self.control_frame, text="Режим отладки: выкл", command=self.toggle_debug)
        self.debug_button.pack(side=tk.LEFT, padx=5)

        # Обработчик кликов
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def create_label_input(self, text, default, attr_name):
        """Создание подписи и поля ввода"""
        frame = tk.Frame(self.control_frame)
        frame.pack(side=tk.LEFT, padx=5)
        label = tk.Label(frame, text=text)
        label.pack()
        entry = tk.Entry(frame, width=5)
        entry.insert(0, str(default))
        entry.pack()
        setattr(self, attr_name, entry)  # Сохранение ссылки

    def create_button(self, text, command):
        """Создание кнопки"""
        button = tk.Button(self.control_frame, text=text, command=command)
        button.pack(side=tk.LEFT, padx=5)

    def set_figure(self, figure):
        """Выбор типа фигуры"""
        self.figure_type = figure

    def toggle_debug(self):
        """Переключение режима отладки"""
        self.debug_mode = not self.debug_mode
        self.debug_button.config(text=f"Режим отладки: {'вкл' if self.debug_mode else 'выкл'}")

    def delay(self):
        """Замедление для режима отладки"""
        if self.debug_mode:
            time.sleep(0.05)
            self.root.update()

    def get_sizes(self):
        """Получение введённых размеров"""
        try:
            size1 = int(self.size1.get())
            size2 = int(self.size2.get())
        except ValueError:
            size1, size2 = 100, 50  # Значения по умолчанию
        return size1, size2

    def on_canvas_click(self, event):
        """Рисование фигуры при клике (без очистки холста)"""
        size1, size2 = self.get_sizes()

        if self.figure_type == "circle":
            self.draw_circle(event.x, event.y, size1)
        elif self.figure_type == "ellipse":
            self.draw_ellipse(event.x, event.y, size1, size2)
        elif self.figure_type == "hyperbola":
            self.draw_hyperbola(event.x, event.y, size1, size2)
        elif self.figure_type == "parabola":
            self.draw_parabola(event.x, event.y, size1)

    def draw_point(self, x, y, color="black"):
        """Рисует точку на холсте и выводит её координаты в консоль"""
        self.canvas.create_oval(x, y, x+1, y+1, fill=color)
        print(f"{self.figure_type.capitalize()}: (x={x}, y={y})")
        self.delay()

    def draw_circle(self, x0, y0, r):
        """Алгоритм рисования окружности (Брезенхэм)"""
        x, y, d = 0, r, 3 - 2 * r
        while x <= y:
            for dx, dy in [(x, y), (y, x), (-y, x), (-x, y), (-x, -y), (-y, -x), (y, -x), (x, -y)]:
                self.draw_point(x0+dx, y0+dy)
            x += 1
            if d > 0:
                y -= 1
                d += 4 * (x - y) + 10
            else:
                d += 4 * x + 6

    def draw_ellipse(self, x0, y0, a, b):
        """Алгоритм рисования эллипса"""
        x, y = 0, b
        d1 = b**2 - a**2 * b + 0.25 * a**2

        while (a**2) * (y - 0.5) > (b**2) * (x + 1):
            for dx, dy in [(x, y), (-x, y), (x, -y), (-x, -y)]:
                self.draw_point(x0+dx, y0+dy)
            x += 1
            if d1 < 0:
                d1 += (2 * b**2) * x + b**2
            else:
                y -= 1
                d1 += (2 * b**2) * x - (2 * a**2) * y + b**2

        d2 = b**2 * (x + 0.5) ** 2 + a**2 * (y - 1) ** 2 - a**2 * b**2
        while y >= 0:
            for dx, dy in [(x, y), (-x, y), (x, -y), (-x, -y)]:
                self.draw_point(x0+dx, y0+dy)
            y -= 1
            if d2 > 0:
                d2 += a**2 - 2 * a**2 * y
            else:
                x += 1
                d2 += (2 * b**2) * x - (2 * a**2) * y + a**2

    def draw_hyperbola(self, x0, y0, a, b):
        """Рисование гиперболы"""
        x, y = a, 0

        d1 = b ** 2 * (x + 0.5) ** 2 - a ** 2 * (y + 1) ** 2 - a ** 2 * b ** 2
        while (b ** 2) * (x - 0.5) > (a ** 2) * (y + 1):
            for dx, dy in [(x, y), (-x, y), (x, -y), (-x, -y)]:
                self.draw_point(x0 + dx, y0 + dy)

            y += 1
            if d1 < 0:
                d1 += (2 * a ** 2) * y + a ** 2
            else:
                x += 1
                d1 += (2 * a ** 2) * y - (2 * b ** 2) * x + a ** 2

        d2 = b ** 2 * (x + 1) ** 2 - a ** 2 * (y + 0.5) ** 2 - a ** 2 * b ** 2
        while x < 200:
            for dx, dy in [(x, y), (-x, y), (x, -y), (-x, -y)]:
                self.draw_point(x0 + dx, y0 + dy)

            x += 1
            if d2 > 0:
                d2 += b ** 2 - (2 * b ** 2) * x
            else:
                y += 1
                d2 += (2 * a ** 2) * y - (2 * b ** 2) * x + b ** 2

    def draw_parabola(self, x0, y0, p):
        """Рисование параболы с двумя точками за шаг"""
        step = 1
        x = 0
        while x <= 200:
            y = (x ** 2) / (4 * p)
            self.draw_point(x0 + x, y0 - y)
            self.draw_point(x0 - x, y0 - y)
            x += step
if __name__ == "__main__":
    root = tk.Tk()
    app = GraphicalEditor(root)
    root.mainloop()
