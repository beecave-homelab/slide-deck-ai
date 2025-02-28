# Running SlideDeck AI with Docker

This guide explains how to run SlideDeck AI using Docker containers.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/barun-saha/slide-deck-ai.git
   cd slide-deck-ai
   ```

2. Create a `.env` file from the template:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file and add your API keys:
   ```
   HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
   PEXEL_API_KEY=your_pexels_api_key
   RUN_IN_OFFLINE_MODE=False
   ```

4. Build and start the container:
   ```bash
   docker-compose up -d
   ```

5. Access SlideDeck AI in your browser at:
   ```
   http://localhost:8501
   ```

## Using Offline LLMs with Ollama

If you want to use Ollama for offline LLMs:

1. Edit the `.env` file:
   ```
   RUN_IN_OFFLINE_MODE=True
   ```

2. Uncomment the Ollama service in `docker-compose.yml`:
   - Uncomment the `depends_on` and `networks` sections in the `slidedeck-ai` service
   - Uncomment the `ollama` service section
   - Uncomment the `volumes` and `networks` sections at the bottom

3. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

4. Pull the models you want to use in Ollama:
   ```bash
   docker exec -it ollama ollama pull mistral:v0.2
   docker exec -it ollama ollama pull mistral-nemo:latest
   ```

5. Access SlideDeck AI and enter the Ollama model name in the text field.

## Environment Variables

- `HUGGINGFACEHUB_API_TOKEN`: Your Hugging Face API token (optional but recommended)
- `PEXEL_API_KEY`: Your Pexels API key for image search
- `RUN_IN_OFFLINE_MODE`: Set to `True` to use Ollama, `False` to use online LLMs

## Stopping the Container

To stop the container:
```bash
docker-compose down
```

## Troubleshooting

- **Container fails to start**: Check the logs with `docker-compose logs`
- **API connection issues**: Verify your API keys in the `.env` file
- **Ollama model not found**: Make sure you've pulled the model with `docker exec -it ollama ollama pull model_name`

## Data Persistence

The container mounts the current directory to `/app` inside the container, so any changes made to the files will persist on your host machine.

For Hugging Face models, the cache is mounted to preserve downloaded models between container restarts. 