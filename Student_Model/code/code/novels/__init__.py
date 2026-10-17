"""
novels/ — 7 Biological Novel Components (Individual Files)
==========================================================
Each novel contribution is in its own file for clarity.
This __init__.py re-exports everything so other modules can
simply do: from novels import LateralInhibition, luminance, etc.
"""

from .luminance_utils import luminance
from .novel1_rlin import LateralInhibition
from .novel2_faeb import FrequencyBranch
from .novel3_arfp import AdaptiveReceptiveField
from .novel4_prcm import PhotoreceptorCurve
from .novel5_spdp import DualPathway
from .novel6_tam import TemporalAdaptation

__all__ = [
    "luminance",
    "LateralInhibition",
    "FrequencyBranch",
    "AdaptiveReceptiveField",
    "PhotoreceptorCurve",
    "DualPathway",
    "TemporalAdaptation",
]
