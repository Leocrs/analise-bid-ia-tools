@echo off
chcp 65001 > nul
REM Script para verificar deployment - Clique duplo para rodar!

echo.
echo [VERIFICANDO DEPLOYMENT]
echo ================================
echo.

REM Teste 1: Vercel Frontend
echo [1] Testando Frontend (Vercel)...
for /f %%i in ('curl -s -w "%%{http_code}" https://analise-bid-ia-tools.vercel.app') do set VERCEL_CODE=%%i
if "%VERCEL_CODE%"=="200" (
    echo [OK] Vercel: HTTP 200
) else (
    echo [ERRO] Vercel: HTTP %VERCEL_CODE%
)

REM Teste 2: Render Backend - Settings
echo.
echo [2] Testando Backend Settings (Render)...
for /f %%i in ('curl -s -w "%%{http_code}" https://analise-bid-ia-backend.onrender.com/api/settings') do set RENDER_SETTINGS_CODE=%%i
if "%RENDER_SETTINGS_CODE%"=="200" (
    echo [OK] Render /api/settings: HTTP 200
) else (
    echo [ERRO] Render /api/settings: HTTP %RENDER_SETTINGS_CODE%
)

REM Teste 3: Render Backend - Chat
echo.
echo [3] Testando Backend Chat (Render)...
for /f %%i in ('curl -s -w "%%{http_code}" -X POST https://analise-bid-ia-backend.onrender.com/api/chat -H "Content-Type: application/json" -d "{\"model\":\"gpt-5\",\"messages\":[{\"role\":\"system\",\"content\":\"Responda breve\"},{\"role\":\"user\",\"content\":\"Teste simples\"}],\"max_tokens\":4000}"') do set RENDER_CHAT_CODE=%%i
if "%RENDER_CHAT_CODE%"=="200" (
    echo [OK] Render /api/chat: HTTP 200
) else if "%RENDER_CHAT_CODE%"=="500" (
    echo [OK] Render /api/chat: HTTP 500 (esperado em teste)
) else (
    echo [ERRO] Render /api/chat: HTTP %RENDER_CHAT_CODE%
)

REM Resumo
echo.
echo ================================
echo RESUMO:
echo Vercel: HTTP %VERCEL_CODE% - Frontend
echo Render Settings: HTTP %RENDER_SETTINGS_CODE% - Config
echo Render Chat: HTTP %RENDER_CHAT_CODE% - API
echo.
if "%VERCEL_CODE%"=="200" (
    if "%RENDER_SETTINGS_CODE%"=="200" (
        if "%RENDER_CHAT_CODE%"=="200" (
            echo *** DEPLOY FUNCIONOU COM SUCESSO ***
        )
    )
)
echo.
pause
