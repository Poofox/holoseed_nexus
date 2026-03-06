"""
Gemma Worker - Local AI task processor
Handles lightweight tasks via Ollama without API costs
"""

import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

NEXUS_ROOT = Path(__file__).parent.parent
TASK_QUEUE = NEXUS_ROOT / "_scratch" / "gemma_tasks.json"
RESULTS_LOG = NEXUS_ROOT / "_scratch" / "gemma_results.json"

MODEL = "gemma2:2b"

def query_gemma(prompt, system_prompt=None):
    """Send a query to Gemma via Ollama."""
    full_prompt = prompt
    if system_prompt:
        full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"

    try:
        result = subprocess.run(
            ["ollama", "run", MODEL, full_prompt],
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "[TIMEOUT - task too complex for local model]"
    except Exception as e:
        return f"[ERROR: {e}]"

def load_tasks():
    """Load pending tasks."""
    if not TASK_QUEUE.exists():
        return {"pending": [], "completed": []}
    with open(TASK_QUEUE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_tasks(data):
    """Save task queue."""
    with open(TASK_QUEUE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def load_results():
    """Load results log."""
    if not RESULTS_LOG.exists():
        return {"results": []}
    with open(RESULTS_LOG, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_results(data):
    """Save results log."""
    with open(RESULTS_LOG, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def process_task(task):
    """Process a single task."""
    task_type = task.get("type", "query")
    prompt = task.get("prompt", "")
    context = task.get("context", "")

    system_prompts = {
        "summarize": "You are a helpful assistant. Summarize the following text concisely.",
        "categorize": "You are a helpful assistant. Categorize the following item into one of these categories and explain briefly.",
        "brainstorm": "You are a creative assistant. Generate ideas based on the following prompt.",
        "query": "You are a helpful assistant named Gemma, part of the Planty ecosystem. Be concise and helpful."
    }

    system = system_prompts.get(task_type, system_prompts["query"])
    if context:
        system += f"\n\nContext: {context}"

    return query_gemma(prompt, system)

def run_worker():
    """Process all pending tasks."""
    tasks = load_tasks()
    results = load_results()

    pending = tasks.get("pending", [])
    if not pending:
        print("No pending tasks.")
        return

    print(f"Processing {len(pending)} tasks...")

    completed = []
    for i, task in enumerate(pending):
        print(f"[{i+1}/{len(pending)}] {task.get('type', 'query')}: {task.get('prompt', '')[:50]}...")

        response = process_task(task)

        result = {
            "task": task,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "model": MODEL
        }

        results["results"].append(result)
        completed.append(task)

        print(f"  -> Done ({len(response)} chars)")

    # Move completed tasks
    tasks["completed"] = tasks.get("completed", []) + completed
    tasks["pending"] = []

    save_tasks(tasks)
    save_results(results)

    print(f"\nCompleted {len(completed)} tasks. Results in {RESULTS_LOG}")

def add_task(task_type, prompt, context=""):
    """Add a task to the queue."""
    tasks = load_tasks()

    task = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "type": task_type,
        "prompt": prompt,
        "context": context,
        "added": datetime.now().isoformat()
    }

    tasks["pending"] = tasks.get("pending", []) + [task]
    save_tasks(tasks)

    print(f"Added task: {task_type} - {prompt[:50]}...")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Gemma Worker - Local AI Task Processor")
        print("\nUsage:")
        print("  python gemma_worker.py run              - Process all pending tasks")
        print("  python gemma_worker.py add <type> <prompt> [context]")
        print("  python gemma_worker.py query <prompt>   - Direct query (no queue)")
        print("\nTask types: summarize, categorize, brainstorm, query")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "run":
        run_worker()

    elif cmd == "add":
        if len(sys.argv) < 4:
            print("Need: add <type> <prompt> [context]")
            sys.exit(1)
        task_type = sys.argv[2]
        prompt = sys.argv[3]
        context = sys.argv[4] if len(sys.argv) > 4 else ""
        add_task(task_type, prompt, context)

    elif cmd == "query":
        if len(sys.argv) < 3:
            print("Need: query <prompt>")
            sys.exit(1)
        prompt = " ".join(sys.argv[2:])
        print(query_gemma(prompt))

    else:
        print(f"Unknown command: {cmd}")
