# SocioLens ASGI Server

A high-performance, GPU-enabled API server built on **FastAPI** for social media sentiment analysis, caption generation, and content scraping.  
This project leverages the **Astral UV** package manager for fast, reproducible Python environments.

---

## ✨ Features

- ⚡ **ASGI-based architecture** using FastAPI for high concurrency
- 🎯 **Sentiment Analysis** with RoBERTa model (Twitter-trained)
- 📸 **Instagram & Twitter Scraping** for posts and captions
- 🤖 **LLM Integration** (Groq) for caption optimization
- 🔥 **Multi-GPU Worker Pool** for parallel model inference
- 📊 **Performance Monitoring** with real-time metrics dashboard
- 🛡️ **Input Validation** for URLs, captions, and text
- 🧹 **Text Cleaning Utilities** for preprocessing
- 🏥 **Health Monitoring** with uptime tracking
- 🔒 **Rate Limiting** to prevent abuse
- 🌐 **CORS Support** for frontend integration

---

## Installation

### 1. Install Astral UV

> **Note:** If you already have `uv` installed, skip this step.

#### Windows (PowerShell, run as Administrator)
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Linux / macOS
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

### 2. Clone the Repository

```bash
git clone https://github.com/Socio-Lens/API-server.git
cd API-server
```

---

### 3. Activate the Virtual Environment

> UV automatically manages environments in `.venv/`

#### Windows
```bash
.venv\Scripts\activate
```

#### Linux / macOS
```bash
source .venv/bin/activate
```

---

### 4. Install Dependencies

Sync dependencies from the `pyproject.toml` file:

```bash
uv sync
```

---

## Running the Development Server

Start the ASGI server in debug mode:

```bash
uv run -m main --debug
```

Or run normally:

```bash
uv run -m main
```

Once started, open [http://127.0.0.1:8000](http://127.0.0.1:8000) to view the API status.

---

## 🧭 Directory Structure

```
API-server/
├── main.py                      # Entry point and server configuration
├── pyproject.toml               # Dependencies and project metadata
├── uv.lock                      # Locked dependency versions
├── .env                         # Environment variables (API keys, secrets)
├── Dockerfile                   # Container configuration
├── compose.yml                  # Docker Compose setup
│
├── routes/                      # API route handlers
│   ├── service.py               # Main service endpoints (sentiment, captions)
│   ├── internal.py              # Internal endpoints (health checks)
│   └── metrics.py               # Performance metrics endpoints
│
├── modules/                     # Core business logic modules
│   ├── LLM/
│   │   └── Groq.py              # Groq LLM client for caption optimization
│   └── scrapper/
│       ├── BaseScrapper.py      # Base scraper interface
│       ├── InstaScrapper.py     # Instagram post scraper
│       └── TwitterScrapper.py   # Twitter/X post scraper
│
├── utils/                       # Utility modules
│   ├── config.py                # Configuration management
│   ├── device.py                # GPU/CPU device detection
│   ├── worker.py                # Multi-GPU worker pool
│   ├── router.py                # Automatic route registration
│   ├── functions.py             # Helper functions (humanize_time, etc.)
│   ├── healthChecker.py         # Health monitoring system
│   ├── metrics.py               # Response time tracking middleware
│   ├── validations.py           # Input validation (URLs, captions, text)
│   └── text_cleaning.py         # Text preprocessing utilities
│
├── templates/                   # Jinja2 HTML templates
│   ├── health.html              # Health dashboard
│   └── metrics.html             # Performance metrics dashboard
│
├── scripts/                     # Utility scripts
│   ├── test_caption_validation.py
│   └── test_url_validation.py
│
├── models/                      # Pre-downloaded ML models
│   └── cardiffnlp_twitter-roberta-base-sentiment-latest/
│
├── assets/                      # Static assets
├── frontend/                    # Frontend components (if any)
└── secret/                      # Secret keys and credentials
```

---

---

## 🚀 API Endpoints

### Service Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/service/sentiment/base` | Classify sentiment of text (positive/negative/neutral) |
| `POST` | `/service/caption/instagram` | Fetch caption from Instagram post URL |
| `POST` | `/service/caption/optimize` | Optimize caption using LLM based on sentiment |

### Monitoring Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/internal/health` | Health dashboard with service status |
| `GET` | `/metrics/dashboard` | Performance metrics dashboard |
| `GET` | `/metrics/stats` | JSON response time statistics |
| `GET` | `/metrics/timeseries?endpoint=...` | Time-series data for specific endpoint |
| `POST` | `/metrics/clear` | Clear metrics data |

### Documentation

| Method | Endpoint | Description |
|--------|----------|-------------|
---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# API Keys
GROQ_API_KEY=your_groq_api_key_here

# Server Configuration
HOST=127.0.0.1
PORT=8000

# Instagram Scraper Credentials (if needed)
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
```

### Command Line Arguments

```bash
# Run with debug mode
python main.py --debug

# Specify number of GPUs
python main.py -n 2

# Custom host and port
python main.py --host 0.0.0.0 --port 8080
```

---

## 🐳 Docker Deployment

Build and run with Docker:

```bash
# Build image
docker build -t sociolens-api .

# Run container
docker run -p 8000:8000 --gpus all sociolens-api
```

Or use Docker Compose:

```bash
docker-compose up -d
```

---

## 📝 Example Usage

### Sentiment Analysis

```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/service/sentiment/base",
    json={"text": "This product is amazing! Best purchase ever!"}
)

print(response.json())
# {
#   "predicted_label": "positive",
#   "confidence": 0.9876,
#   "all_scores": {
#     "positive": 0.9876,
#     "neutral": 0.0098,
#     "negative": 0.0026
#   }
# }
```

### Instagram Caption Extraction

```python
response = requests.post(
    "http://127.0.0.1:8000/service/caption/instagram",
    json={"url": "https://www.instagram.com/p/ABC123xyz/"}
)

print(response.json())
# {"caption": "Beautiful sunset at the beach! 🌅"}
```

### Caption Optimization

```python
response = requests.post(
    "http://127.0.0.1:8000/service/caption/optimize",
    json={
        "sentiment": "positive",
        "caption": "Nice product"
    }
)

print(response.json())
# {"caption": "Absolutely amazing product! Exceeded all expectations! ⭐"}
```

---

## 🧪 Testing

Run validation tests:

```bash
# Test caption validation rules
python scripts/test_caption_validation.py

# Test URL validation
python scripts/test_url_validation.py
```

---

## 📦 Key Dependencies

- **FastAPI** - Modern web framework
- **uvicorn** - ASGI server
- **torch** - PyTorch for ML models
- **transformers** - Hugging Face transformers
- **groq** - Groq LLM API client
- **instaloader** - Instagram scraping
- **twikit** - Twitter/X scraping
- **slowapi** - Rate limiting
- **requests** - HTTP client
- **beautifulsoup4** - HTML parsing
- **jinja2** - Template engine

---

## 💡 Tips

**Development with hot reload:**
```bash
uv run main.py --debug
```

**Production mode:**
```bash
uv run main.py
```

**Install new package:**
```bash
uv add package-name
```

**Update dependencies:**
```bash
uv sync
```

**Clear metrics data:**
```bash
curl -X POST http://127.0.0.1:8000/metrics/clear
```

---
http://127.0.0.1:8000/metrics/dashboard
```

Features:
- Auto-refreshes every 10 seconds
- Color-coded performance indicators
- HTTP method badges
- Comprehensive statistics table

---

## 🛡️ Input Validation

The API includes robust validation for:

**Caption/Text Validation:**
- Length limits (1-500 characters)
- Empty/whitespace checks
- Excessive special characters detection
- Spam/repetition detection
- Emoji limits
- Control character filtering
- Word count limits

**URL Validation (Instagram):**
- Valid URL format
- Domain verification (instagram.com)
- Post type validation (/p/, /reel/, /tv/)
- Shortcode presence and format
- Length constraints

Test validation scripts available in `scripts/`:
```bash
python scripts/test_caption_validation.py
python scripts/test_url_validation.py
```

---

## 🧹 Text Cleaning

Text preprocessing utilities in `utils/text_cleaning.py`:

```python
from utils.text_cleaning import clean_text

cleaned = clean_text(
    "Check this out! https://example.com 😊 #amazing @user",
    lower=True,
    remove_urls=True,
    remove_emojis=True,
    remove_mentions=True,
    remove_hashtag_symbol=True,
    normalize_whitespace=True
)
# Output: "check this out amazing"
```

Options:
- HTML tag removal
- URL removal
- @mention removal
- Hashtag cleaning
- Emoji removal
- Punctuation stripping
- Whitespace normalization
- Case preservation for specific words

---

## Health Dashboard

Visit:
```
http://127.0.0.1:8000/internal/health
```

Features:
- Real-time service status
- Worker pool status
- Model loading state
- Uptime history (last 90 checks)
- Background health checker

---

## Contributors

| Name | GitHub | Email |
|------|---------|-------|
| **Ananth Sankar** | [itsAnanth](https://github.com/itsAnanth) | ananthsankar2003@gmail.com |
| **Gautham Krishnal J** | [Knightrider16](https://github.com/Knightrider16) | gauthamkrishnalj@gmail.com |
| **Govind V Kartha** | [Govind-v-kartha](https://github.com/Govind-v-kartha) | knvgovind@gmail.com |
| **Sreedev R** | [Sdvrx](https://github.com/Sdvrx) | sreedevr44@gmail.com |
| **Manav M Nair** | [ManavMNair](https://github.com/ManavMNair) | manavmnair511@gmail.com |
---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 💡 Tip

For faster local development with hot reload:
```bash
uv run -m main --debug
```

For production (no reload):
```bash
uv run -m main
```

---

