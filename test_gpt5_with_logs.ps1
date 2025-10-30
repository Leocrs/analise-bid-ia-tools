# 🔍 Script para testar GPT-5 direto do PowerShell
# Uso: Execute no Terminal do VS Code (PowerShell)

Write-Host "=================================================="
Write-Host "🔍 TESTE DE DIAGNÓSTICO GPT-5 COM POWERSHELL" -ForegroundColor Cyan
Write-Host "=================================================="
Write-Host ""

$BACKEND_URL = "https://analise-bid-ia-backend.onrender.com"
$DIAGNOSTIC_ENDPOINT = "$BACKEND_URL/api/test-gpt5"

Write-Host "📍 Endpoint: $DIAGNOSTIC_ENDPOINT" -ForegroundColor Green
Write-Host "⏰ Horário: $(Get-Date)" -ForegroundColor Green
Write-Host ""

# Teste 1: Teste simples
Write-Host "🧪 Teste 1: Teste simples" -ForegroundColor Yellow
Write-Host "Mensagem: 'Teste simples: responda OK'" -ForegroundColor Gray
Write-Host ""

$body1 = @{
    message = "Teste simples: responda OK"
} | ConvertTo-Json

Write-Host "📤 Enviando requisição..." -ForegroundColor Blue
$start1 = Get-Date

try {
    $response1 = Invoke-RestMethod `
        -Uri $DIAGNOSTIC_ENDPOINT `
        -Method POST `
        -ContentType "application/json" `
        -Body $body1
    
    $end1 = Get-Date
    $time1 = ($end1 - $start1).TotalSeconds
    
    Write-Host "✅ Resposta recebida em $time1 segundos" -ForegroundColor Green
    Write-Host ""
    Write-Host "📦 Resultado:" -ForegroundColor Blue
    $response1 | ConvertTo-Json -Depth 10 | Write-Host -ForegroundColor White
}
catch {
    Write-Host "❌ ERRO: $_" -ForegroundColor Red
    Write-Host ""
}

Write-Host ""
Write-Host "=================================================="
Write-Host ""

# Teste 2: Teste com prompt mais longo
Write-Host "🧪 Teste 2: Teste com prompt mais longo" -ForegroundColor Yellow
Write-Host "Mensagem: Multi-line prompt" -ForegroundColor Gray
Write-Host ""

$body2 = @{
    message = "Você é um assistente especializado em análise de documentos.`n`nAnalise o seguinte texto:`n`nO documento trata de análise de licitações públicas.`n`nQual é o assunto principal?"
} | ConvertTo-Json

Write-Host "📤 Enviando requisição..." -ForegroundColor Blue
$start2 = Get-Date

try {
    $response2 = Invoke-RestMethod `
        -Uri $DIAGNOSTIC_ENDPOINT `
        -Method POST `
        -ContentType "application/json" `
        -Body $body2
    
    $end2 = Get-Date
    $time2 = ($end2 - $start2).TotalSeconds
    
    Write-Host "✅ Resposta recebida em $time2 segundos" -ForegroundColor Green
    Write-Host ""
    Write-Host "📦 Resultado:" -ForegroundColor Blue
    $response2 | ConvertTo-Json -Depth 10 | Write-Host -ForegroundColor White
}
catch {
    Write-Host "❌ ERRO: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=================================================="
Write-Host "✅ Testes concluídos!" -ForegroundColor Green
