"""
PixelForge UI3 — Entry Point
=================================
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import PixelForgeApp


def main():
    app = PixelForgeApp()
    app.mainloop()


if __name__ == "__main__":
    main()
