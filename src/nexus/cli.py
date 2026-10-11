"""Command-line entry point for Zoavintsoa AI Nexus."""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any

from nexus.config import Settings
from nexus.benchmark import parse_benchmark, run_benchmark
from nexus.errors import NexusError
from nexus.inventory import inventory
from nexus.orchestrator import Orchestrator
from nexus.resource_manager import plan_resources
from nexus.router import route_task, classify_task
from nexus.sessions import export_session, import_session
from nexus.state import StateStore
from nexus.workflow import parse_workflow, execute_workflow
from nexus.providers.ollama import OllamaClient
from nexus.providers.openai_compatible import OpenAICompatibleClient


def _client(settings: Settings) -> Any:
    if settings.provider == "openai-compatible":
        return OpenAICompatibleClient(
            settings.compatible_host, settings.request_timeout, settings.compatible_api_key
        )
    return OllamaClient(settings.ollama_host, settings.request_timeout)


def _profile_dicts(client: Any, provider: str) -> list[dict[str, Any]]:
    if isinstance(client, OllamaClient):
        return [profile.to_dict() for profile in inventory(client)]
    return [
        {"name": item["name"], "provider": item.get("provider", provider),
         "size_bytes": item.get("size"), "capabilities": []}
        for item in client.list_models() if isinstance(item, dict) and item.get("name")
    ]


def _store_profiles(provider: str, profiles: list[dict[str, Any]]) -> None:
    try:
        StateStore().save_profiles(provider, profiles)
    except (OSError, sqlite3.Error) as exc:
        print(f"Warning: could not persist model profiles: {exc}", file=sys.stderr)


def _record_run(provider: str, model: str, prompt: str, elapsed: float, success: bool) -> None:
    try:
        StateStore().record_run(provider, model, classify_task(prompt), elapsed, success)
    except (OSError, sqlite3.Error) as exc:
        print(f"Warning: could not persist run metrics: {exc}", file=sys.stderr)


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
    _store_profiles("ollama", [profile.to_dict() for profile in profiles])
    if as_json:
        print(json.dumps([profile.to_dict() for profile in profiles], indent=2, ensure_ascii=False))
        return 0
    if not profiles:
        print("No Ollama models found. Pull a model with: ollama pull <model>")
        return 0
    for profile in profiles:
        size = f"{profile.size_bytes / 1_000_000_000:.2f} GB" if profile.size_bytes is not None else "size unknown"
        print(f"\n{profile.name} — {size}")
        print(f"  Family: {profile.family or 'unknown'}")
        print(f"  Parameters: {profile.parameter_size or 'unknown'}")
        print(f"  Quantization: {profile.quantization or 'unknown'}")
        print("  Capabilities: " + (", ".join(profile.capabilities) if profile.capabilities else "not reported"))
        if profile.details_error:
            print(f"  Metadata warning: {profile.details_error}")
    return 0


def _print_profiles(provider: str) -> int:
    profiles = StateStore().get_profiles(provider)
    if not profiles:
        print("No saved profiles. Run 'nexus profiles sync' first.")
        return 0
    print(json.dumps(profiles, indent=2, ensure_ascii=False))
    return 0


def _print_metrics(provider: str | None, as_json: bool = False) -> int:
    rows = StateStore().metrics(provider)
    if not rows:
        print("No recorded model metrics yet. Run 'nexus ask' or 'nexus collaborate'.")
        return 0
    if as_json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
    else:
        for row in rows:
            print(f"{row['model']} | {row['task_type']} | runs={row['runs']} "
                  f"| avg={row['avg_seconds']}s | success={row['successes']} "
                  f"| failures={row['failures']} | last={row['last_run']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="nexus", description="Zoavintsoa AI Nexus")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="Check provider and local resource availability")
    sub.add_parser("models", help="List models available from the configured provider")
    inventory_parser = sub.add_parser("inventory", help="Show provider-reported model metadata")
    inventory_parser.add_argument("--json", action="store_true", help="Output inventory as JSON")
    ask = sub.add_parser("ask", help="Ask one model")
    model_choice = ask.add_mutually_exclusive_group(required=True)
    model_choice.add_argument("--model", help="Exact model name")
    model_choice.add_argument("--auto", action="store_true", help="Select a model using reported capabilities and metadata")
    ask.add_argument("--session-out", help="Optionally export this result to a JSON session")
    ask.add_argument("prompt")
    collab = sub.add_parser("collaborate", help="Ask several models and synthesize their contributions")
    collab.add_argument("--models", required=True, help="Comma-separated installed model names")
    collab.add_argument("--session-out", help="Optionally export this result to a JSON session")
    collab.add_argument("prompt")

    profiles = sub.add_parser("profiles", help="Manage persistent local model profiles")
    profiles_sub = profiles.add_subparsers(dest="profiles_command", required=True)
    profiles_sub.add_parser("sync", help="Refresh saved profiles from the configured provider")
    profiles_sub.add_parser("list", help="List saved model profiles")

    metrics = sub.add_parser("metrics", help="Show locally stored model performance metrics")
    metrics.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    metrics.add_argument("--clear", action="store_true", help="Delete recorded metrics")
    route = sub.add_parser("route", help="Explain automatic task-to-model routing")
    route.add_argument("--model", help="Explicit model override")
    route.add_argument("prompt")

    resources = sub.add_parser("resources", help="Estimate safe parallel model concurrency")
    resources.add_argument("--models", required=True, help="Comma-separated model names")

    workflow = sub.add_parser("workflow", help="Validate or run a declarative JSON workflow")
    workflow_sub = workflow.add_subparsers(dest="workflow_command", required=True)
    for name, help_text in (("plan", "Validate and display a workflow plan"), ("run", "Execute a workflow")):
        command = workflow_sub.add_parser(name, help=help_text)
        command.add_argument("--file", required=True, help="Path to a workflow JSON file")
        if name == "run":
            command.add_argument("--session-out", help="Optionally export workflow output")

    benchmark = sub.add_parser("benchmark", help="Run a user-defined latency benchmark across models")
    benchmark.add_argument("--file", required=True, help="Path to benchmark JSON")
    benchmark.add_argument("--out", help="Write complete benchmark results to a JSON file")

    session = sub.add_parser("session", help="Inspect an exported JSON session")
    session_sub = session.add_subparsers(dest="session_command", required=True)
    show = session_sub.add_parser("show", help="Validate and print an exported session")
    show.add_argument("--file", required=True)

    args = parser.parse_args(argv)
    try:
        settings = Settings.from_env()
        client = _client(settings)
        store = StateStore()

        if args.command == "doctor":
            models = client.list_models()
            print(f"Provider: {settings.provider}")
            print(f"Endpoint: {client.host}")
            if isinstance(client, OllamaClient):
                print(f"Ollama version: {client.version()}")
            print(f"Models available: {len(models)}")
            print(f"Requested concurrency: {settings.max_workers}")
            plan = plan_resources(
                [str(item.get("name")) for item in models if item.get("name")],
                _profile_dicts(client, settings.provider), settings.max_workers,
                settings.memory_budget_fraction,
            )
            print(f"Recommended concurrency: {plan.recommended_workers}")
            for warning in plan.warnings:
                print(f"Resource warning: {warning}")
            print(f"Persistent state: {store.path}")
            return 0

        if args.command == "models":
            return _print_models(client)
        if args.command == "inventory":
            return _print_inventory(client, args.json)
        if args.command == "ask":
            model = args.model
            if args.auto:
                profiles_data = _profile_dicts(client, settings.provider)
                decision = route_task(args.prompt, profiles_data)
                if not decision.selected_model:
                    raise ValueError("Automatic routing could not select a model; use --model.")
                model = decision.selected_model
                print(f"Auto-selected model: {model} ({decision.reason})", file=sys.stderr)
                if isinstance(client, OllamaClient):
                    _store_profiles(settings.provider, profiles_data)
            started = time.monotonic()
            success = False
            result = ""
            try:
                result = client.chat(model, args.prompt)
                print(result)
                success = True
            finally:
                _record_run(settings.provider, model, args.prompt, time.monotonic() - started, success)
            if args.session_out:
                export_session(args.session_out, args.prompt, settings.provider, [model],
                               {"answer": result})
                print(f"Session exported: {Path(args.session_out).expanduser()}")
            return 0
        if args.command == "collaborate":
            models = list(dict.fromkeys(name.strip() for name in args.models.split(",") if name.strip()))
            if not models:
                raise ValueError("Provide at least one model name.")
            profiles = _profile_dicts(client, settings.provider)
            if isinstance(client, OllamaClient):
                _store_profiles(settings.provider, profiles)
            plan = plan_resources(models, profiles, settings.max_workers, settings.memory_budget_fraction)
            for warning in plan.warnings:
                print(f"Resource warning: {warning}", file=sys.stderr)
            result = Orchestrator(client, plan.recommended_workers).collaborate(models, args.prompt)
            for contribution in result.contributions:
                status = "OK" if contribution.succeeded else "FAILED"
                elapsed = f" — {contribution.latency_seconds:.2f}s" if contribution.latency_seconds is not None else ""
                print(f"\n[{status}] {contribution.model}{elapsed}")
                print(contribution.content if contribution.succeeded else contribution.error)
                _record_run(settings.provider, contribution.model, args.prompt,
                            contribution.latency_seconds or 0.0, contribution.succeeded)
            print("\n=== SYNTHESIS ===\n")
            print(result.synthesis)
            if args.session_out:
                payload = {
                    "contributions": [
                        {"model": item.model, "content": item.content, "error": item.error,
                         "latency_seconds": item.latency_seconds}
                        for item in result.contributions
                    ],
                    "synthesis": result.synthesis,
                }
                export_session(args.session_out, args.prompt, settings.provider, models, payload)
                print(f"Session exported: {Path(args.session_out).expanduser()}")
            return 0
        if args.command == "profiles":
            if args.profiles_command == "sync":
                profiles_data = _profile_dicts(client, settings.provider)
                store.save_profiles(settings.provider, profiles_data)
                print(f"Saved {len(profiles_data)} profile(s) for provider {settings.provider}.")
                return 0
            return _print_profiles(settings.provider)
        if args.command == "metrics":
            if args.clear:
                count = store.clear_metrics()
                print(f"Deleted {count} metric record(s).")
                return 0
            return _print_metrics(settings.provider, args.json)
        if args.command == "route":
            profiles_data = _profile_dicts(client, settings.provider)
            decision = route_task(args.prompt, profiles_data, args.model)
            print(f"Task type: {decision.task_type}")
            print(f"Selected model: {decision.selected_model or 'none'}")
            print(f"Reason: {decision.reason}")
            if decision.candidates:
                print("Candidates: " + ", ".join(decision.candidates))
            return 0 if decision.selected_model else 2
        if args.command == "resources":
            models = list(dict.fromkeys(name.strip() for name in args.models.split(",") if name.strip()))
            profiles_data = _profile_dicts(client, settings.provider)
            plan = plan_resources(models, profiles_data, settings.max_workers, settings.memory_budget_fraction)
            print(json.dumps({
                "requested_workers": plan.requested_workers,
                "recommended_workers": plan.recommended_workers,
                "available_memory_bytes": plan.available_memory_bytes,
                "estimated_model_memory_bytes": plan.estimated_model_memory_bytes,
                "warnings": list(plan.warnings),
                "note": "Estimates are heuristic and do not measure GPU VRAM or guarantee safe loading.",
            }, indent=2, ensure_ascii=False))
            return 0
        if args.command == "benchmark":
            benchmark_data = json.loads(Path(args.file).expanduser().read_text(encoding="utf-8"))
            tasks = parse_benchmark(benchmark_data)
            results = run_benchmark(client, tasks)
            for item in results:
                _record_run(settings.provider, item["model"], next(
                    task["prompt"] for task in tasks if task["id"] == item["task_id"]
                ), item["elapsed_seconds"], item["succeeded"])
            report = {
                "provider": settings.provider,
                "tasks": len(tasks),
                "model_runs": len(results),
                "succeeded": sum(1 for item in results if item["succeeded"]),
                "failed": sum(1 for item in results if not item["succeeded"]),
                "results": results,
                "note": "Latency and success are measured; answer quality is not automatically scored.",
            }
            if args.out:
                target = Path(args.out).expanduser()
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                print(f"Benchmark report saved: {target}")
            else:
                print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if report["failed"] == 0 else 2
        if args.command == "workflow":
            workflow_data = json.loads(Path(args.file).expanduser().read_text(encoding="utf-8"))
            steps = parse_workflow(workflow_data)
            if args.workflow_command == "plan":
                print(json.dumps([
                    {"id": step.id, "model": step.model, "depends_on": list(step.depends_on),
                     "prompt": step.prompt}
                    for step in steps
                ], indent=2, ensure_ascii=False))
                return 0
            profiles_data = _profile_dicts(client, settings.provider)
            if isinstance(client, OllamaClient):
                _store_profiles(settings.provider, profiles_data)
            plan = plan_resources([step.model for step in steps], profiles_data,
                                  settings.max_workers, settings.memory_budget_fraction)
            for warning in plan.warnings:
                print(f"Resource warning: {warning}", file=sys.stderr)
            result = execute_workflow(client, steps, plan.recommended_workers)
            for step in steps:
                _record_run(settings.provider, step.model, step.prompt,
                            result.elapsed_seconds.get(step.id, 0.0), step.id in result.outputs)
            print(json.dumps({
                "outputs": result.outputs, "errors": result.errors,
                "elapsed_seconds": result.elapsed_seconds,
                "recommended_workers": plan.recommended_workers,
            }, indent=2, ensure_ascii=False))
            if args.session_out:
                export_session(args.session_out, "workflow:" + str(args.file), settings.provider,
                               [step.model for step in steps],
                               {"outputs": result.outputs, "errors": result.errors,
                                "elapsed_seconds": result.elapsed_seconds})
                print(f"Session exported: {Path(args.session_out).expanduser()}")
            return 0 if not result.errors else 2
        if args.command == "session" and args.session_command == "show":
            print(json.dumps(import_session(args.file), indent=2, ensure_ascii=False))
            return 0
    except (NexusError, ValueError, OSError, json.JSONDecodeError, sqlite3.Error) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
