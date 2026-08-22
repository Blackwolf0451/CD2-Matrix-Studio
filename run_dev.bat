@echo off
setlocal
set PYTHONPATH=%CD%\src
py -3 -m pip install -r requirements.txt
py -3 main.py
