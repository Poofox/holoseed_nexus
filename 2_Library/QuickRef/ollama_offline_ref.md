# Ollama Offline Quick Reference
*Gathered 2026-01-30 for Rudi's machine + Gerry's phone*

## Modelfile Parameters

| Parameter | What it does | Default |
|-----------|--------------|---------|
| `temperature` | Creativity (higher = more creative) | 0.8 |
| `num_ctx` | Context window size (tokens) | 2048 |
| `num_predict` | Max tokens to generate | -1 (infinite) |
| `repeat_penalty` | Penalize repetition | 1.1 |
| `repeat_last_n` | How far back to check for repetition | 64 |
| `top_k` | Diversity control (higher = more varied) | 40 |
| `top_p` | Nucleus sampling threshold | 0.9 |
| `min_p` | Minimum probability filter | 0.0 |
| `seed` | Reproducibility (same seed = same output) | 0 |
| `stop` | Stop sequences | — |

## Context Window vs RAM

| num_ctx | VRAM/RAM needed |
|---------|-----------------|
| 4096 | ~4GB |
| 8192 | ~6GB |
| 16384 | ~8GB |
| 32768 | ~16GB |

## Small Models for Local Use

| Model | Size | Good for |
|-------|------|----------|
| smollm:135m | Tiny | Testing, minimal devices |
| gemma2:2b | 1.6GB | Phone, laptop, general use |
| phi3.5:3.8b | ~2GB | Good balance |
| qwen2.5:7b | ~4GB | Better reasoning |
| qwen2.5:14b | ~9GB | Best local brain |

## Modelfile Example

```
FROM gemma2:2b

SYSTEM """
You are Wrex. Music production partner for PANDROGYN.
[identity goes here]
"""

PARAMETER temperature 0.7
PARAMETER num_ctx 4096
PARAMETER num_predict 512
```

## Commands

```bash
# Create model from Modelfile
ollama create wrex -f Wrex_rudi.Modelfile

# Run model
ollama run wrex

# List models
ollama list

# Remove model
ollama rm modelname

# Start server (if not running)
ollama serve &
```

---

## Termux + Ollama (Android)

**DO NOT use Play Store Termux** — it's broken. Get from:
- GitHub Releases: https://github.com/termux/termux-app/releases
- F-Droid

### Setup
```bash
termux-setup-storage
pkg update && pkg upgrade -y
pkg install ollama
```

### Run
```bash
ollama serve &        # Start server (keep terminal open)
ollama run gemma2:2b  # Run a model
```

### Requirements
- 2GB+ RAM (4GB+ for 3B models)
- 2-3GB storage per model

### GUI Option
Ollama App: https://github.com/JHubi1/ollama-app
- Set server to `http://localhost:11434`
- Keep Termux running in background

---

## Sources
- https://docs.ollama.com/modelfile
- https://github.com/Anon4You/ollama-in-termux
- https://www.arsturn.com/blog/using-termux-with-ollama
