# CreatorIQ

CreatorIQ is a channel analytics and strategy application for YouTube creators. It combines recent-video statistics with a structured Gemini-generated strategy report, helping independent creators and small creator teams review performance and turn a sample of channel data into practical ideas.

The application separates measured analytics from generated recommendations and marks whether channel data came from the YouTube API or a synthetic demo source.

## Key features

- **YouTube channel analytics:** Retrieves channel metadata and up to 15 recent uploads, then calculates available view, like, comment, and engagement metrics.
- **Channel dashboard:** Summarizes retrieved recent-video metrics, displays a video views chart, and links to the sampled YouTube videos.
- **AI strategy report:** Sends a validated analytics snapshot to Gemini and renders a structured report with an assessment, observed patterns, content gaps, hypotheses, recommendations, and five content ideas.
- **Content intelligence view:** Displays video performance comparisons and additional guidance. Some narrative guidance on this page is static prototype content, not generated from the current channel.
- **Memory Center and chat API:** Includes Memory Center and chat routes backed by a prototype local-memory service. These are not equivalent to a verified persistent Hindsight Cloud integration; see [Current limitations](#current-limitations).
- **Demo mode:** Provides synthetic analytics when the backend YouTube API key is not configured, and the frontend also has a local synthetic fallback if its analytics request fails. Demo provenance is represented as `demo`.
- **Channel session state:** Keeps the selected channel URL and analytics response in browser `localStorage` so the current dashboard state survives a page reload.

## Application screenshots

No application screenshots are currently included in the repository. Add captures in these locations when available:

> **Landing page and channel selection:** Screenshot placeholder — add a current application capture.

> **Channel analytics dashboard:** Screenshot placeholder — add a current application capture.

> **AI strategy report:** Screenshot placeholder — add a current application capture.

> **Memory Center:** Screenshot placeholder — add a current application capture.

## Technology stack

| Area | Technologies in the repository |
|---|---|
| Frontend | React 18, TypeScript, Vite 6, Tailwind CSS 3, React Router, Axios, Recharts, Lucide |
| Backend | Python, FastAPI, Pydantic 2, Uvicorn |
| AI service | Google Gemini through the `google-genai` Python SDK |
| External data APIs | YouTube Data API v3; Gemini API |
| Storage and caching | Browser `localStorage`; process-local Python dictionaries for the analytics snapshot cache and prototype memory service |
| Developer tooling | npm, TypeScript compiler, Python `unittest`, Git |

There is no configured SQL database or durable application datastore.

## System architecture

```mermaid
flowchart LR
    User[Creator]
    subgraph Browser["Browser"]
        UI["React and TypeScript UI"]
        LocalStorage["localStorage<br/>selected channel and analytics"]
    end

    subgraph Backend["FastAPI backend"]
        Routes["YouTube, Analytics,<br/>Insights, Chat and Memory routes"]
        Snapshot["Process-local analytics snapshot cache<br/>300-second TTL, up to 128 entries"]
        YouTubeService["YouTube data service"]
        Analytics["Analytics calculations"]
        Insights["Structured insights service"]
        MemoryService["Prototype Hindsight service<br/>process-local memory and mock defaults"]
    end

    YouTubeAPI["YouTube Data API v3"]
    Gemini["Gemini API<br/>configured model"]
    Hindsight["Optional Hindsight endpoint<br/>best-effort, unverified sync"]

    User --> UI
    UI <--> LocalStorage
    UI -->|"HTTP JSON requests"| Routes
    Routes --> Snapshot
    Snapshot --> YouTubeService
    YouTubeService -->|"API key configured"| YouTubeAPI
    YouTubeService -->|"No API key"| Demo["Synthetic backend demo data"]
    Snapshot --> Analytics
    Analytics -->|"Analytics snapshot"| Routes
    Routes --> Insights
    Insights --> Gemini
    Gemini -->|"Structured strategy"| Insights
    Routes --> MemoryService
    MemoryService -.->|"Best-effort request when configured;<br/>not a verified working integration"| Hindsight
```

For analytics and insights requests, the backend reuses a process-local snapshot when possible. The insights route passes that analytics snapshot to Gemini rather than independently fetching YouTube data. A successful response retains the snapshot's `data_source`.

## Project structure

```text
CreatorIQ/
├── backend/
│   ├── config.py                   # Environment-variable loading
│   ├── main.py                     # FastAPI app, CORS and route registration
│   ├── routes/                     # YouTube, analytics, insights, chat, memory
│   ├── schemas/                    # Pydantic request and response models
│   ├── services/                   # YouTube, analytics, Gemini and memory logic
│   └── .env.example                # Backend environment-variable template
├── frontend/
│   ├── src/
│   │   ├── components/             # Shared header, layout, sidebar and metric card
│   │   ├── context/                # Selected channel state
│   │   ├── pages/                  # Dashboard, intelligence, strategist, memory, settings
│   │   ├── services/api.ts         # Axios client and API methods
│   │   └── types/api.ts            # TypeScript API response types
│   ├── package.json                # Frontend scripts and dependencies
│   └── vite.config.ts              # Dev server and backend API proxy
├── tests/                          # Python service and route tests
├── requirements.txt                # Python dependencies
└── README.md
```

## Prerequisites

- **Python 3.10 or later.** The backend uses Python 3.10 type syntax; `requirements.txt` does not pin a Python minor version.
- **Node.js 18 or later** and npm, for the Vite 6 frontend.
- **Git**, to clone and manage the repository.
- A **YouTube Data API key** for live YouTube data.
- A **Gemini API key** to generate strategy reports.

The backend can start without the YouTube and Gemini keys, but those services then use demo behavior or return a configuration error as described below.

## Installation and setup (Windows PowerShell)

Run commands from the repository root unless noted.

### 1. Create and activate a backend virtual environment

```powershell
Set-Location C:\path\to\CreatorIQ
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell does not allow activation scripts in your environment, use the virtual environment's Python directly, for example:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Configure backend environment variables

Create `backend\.env` from the checked-in template only when the file does not already exist:

```powershell
if (-not (Test-Path backend\.env)) {
    Copy-Item backend\.env.example backend\.env
}
notepad backend\.env
```

Edit the local file and set the credentials you have. Do not commit `backend\.env`; it is ignored by Git.

### 3. Install frontend dependencies

In a second PowerShell terminal:

```powershell
Set-Location C:\path\to\CreatorIQ\frontend
npm ci
```

## Environment variables

The backend template is [`backend/.env.example`](backend/.env.example). `backend/config.py` loads `backend/.env`. No real credentials are documented here.

| Variable | Required? | Purpose and behavior |
|---|---|---|
| `YOUTUBE_API_KEY` | Optional for demo; required for live YouTube data | Used by the YouTube Data API v3 service. If missing or left as the template placeholder, the backend returns clearly tagged synthetic demo data. |
| `GEMINI_API_KEY` | Optional to start; required for AI strategy generation | Authenticates Gemini requests. If absent, the insights service returns a configuration error rather than a generated strategy. |
| `GEMINI_MODEL` | Optional | Selects the Gemini model. The backend configuration defaults to `gemini-3.5-flash-lite` when this variable is unset. |
| `HINDSIGHT_API_KEY` | Optional; not present in `backend/.env.example` | The prototype service combines it with the `Bearer` scheme for HTTP authentication on its best-effort memory POST. The remote integration is not verified or functional as implemented; see [Current limitations](#current-limitations). |
| `HINDSIGHT_BASE_URL` | Optional; not present in `backend/.env.example` | Base URL used for the prototype's external memory POST. The code default is `https://hindsight.vectorize.io`; the configured base URL and request endpoint have not been verified against a working Hindsight API. |
| `VITE_API_BASE_URL` | Optional; not present in the backend template | Read by the frontend Axios client. When empty, the Vite development server proxies `/api` requests to `http://localhost:8000`. Set it in the frontend's Vite environment when using a different backend host. |

The checked-in backend template currently contains only `YOUTUBE_API_KEY`, `GEMINI_API_KEY`, and `GEMINI_MODEL`. `HINDSIGHT_API_KEY` and `HINDSIGHT_BASE_URL` are read by backend configuration but are not listed in that template. `VITE_API_BASE_URL` is a frontend Vite setting and is also not listed in the backend template.

## Running the application

### Backend

From the repository root, with the virtual environment active:

```powershell
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

- API base URL: <http://localhost:8000>
- Interactive Swagger documentation: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>

### Frontend

In a second terminal:

```powershell
Set-Location C:\path\to\CreatorIQ\frontend
npm run dev
```

Vite serves the application at <http://localhost:5173> and proxies `/api` requests to the local backend. The backend CORS configuration also allows `http://localhost:3000`.

## API overview

All application endpoints are registered by `backend/main.py`. JSON request and response contracts are defined in `backend/schemas/`.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Returns a basic backend health response. |
| `POST` | `/api/youtube/channel` | Retrieves channel metadata and recent videos. |
| `POST` | `/api/analytics/channel` | Returns calculated recent-video analytics and `data_source`. Uses the shared snapshot cache. |
| `POST` | `/api/insights/channel` | Reuses the analytics snapshot and requests a structured Gemini strategy report. Requires Gemini configuration to generate a report. |
| `POST` | `/api/chat` | Prototype keyword-routed strategist reply and memory interaction; this is not the Gemini strategy endpoint. |
| `GET` | `/api/memory/{channel_id}` | Returns memory clusters from the prototype memory service. |
| `POST` | `/api/memory` | Adds a memory item to the process-local service and attempts optional external synchronization. |

The channel endpoints accept a JSON body shaped as `{"channel_url": "https://www.youtube.com/@handle"}`. Use `/docs` for the live OpenAPI schema and validation details.

## Testing and build checks

Run the backend tests from the repository root:

```powershell
python -m unittest discover -s tests
```

The frontend TypeScript check and production build are combined in the configured script:

```powershell
Set-Location frontend
npm run build
```

At the time this README was prepared, the backend test command completed successfully with **44 tests passing**. The frontend package does not define a lint script.

## Current limitations

- **Demo data is not YouTube data.** The backend returns synthetic records when its YouTube API key is missing or is the template placeholder. Separately, the frontend analytics client catches analytics request failures and creates local synthetic demo analytics. The responses are tagged `demo`; do not treat these metrics as real channel results.
- **Live API failures are not equivalent to demo success.** When a non-placeholder YouTube key is configured, backend YouTube API errors are returned as errors. The frontend's separate analytics fallback can still display local demo data if its analytics request fails.
- **Analytics describe a recent sample.** The backend retrieves up to 15 recent videos. Derived averages and engagement rates represent available data in that sample, not the channel's lifetime performance, audience retention, or audience demographics.
- **Gemini output is generated, not guaranteed.** Strategy generation requires a working Gemini configuration and provider response. The backend validates structured output, recommendation/idea counts, and evidence references; unsupported video references are removed rather than matched approximately.
- **The analytics snapshot cache is process-local.** It has a five-minute TTL and a 128-entry capacity. It is not durable, shared between workers, or a database.
- **Memory is a prototype, not durable vector memory.** The service stores items in a Python in-memory dictionary, provides hardcoded default memories when no items exist, and the chat route creates keyword-based replies. Process restarts clear locally stored memories.
- **Hindsight Cloud integration is not functional as implemented.** The service uses `HINDSIGHT_API_KEY` as the credential with the HTTP `Bearer` scheme, then attempts a POST using the configured base URL plus `/api/v1/memories`, with a `channel_id`/`title`/`content`/`category` payload. The current base URL, endpoint, and request payload do not match a verified Hindsight API contract; the request also lacks a bank ID. Memory recall reads only the local in-process dictionary and never calls a remote recall endpoint. External request errors are swallowed, so a failed sync is not reported to callers. Configuring the Hindsight variables alone therefore does not enable working Hindsight Cloud storage or retrieval.
- **Some dashboard guidance is static.** The dashboard and Content Intelligence page include narrative claims and example guidance that are not calculated from the selected channel's data or produced by Gemini. The AI Strategist report is the separate backend-generated report.
- **No authentication or user/account persistence is implemented.** The app is designed as a local prototype; do not expose it publicly with private API credentials without adding appropriate access controls.

## Future improvements

- Complete and test Hindsight integration against the provider's documented API and authentication requirements, or remove unsupported integration claims from the UI.
- Replace prototype chat behavior and canned memory defaults with explicit, validated AI and memory workflows.
- Make analytics failures visibly distinct from local demo fallback throughout the UI.
- Replace static dashboard guidance with clearly sourced metrics or generated recommendations.
- Add durable, shared storage and a distributed cache if multi-process deployment is required.
- Add authentication, rate limiting, structured operational logging, and deployment-specific CORS configuration before public hosting.
- Add frontend interaction tests and automated linting to complement the existing backend tests and production build.

## Contributing

Contributions should preserve the explicit distinction between YouTube API data and demo data. For behavior changes, update the relevant backend tests or frontend types and run the test/build commands above. Keep credentials in local environment files and never include them in commits.

## License

No license has been specified in this repository. All rights remain with their respective owners; contact the project maintainers before reusing or distributing the code.
