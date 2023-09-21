@echo off
setlocal enabledelayedexpansion

REM 设置虚拟环境的名称
set VENV_NAME=myenv

REM 创建虚拟环境
python -m venv %VENV_NAME%

REM 激活虚拟环境
call %VENV_NAME%\Scripts\activate

pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

python -m pip install --upgrade pip

REM 安装依赖项
pip install -r requirements.txt

REM 退出虚拟环境
deactivate

echo 环境设置完成
pause
