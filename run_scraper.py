#!/usr/bin/env python3
import sys
import os

# Add src to path so we can import the package
sys.path.insert(0, os.path.abspath("src"))

from web_doc_scraper.scraper import main

if __name__ == "__main__":
    main()
