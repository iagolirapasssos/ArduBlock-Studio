@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo Gerando listagem de arquivos...
echo.

set "OUTPUT_FILE=out.txt"
set "SCRIPT_NAME=%~nx0"

REM Limpar arquivo de saída
type nul > "%OUTPUT_FILE%"

REM Função para verificar se um caminho deve ser excluído
call :ProcessDirectory "."

echo.
echo Concluído! Resultados salvos em %OUTPUT_FILE%
type "%OUTPUT_FILE%"
pause
exit /b

:ProcessDirectory
set "current_dir=%~1"

for /r "%current_dir%" %%F in (*) do (
    set "exclude=0"
   
    REM Verificar se é o próprio script
    if "%%~nxF"=="%SCRIPT_NAME%" set exclude=1
   
    REM Verificar arquivos específicos
    if "%%~nxF"=="database.rules.json" set exclude=1
    if "%%~nxF"=="package-lock.json" set exclude=1
   
    REM Verificar extensões de imagem
    if /i "%%~xF"==".png" set exclude=1
    if /i "%%~xF"==".jpg" set exclude=1
    if /i "%%~xF"==".jpeg" set exclude=1
    if /i "%%~xF"==".gif" set exclude=1
    if /i "%%~xF"==".webp" set exclude=1
    if /i "%%~xF"==".svg" set exclude=1
    if /i "%%~xF"==".bmp" set exclude=1
    if /i "%%~xF"==".ico" set exclude=1
    if /i "%%~xF"==".avif" set exclude=1
    if /i "%%~xF"==".css" set exclude=1
   
    REM Verificar extensões Python compiladas
    if /i "%%~xF"==".pyc" set exclude=1
    if /i "%%~xF"==".pyo" set exclude=1
   
    REM Verificar se está em diretórios excluídos
    echo "%%~dpF" | findstr /i "node_modules" >nul
    if not errorlevel 1 set exclude=1
    echo "%%~dpF" | findstr /i "builder_script" >nul
    if not errorlevel 1 set exclude=1
    echo "%%~dpF" | findstr /i "__pycache__" >nul
    if not errorlevel 1 set exclude=1
   
    if !exclude!==0 (
        REM Calcular caminho relativo
        set "full_path=%%F"
        set "full_path=!full_path:%CD%\=!"
       
        echo Processando: !full_path!
        echo !full_path!: >> "%OUTPUT_FILE%"
       
        REM Tentar ler o arquivo (apenas texto)
        type "%%F" >> "%OUTPUT_FILE%" 2>nul
        if errorlevel 1 (
            echo [Não foi possível ler o arquivo] >> "%OUTPUT_FILE%"
        )
       
        echo. >> "%OUTPUT_FILE%"
        echo. >> "%OUTPUT_FILE%"
    )
)

exit /b
