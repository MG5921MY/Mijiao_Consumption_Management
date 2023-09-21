@echo off
setlocal enabledelayedexpansion

REM 设置虚拟环境的名称
set VENV_NAME=myenv


REM 激活虚拟环境
call %VENV_NAME%\Scripts\activate

REM 启动应用程序
streamlit run app.py

REM 退出虚拟环境
deactivate

echo 环境设置完成
pause
