"""
Dark Neumorphism Dashboard — Entry Point
==========================================
"""

import sys
import os
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import NeuDashboard


def main():
    root = tk.Tk()
    NeuDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
