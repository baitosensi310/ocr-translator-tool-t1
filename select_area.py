import tkinter as tk


class ScreenSelector:
    def __init__(self):
        # 建立主視窗
        self.root = tk.Tk()

        # 記錄起點與終點座標
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0

        # 最後回傳的範圍
        self.selected_area = None

        # 視窗全螢幕、置頂、半透明
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.3)

        # 背景顏色
        self.root.configure(bg="black")

        # 建立畫布
        self.canvas = tk.Canvas(self.root, cursor="cross", bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 矩形框 id
        self.rect = None

        # 綁定滑鼠事件
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        # 按 ESC 離開
        self.root.bind("<Escape>", self.close)

    def on_mouse_down(self, event):
        # 滑鼠按下時，記錄起點
        self.start_x = event.x
        self.start_y = event.y

        # 如果之前有矩形，先刪掉
        if self.rect:
            self.canvas.delete(self.rect)

        # 先建立一個初始矩形
        self.rect = self.canvas.create_rectangle(
            self.start_x,
            self.start_y,
            self.start_x,
            self.start_y,
            outline="red",
            width=2
        )

    def on_mouse_drag(self, event):
        # 滑鼠拖曳時，更新終點
        self.end_x = event.x
        self.end_y = event.y

        # 更新矩形大小
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.end_x, self.end_y)

    def on_mouse_up(self, event):
        # 滑鼠放開時，記錄終點
        self.end_x = event.x
        self.end_y = event.y

        # 保證左上到右下順序正確
        x1 = min(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)

        self.selected_area = (x1, y1, x2, y2)

        # 關閉選取視窗
        self.root.quit()
        self.root.destroy()

    def close(self, event=None):
        self.selected_area = None
        self.root.quit()
        self.root.destroy()

    def get_area(self):
        self.root.mainloop()
        return self.selected_area


if __name__ == "__main__":
    selector = ScreenSelector()
    area = selector.get_area()
    print("選到的範圍：", area)