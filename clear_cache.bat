@echo off
REM 프로그램 캐시 삭제 스크립트
REM Python .pyc 파일과 __pycache__ 디렉토리를 삭제합니다

echo.
echo ============================================================
echo 캐시 삭제 중...
echo ============================================================
echo.

REM Python 프로세스 종료
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul

REM .pyc 파일 삭제
for /r . %%A in (*.pyc) do (
    del /Q "%%A" 2>nul
)

REM __pycache__ 디렉토리 삭제
for /d /r . %%A in (__pycache__) do (
    rmdir /S /Q "%%A" 2>nul
)

echo.
echo ✓ 캐시가 삭제되었습니다.
echo.
echo 이제 프로그램을 다시 실행하세요:
echo   - run_contract_generator.bat 더블클릭
echo   - 또는 python main.py
echo.
pause
