"""
PixelForge — Dark Neumorphism Edition
========================================
Entry point.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent)

from app import PixelForgeApp


def main():
    app = PixelForgeApp()
    app.run()


if __name__ == "__main__":
    main()
