# 🤖 MiMo Form Agent

Simple AI agent that uses **Xiaomi MiMo V2.5 Pro** to auto-fill and submit web forms intelligently.

## What it does

- Reads form fields from any webpage using Playwright
- Uses MiMo reasoning to generate contextual form responses
- Auto-fills and submits forms with human-like behavior
- Handles CAPTCHAs via external solver APIs

## Quick Start

```bash
pip install -r requirements.txt
playwright install chromium
python agent.py --url "https://example.com/form" --config config.json
```

## Config

```json
{
  "mimo_api_key": "your-key",
  "model": "mimo-v2.5-pro",
  "headless": true,
  "delay_ms": 500
}
```

## How it works

```
1. Playwright loads target page
2. Agent extracts form fields (labels, types, placeholders)
3. MiMo generates appropriate responses based on context
4. Agent fills form with realistic typing delays
5. Submits and verifies success
```

## License

MIT
