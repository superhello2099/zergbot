"""ZergBot Demo Mode - Zero-config demo experience."""

from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rich.console import Console


# Demo tasks - pre-built examples that showcase ZergBot capabilities
DEMO_TASKS = {
    "meme": {
        "name": "Meme Generator",
        "description": "Generate a funny meme caption",
        "prompt": """You are a meme generator. Given a topic, create a funny meme caption.

Topic: AI taking over the world

Generate:
1. Top text (setup)
2. Bottom text (punchline)
3. Suggested meme template (e.g., "Distracted Boyfriend", "Drake Hotline Bling")

Be funny and relatable!""",
    },
    "research": {
        "name": "Research Agent",
        "description": "Research a topic and summarize findings",
        "prompt": """You are a research agent. Research the following topic and provide a brief summary.

Topic: What are the key differences between LangChain and CrewAI?

Provide:
1. Brief overview of each framework
2. Key differences (3-5 points)
3. When to use each one
4. Your recommendation

Be concise and informative.""",
    },
    "code": {
        "name": "Code Helper",
        "description": "Help with coding questions",
        "prompt": """You are a coding assistant. Help answer the following question:

Question: How do I implement a simple rate limiter in Python using a decorator?

Provide:
1. A working code example
2. Brief explanation of how it works
3. Usage example
4. Any caveats or improvements to consider

Be practical and clear.""",
    },
}


async def run_demo(console: "Console") -> None:
    """Run interactive CLI demo."""
    from zergbot import __logo__

    console.print(f"\n{__logo__} [bold]ZergBot Demo Mode[/bold]")
    console.print("=" * 50)
    console.print()
    console.print("Available demo tasks:")
    for key, task in DEMO_TASKS.items():
        console.print(f"  [cyan]{key}[/cyan]: {task['description']}")
    console.print()
    console.print("Commands:")
    console.print("  [dim]Type a task name (meme/research/code) to run it[/dim]")
    console.print("  [dim]Type 'quit' to exit[/dim]")
    console.print()

    while True:
        try:
            user_input = console.input("[bold blue]demo>[/bold blue] ").strip().lower()

            if not user_input:
                continue

            if user_input in ("quit", "exit", "q"):
                console.print("Goodbye!")
                break

            if user_input in DEMO_TASKS:
                await run_task_demo(user_input, console)
            else:
                console.print(f"[yellow]Unknown task: {user_input}[/yellow]")
                console.print("Available: meme, research, code")

        except KeyboardInterrupt:
            console.print("\nGoodbye!")
            break


async def run_task_demo(task_name: str, console: "Console") -> None:
    """Run a specific demo task."""
    import os

    from zergbot import __logo__
    from zergbot.bus.queue import MessageBus
    from zergbot.providers.litellm_provider import LiteLLMProvider
    from zergbot.agent.loop import AgentLoop

    if task_name not in DEMO_TASKS:
        console.print(f"[red]Unknown task: {task_name}[/red]")
        console.print(f"Available: {', '.join(DEMO_TASKS.keys())}")
        return

    task = DEMO_TASKS[task_name]
    console.print(f"\n{__logo__} Running: [bold]{task['name']}[/bold]")
    console.print("-" * 40)

    # Get API key from environment or use demo mode
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    demo_mode = os.environ.get("ZERGBOT_DEMO_MODE", "0") == "1"

    if not api_key and not demo_mode:
        console.print("[yellow]No API key found. Showing simulated output...[/yellow]")
        console.print()
        _show_simulated_output(task_name, console)
        return

    # Run actual agent
    try:
        bus = MessageBus()
        provider = LiteLLMProvider(
            api_key=api_key,
            api_base=os.environ.get("OPENROUTER_API_BASE"),
            default_model="openrouter/google/gemini-2.0-flash-001",  # Free model
        )

        agent = AgentLoop(
            bus=bus,
            provider=provider,
            workspace=Path.home() / ".zergbot" / "demo",
        )

        response = await agent.process_direct(
            task["prompt"], session_key=f"demo:{task_name}"
        )
        console.print()
        console.print(response)
        console.print()

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[yellow]Showing simulated output instead...[/yellow]")
        _show_simulated_output(task_name, console)


def _show_simulated_output(task_name: str, console: "Console") -> None:
    """Show simulated output when no API key is available."""
    simulated = {
        "meme": """
[bold]Meme Generated![/bold]

Template: Distracted Boyfriend

Top Text: "My stable, well-tested code"
Bottom Text: "Me chasing the new AI framework that dropped 5 minutes ago"

Alternative:
Template: Drake Hotline Bling
- Nah: "Reading the documentation"
- Yeah: "Asking ChatGPT and hoping for the best"
""",
        "research": """
[bold]Research Summary: LangChain vs CrewAI[/bold]

Overview:
* LangChain: Comprehensive framework for building LLM applications
* CrewAI: Focused on multi-agent collaboration

Key Differences:
1. Scope: LangChain is broader, CrewAI is agent-focused
2. Learning Curve: CrewAI is simpler to start with
3. Flexibility: LangChain offers more customization
4. Use Case: LangChain for pipelines, CrewAI for agent teams

Recommendation: Start with CrewAI for multi-agent tasks, use LangChain for complex pipelines.
""",
        "code": """
[bold]Rate Limiter Implementation[/bold]

```python
import time
from functools import wraps

def rate_limit(calls: int, period: float):
    \"\"\"Rate limiting decorator.\"\"\"
    timestamps = []

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old timestamps
            while timestamps and timestamps[0] < now - period:
                timestamps.pop(0)

            if len(timestamps) >= calls:
                wait = period - (now - timestamps[0])
                raise Exception(f"Rate limit exceeded. Try again in {wait:.1f}s")

            timestamps.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@rate_limit(calls=5, period=60)
def api_call():
    print("API called!")
```

Caveats: This is per-process only. For distributed systems, use Redis.
""",
    }

    console.print(simulated.get(task_name, "[dim]No simulation available[/dim]"))


def run_web_demo(port: int, console: "Console") -> None:
    """Run web-based demo interface."""
    from zergbot import __logo__

    # Create demo HTML
    html_content = _create_demo_html()

    # Create a temporary directory for serving
    demo_dir = Path.home() / ".zergbot" / "demo" / "web"
    demo_dir.mkdir(parents=True, exist_ok=True)

    index_file = demo_dir / "index.html"
    index_file.write_text(html_content)

    console.print(f"\n{__logo__} [bold]ZergBot Web Demo[/bold]")
    console.print("=" * 50)
    console.print()
    console.print(
        f"Open in browser: [link=http://localhost:{port}]http://localhost:{port}[/link]"
    )
    console.print()
    console.print("[dim]Press Ctrl+C to stop[/dim]")
    console.print()

    import os

    os.chdir(demo_dir)

    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Suppress access logs

    try:
        with HTTPServer(("", port), QuietHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        console.print("\nServer stopped.")


def _create_demo_html() -> str:
    """Create the demo web interface HTML."""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZergBot Demo</title>
    <style>
        :root {
            --bg: #0a0a0a;
            --surface: #141414;
            --border: #2a2a2a;
            --text: #e0e0e0;
            --accent: #00ff88;
            --accent-dim: #00cc6a;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        header {
            padding: 2rem;
            text-align: center;
            border-bottom: 1px solid var(--border);
        }
        .logo { font-size: 3rem; margin-bottom: 0.5rem; }
        h1 { font-size: 1.5rem; font-weight: 600; }
        .subtitle { color: #888; margin-top: 0.5rem; }
        main {
            flex: 1;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            width: 100%;
        }
        .tasks {
            display: grid;
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .task-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        .task-card:hover {
            border-color: var(--accent);
            transform: translateY(-2px);
        }
        .task-card.active {
            border-color: var(--accent);
            background: #0a1a10;
        }
        .task-icon { font-size: 2rem; margin-bottom: 0.5rem; }
        .task-name { font-weight: 600; margin-bottom: 0.25rem; }
        .task-desc { font-size: 0.875rem; color: #888; }
        .output-area {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            min-height: 300px;
            white-space: pre-wrap;
            font-family: 'SF Mono', Monaco, monospace;
            font-size: 0.875rem;
            line-height: 1.6;
        }
        .output-area.loading {
            display: flex;
            align-items: center;
            justify-content: center;
            color: #888;
        }
        .spinner {
            width: 24px;
            height: 24px;
            border: 2px solid var(--border);
            border-top-color: var(--accent);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 0.5rem;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        footer {
            padding: 1rem;
            text-align: center;
            color: #666;
            font-size: 0.75rem;
            border-top: 1px solid var(--border);
        }
        a { color: var(--accent); text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <header>
        <div class="logo">&#x1F41B;</div>
        <h1>ZergBot Demo</h1>
        <p class="subtitle">A lightweight AI agent framework</p>
    </header>
    <main>
        <div class="tasks">
            <div class="task-card" data-task="meme">
                <div class="task-icon">&#x1F3AD;</div>
                <div class="task-name">Meme Generator</div>
                <div class="task-desc">Generate funny meme captions</div>
            </div>
            <div class="task-card" data-task="research">
                <div class="task-icon">&#x1F4DA;</div>
                <div class="task-name">Research Agent</div>
                <div class="task-desc">Research topics and summarize findings</div>
            </div>
            <div class="task-card" data-task="code">
                <div class="task-icon">&#x1F4BB;</div>
                <div class="task-name">Code Helper</div>
                <div class="task-desc">Get help with coding questions</div>
            </div>
        </div>
        <div id="output" class="output-area">
            <span style="color: #888;">Click a task above to see ZergBot in action!</span>
        </div>
    </main>
    <footer>
        <p>ZergBot v0.1.0 | <a href="https://github.com/superhello2099/zergbot">GitHub</a> | MIT License</p>
    </footer>
    <script>
        const output = document.getElementById('output');
        const cards = document.querySelectorAll('.task-card');

        const demos = {
            meme: `Meme Generated!

Template: Distracted Boyfriend

Top Text: "My stable, well-tested code"
Bottom Text: "Me chasing the new AI framework that dropped 5 minutes ago"

---

Alternative:
Template: Drake Hotline Bling
- Nah: "Reading the documentation"
- Yeah: "Asking ChatGPT and hoping for the best"`,

            research: `Research Summary: LangChain vs CrewAI

Overview:
- LangChain: Comprehensive framework for building LLM applications
- CrewAI: Focused on multi-agent collaboration

Key Differences:
1. Scope: LangChain is broader, CrewAI is agent-focused
2. Learning Curve: CrewAI is simpler to start with
3. Flexibility: LangChain offers more customization
4. Use Case: LangChain for pipelines, CrewAI for agent teams

Recommendation: Start with CrewAI for multi-agent tasks,
use LangChain for complex pipelines.`,

            code: `Rate Limiter Implementation

import time
from functools import wraps

def rate_limit(calls: int, period: float):
    """Rate limiting decorator."""
    timestamps = []

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old timestamps
            while timestamps and timestamps[0] < now - period:
                timestamps.pop(0)

            if len(timestamps) >= calls:
                wait = period - (now - timestamps[0])
                raise Exception(f"Rate limit exceeded. Try in {wait:.1f}s")

            timestamps.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@rate_limit(calls=5, period=60)
def api_call():
    print("API called!")

Caveats: This is per-process only.
For distributed systems, use Redis.`
        };

        cards.forEach(card => {
            card.addEventListener('click', () => {
                cards.forEach(c => c.classList.remove('active'));
                card.classList.add('active');

                output.classList.add('loading');
                output.textContent = 'Running task...';

                setTimeout(() => {
                    output.classList.remove('loading');
                    output.textContent = demos[card.dataset.task];
                }, 1000);
            });
        });
    </script>
</body>
</html>'''
