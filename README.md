# Local LLM Log Processor

A small Docker Compose project that analyzes log files with a local Ollama model. Log content stays on the Compose network and is not sent to a hosted AI API.

This project uses Ollama's `phi3:mini` tag (Phi-3 Mini, Microsoft's compact Phi-3 model). There is no `phi3:nano` Ollama model tag; Mini is the available small Phi-3 variant used here.

## Run

1. Put `.log`, `.txt`, or `.gz` files under `logs/`.
2. Build the processor image, pull Phi-3 Mini, and analyze the files:

   ```bash
   docker compose run --build --rm log-processor
   ```

The first run downloads the Ollama image and model and requires internet access. Model files persist in the `ollama-data` volume. Results are written to `reports/analysis.json` and `reports/analysis.md`.

Stop Ollama while preserving the model:

```bash
docker compose down
```

Remove containers and the downloaded model:

```bash
docker compose down --volumes
```

## Options

Pass one or more input files or directories. Directory scans are recursive and include `.log`, `.txt`, and `.gz` files.

```bash
docker compose run --build --rm log-processor /logs/service.log --output /reports/service-analysis.json --chunk-lines 80
```

The app breaks large files into line-bounded requests and combines their summaries. Change the model by setting `OLLAMA_MODEL` in `docker-compose.yml` to another Ollama model tag.

## Hardware

Phi-3 Mini needs several gigabytes of memory and disk space. CPU inference works but can be slow; Ollama may use supported host acceleration when configured. The Ollama API is only exposed inside the Compose network by default.

## Tests

```bash
python3 -m unittest discover -s tests -v
```