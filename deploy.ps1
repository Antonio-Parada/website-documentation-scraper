# Website Documentation Scraper - Windows Deployment Script
# =========================================================

$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting deployment to scrape.mypp.site..." -ForegroundColor Green

# Check if Firebase CLI is installed
try {
    firebase --version | Out-Null
} catch {
    Write-Host "❌ Firebase CLI is not installed. Please install it first:" -ForegroundColor Red
    Write-Host "npm install -g firebase-tools" -ForegroundColor Yellow
    exit 1
}

# Check if logged in to Firebase
try {
    firebase projects:list | Out-Null
} catch {
    Write-Host "❌ Not logged in to Firebase. Please log in first:" -ForegroundColor Red
    Write-Host "firebase login" -ForegroundColor Yellow
    exit 1
}

# Build frontend
Write-Host "📦 Building React frontend..." -ForegroundColor Cyan
Set-Location frontend
npm install
npm run build
Set-Location ..

# Install backend dependencies
Write-Host "📦 Installing backend dependencies..." -ForegroundColor Cyan
Set-Location backend
pip install -r requirements.txt
Set-Location ..

# Deploy to Firebase
Write-Host "🔥 Deploying to Firebase..." -ForegroundColor Cyan
firebase deploy --only hosting,functions

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🌐 Your app is available at: https://scrape.mypp.site" -ForegroundColor Green
Write-Host "📚 API documentation: https://scrape.mypp.site/api/docs" -ForegroundColor Green

# Instructions for custom domain setup
Write-Host ""
Write-Host "🔗 To set up custom domain scrape.mypp.site:" -ForegroundColor Yellow
Write-Host "1. Go to Firebase Console -> Hosting" -ForegroundColor White
Write-Host "2. Add custom domain: scrape.mypp.site" -ForegroundColor White
Write-Host "3. Add CNAME record to your DNS:" -ForegroundColor White
Write-Host "   Name: scrape" -ForegroundColor White
Write-Host "   Type: CNAME" -ForegroundColor White
Write-Host "   Value: website-scraper-mypp.web.app" -ForegroundColor White
Write-Host "4. Wait for SSL certificate provisioning" -ForegroundColor White
