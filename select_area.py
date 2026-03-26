import tkinter as tk


class ScreenSelector:
    def __init__(self):
        self.root = tk.Tk()

        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0

        self.selected_area = None

        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.3)
        self.root.configure(bg="black")

        self.canvas = tk.Canvas(self.root, cursor="cross", bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.rect = None

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        self.root.bind("<Escape>", self.close)

    def on_mouse_down(self, event):
        self.start_x = event.x
        self.start_y = event.y

        if self.rect:
            self.canvas.delete(self.rect)

        self.rect = self.canvas.create_rectangle(
            self.start_x,
            self.start_y,
            self.start_x,
            self.start_y,
            outline="red",
            width=2
        )

    def on_mouse_drag(self, event):
        self.end_x = event.x
        self.end_y = event.y
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.end_x, self.end_y)

    def on_mouse_up(self, event):
        self.end_x = event.x
        self.end_y = event.y

        x1 = min(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)

        self.selected_area = (x1, y1, x2, y2)

        self.root.quit()
        self.root.destroy()

    def close(self, event=None):
        self.selected_area = None
        self.root.quit()
        self.root.destroy()

    def get_area(self):
        self.root.mainloop()
        return self.selected_area