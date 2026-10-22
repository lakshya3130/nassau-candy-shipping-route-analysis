"""Compatibility entry point for the Streamlit dashboard."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().with_name("dashboard.py")))
