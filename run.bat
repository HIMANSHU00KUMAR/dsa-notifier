@echo off
setlocal
if exist "C:\Users\himan\AppData\Local\Programs\Python\Python312\python.exe" (
    "C:\Users\himan\AppData\Local\Programs\Python\Python312\python.exe" main.py %*
) else (
    python main.py %*
)
