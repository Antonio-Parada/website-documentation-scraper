# Website Documentation Scraper (Development Prototype)

**⚠️ EXPERIMENTAL SOFTWARE ⚠️**

This is a **basic prototype** for scraping websites and converting them to Markdown using LLMs. It is **not** production-ready.

## 📝 Description
This tool uses `scrapegraphai` and Google's Gemini models to extract content from websites.
**Cost Warning:** This tool uses the Gemini API. Each page scraped will consume tokens. Monitoring your usage is your responsibility.

## ⚠️ Known Limitations
- **Blocking GUI:** The `gui.py` script uses Tkinter and may freeze the UI while scraping is in progress.
- **Cost:** Uses LLMs for every page, which can be slow and expensive.
- **Stability:** The underlying libraries are evolving rapidly. This code may break with updates to dependencies.
- **Structure:** This is a basic implementation, not a robust crawling framework.

## 🛠️ Installation

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Set API Key:**
    You need a Google Gemini API key.
    ```bash
    # Linux/Mac
    export GOOGLE_APIKEY="your_key_here"
    # Windows
    set GOOGLE_APIKEY=your_key_here
    ```

## 🚀 Usage

### Command Line
Run the scraper using the entry point script:
```bash
python run_scraper.py https://example.com --max-pages 5
```

### GUI
Start the graphical interface:
```bash
python src/web_doc_scraper/gui.py
```
*(Note: The GUI may become unresponsive during scraping operations.)*

### Backend Server
Start the Flask server:
```bash
python src/web_doc_scraper/backend.py
```

## 📂 Project Structure
- `src/web_doc_scraper/`: Source code.
  - `config.py`: Configuration (API keys, model selection).
  - `scraper.py`: Main logic.
  - `gui.py`: Basic Tkinter interface.
  - `backend.py`: Simple Flask server.
- `scripts/experimental/`: Experimental scripts (unsupported).
- `tests/`: Test files.
- `output/`: Generated documentation (default).

## 🧪 Verification
To verify the installation, run:
```bash
python verify_install.py
```
This attempts to scrape one page from `example.com`.
