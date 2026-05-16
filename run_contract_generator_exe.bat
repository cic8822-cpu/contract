@echo off
REM ============================================================================
REM 계약서 자동작성 프로그램 - EXE 실행 스크립트 (테스트용)
REM Contract Generator - EXE Launcher (For Testing)
REM ============================================================================

setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

REM 현재 디렉토리를 스크립트 위치로 설정
cd /d "%~dp0"

REM 배너 출력
echo.
echo ============================================================================
echo   계약서 자동작성 프로그램 EXE 버전 (Contract Generator - EXE Version)
echo ============================================================================
echo.

REM EXE 파일 확인
if not exist "dist\contract_generator.exe" (
    echo [ERROR] EXE 파일을 찾을 수 없습니다: dist\contract_generator.exe
    echo.
    pause
    exit /b 1
)

echo [1/1] EXE 시작 중...
echo.
echo ============================================================================
echo.

REM EXE 실행
dist\contract_generator.exe
set EXEXIT=%errorlevel%

if %EXEXIT% neq 0 (
    echo.
    echo ============================================================================
    echo [ERROR] 프로그램 실행 중 오류가 발생했습니다! (종료 코드: %EXEXIT%)
    echo ============================================================================
    echo.
    pause
    exit /b %EXEXIT%
) else (
    echo.
    echo ============================================================================
    echo 프로그램이 정상 종료되었습니다.
    echo ============================================================================
    echo.
)

exit /b 0
