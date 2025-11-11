# SocioLens ASGI Server

A high-performance, GPU-enabled API server built on **FastAPI** for social media sentiment analysis and related tasks.  
This project leverages the **Astral UV** package manager for fast, reproducible Python environments.

---

## Features

- ASGI-based architecture using **FastAPI**
- Multi-GPU worker pool for model inference
- Modular routing with automatic discovery
- Local model caching for offline use
- Health monitoring and internal dashboards

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
|── app/
│   ├── routes/             # FastAPI routes
│   ├── utils/              # Config, device, worker utilities
│   └── templates/          # HTML templates (health dashboard, etc.)
├── main.py                 # Entry point
├── pyproject.toml          # Dependencies and UV config
└── README.md
```

---

## Health Dashboard

Visit:
```
http://127.0.0.1:8000/internal/health
```

to view the real-time service health dashboard with uptime, worker status, and model information.

---

## Contributors

| Name | GitHub | Email |
|------|---------|-------|
| **Ananth Sankar** | [itsAnanth](https://github.com/itsAnanth) | ananthsankar2003@gmail.com |
| **Gautham Krishnal J** | [Knightrider16](https://github.com/Knightrider16) | gauthamkrishnalj@gmail.com |
| **Govind V Kartha** | [Govind-v-kartha](https://github.com/Govind-v-kartha) | knvgovind@gmail.com |
| **Sreedev R** | [Sdvrx](https://github.com/Sdvrx) | sreedevr44@gmail.com |

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

