@echo off
REM ============================================================================
REM 계약서 자동작성 프로그램 - 실행 스크립트
REM Contract Generator - Launcher Script
REM ============================================================================
REM
REM 이 파일을 더블클릭하여 프로그램을 실행하세요.
REM Double-click this file to run the application.
REM
REM ============================================================================

setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

REM 현재 디렉토리를 스크립트 위치로 설정
cd /d "%~dp0"

REM 배너 출력
echo.
echo ============================================================================
echo   계약서 자동작성 프로그램 (Contract Generator)
echo ============================================================================
echo.

REM Python 경로 확인
echo [1/3] Python 환경 확인 중...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python을 찾을 수 없습니다!
    echo.
    echo 해결 방법:
    echo  1. Python 3.9 이상이 설치되어 있는지 확인하세요
    echo  2. Python을 다운로드하세요: https://www.python.org/downloads/
    echo  3. 설치 시 "Add Python to PATH" 옵션을 반드시 선택하세요
    echo  4. 컴퓨터를 재시작한 후 다시 시도하세요
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✓ %PYTHON_VERSION% 설치됨

REM 필수 패키지 확인
echo [2/3] 필수 패키지 확인 중...
python -c "import openpyxl, loguru" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] 일부 필수 패키지가 설치되지 않았습니다.
    echo 다음 명령어를 실행하여 패키지를 설치하세요:
    echo.
    echo   pip install -r requirements.txt
    echo.
    echo 계속 진행하시겠습니까? (Y/N)
    set /p CHOICE="선택: "
    if /i not "%CHOICE%"=="Y" exit /b 1
)
echo ✓ 필수 패키지 확인 완료

REM 프로그램 실행 (Python 캐시 무시: -B 플래그)
echo [3/3] 프로그램 시작 중...
echo.
echo ============================================================================
echo.
python -B main.py
set PYEXIT=%errorlevel%

if %PYEXIT% neq 0 (
    echo.
    echo ============================================================================
    echo [ERROR] 프로그램 실행 중 오류가 발생했습니다! (종료 코드: %PYEXIT%)
    echo ============================================================================
    echo.
    echo 해결 방법:
    echo  1. 위의 오류 메시지를 확인하세요
    echo  2. README.md 파일의 "문제 해결" 섹션을 읽으세요
    echo  3. 문제가 계속되면 Python과 패키지를 다시 설치하세요
    echo.
    pause
    exit /b %PYEXIT%
) else (
    echo.
    echo ============================================================================
    echo 프로그램이 정상 종료되었습니다.
    echo ============================================================================
    echo.
)

exit /b 0
