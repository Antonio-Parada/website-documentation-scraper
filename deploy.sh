#!/bin/bash

# Website Documentation Scraper - Deployment Script
# ==================================================

set -e

echo "🚀 Starting deployment to scrape.mypp.site..."

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI is not installed. Please install it first:"
    echo "npm install -g firebase-tools"
    exit 1
fi

# Check if logged in to Firebase
if ! firebase projects:list &> /dev/null; then
    echo "❌ Not logged in to Firebase. Please log in first:"
    echo "firebase login"
    exit 1
fi

# Build frontend
echo "📦 Building React frontend..."
cd frontend
npm install
npm run build
cd ..

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Deploy to Firebase
echo "🔥 Deploying to Firebase..."
firebase deploy --only hosting,functions

echo "✅ Deployment complete!"
echo "🌐 Your app is available at: https://scrape.mypp.site"
echo "📚 API documentation: https://scrape.mypp.site/api/docs"

# Instructions for custom domain setup
echo ""
echo "🔗 To set up custom domain scrape.mypp.site:"
echo "1. Go to Firebase Console -> Hosting"
echo "2. Add custom domain: scrape.mypp.site"
echo "3. Add CNAME record to your DNS:"
echo "   Name: scrape"
echo "   Type: CNAME"
echo "   Value: website-scraper-mypp.web.app"
echo "4. Wait for SSL certificate provisioning"
