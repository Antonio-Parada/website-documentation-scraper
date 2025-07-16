"""
Website Documentation Scraper Backend Server
============================================

Flask-based backend server providing API endpoints for:
- Starting/stopping scraping jobs
- Monitoring progress
- Managing scraper state
- Serving scraped documents
"""

import os
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import uuid

# Import our scraper
from website_doc_scraper import WebsiteDocumentationScraper

# Ensure API key is set
if "GOOGLE_APIKEY" not in os.environ:
    raise ValueError("Please set the GOOGLE_APIKEY environment variable")

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Global state
active_scrapers = {}  # job_id -> scraper_instance
scraper_threads = {}  # job_id -> thread
scraper_status = {}   # job_id -> status_info

def create_scraper_job(base_url, output_dir="docs", max_depth=3, delay=2.0, max_pages=100):
    """Create a new scraping job"""
    job_id = str(uuid.uuid4())
    
    scraper = WebsiteDocumentationScraper(
        base_url=base_url,
        output_dir=output_dir,
        max_depth=max_depth,
        delay=delay,
        max_pages=max_pages
    )
    
    active_scrapers[job_id] = scraper
    scraper_status[job_id] = {
        "status": "created",
        "base_url": base_url,
        "output_dir": output_dir,
        "max_depth": max_depth,
        "delay": delay,
        "max_pages": max_pages,
        "created_at": datetime.now().isoformat(),
        "progress": 0,
        "processed_count": 0,
        "visited_count": 0,
        "failed_count": 0,
        "pending_count": 0
    }
    
    return job_id

def scraper_worker(job_id):
    """Worker function for scraping in a separate thread"""
    try:
        scraper = active_scrapers[job_id]
        scraper_status[job_id]["status"] = "running"
        scraper_status[job_id]["started_at"] = datetime.now().isoformat()
        
        # Load state if resuming
        scraper.load_state()
        scraper.start_time = time.time()
        
        # Main scraping loop
        while scraper.pending_urls and scraper.processed_count < scraper.max_pages:
            if scraper_status[job_id]["status"] == "stopping":
                break
                
            url, depth = scraper.pending_urls.pop(0)
            
            if url in scraper.visited_urls:
                continue
            
            scraper.visited_urls.add(url)
            
            # Process URL
            success = scraper.process_url(url, depth)
            
            if not success:
                scraper.failed_urls.add(url)
            
            # Update status
            scraper_status[job_id].update({
                "processed_count": scraper.processed_count,
                "visited_count": len(scraper.visited_urls),
                "failed_count": len(scraper.failed_urls),
                "pending_count": len(scraper.pending_urls),
                "progress": (scraper.processed_count / scraper.max_pages) * 100,
                "current_url": url,
                "last_updated": datetime.now().isoformat()
            })
            
            # Save state periodically
            if scraper.processed_count % 10 == 0:
                scraper.save_state()
            
            # Respectful delay
            time.sleep(scraper.delay)
        
        # Final save and index generation
        scraper.save_state()
        scraper.generate_index()
        
        # Update final status
        summary = scraper.generate_summary()
        scraper_status[job_id].update({
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "summary": summary
        })
        
    except Exception as e:
        scraper_status[job_id].update({
            "status": "error",
            "error": str(e),
            "error_at": datetime.now().isoformat()
        })
    
    finally:
        # Clean up thread reference
        if job_id in scraper_threads:
            del scraper_threads[job_id]

@app.route('/api/jobs', methods=['POST'])
def create_job():
    """Create a new scraping job"""
    data = request.get_json()
    
    if not data or 'base_url' not in data:
        return jsonify({"error": "base_url is required"}), 400
    
    job_id = create_scraper_job(
        base_url=data['base_url'],
        output_dir=data.get('output_dir', 'docs'),
        max_depth=data.get('max_depth', 3),
        delay=data.get('delay', 2.0),
        max_pages=data.get('max_pages', 100)
    )
    
    return jsonify({"job_id": job_id, "status": "created"}), 201

@app.route('/api/jobs/<job_id>/start', methods=['POST'])
def start_job(job_id):
    """Start a scraping job"""
    if job_id not in active_scrapers:
        return jsonify({"error": "Job not found"}), 404
    
    if scraper_status[job_id]["status"] == "running":
        return jsonify({"error": "Job already running"}), 400
    
    # Start scraping thread
    thread = threading.Thread(target=scraper_worker, args=(job_id,))
    thread.daemon = True
    thread.start()
    
    scraper_threads[job_id] = thread
    
    return jsonify({"status": "started"})

@app.route('/api/jobs/<job_id>/stop', methods=['POST'])
def stop_job(job_id):
    """Stop a scraping job"""
    if job_id not in active_scrapers:
        return jsonify({"error": "Job not found"}), 404
    
    scraper_status[job_id]["status"] = "stopping"
    
    return jsonify({"status": "stopping"})

@app.route('/api/jobs/<job_id>/status', methods=['GET'])
def get_job_status(job_id):
    """Get status of a scraping job"""
    if job_id not in active_scrapers:
        return jsonify({"error": "Job not found"}), 404
    
    return jsonify(scraper_status[job_id])

@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List all scraping jobs"""
    return jsonify({
        "jobs": [
            {"job_id": job_id, **status}
            for job_id, status in scraper_status.items()
        ]
    })

@app.route('/api/jobs/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    """Delete a scraping job"""
    if job_id not in active_scrapers:
        return jsonify({"error": "Job not found"}), 404
    
    # Stop if running
    if scraper_status[job_id]["status"] == "running":
        scraper_status[job_id]["status"] = "stopping"
        time.sleep(1)  # Give it time to stop
    
    # Clean up
    del active_scrapers[job_id]
    del scraper_status[job_id]
    
    if job_id in scraper_threads:
        del scraper_threads[job_id]
    
    return jsonify({"status": "deleted"})

@app.route('/api/jobs/<job_id>/files', methods=['GET'])
def list_job_files(job_id):
    """List files generated by a scraping job"""
    if job_id not in active_scrapers:
        return jsonify({"error": "Job not found"}), 404
    
    scraper = active_scrapers[job_id]
    output_dir = Path(scraper.output_dir)
    
    if not output_dir.exists():
        return jsonify({"files": []})
    
    files = []
    for file_path in output_dir.glob("*.md"):
        files.append({
            "filename": file_path.name,
            "size": file_path.stat().st_size,
            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        })
    
    return jsonify({"files": files})

@app.route('/api/jobs/<job_id>/files/<filename>', methods=['GET'])
def get_job_file(job_id, filename):
    """Get a specific file from a scraping job"""
    if job_id not in active_scrapers:
        return jsonify({"error": "Job not found"}), 404
    
    scraper = active_scrapers[job_id]
    file_path = Path(scraper.output_dir) / filename
    
    if not file_path.exists():
        return jsonify({"error": "File not found"}), 404
    
    return send_file(file_path, as_attachment=True)

@app.route('/api/jobs/<job_id>/download', methods=['GET'])
def download_job_archive(job_id):
    """Download all files from a scraping job as a zip archive"""
    if job_id not in active_scrapers:
        return jsonify({"error": "Job not found"}), 404
    
    scraper = active_scrapers[job_id]
    output_dir = Path(scraper.output_dir)
    
    if not output_dir.exists():
        return jsonify({"error": "No files to download"}), 404
    
    # Create zip archive
    import zipfile
    import tempfile
    
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
        with zipfile.ZipFile(tmp.name, 'w') as zf:
            for file_path in output_dir.glob("*.md"):
                zf.write(file_path, file_path.name)
        
        return send_file(tmp.name, as_attachment=True, 
                        download_name=f"scraped_docs_{job_id}.zip")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_jobs": len(active_scrapers),
        "running_jobs": sum(1 for status in scraper_status.values() 
                          if status["status"] == "running")
    })

@app.route('/')
def index():
    """Simple web interface"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Website Documentation Scraper</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .job { border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; }
            .status { padding: 5px 10px; border-radius: 3px; color: white; }
            .running { background-color: #28a745; }
            .completed { background-color: #17a2b8; }
            .error { background-color: #dc3545; }
            .created { background-color: #6c757d; }
            .form-group { margin: 10px 0; }
            label { display: block; margin-bottom: 5px; }
            input, select { width: 100%; padding: 8px; margin-bottom: 10px; }
            button { padding: 10px 20px; background-color: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer; }
            button:hover { background-color: #0056b3; }
            .progress { width: 100%; height: 20px; background-color: #f0f0f0; border-radius: 10px; overflow: hidden; }
            .progress-bar { height: 100%; background-color: #007bff; transition: width 0.3s ease; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Website Documentation Scraper</h1>
            
            <div class="job">
                <h3>Create New Scraping Job</h3>
                <form id="jobForm">
                    <div class="form-group">
                        <label>Website URL:</label>
                        <input type="url" id="baseUrl" value="https://scrapegraph-ai.readthedocs.io" required>
                    </div>
                    <div class="form-group">
                        <label>Output Directory:</label>
                        <input type="text" id="outputDir" value="docs">
                    </div>
                    <div class="form-group">
                        <label>Max Depth:</label>
                        <input type="number" id="maxDepth" value="2" min="1" max="10">
                    </div>
                    <div class="form-group">
                        <label>Max Pages:</label>
                        <input type="number" id="maxPages" value="50" min="1" max="1000">
                    </div>
                    <div class="form-group">
                        <label>Delay (seconds):</label>
                        <input type="number" id="delay" value="1.5" min="0.5" max="10" step="0.5">
                    </div>
                    <button type="submit">Create Job</button>
                </form>
            </div>
            
            <div id="jobs">
                <h3>Active Jobs</h3>
                <div id="jobsList"></div>
            </div>
        </div>
        
        <script>
            // Auto-refresh jobs every 5 seconds
            setInterval(loadJobs, 5000);
            loadJobs();
            
            document.getElementById('jobForm').addEventListener('submit', function(e) {
                e.preventDefault();
                createJob();
            });
            
            function createJob() {
                const data = {
                    base_url: document.getElementById('baseUrl').value,
                    output_dir: document.getElementById('outputDir').value,
                    max_depth: parseInt(document.getElementById('maxDepth').value),
                    max_pages: parseInt(document.getElementById('maxPages').value),
                    delay: parseFloat(document.getElementById('delay').value)
                };
                
                fetch('/api/jobs', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.job_id) {
                        startJob(data.job_id);
                    }
                });
            }
            
            function loadJobs() {
                fetch('/api/jobs')
                .then(response => response.json())
                .then(data => {
                    const jobsList = document.getElementById('jobsList');
                    jobsList.innerHTML = '';
                    
                    data.jobs.forEach(job => {
                        const jobDiv = document.createElement('div');
                        jobDiv.className = 'job';
                        jobDiv.innerHTML = `
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong>${job.base_url}</strong>
                                    <span class="status ${job.status}">${job.status}</span>
                                </div>
                                <div>
                                    <button onclick="startJob('${job.job_id}')" ${job.status === 'running' ? 'disabled' : ''}>Start</button>
                                    <button onclick="stopJob('${job.job_id}')" ${job.status !== 'running' ? 'disabled' : ''}>Stop</button>
                                    <button onclick="deleteJob('${job.job_id}')">Delete</button>
                                </div>
                            </div>
                            <div>
                                <div class="progress">
                                    <div class="progress-bar" style="width: ${job.progress || 0}%"></div>
                                </div>
                                <small>
                                    Pages: ${job.processed_count || 0} | 
                                    Visited: ${job.visited_count || 0} | 
                                    Failed: ${job.failed_count || 0} | 
                                    Pending: ${job.pending_count || 0}
                                </small>
                            </div>
                        `;
                        jobsList.appendChild(jobDiv);
                    });
                });
            }
            
            function startJob(jobId) {
                fetch(`/api/jobs/${jobId}/start`, {method: 'POST'})
                .then(() => loadJobs());
            }
            
            function stopJob(jobId) {
                fetch(`/api/jobs/${jobId}/stop`, {method: 'POST'})
                .then(() => loadJobs());
            }
            
            function deleteJob(jobId) {
                if (confirm('Are you sure you want to delete this job?')) {
                    fetch(`/api/jobs/${jobId}`, {method: 'DELETE'})
                    .then(() => loadJobs());
                }
            }
        </script>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    print("🚀 Starting Website Documentation Scraper Backend Server")
    print("=" * 60)
    print("📡 Server running on http://localhost:5000")
    print("📊 Web interface: http://localhost:5000")
    print("🔧 API documentation: http://localhost:5000/api/health")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
