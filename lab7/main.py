import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.spatial import Voronoi, voronoi_plot_2d
import scipy.spatial

class GeometryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Триангуляция Делоне и диаграмма Вороного")

        self.canvas_size = 600  # Фиксированное поле 600x600 пикселей

        # Основное окно
        self.root.geometry(f"{self.canvas_size}x{self.canvas_size + 100}")

        # Холст для Matplotlib, на котором будем отображать диаграмму
        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.ax.set_xlim(0, self.canvas_size)
        self.ax.set_ylim(0, self.canvas_size)
        self.ax.set_aspect('equal')
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Кнопки
        self.btn_delaunay = tk.Button(root, text="Триангуляция Делоне", command=self.compute_delaunay)
        self.btn_delaunay.pack()

        self.btn_voronoi = tk.Button(root, text="Диаграмма Вороного", command=self.voronoi_diagram)
        self.btn_voronoi.pack()

        self.btn_clear = tk.Button(root, text="Очистить", command=self.clear_canvas)
        self.btn_clear.pack()

        # Список точек
        self.points = []

        # Обработка кликов
        self.canvas.mpl_connect("button_press_event", self.on_click)

    def on_click(self, event):
        """Добавление точки при клике"""
        if event.xdata is not None and event.ydata is not None:
            if 0 <= event.xdata <= self.canvas_size and 0 <= event.ydata <= self.canvas_size:
                self.points.append((event.xdata, event.ydata))
                self.ax.plot(event.xdata, event.ydata, "ko")
                self.canvas.draw()

    def compute_delaunay(self):
        """Построение триангуляции Делоне"""
        if len(self.points) < 3:
            print("Нужно хотя бы 3 точки!")
            return

        self.ax.clear()
        self.ax.set_xlim(0, self.canvas_size)
        self.ax.set_ylim(0, self.canvas_size)
        self.ax.set_title("Триангуляция Делоне")

        points = np.array(self.points)
        self.ax.plot(points[:, 0], points[:, 1], "ko")

        # Используем scipy для триангуляции Делоне
        delaunay = scipy.spatial.Delaunay(points)

        for simplex in delaunay.simplices:
            for i in range(3):
                p1 = points[simplex[i]]
                p2 = points[simplex[(i + 1) % 3]]
                self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'b-')

        self.canvas.draw()

    def voronoi_diagram(self):
        """Строит диаграмму Вороного с использованием SciPy и отображает ее через Matplotlib в Tkinter."""
        if len(self.points) < 3:
            print("Нужно больше точек для диаграммы Вороного!")
            return

        try:
            # Используем SciPy для построения диаграммы Вороного
            points_array = np.array(self.points)  # Преобразуем список точек в массив NumPy
            vor = Voronoi(points_array)

            # Отображаем диаграмму Вороного с использованием scipy.spatial.voronoi_plot_2d
            self.ax.clear()
            self.ax.set_xlim(0, self.canvas_size)
            self.ax.set_ylim(0, self.canvas_size)
            self.ax.set_title("Диаграмма Вороного")

            # Параметры для отображения диаграммы
            voronoi_plot_2d(vor, ax=self.ax, show_vertices=False, line_colors='red', line_width=2, line_alpha=0.6)

            self.canvas.draw()

        except Exception as e:
            print(f"Ошибка при построении диаграммы Вороного: {e}")

    def clear_canvas(self):
        """Очистка экрана"""
        self.points.clear()
        self.ax.clear()
        self.ax.set_xlim(0, self.canvas_size)
        self.ax.set_ylim(0, self.canvas_size)
        self.ax.set_aspect('equal')
        self.canvas.draw()


# Запуск
root = tk.Tk()
app = GeometryApp(root)
root.mainloop()
