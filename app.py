# app.py
"""
Root-level redirector — for backward compatibility.

The project has been restructured into separate apps:
  - hub/app.py                              → FBI Hub (landing page)
  - apps/group_executive_report/app.py      → Group Executive Report dashboard

To run locally:
  Option 1: Use the run script
    .\\scripts\\run_local.ps1

  Option 2: Run individually
    cd hub && streamlit run app.py --server.port 8501
    cd apps/group_executive_report && streamlit run app.py --server.port 8502

This file keeps the old entry point working for anyone who runs
`streamlit run app.py` from the repo root out of habit.
It simply launches the hub.
"""

import subprocess
import sys
import os

hub_app = os.path.join(os.path.dirname(__file__), "hub", "app.py")
subprocess.run([sys.executable, "-m", "streamlit", "run", hub_app] + sys.argv[1:])