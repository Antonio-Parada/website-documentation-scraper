"""
Website Documentation Scraper GUI
=================================

Cross-platform GUI interface for the website documentation scraper.
Built with tkinter for universal compatibility.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import json
import os
import time
from pathlib import Path
from datetime import datetime
import queue
import webbrowser

# Import our scraper
from website_doc_scraper import WebsiteDocumentationScraper

# Ensure API key is set
if "GOOGLE_APIKEY" not in os.environ:
    raise ValueError("Please set the GOOGLE_APIKEY environment variable")

class ScraperGUI:
    """GUI interface for the website documentation scraper"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Website Documentation Scraper")
        self.root.geometry("800x700")
        
        # Configure for Mac styling
        if os.name == 'posix':  # macOS/Linux
            self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.scraper = None
        self.scraping_thread = None
        self.is_scraping = False
        self.message_queue = queue.Queue()
        
        # Create GUI elements
        self.create_widgets()
        
        # Start message processor
        self.root.after(100, self.process_messages)
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Website Documentation Scraper", 
                              font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # URL input
        ttk.Label(main_frame, text="Website URL:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar(value="https://scrapegraph-ai.readthedocs.io")
        url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50)
        url_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Output directory
        ttk.Label(main_frame, text="Output Directory:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_var = tk.StringVar(value="docs")
        output_entry = ttk.Entry(main_frame, textvariable=self.output_var, width=40)
        output_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output_dir).grid(row=2, column=2, pady=5)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Scraping Settings", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        settings_frame.columnconfigure(1, weight=1)
        
        # Max depth
        ttk.Label(settings_frame, text="Max Depth:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.depth_var = tk.IntVar(value=2)
        depth_spin = ttk.Spinbox(settings_frame, from_=1, to=10, width=10, textvariable=self.depth_var)
        depth_spin.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # Max pages
        ttk.Label(settings_frame, text="Max Pages:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.pages_var = tk.IntVar(value=50)
        pages_spin = ttk.Spinbox(settings_frame, from_=1, to=1000, width=10, textvariable=self.pages_var)
        pages_spin.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Delay
        ttk.Label(settings_frame, text="Delay (seconds):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.delay_var = tk.DoubleVar(value=1.5)
        delay_spin = ttk.Spinbox(settings_frame, from_=0.5, to=10.0, increment=0.5, width=10, textvariable=self.delay_var)
        delay_spin.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Resume checkbox
        self.resume_var = tk.BooleanVar(value=True)
        resume_check = ttk.Checkbutton(settings_frame, text="Resume previous crawl", variable=self.resume_var)
        resume_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Scraping", command=self.start_scraping)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop Scraping", command=self.stop_scraping, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.open_button = ttk.Button(button_frame, text="Open Output Folder", command=self.open_output_folder)
        self.open_button.pack(side=tk.LEFT, padx=5)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        progress_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to scrape")
        status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        status_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Stats labels
        self.stats_var = tk.StringVar(value="Pages: 0 | Visited: 0 | Failed: 0 | Pending: 0")
        stats_label = ttk.Label(progress_frame, textvariable=self.stats_var)
        stats_label.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # Log output
        log_frame = ttk.LabelFrame(main_frame, text="Log Output", padding="10")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # Log text widget
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear log button
        ttk.Button(log_frame, text="Clear Log", command=self.clear_log).grid(row=1, column=0, pady=5)
    
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_var.set(directory)
    
    def open_output_folder(self):
        """Open output folder in file explorer"""
        output_path = Path(self.output_var.get())
        if output_path.exists():
            if os.name == 'nt':  # Windows
                os.startfile(output_path)
            elif os.name == 'posix':  # macOS/Linux
                os.system(f'open "{output_path}"')
        else:
            messagebox.showwarning("Warning", "Output directory does not exist yet.")
    
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_line)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Clear log output"""
        self.log_text.delete(1.0, tk.END)
    
    def update_progress(self, current, total, status=""):
        """Update progress bar and status"""
        if total > 0:
            progress = (current / total) * 100
            self.progress_var.set(progress)
        
        if status:
            self.status_var.set(status)
        
        self.root.update_idletasks()
    
    def update_stats(self, processed, visited, failed, pending):
        """Update statistics display"""
        stats_text = f"Pages: {processed} | Visited: {visited} | Failed: {failed} | Pending: {pending}"
        self.stats_var.set(stats_text)
        self.root.update_idletasks()
    
    def start_scraping(self):
        """Start the scraping process"""
        if self.is_scraping:
            return
        
        # Validate input
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a website URL")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_var.set(url)
        
        # Create scraper
        self.scraper = WebsiteDocumentationScraper(
            base_url=url,
            output_dir=self.output_var.get(),
            max_depth=self.depth_var.get(),
            delay=self.delay_var.get(),
            max_pages=self.pages_var.get()
        )
        
        # Update UI
        self.is_scraping = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.status_var.set("Starting scrape...")
        
        # Start scraping thread
        self.scraping_thread = threading.Thread(target=self.scrape_worker)
        self.scraping_thread.daemon = True
        self.scraping_thread.start()
        
        self.log_message(f"Started scraping: {url}")
    
    def stop_scraping(self):
        """Stop the scraping process"""
        if not self.is_scraping:
            return
        
        self.is_scraping = False
        self.status_var.set("Stopping...")
        self.log_message("Scraping stopped by user")
        
        # Update UI
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def scrape_worker(self):
        """Worker thread for scraping"""
        try:
            # Load state if resuming
            if self.resume_var.get():
                self.scraper.load_state()
            
            self.scraper.start_time = time.time()
            
            # Custom processing with GUI updates
            while self.scraper.pending_urls and self.scraper.processed_count < self.scraper.max_pages and self.is_scraping:
                url, depth = self.scraper.pending_urls.pop(0)
                
                if url in self.scraper.visited_urls:
                    continue
                
                self.scraper.visited_urls.add(url)
                
                # Update GUI
                self.message_queue.put(('log', f"Processing: {url}"))
                self.message_queue.put(('progress', (self.scraper.processed_count, self.scraper.max_pages, f"Processing: {url}")))
                
                # Process URL
                success = self.scraper.process_url(url, depth)
                
                if not success:
                    self.scraper.failed_urls.add(url)
                
                # Update stats
                self.message_queue.put(('stats', (
                    self.scraper.processed_count,
                    len(self.scraper.visited_urls),
                    len(self.scraper.failed_urls),
                    len(self.scraper.pending_urls)
                )))
                
                # Save state periodically
                if self.scraper.processed_count % 10 == 0:
                    self.scraper.save_state()
                
                # Respectful delay
                time.sleep(self.scraper.delay)
            
            # Final save and index generation
            self.scraper.save_state()
            self.scraper.generate_index()
            
            # Generate summary
            summary = self.scraper.generate_summary()
            
            # Update GUI
            self.message_queue.put(('log', "Scraping completed successfully!"))
            self.message_queue.put(('log', f"Generated {summary['processed_count']} pages in {summary['elapsed_time']:.1f}s"))
            self.message_queue.put(('complete', None))
            
        except Exception as e:
            self.message_queue.put(('error', str(e)))
        finally:
            self.is_scraping = False
    
    def process_messages(self):
        """Process messages from the scraping thread"""
        try:
            while True:
                message_type, data = self.message_queue.get_nowait()
                
                if message_type == 'log':
                    self.log_message(data)
                elif message_type == 'progress':
                    current, total, status = data
                    self.update_progress(current, total, status)
                elif message_type == 'stats':
                    processed, visited, failed, pending = data
                    self.update_stats(processed, visited, failed, pending)
                elif message_type == 'complete':
                    self.start_button.config(state=tk.NORMAL)
                    self.stop_button.config(state=tk.DISABLED)
                    self.status_var.set("Scraping completed!")
                    self.progress_var.set(100)
                elif message_type == 'error':
                    self.log_message(f"Error: {data}")
                    self.start_button.config(state=tk.NORMAL)
                    self.stop_button.config(state=tk.DISABLED)
                    self.status_var.set("Error occurred")
                    messagebox.showerror("Scraping Error", str(data))
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_messages)

def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = ScraperGUI(root)
    
    # Configure for better Mac appearance
    if os.name == 'posix':
        try:
            root.tk.call('tk', 'scaling', 1.5)  # Better scaling on Mac
        except:
            pass
    
    root.mainloop()

if __name__ == "__main__":
    main()
