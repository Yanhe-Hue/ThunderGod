@echo off
chcp 65001 >nul
set "ALLURE_OPTS=-Duser.language=zh -Duser.region=CN"
set "AITEST_ENV_ROOT=%AITESTSTUDIO_ENV_ROOT%"
if not defined AITEST_ENV_ROOT (
    for /f "usebackq delims=" %%R in (`"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "%~dp0resolve_environment_runtime_root.ps1"`) do set "AITEST_ENV_ROOT=%%R"
)

if exist "%AITEST_ENV_ROOT%\java\bin\java.exe" (
    set "JAVA_HOME=%AITEST_ENV_ROOT%\java"
    set "PATH=%AITEST_ENV_ROOT%\java\bin;%PATH%"
)

set "ALLURE_CMD="
if defined ALLURE_HOME if exist "%ALLURE_HOME%\bin\allure.bat" set "ALLURE_CMD=%ALLURE_HOME%\bin\allure.bat"
if not defined ALLURE_CMD if exist "%AITEST_ENV_ROOT%\allure\bin\allure.bat" set "ALLURE_CMD=%AITEST_ENV_ROOT%\allure\bin\allure.bat"
if not defined ALLURE_CMD (
    for /d %%D in ("%AITEST_ENV_ROOT%\allure\*") do (
        if exist "%%~fD\bin\allure.bat" set "ALLURE_CMD=%%~fD\bin\allure.bat"
    )
)
if not defined ALLURE_CMD (
    for /f "delims=" %%I in ('where allure.bat 2^>nul') do if not defined ALLURE_CMD set "ALLURE_CMD=%%~fI"
)
if not defined ALLURE_CMD (
    echo [ERROR] Allure CLI not found. Please initialize or repair the environment first.
    exit /b 1
)

for %%I in ("%ALLURE_CMD%\..\..") do set "ALLURE_HOME=%%~fI"

echo Opening Allure report...
echo.

pushd "%~dp0"
if exist "reports\index.html" (
    call "%ALLURE_CMD%" open reports
) else (
    echo Generating report from allure-results...
    call "%ALLURE_CMD%" generate allure-results -o reports --clean
    if errorlevel 1 (
        echo [ERROR] Allure report generation failed.
        popd
        exit /b 1
    )
    call "%ALLURE_CMD%" open reports
)
popd
