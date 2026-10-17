"""
conftest.py — Shared fixtures for all unit tests.
"""

import sys
import os

# Add the parent code/ directory to sys.path so `novels`, `losses`, `model` etc. are importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import torch


@pytest.fixture
def device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


@pytest.fixture
def seed():
    torch.manual_seed(42)


@pytest.fixture
def rgb_tensor(seed):
    """Small random [B,3,H,W] tensor in [0,1] — standard test input."""
    return torch.rand(2, 3, 32, 32)


@pytest.fixture
def rgb_pair(seed):
    """Pred / target pair for loss tests."""
    pred = torch.rand(2, 3, 32, 32)
    target = torch.rand(2, 3, 32, 32)
    return pred, target
