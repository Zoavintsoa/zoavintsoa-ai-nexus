"""Command-line entry point for AI Nexus."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from nexus.config import Settings
from nexus.errors import NexusError
from nexus.inventory import inventory
from nexus.orchestrator import Orchestrator
from nexus.providers.ollama import OllamaClient
from nexus.providers.openai_compatible import OpenAICompatibleClient


def _client() -> Any:
    settings = Settings.from_env()
    if settings.provider == "openai-compatible":
        return OpenAICompatibleClient(settings.compatible_host, settings.request_timeout)
    return OllamaClient(settings.ollama_host, settings.request_timeout)


def _print_models(client: Any) -> int:
    models = client.list_models()
    if not models:
        print("No models found for the configured provider.")
        return 0
    for item in models:
        name = item.get("name", "(unnamed)")
        size = item.get("size")
        size_text = f" ({size / 1_000_000_000:.1f} GB)" if isinstance(size, (int, float)) else ""
        owner = item.get("provider")
        owner_text = f" [{owner}]" if isinstance(owner, str) and owner else ""
        print(f"- {name}{size_text}{owner_text}")
    return 0


def _print_inventory(client: Any, as_json: bool = False) -> int:
    if not isinstance(client, OllamaClient):
        print("Detailed inventory is currently available for Ollama only.", file=sys.stderr)
        return 2
    profiles = inventory(client)
    if as_json:
        print(json.dumps([profile.to_dict() for profile in profiles], indent=2, ensure_ascii=False))
        return 0
    if not profiles:
        print("No Ollama models found. Pull a model with: ollama pull <model>")
        return 0
    for profile in profiles:
        size = (
            f"{profile.size_bytes / 1_000_000_000:.2f} GB"
            if profile.size_bytes is not None else "size unknown"
        )
        print(f"\n{profile.name} — {size}")
        print(f"  Family: {profile.family or 'unknown'}")
        print(f"  Parameters: {profile.parameter_size or 'unknown'}")
        print(f"  Quantization: {profile.quantization or 'unknown'}")
        print("  Capabilities: " + (", ".join(profile.capabilities) if profile.capabilities else "not reported"))
        if profile.details_error:
            print(f"  Metadata warning: {profile.details_error}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="nexus", description="Zoavintsoa AI Nexus")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="Check connection to the configured provider")
    sub.add_parser("models", help="List models available from the configured provider")
    inventory_parser = sub.add_parser("inventory", help="Show provider-reported model metadata")
    inventory_parser.add_argument("--json", action="store_true", help="Output inventory as JSON")
    ask = sub.add_parser("ask", help="Ask one model from the configured provider")
    ask.add_argument("--model", required=True)
    ask.add_argument("prompt")
    collab = sub.add_parser("collaborate", help="Ask several models and synthesize their contributions")
    collab.add_argument("--models", required=True, help="Comma-separated installed model names")
    collab.add_argument("prompt")
    args = parser.parse_args(argv)
    client = _client()
    settings = Settings.from_env()

    try:
        if args.command == "doctor":
            models = client.list_models()
            print(f"Provider: {settings.provider}")
            print(f"Endpoint: {client.host}")
            if isinstance(client, OllamaClient):
                print(f"Ollama version: {client.version()}")
            print(f"Models available: {len(models)}")
            return 0
        if args.command == "models":
            return _print_models(client)
        if args.command == "inventory":
            return _print_inventory(client, args.json)
        if args.command == "ask":
            print(client.chat(args.model, args.prompt))
            return 0
        if args.command == "collaborate":
            models = [name.strip() for name in args.models.split(",") if name.strip()]
            result = Orchestrator(client, settings.max_workers).collaborate(models, args.prompt)
            for contribution in result.contributions:
                status = "OK" if contribution.succeeded else "FAILED"
                print(f"\n[{status}] {contribution.model}")
                print(contribution.content if contribution.succeeded else contribution.error)
            print("\n=== SYNTHESIS ===\n")
            print(result.synthesis)
            return 0
    except (NexusError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
