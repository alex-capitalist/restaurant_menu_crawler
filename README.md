# Agentic Menu Extractor (Prototype)

## What this is
A prototype agentic menu extraction pipeline:
- uses Playwright to render pages,
- extracts menu candidate links,
- uses a configurable local LLM API to reason and classify menus,
- outputs `output.json`.

The LLM server is expected to be run separately (local or cloud).

## Pre-requisites
- Docker (optional) or Python 3.9+
- If running without Docker: `pip install -r requirements.txt` and `playwright install`
- Local LLM server (recommended options below)

## Configuration
The application can be configured via environment variables:

- `MAX_CRAWL_DEPTH`: Maximum crawling depth (default: 3)
- `NOISE_CONFIDENCE_THRESHOLD`: Threshold for filtering noise links (default: 0.7)
- `MENU_ITEM_CLASSIFIER_CONFIDENCE_THRESHOLD`: Threshold for menu classification (default: 0.7)
- `OPENAI_API_BASE`: LLM API base URL (default: http://localhost:1234/v1)
- `OPENAI_API_KEY`: API key (default: sk-noauth)
- `OPENAI_MODEL`: Model name (default: gpt-oss-20b)

## Recommended local LLM options
1. **Text Generation Inference (TGI) by Hugging Face**
   - Pros: support for many models, REST API.
   - Example quick start:
     - Pull TGI Docker image and run with model: (you must download the model to the server first)
     - See https://github.com/huggingface/text-generation-inference
   - Endpoint expected by this repo: `POST http://localhost:8080/generate` with JSON `{ "prompt": "<text>", "max_new_tokens": 512 }` returning `{ "text": "..." }`.
   - You might need a HF token to download model weights.

2. **Ollama** (https://ollama.com) — if installed locally you can host models and it exposes an HTTP API.

3. **gpt4all / llama.cpp** adapters — you can create a thin HTTP adapter wrapper if needed.

## How to run (using Docker)
1. Build image:
   ```bash
   docker build -t menu-agent .


## TODO - inlcude in the end version of the documentation


# Future
* if no menu found, then do the 2nd fallback to the expensive online model like ChatGPT 4.5 etc. (then the fallback stack would look like `heuristics -> local model -> expensive online model`)

This prototype runs as a standalone Python script. In production, this would be orchestrated with `n8n` or `Airflow` to schedule regular scrapes, handle retries, and scale horizontall

* caching is not implemented

# Notes on Decisions
- Heuristics-first → cheapest; agent only when needed (as requested).
- Depth=2 BFS with menu keyword prioritization to keep crawl bounded.
- SPA link discovery via onclick, data-href, role="link" in addition to `<a href>`
- Language loop avoidance via canonicalizing `/de/`, `/en/`, `?lang=de`, etc.
- No OCR in this test; PDF first-page text only (PyMuPDF).
- Agent doesn’t drive the browser (keeps implementation simple), but it reasons over crawled artifacts to pick and classify menus, which is enough to show the agentic value add in a test assignment.

- Focus was on readability rather than on performance. Premature optimization is the root of the evil, and I'd start optimizing it once it is a part of a big ecosystem.

# How to run 
# Requirements
* LLM Server (a.k.a developer's PC) has a GPU with minimum 8Gb of VRAM (ideally 16Gb), and minimum 16Gb RAM on Windows. In theory, Mac with 24Gb RAM should be sufficient too.

# Pre-requisite: Get a local chat gpt server running.
The fastest way will be:
- install LM Studio (from https://lmstudio.ai/)
- open the LM Studio and install gpt-oss-20b model (`OpenAI's gpt-oss 20B` MXFP4), then pick it on the menu
- (left hand side menu) click on `Developer`, and then click on `Status: ` to **run** the server.

# Run locally

1) (one time only) Set up virtual python environment. Execute the commands in the root folder of the project:
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install --with-deps
```

2) command line:
Execute the commands in the root folder of the project:
```
.venv\Scripts\activate
python -m src.main
```

or 

command with line parameters

```
python -m src.main --input input\restaurants.json --types input\menutypes.json --formats input\menuformat.json --out output\output.json
```

# (optionally) Run in a Docker container

```
docker build -t menu-agent .
docker run --rm --net=host --env-file .env -v $PWD:/app menu-agent
```