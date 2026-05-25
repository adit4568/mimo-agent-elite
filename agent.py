#!/usr/bin/env python3
"""
MiMo Form Agent — AI-powered form filler using Xiaomi MiMo V2.5 Pro
"""

import json
import time
import random
import argparse
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright


def load_config(path="config.json"):
    with open(path) as f:
        return json.load(f)


def ask_mimo(api_key, model, prompt):
    """Ask MiMo to generate a form response."""
    r = requests.post(
        "https://api.xiaomimimo.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7},
        timeout=30,
    )
    return r.json()["choices"][0]["message"]["content"]


def extract_fields(page):
    """Extract form fields from the page."""
    fields = []
    for el in page.query_selector_all("input, textarea, select"):
        field = {
            "tag": el.evaluate("e => e.tagName.toLowerCase()"),
            "type": el.get_attribute("type") or "text",
            "name": el.get_attribute("name") or "",
            "placeholder": el.get_attribute("placeholder") or "",
            "label": "",
        }
        # Try to find label
        label_el = page.query_selector(f'label[for="{el.get_attribute("id") or ""}"]')
        if label_el:
            field["label"] = label_el.inner_text()
        fields.append(field)
    return fields


def fill_form(page, fields, responses, delay_ms=500):
    """Fill form fields with generated responses."""
    for field, value in zip(fields, responses):
        if not value:
            continue
        selector = f'[name="{field["name"]}"]' if field["name"] else None
        if not selector:
            continue

        try:
            if field["tag"] == "select":
                page.select_option(selector, value=value)
            else:
                page.fill(selector, "")
                for char in value:
                    page.type(selector, char, delay=random.randint(30, 80))
            time.sleep(delay_ms / 1000)
        except Exception as e:
            print(f"  [!] Skip {field['name']}: {e}")


def main():
    parser = argparse.ArgumentParser(description="MiMo Form Agent")
    parser.add_argument("--url", required=True, help="Target form URL")
    parser.add_argument("--config", default="config.json", help="Config file")
    parser.add_argument("--dry-run", action="store_true", help="Extract fields only")
    args = parser.parse_args()

    cfg = load_config(args.config)
    print(f"[*] MiMo Form Agent")
    print(f"    Model: {cfg.get('model', 'mimo-v2.5-pro')}")
    print(f"    Target: {args.url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=cfg.get("headless", True))
        page = browser.new_page()
        page.goto(args.url, wait_until="networkidle", timeout=30000)

        # Extract fields
        fields = extract_fields(page)
        print(f"    Found {len(fields)} form fields")

        if args.dry_run:
            for f in fields:
                print(f"      - {f['name'] or f['label']}: {f['type']}")
            browser.close()
            return

        # Ask MiMo to generate responses
        prompt = f"Fill this form. Fields:\n"
        for f in fields:
            prompt += f"- {f['label'] or f['name']} ({f['type']}): {f['placeholder']}\n"
        prompt += "\nReturn JSON array of values in order."

        print("    Generating responses with MiMo...")
        raw = ask_mimo(cfg["mimo_api_key"], cfg.get("model", "mimo-v2.5-pro"), prompt)
        responses = json.loads(raw)

        # Fill and submit
        print("    Filling form...")
        fill_form(page, fields, responses, cfg.get("delay_ms", 500))
        print("    [+] Done")

        browser.close()


if __name__ == "__main__":
    main()
