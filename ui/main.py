#!/usr/bin/env python3
"""
main.py — ImageEnhancer Pro Entry Point
=========================================
Launch the app:  python main.py
"""

import sys
import os

# Ensure the ui/ directory is on sys.path so local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import ImageEnhancerPro


def main():
    app = ImageEnhancerPro()
    app.mainloop()


if __name__ == "__main__":
    main()
