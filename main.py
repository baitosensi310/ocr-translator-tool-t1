import multiprocessing

from toolbar_window import ToolbarWindow

if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = ToolbarWindow()
    app.show()
