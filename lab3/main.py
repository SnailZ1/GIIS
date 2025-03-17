import tkinter as tk
import numpy as np

class CurveEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Графический редактор кривых")

        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack()

        self.points = []
        self.selected_point = None
        self.current_curve = "bezier"

        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.pack()

        tk.Button(self.buttons_frame, text="Безье", command=lambda: self.set_curve("bezier")).pack(side=tk.LEFT)
        tk.Button(self.buttons_frame, text="Эрмит", command=lambda: self.set_curve("hermite")).pack(side=tk.LEFT)
        tk.Button(self.buttons_frame, text="B-сплайн", command=lambda: self.set_curve("bspline")).pack(side=tk.LEFT)
        tk.Button(self.buttons_frame, text="Очистить", command=self.clear_canvas).pack(side=tk.LEFT)

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def set_curve(self, curve_type):
        self.current_curve = curve_type
        self.redraw()

    def clear_canvas(self):
        self.points = []
        self.canvas.delete("all")

    def on_click(self, event):
        """Добавление или выбор ближайшей точки"""
        self.selected_point = None
        min_dist = float('inf')

        for i, (x, y) in enumerate(self.points):
            dist = (x - event.x) ** 2 + (y - event.y) ** 2
            if dist < 100:
                if dist < min_dist:
                    min_dist = dist
                    self.selected_point = i

        if self.selected_point is None:
            self.points.append((event.x, event.y))
            self.redraw()

    def on_drag(self, event):
        """Перемещение выбранной точки"""
        if self.selected_point is not None and 0 <= self.selected_point < len(self.points):
            self.points[self.selected_point] = (event.x, event.y)
            self.redraw()

    def on_release(self, event):
        """Сброс выбранной точки"""
        self.selected_point = None

    def redraw(self):
        self.canvas.delete("all")
        for x, y in self.points:
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="red")

        if self.current_curve == "bezier":
            self.draw_bezier()
        elif self.current_curve == "hermite":
            self.draw_hermite()
        elif self.current_curve == "bspline":
            self.draw_bspline()

    def draw_bezier(self):
        if len(self.points) < 4:
            return
        step = 100
        for i in range(len(self.points) - 3):
            p0, p1, p2, p3 = self.points[i:i+4]
            for t in np.linspace(0, 1, step):
                x, y = self.bezier_point(p0, p1, p2, p3, t)
                self.canvas.create_oval(x, y, x+1, y+1, fill="black")

    def bezier_point(self, p0, p1, p2, p3, t):
        M = np.array([
            [-1,  3, -3, 1],
            [ 3, -6,  3, 0],
            [-3,  3,  0, 0],
            [ 1,  0,  0, 0]
        ])
        T = np.array([t**3, t**2, t, 1])
        P = np.array([p0, p1, p2, p3])
        return T @ M @ P

    def draw_hermite(self):
        if len(self.points) < 4:
            return
        step = 100
        for i in range(0, len(self.points) - 3, 3):
            p0, p1, p2, p3 = self.points[i:i+4]
            for t in np.linspace(0, 1, step):
                x, y = self.hermite_point(p0, p1, p2, p3, t)
                self.canvas.create_oval(x, y, x+1, y+1, fill="blue")

    def hermite_point(self, p0, p1, p2, p3, t):
        h1 = 2 * t**3 - 3 * t**2 + 1
        h2 = -2 * t**3 + 3 * t**2
        h3 = t**3 - 2 * t**2 + t
        h4 = t**3 - t**2
        x = h1 * p0[0] + h2 * p3[0] + h3 * (p1[0] - p0[0]) + h4 * (p2[0] - p3[0])
        y = h1 * p0[1] + h2 * p3[1] + h3 * (p1[1] - p0[1]) + h4 * (p2[1] - p3[1])
        return x, y

    def draw_bspline(self):
        if len(self.points) < 4:
            return
        step = 100
        for i in range(len(self.points) - 3):
            p0, p1, p2, p3 = self.points[i:i+4]
            for t in np.linspace(0, 1, step):
                x, y = self.bspline_point(p0, p1, p2, p3, t)
                self.canvas.create_oval(x, y, x+1, y+1, fill="green")

    def bspline_point(self, p0, p1, p2, p3, t):
        B = np.array([
            [-1,  3, -3,  1],
            [ 3, -6,  3,  0],
            [-3,  0,  3,  0],
            [ 1,  4,  1,  0]
        ]) / 6
        T = np.array([t**3, t**2, t, 1])
        P = np.array([p0, p1, p2, p3])
        return T @ B @ P

root = tk.Tk()
app = CurveEditor(root)
root.mainloop()
