# Docker Setup for MenuCrawler

This guide explains how to run MenuCrawler in a Docker container, especially when using a local AI model.

## Prerequisites

1. Docker and Docker Compose installed
2. A local AI model server running (e.g., Ollama, LM Studio, etc.)

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Start your local AI model server** (e.g., Ollama):
   ```bash
   ollama serve
   ```

2. **Run the crawler**:
   ```bash
   docker-compose up --build
   ```

3. **Check results**:
   ```bash
   # Results will be in ./output/output.json
   cat output/output.json
   ```

### Option 2: Using Docker directly

1. **Build the image**:
   ```bash
   docker build -t menucrawler .
   ```

2. **Run with host networking** (to access localhost):
   ```bash
   docker run --network host \
     -v $(pwd)/input:/app/input:ro \
     -v $(pwd)/output:/app/output \
     -v $(pwd)/prompts:/app/prompts:ro \
     -e OPENAI_API_BASE=http://localhost:1234/v1 \
     menucrawler
   ```

3. **Or run with bridge networking** (using host.docker.internal):
   ```bash
   docker run \
     -v $(pwd)/input:/app/input:ro \
     -v $(pwd)/output:/app/output \
     -v $(pwd)/prompts:/app/prompts:ro \
     -e OPENAI_API_BASE=http://host.docker.internal:1234/v1 \
     menucrawler
   ```

## Configuration

### Environment Variables

You can customize the behavior using environment variables:

- `OPENAI_API_BASE`: URL of your AI model server (default: `http://host.docker.internal:1234/v1`)
- `OPENAI_API_KEY`: API key (default: `sk-noauth` for local models)
- `OPENAI_MODEL`: Model name (default: `gpt-oss-20b`)
- `MAX_CRAWL_DEPTH`: Maximum crawl depth (default: `3`)

### Using a Custom Configuration

1. **Copy the example config**:
   ```bash
   cp config.env.example .env
   ```

2. **Edit the configuration**:
   ```bash
   # Edit .env with your settings
   nano .env
   ```

3. **Run with custom config**:
   ```bash
   docker-compose --env-file .env up
   ```

## Common AI Model Setups

### Ollama

1. **Install and start Ollama**:
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Start the server
   ollama serve
   
   # Pull a model (optional)
   ollama pull llama2
   ```

2. **Configure for Ollama**:
   ```bash
   # Ollama typically runs on port 11434
   export OPENAI_API_BASE=http://localhost:11434/v1
   export OPENAI_MODEL=llama2
   ```

### LM Studio

1. **Start LM Studio** and enable the local server
2. **Configure the connection**:
   ```bash
   # LM Studio typically runs on port 1234
   export OPENAI_API_BASE=http://localhost:1234/v1
   export OPENAI_MODEL=your-model-name
   ```

### OpenAI API

If you want to use OpenAI's API instead of a local model:

```bash
export OPENAI_API_BASE=https://api.openai.com/v1
export OPENAI_API_KEY=your-openai-api-key
export OPENAI_MODEL=gpt-4
```

## Troubleshooting

### "Connection refused" errors

This usually means the container can't reach your local AI model. Try:

1. **Check if your model server is running**:
   ```bash
   curl http://localhost:1234/v1/models
   ```

2. **Use host networking**:
   ```bash
   docker run --network host ...
   ```

3. **Check the port** - make sure you're using the correct port for your model server

### Permission issues

If you get permission errors with mounted volumes:

```bash
# Fix ownership
sudo chown -R $USER:$USER output/
```

### Model not responding

1. **Check model server logs**
2. **Verify the model name** matches what's available on your server
3. **Test the API directly**:
   ```bash
   curl -X POST http://localhost:1234/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"model": "your-model", "messages": [{"role": "user", "content": "Hello"}]}'
   ```

## Development

### Building for development

```bash
# Build without cache
docker-compose build --no-cache

# Run in development mode with live reload
docker-compose -f docker-compose.dev.yml up
```

### Debugging

```bash
# Run with shell access
docker run -it --network host \
  -v $(pwd):/app \
  menucrawler /bin/bash

# Check logs
docker-compose logs -f
```
