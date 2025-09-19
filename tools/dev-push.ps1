param(
  [string]$Msg = "chore: dev push"
)

# Repo root guard
if (-not (Test-Path .git)) { Write-Error "Run from repo root"; exit 1 }

Write-Host "== Format, lint, test, build ==" -ForegroundColor Cyan
pushd app
if (-not (Test-Path package-lock.json)) { npm i --package-lock-only | Out-Null }
npm run format
npm run lint
npm test
npm run build
popd

Write-Host "== Stage typical app changes ==" -ForegroundColor Cyan
git add app\src\ app\index.html app\vite.config.ts app\public\manifest.webmanifest 2>$null

Write-Host "== Commit (no-op if nothing changed) ==" -ForegroundColor Cyan
git commit -m $Msg 2>$null

Write-Host "== Push to main ==" -ForegroundColor Cyan
git pull --rebase origin main
git push origin main

Write-Host "== Trigger Pages deploy (tiny no-op under app/) ==" -ForegroundColor Cyan
Set-Content -Encoding UTF8 app\.pages-trigger ("deploy: " + (Get-Date -Format o))
git add app\.pages-trigger
git commit -m "chore: trigger gh-pages deploy" 2>$null
git push origin main

Write-Host "Done. Pages will update shortly at https://csm120.github.io/keyquest/"
