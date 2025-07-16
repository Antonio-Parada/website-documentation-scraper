# Website Documentation Scraper

e **🚀 Now Available as Web Application!**  
e Deploy to: `scrape.mypp.site` with Firebase hosting and custom domain support

An intelligent web scraper that automatically extracts and formats website documentation using AI-powered analysis. The system uses Google's Gemini LLM to analyze website structure and optimize scraping parameters for maximum efficiency.

## 🌟 Features

### 🤖 **AI-Powered Intelligence**
- **LLM-Guided Analysis**: Gemini 2.5 Flash analyzes website structure and recommends optimal scraping parameters
- **BeautifulSoup Pre-Analysis**: Initial page structure assessment before LLM processing
- **Adaptive Configuration**: Dynamic parameter adjustment based on site complexity and type
- **Performance Optimization**: Smart delay and depth recommendations for respectful crawling

### 🎯 **Web Application (NEW!)**
- **Modern React Frontend**: Intuitive web interface replacing CLI
- **Real-time Progress Tracking**: Live updates during scraping operations
- **Job Management**: Background processing with status monitoring
- **Results Dashboard**: Browse, preview, and download scraped documentation
- **Custom Domain Support**: Deploy to `scrape.mypp.site`

### 📚 **Documentation Processing**
- **Intelligent Content Extraction**: Focuses on main documentation content
- **Multiple Format Support**: Markdown, HTML, and custom formats
- **Quality Scoring**: Automatic content quality assessment
- **Structured Output**: Organized file hierarchy with index generation
- **Resume Capability**: Continue interrupted scraping sessions

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │   Backend API   │    │   LLM Service   │
│   (React + TS)  │◄──►│   (FastAPI)     │◄──►│   (Gemini)      │
│                 │    │                 │    │                 │
│ • URL Input     │    │ • Job Queue     │    │ • Site Analysis │
│ • Config UI     │    │ • Progress      │    │ • System Prompts│
│ • Results View  │    │ • File Storage  │    │ • Optimization  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Firebase CLI
- Google API Key for Gemini

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Antonio-Parada/website-documentation-scraper.git
   cd website-documentation-scraper
   ```

2. **Set up environment:**
   ```bash
   # Set your Google API key
   export GOOGLE_APIKEY="your-gemini-api-key"
   
   # Install backend dependencies
   cd backend
   pip install -r requirements.txt
   cd ..
   
   # Install frontend dependencies
   cd frontend
   npm install
   cd ..
   ```

3. **Run locally:**
   ```bash
   # Terminal 1: Start backend
   cd backend
   python main.py
   
   # Terminal 2: Start frontend
   cd frontend
   npm start
   ```

4. **Deploy to Firebase:**
   ```bash
   # Windows
   ./deploy.ps1
   
   # Linux/Mac
   ./deploy.sh
   ```

## 🔧 Configuration

### Firebase Setup
1. Create a Firebase project
2. Enable Hosting and Functions
3. Update `.firebaserc` with your project ID
4. Configure custom domain in Firebase Console

### Environment Variables
```bash
GOOGLE_APIKEY=your-gemini-api-key
FIREBASE_PROJECT_ID=your-project-id
```

### Custom Domain Setup
1. Go to Firebase Console → Hosting
2. Add custom domain: `scrape.mypp.site`
3. Add CNAME record to your DNS:
   - Name: `scrape`
   - Type: `CNAME`
   - Value: `your-project.web.app`

## 📱 Web Interface

### Main Features
- **URL Analysis**: Enter a URL and get AI-powered structure analysis
- **Smart Configuration**: LLM-recommended settings with user overrides
- **Progress Monitoring**: Real-time scraping progress with ETA
- **Results Dashboard**: Browse generated files, view quality metrics
- **Download Options**: ZIP archives, individual files, or bulk export

### API Endpoints
- `POST /api/v1/analysis/pre-analyze` - BeautifulSoup analysis
- `POST /api/v1/analysis/llm-analyze` - Gemini-powered analysis
- `POST /api/v1/scraping/jobs` - Start scraping job
- `GET /api/v1/scraping/jobs/{id}` - Get job status
- `GET /api/v1/results/{id}` - Download results

## 💡 Usage Examples

### Web Interface
1. Open `https://scrape.mypp.site`
2. Enter target URL
3. Review AI recommendations
4. Adjust parameters if needed
5. Start scraping and monitor progress
6. Download results when complete

### API Usage
```python
import requests

# Pre-analyze a website
response = requests.post('https://scrape.mypp.site/api/v1/analysis/pre-analyze', 
                        json={'url': 'https://docs.python.org'})
analysis = response.json()

# Start scraping job
job_response = requests.post('https://scrape.mypp.site/api/v1/scraping/jobs',
                           json={
                               'url': 'https://docs.python.org',
                               'max_depth': 3,
                               'max_pages': 100,
                               'llm_guided': True
                           })
job_id = job_response.json()['job_id']

# Monitor progress
status = requests.get(f'https://scrape.mypp.site/api/v1/scraping/jobs/{job_id}')
```

## 🧪 Legacy CLI Usage

The original CLI interface is still available for power users:

```bash
# Basic scraping
python website_doc_scraper.py https://docs.python.org --depth 3 --pages 100

# LLM-guided configuration
python experimental/llm_guided_cli.py https://docs.python.org

# Smart scraper with AI optimization
python experimental/smart_scraper.py https://docs.python.org --non-interactive
```

## 📊 Performance Metrics

The system provides comprehensive performance analysis:
- **Efficiency Score**: Success rate of page processing
- **Completion Rate**: Percentage of discovered pages processed
- **Speed Metrics**: Pages per second, total duration
- **Quality Assessment**: Content quality grading (A-F)
- **Recommendations**: Suggestions for optimization

## 🔒 Security  Best Practices

- **Rate Limiting**: Respectful crawling with configurable delays
- **User-Agent**: Proper identification in requests
- **Robots.txt**: Respects site crawling policies
- **Error Handling**: Graceful failure management
- **API Authentication**: Secure API key management

## 🚦 Development Workflow

### Branch Structure
```
main                    # Stable releases
├── feature/web-app     # Web application development
├── feature/api-backend # Backend API development
└── feature/frontend    # React frontend development
```

### Deployment Pipeline
1. **Development**: Local testing with emulators
2. **Staging**: Firebase hosting preview
3. **Production**: Custom domain deployment

## 📈 Roadmap

### Phase 1: Backend Foundation ✅
- FastAPI application structure
- Pydantic data models
- Firebase Functions integration

### Phase 2: Frontend Development 🔄
- React TypeScript application
- Material-UI components
- Real-time progress updates

### Phase 3: Advanced Features 📋
- User authentication
- Job history and analytics
- Batch processing
- Export format options

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments
- **Google Gemini**: AI-powered website analysis
- **ScrapeGraphAI**: Core scraping capabilities
- **Firebase**: Hosting and serverless functions
- **React**: Modern web interface
- **FastAPI**: High-performance backend API

---

**🌐 Live Demo**: [scrape.mypp.site](https://scrape.mypp.site)  
**📚 API Docs**: [scrape.mypp.site/api/docs](https://scrape.mypp.site/api/docs)  
**🐛 Issues**: [GitHub Issues](https://github.com/Antonio-Parada/website-documentation-scraper/issues)

