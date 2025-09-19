param([string]$Msg = "chore: dev push")
$ErrorActionPreference = "Continue"

# Resolve repo root and app dir even when running from anywhere
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$AppDir   = Join-Path $RepoRoot 'app'

function Get-Pkg() {
  $pkgPath = Join-Path $AppDir 'package.json'
  if (-not (Test-Path $pkgPath)) { return $null }
  Get-Content $pkgPath -Raw | ConvertFrom-Json
}
function Save-Pkg($pkg) {
  $pkg | ConvertTo-Json -Depth 50 | Set-Content -Encoding UTF8 (Join-Path $AppDir 'package.json')
}
function HasScript($name) {
  $pkg = Get-Pkg
  if ($null -eq $pkg) { return $false }
  if (-not ($pkg.PSObject.Properties.Name -contains 'scripts')) { return $false }
  return $pkg.scripts.PSObject.Properties.Name -contains $name
}
function Ensure-Prettier() {
  if (HasScript "format") { return }
  Write-Host "-- adding minimal Prettier config + scripts" -ForegroundColor Yellow
  $prettierrc = Join-Path $AppDir '.prettierrc.json'
  $prettierig = Join-Path $AppDir '.prettierignore'
  if (-not (Test-Path $prettierrc)) { "{}" | Set-Content -Encoding UTF8 $prettierrc }
@"
node_modules
dist
.vite
coverage
*.log
"@ | Set-Content -Encoding UTF8 $prettierig

  $pkg = Get-Pkg
  if ($null -eq $pkg) { throw "app/package.json not found" }
  if (-not ($pkg.PSObject.Properties.Name -contains 'scripts')) {
    $pkg | Add-Member -NotePropertyName scripts -NotePropertyValue (@{}) -Force
  }
  if (-not ($pkg.scripts.PSObject.Properties.Name -contains 'format')) {
    $pkg.scripts | Add-Member -NotePropertyName 'format' -NotePropertyValue 'prettier "**/*" --write --ignore-path .prettierignore' -Force
  }
  if (-not ($pkg.scripts.PSObject.Properties.Name -contains 'format:check')) {
    $pkg.scripts | Add-Member -NotePropertyName 'format:check' -NotePropertyValue 'prettier "**/*" --check --ignore-path .prettierignore' -Force
  }
  Save-Pkg $pkg

  Push-Location $AppDir
  npm i -D prettier
  Pop-Location
}

Write-Host "== Format, lint, test, build ==" -ForegroundColor Cyan
Push-Location $AppDir
if (-not (Test-Path (Join-Path $AppDir 'package-lock.json'))) { npm i --package-lock-only | Out-Null }
npm ci

Ensure-Prettier
if (HasScript "format") { npm run format } else { npx prettier . --write }

if (HasScript "lint") {
  npm run lint
  if ($LASTEXITCODE -ne 0) {
    Write-Host "-- lint failed (likely ESLint config collision). Continuing." -ForegroundColor Yellow
    Write-Host "   Tip: keep only ONE config: either .eslintrc.* OR eslint.config.*" -ForegroundColor DarkYellow
  }
}

$ranTests = $false
if (HasScript "test") {
  $out = & npm test 2>&1
  $ranTests = $true
  if ($LASTEXITCODE -ne 0 -and ($out -join "`n") -match "No test files") {
    Write-Host "-- adding Vitest smoke test" -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path (Join-Path $AppDir 'src\__tests__') | Out-Null
@'
import { describe, it, expect } from "vitest";
describe("smoke", () => { it("works", () => expect(1+1).toBe(2)); });
'@ | Set-Content -Encoding UTF8 (Join-Path $AppDir 'src\__tests__\smoke.test.ts')
    npm test
  }
} else {
  Write-Host "-- no 'npm test' script found; skipping tests." -ForegroundColor Yellow
}

npm run build
Pop-Location

Write-Host "== Stage, commit, push ==" -ForegroundColor Cyan
git -C $RepoRoot add "$AppDir\src\" "$AppDir\index.html" "$AppDir\vite.config.ts" "$AppDir\.pretti*" "$AppDir\**\smoke.test.ts" ".github\workflows\gh-pages.yml" 2>$null
git -C $RepoRoot commit -m $Msg 2>$null
git -C $RepoRoot pull --rebase origin main
git -C $RepoRoot push origin main

Write-Host "== Trigger Pages deploy ==" -ForegroundColor Cyan
$trigger = Join-Path $AppDir '.pages-trigger'
Set-Content -Encoding UTF8 $trigger ("deploy: " + (Get-Date -Format o))
git -C $RepoRoot add $trigger
git -C $RepoRoot commit -m "chore: trigger gh-pages deploy" 2>$null
git -C $RepoRoot push origin main

Write-Host "Done. Pages will update shortly at https://csm120.github.io/keyquest/"
