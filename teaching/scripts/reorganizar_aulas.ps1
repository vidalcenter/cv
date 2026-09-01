# Script para reorganizar todas as aulas em pastas individuais
# Cada aula ficará em: aulas/<disciplina>/aulas/<aulaNN_name>/<aulaNN_name>.qmd

$workspace = "c:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\meu_site"
$disciplines = @(
    "aulas\analise_dados_ambientais\aulas",
    "aulas\extensao_rural\aulas",
    "aulas\bioengenharia_de_solos\aulas",
    "aulas\geotecnologias_sig\aulas",
    "aulas\geotexteis\aulas",
    "aulas\ciencia_pi\SLIDES_QUARTO",
    "aulas\introducao_estatistica\SLIDES_QUARTO"
)

foreach ($disc in $disciplines) {
    $fullPath = Join-Path $workspace $disc
    Write-Host "`n=== Processando: $disc ===" -ForegroundColor Cyan
    
    if (-not (Test-Path $fullPath)) {
        Write-Host "Pasta não encontrada: $fullPath" -ForegroundColor Yellow
        continue
    }
    
    Push-Location $fullPath
    
    # 1. Criar pastas e mover arquivos
    Get-ChildItem -Filter "*.qmd" | Where-Object { 
        $_.Name -match '^(aula|Tema|tema)\d+' 
    } | ForEach-Object {
        $base = $_.BaseName
        
        # Criar pasta se não existir
        if (-not (Test-Path $base)) {
            New-Item -ItemType Directory -Path $base -Force | Out-Null
        }
        
        # Mover .qmd
        if (Test-Path "$base.qmd") {
            Move-Item -Path "$base.qmd" -Destination "$base\" -Force
        }
        
        # Mover .html se existir
        if (Test-Path "$base.html") {
            Move-Item -Path "$base.html" -Destination "$base\" -Force
        }
        
        Write-Host "  ✓ $base" -ForegroundColor Green
    }
    
    # 2. Atualizar caminhos relativos nos .qmd
    Get-ChildItem -Directory | Where-Object { 
        $_.Name -match '^(aula|Tema|tema)\d+' 
    } | ForEach-Object {
        $qmdFile = Join-Path $_.FullName "$($_.Name).qmd"
        
        if (Test-Path $qmdFile) {
            $content = Get-Content $qmdFile -Raw -Encoding UTF8
            
            # Adicionar um nível ../ aos caminhos de assets
            $content = $content -replace '../../assets/', '../../../assets/'
            $content = $content -replace '../assets/', '../../assets/'
            
            Set-Content $qmdFile -Value $content -Encoding UTF8 -NoNewline
        }
    }
    
    Pop-Location
}

Write-Host "`n=== Concluido! ===" -ForegroundColor Green
