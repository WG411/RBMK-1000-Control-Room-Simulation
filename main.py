from __future__ import annotations
import tkinter as tk
from tkinter import ttk

from ui import App


def main():

    root = tk.Tk()

    try:

        ttk.Style().theme_use(
            "clam"
        )

    except tk.TclError:

        pass

    App(root)

    root.mainloop()


if __name__ == "__main__":
    main()