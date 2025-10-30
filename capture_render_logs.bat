@echo off
REM Capture logs from Render backend
REM You need to have 'heroku' CLI installed or use web dashboard

echo ========================================
echo RENDER LOGS CAPTURE SCRIPT
echo ========================================
echo.
echo Option 1: WEB DASHBOARD (Recommended)
echo Open this link in your browser:
echo https://dashboard.render.com
echo.
echo Steps:
echo 1. Go to Services
echo 2. Click on "analise-bid-ia-backend"
echo 3. Click "Logs" tab
echo 4. Look for messages starting with:
echo    - "🤖 === CHAMANDO OPENAI ==="
echo    - "🔎 === ANALISANDO RESPOSTA ==="
echo    - "📊 Análise de Content:"
echo    - "❌ ERRO CRÍTICO"
echo 5. Select ALL logs (Ctrl+A)
echo 6. Copy (Ctrl+C)
echo 7. Paste in a text file and send to the developer
echo.
echo Option 2: COMMAND LINE (if you have render-cli)
echo Run: render logs analise-bid-ia-backend --tail
echo.
echo ========================================
echo IMPORTANT: The logs MUST include the "🔎 === ANALISANDO RESPOSTA ===" section
echo This will show us exactly why content is empty!
echo ========================================
pause
