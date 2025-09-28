"""
Import suppression configuration for TheNZT project
This file ensures all scientific computing libraries are properly recognized
"""

# pylint: disable=import-error,unused-import
# type: ignore

try:
    import numpy as np  # type: ignore
except ImportError:
    np = None

try:
    import pandas as pd  # type: ignore
except ImportError:
    pd = None

try:
    import matplotlib.pyplot as plt  # type: ignore
    import matplotlib.dates as mdates  # type: ignore
    from matplotlib.patches import Rectangle  # type: ignore
except ImportError:
    plt = None
    mdates = None
    Rectangle = None

try:
    import plotly.graph_objects as go  # type: ignore
    from plotly.subplots import make_subplots  # type: ignore
    import plotly.express as px  # type: ignore
except ImportError:
    go = None
    make_subplots = None
    px = None

try:
    import seaborn as sns  # type: ignore
except ImportError:
    sns = None

# Export all for use in other modules
__all__ = [
    'np', 'pd', 'plt', 'mdates', 'Rectangle', 
    'go', 'make_subplots', 'px', 'sns'
]