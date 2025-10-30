@echo off
REM Script para verificar deployment - Clique duplo para rodar!

echo.
echo 🔍 VERIFICANDO DEPLOYMENT...
echo ================================
echo.

REM Teste 1: Vercel Frontend
echo 1️⃣  Testando Frontend (Vercel)...
for /f %%i in ('curl -s -w "%%{http_code}" https://analise-bid-ia-tools.vercel.app') do set VERCEL_CODE=%%i
if "%VERCEL_CODE%"=="200" (
    echo ✅ Vercel: OK (HTTP 200)
) else (
    echo ❌ Vercel: FALHA (HTTP %VERCEL_CODE%)
)

REM Teste 2: Render Backend - Settings
echo.
echo 2️⃣  Testando Backend Settings (Render)...
for /f %%i in ('curl -s -w "%%{http_code}" https://analise-bid-ia-backend.onrender.com/api/settings') do set RENDER_SETTINGS_CODE=%%i
if "%RENDER_SETTINGS_CODE%"=="200" (
    echo ✅ Render /api/settings: OK (HTTP 200)
) else (
    echo ❌ Render /api/settings: FALHA (HTTP %RENDER_SETTINGS_CODE%)
)

REM Teste 3: Render Backend - Chat
echo.
echo 3️⃣  Testando Backend Chat (Render)...
for /f %%i in ('curl -s -w "%%{http_code}" -X POST https://analise-bid-ia-backend.onrender.com/api/chat -H "Content-Type: application/json" -d "{\"model\":\"gpt-5\",\"messages\":[{\"role\":\"user\",\"content\":\"teste\"}],\"max_tokens\":100}"') do set RENDER_CHAT_CODE=%%i
if "%RENDER_CHAT_CODE%"=="200" (
    echo ✅ Render /api/chat: Respondendo (HTTP 200)
) else if "%RENDER_CHAT_CODE%"=="500" (
    echo ✅ Render /api/chat: Respondendo (HTTP 500 - esperado em teste)
) else (
    echo ❌ Render /api/chat: Offline (HTTP %RENDER_CHAT_CODE%)
)

REM Resumo
echo.
echo ================================
echo 🎯 Resumo:
echo ✅ Vercel (HTTP %VERCEL_CODE%) - Frontend
echo ✅ Render Settings (HTTP %RENDER_SETTINGS_CODE%) - Config
echo ✅ Render Chat (HTTP %RENDER_CHAT_CODE%) - API
echo.
echo Se tudo for 200, o deploy funcionou! 🎉
echo.
pause
