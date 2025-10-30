@echo off
REM ============================================================
REM CAPTURADOR DE LOGS DO RENDER - Execute AGORA!
REM ============================================================
REM
REM Este script abre o dashboard do Render no seu navegador
REM para que você possa copiar os logs do backend.
REM
REM INSTRUÇÕES:
REM 1. Abra este arquivo (vai abrir o navegador automaticamente)
REM 2. Clique em "analise-bid-ia-backend" (o seu service)
REM 3. Vá para a aba "Logs"
REM 4. Procure pelas linhas que começam com:
REM    - 🤖 === CHAMANDO OPENAI ===
REM    - 🔎 === ANALISANDO RESPOSTA ===
REM    - ❌ ERRO CRÍTICO
REM 5. Selecione TUDO (Ctrl+A) e copie (Ctrl+C)
REM 6. Cole em um arquivo de texto e me envie
REM
REM ============================================================

echo.
echo ⏳ Abrindo Render Dashboard...
echo.
timeout /t 2

start https://dashboard.render.com

echo.
echo ✅ Dashboard aberto! 
echo.
echo PRÓXIMOS PASSOS:
echo 1. Clique em "Services" (à esquerda)
echo 2. Clique em "analise-bid-ia-backend"
echo 3. Clique na aba "Logs" (ao topo)
echo 4. Role até o final dos logs
echo 5. Procure pelos logs que começam com:
echo    🤖 === CHAMANDO OPENAI ===
echo    🔎 === ANALISANDO RESPOSTA ===
echo 6. Copie TUDO (Ctrl+A depois Ctrl+C)
echo 7. Cole em um arquivo .txt e me envie
echo.
pause
