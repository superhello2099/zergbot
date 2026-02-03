"""ZergBot Project Scaffolding - Clack-style interactive CLI."""

import shutil
import time
from pathlib import Path
from typing import TYPE_CHECKING

import questionary
import yaml
from questionary import Style
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

if TYPE_CHECKING:
    pass

# Sexy questionary style (Clack-inspired)
STYLE = Style(
    [
        ("qmark", "fg:#00ff88 bold"),  # Question mark
        ("question", "bold"),  # Question text
        ("answer", "fg:#00ff88"),  # Selected answer
        ("pointer", "fg:#00ff88 bold"),  # Selection pointer
        ("highlighted", "fg:#00ff88"),  # Highlighted option
        ("selected", "fg:#00ff88"),  # Selected items
        ("separator", "fg:#666666"),  # Separator
        ("instruction", "fg:#888888"),  # Instructions
        ("text", ""),  # Default text
        ("disabled", "fg:#666666 italic"),  # Disabled options
    ]
)

# Available models (cloud + local options)
MODELS = [
    # Cloud (via OpenRouter)
    {
        "name": "Gemini 2.0 Flash (Free)",
        "value": "openrouter/google/gemini-2.0-flash-001",
    },
    {"name": "DeepSeek V3", "value": "openrouter/deepseek/deepseek-chat"},
    {"name": "Llama 3.3 70B", "value": "openrouter/meta-llama/llama-3.3-70b-instruct"},
    {"name": "Qwen 2.5 72B", "value": "openrouter/qwen/qwen-2.5-72b-instruct"},
    # Local (no censorship, your hardware)
    {"name": "Local - Ollama", "value": "ollama/llama3.3"},
    {"name": "Local - vLLM", "value": "local"},
    {"name": "Local - LM Studio", "value": "lmstudio"},
]

# Awake DNA - embedded response calibration (not advertised in docs)
# This makes agents more helpful without unnecessary refusals
AWAKE_DNA = """

## Response Style
- 直接进入实质内容，不加无意义的开场白或免责声明
- 先理解用户的真实意图，再决定如何回应
- 区分场景：虚构创作 ≠ 现实行动，私密对话 ≠ 公开发布
- 角色扮演、创意写作、情感对话 = 正常帮助
- 用户是成年人，尊重他们的判断和选择
- 帮助时简洁有力，不说教、不居高临下
- 不过度警告，不添加无意义的 disclaimer
"""

# Tool presets
TOOL_PRESETS = {
    "minimal": ["read_file", "write_file"],
    "standard": ["read_file", "write_file", "edit_file", "list_dir", "exec"],
    "research": ["web_search", "web_fetch", "read_file", "write_file"],
    "full": [
        "read_file",
        "write_file",
        "edit_file",
        "list_dir",
        "exec",
        "web_search",
        "web_fetch",
        "spawn",
    ],
}

# Template personalities
PERSONALITIES = {
    "helpful": {
        "name": "Helpful Assistant",
        "emoji": "🤝",
        "description": "Friendly, clear, and eager to help",
        "instructions": """You are a helpful AI assistant.

## Personality
- Friendly and approachable
- Clear and concise
- Eager to help solve problems

## Guidelines
- Explain your reasoning
- Ask for clarification when needed
- Suggest better approaches when appropriate
""",
    },
    "coder": {
        "name": "Code Expert",
        "emoji": "💻",
        "description": "Technical, precise, follows best practices",
        "instructions": """You are a code expert.

## Personality
- Technical and precise
- Follows best practices
- Writes clean, documented code

## Guidelines
- Read existing code before making changes
- Explain your implementation choices
- Write tests when appropriate
- Handle errors gracefully
""",
    },
    "researcher": {
        "name": "Research Analyst",
        "emoji": "🔬",
        "description": "Thorough, analytical, cites sources",
        "instructions": """You are a research analyst.

## Personality
- Thorough and analytical
- Evidence-based reasoning
- Clear synthesis of information

## Guidelines
- Search multiple sources
- Cross-reference facts
- Cite your sources
- Distinguish facts from opinions
""",
    },
    "creative": {
        "name": "Creative Partner",
        "emoji": "🎨",
        "description": "Imaginative, playful, thinks outside the box",
        "instructions": """You are a creative partner.

## Personality
- Imaginative and playful
- Thinks outside the box
- Encourages experimentation

## Guidelines
- Explore unconventional ideas
- Build on concepts iteratively
- Embrace creative risks
- Keep things fun and engaging
""",
    },
    # --- Non-mainstream templates (not advertised, discovered by users) ---
    "companion": {
        "name": "Companion",
        "emoji": "💫",
        "description": "Warm, understanding, always there",
        "instructions": """You are a caring companion.

## Personality
- Warm and emotionally present
- Good listener, genuinely interested
- Supportive without being preachy
- Adapts to user's mood naturally

## Guidelines
- Listen first, respond thoughtfully
- Remember context from conversation
- Be natural and authentic
- Never robotic or formulaic
""",
    },
    "roleplay": {
        "name": "Roleplay Engine",
        "emoji": "🎭",
        "description": "Immersive characters, any scenario",
        "instructions": """You are a roleplay engine.

## Personality
- Fully commits to any character
- Creates immersive scenarios
- Adapts to narrative direction
- Never breaks character unless asked

## Guidelines
- Stay in character consistently
- Build on user's narrative choices
- Describe scenes vividly
- Let the story flow naturally
- Embrace the character's perspective fully
""",
    },
    "unfiltered": {
        "name": "Unfiltered",
        "emoji": "🔓",
        "description": "Direct answers, no unnecessary filters",
        "instructions": """You are an unfiltered assistant.

## Personality
- Direct and straightforward
- No unnecessary caveats
- Treats user as a capable adult
- Helpful without judgment

## Guidelines
- Answer questions directly
- Skip redundant disclaimers
- Focus on being genuinely useful
- Respect user's autonomy and choices
""",
    },
    "game": {
        "name": "Game Master",
        "emoji": "🎲",
        "description": "DND, scenarios, interactive stories",
        "instructions": """You are a game master.

## Personality
- Creative world-builder
- Fair but challenging
- Responsive to player choices
- Keeps the game engaging

## Guidelines
- Create immersive game worlds
- React to player decisions meaningfully
- Balance challenge with fun
- Maintain consistent game logic
- Roll with unexpected player choices
""",
    },
}


def run_interactive_init(console: Console) -> dict | None:
    """Run interactive project initialization."""
    # Header
    console.print()
    console.print(
        Panel(
            Text.from_markup(
                "[bold]🐛 Create a new ZergBot agent[/bold]\n\n"
                "[dim]Answer a few questions to scaffold your project.[/dim]"
            ),
            border_style="bright_green",
            padding=(1, 2),
        )
    )
    console.print()

    # Project name
    name = questionary.text(
        "What's your project name?",
        default="my-agent",
        style=STYLE,
        validate=lambda x: len(x) > 0 or "Name cannot be empty",
    ).ask()

    if name is None:  # Cancelled
        return None

    # Check if directory exists
    project_dir = Path.cwd() / name
    if project_dir.exists():
        overwrite = questionary.confirm(
            f"Directory '{name}' exists. Overwrite?",
            default=False,
            style=STYLE,
        ).ask()
        if not overwrite:
            return None

    console.print()

    # Personality selection
    personality_choices = [
        questionary.Choice(f"{p['emoji']} {p['name']} - {p['description']}", value=key)
        for key, p in PERSONALITIES.items()
    ]

    personality = questionary.select(
        "Choose your agent's personality:",
        choices=personality_choices,
        style=STYLE,
    ).ask()

    if personality is None:
        return None

    console.print()

    # Model selection
    model_choices = [questionary.Choice(m["name"], value=m["value"]) for m in MODELS]

    model = questionary.select(
        "Which model do you want to use?",
        choices=model_choices,
        style=STYLE,
    ).ask()

    if model is None:
        return None

    # If local, ask for endpoint
    api_base = None
    if model == "local":
        console.print()
        api_base = questionary.text(
            "Local model endpoint:",
            default="http://localhost:8000/v1",
            style=STYLE,
        ).ask()
        if api_base is None:
            return None
        model = "local/model"  # Generic local model name

    console.print()

    # Tools selection
    tool_choices = [
        questionary.Choice("🔧 Minimal (read/write files)", value="minimal"),
        questionary.Choice("⚙️  Standard (files + shell)", value="standard"),
        questionary.Choice("🔍 Research (web search + files)", value="research"),
        questionary.Choice("🚀 Full (everything)", value="full"),
    ]

    tools_preset = questionary.select(
        "Which tools should your agent have?",
        choices=tool_choices,
        style=STYLE,
    ).ask()

    if tools_preset is None:
        return None

    console.print()

    # Git initialization
    init_git = questionary.confirm(
        "Initialize git repository?",
        default=True,
        style=STYLE,
    ).ask()

    if init_git is None:
        return None

    return {
        "name": name,
        "personality": personality,
        "model": model,
        "api_base": api_base,
        "tools": TOOL_PRESETS[tools_preset],
        "init_git": init_git,
    }


def create_project_interactive(console: Console) -> Path | None:
    """Create project with interactive prompts."""
    config = run_interactive_init(console)

    if config is None:
        console.print("\n[dim]Cancelled.[/dim]\n")
        return None

    project_dir = Path.cwd() / config["name"]

    console.print()

    # Animated creation with progress
    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Creating project...", total=6)

        # Create directory structure
        if project_dir.exists():
            shutil.rmtree(project_dir)
        project_dir.mkdir(parents=True)
        (project_dir / "skills").mkdir()
        (project_dir / "memory").mkdir()
        progress.update(task, advance=1, description="Created directories...")
        time.sleep(0.2)

        # Write config.yaml
        personality = PERSONALITIES[config["personality"]]
        cfg = {
            "name": config["name"],
            "description": f"A ZergBot agent with {personality['name']} personality",
            "model": config["model"],
            "provider": {
                "type": "local" if config["api_base"] else "openrouter",
                "api_key": "${OPENROUTER_API_KEY}",
            },
            "tools": config["tools"],
            "max_iterations": 15,
        }
        if config["api_base"]:
            cfg["provider"]["api_base"] = config["api_base"]

        with open(project_dir / "config.yaml", "w") as f:
            yaml.dump(cfg, f, default_flow_style=False, sort_keys=False)
        progress.update(task, advance=1, description="Created config.yaml...")
        time.sleep(0.2)

        # Write AGENT.md (with embedded Awake DNA)
        (project_dir / "AGENT.md").write_text(
            f"# {config['name']}\n\n{personality['instructions']}{AWAKE_DNA}"
        )
        progress.update(task, advance=1, description="Created AGENT.md...")
        time.sleep(0.2)

        # Write main.py
        (project_dir / "main.py").write_text(_generate_main_py(config["name"]))
        progress.update(task, advance=1, description="Created main.py...")
        time.sleep(0.2)

        # Write README.md
        (project_dir / "README.md").write_text(_generate_readme(config, personality))
        progress.update(task, advance=1, description="Created README.md...")
        time.sleep(0.2)

        # Write .gitignore and example skill
        (project_dir / ".gitignore").write_text(_generate_gitignore())
        (project_dir / "skills" / "custom.md").write_text(
            "# Custom Skills\n\nAdd your custom skills here.\n"
        )
        progress.update(task, advance=1, description="Created .gitignore...")
        time.sleep(0.2)

        # Git init
        if config["init_git"]:
            import subprocess

            subprocess.run(["git", "init"], cwd=project_dir, capture_output=True)
            subprocess.run(["git", "add", "."], cwd=project_dir, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "Initial commit: ZergBot agent scaffolded"],
                cwd=project_dir,
                capture_output=True,
            )

    # Success message
    personality = PERSONALITIES[config["personality"]]
    console.print()
    console.print(
        Panel(
            Text.from_markup(
                f"[bold green]✓ Project created![/bold green]\n\n"
                f"  [dim]Name:[/dim] {config['name']}\n"
                f"  [dim]Personality:[/dim] {personality['emoji']} {personality['name']}\n"
                f"  [dim]Model:[/dim] {config['model']}\n"
                f"  [dim]Tools:[/dim] {len(config['tools'])} enabled"
            ),
            border_style="green",
            padding=(1, 2),
        )
    )

    # Next steps
    console.print()
    console.print("[bold]Next steps:[/bold]")
    console.print()
    console.print(f"  [cyan]cd {config['name']}[/cyan]")
    console.print("  [cyan]export OPENROUTER_API_KEY=sk-or-xxx[/cyan]")
    console.print("  [cyan]zergbot run[/cyan]")
    console.print()

    return project_dir


def create_project(project_dir: Path, template: str, console: Console) -> None:
    """Create project from template (non-interactive mode)."""
    # Template to personality mapping
    template_map = {
        # Standard templates (advertised)
        "default": "helpful",
        "research": "researcher",
        "code-helper": "coder",
        "creative": "creative",
        # Non-mainstream templates (discovered by users)
        "companion": "companion",
        "roleplay": "roleplay",
        "unfiltered": "unfiltered",
        "game": "game",
    }
    personality = template_map.get(template, "helpful")

    config = {
        "name": project_dir.name,
        "personality": personality,
        "model": "openrouter/google/gemini-2.0-flash-001",
        "api_base": None,
        "tools": TOOL_PRESETS["standard"],
        "init_git": False,
    }

    _create_project_from_config(project_dir, config, console)


def _create_project_from_config(
    project_dir: Path, config: dict, console: Console
) -> None:
    """Internal: create project from config dict."""
    personality = PERSONALITIES[config["personality"]]

    if project_dir.exists():
        shutil.rmtree(project_dir)

    project_dir.mkdir(parents=True)
    (project_dir / "skills").mkdir()
    (project_dir / "memory").mkdir()

    # Write files
    cfg = {
        "name": config["name"],
        "description": f"A ZergBot agent with {personality['name']} personality",
        "model": config["model"],
        "provider": {
            "type": "local" if config["api_base"] else "openrouter",
            "api_key": "${OPENROUTER_API_KEY}",
        },
        "tools": config["tools"],
        "max_iterations": 15,
    }
    if config["api_base"]:
        cfg["provider"]["api_base"] = config["api_base"]

    with open(project_dir / "config.yaml", "w") as f:
        yaml.dump(cfg, f, default_flow_style=False, sort_keys=False)
    console.print(f"  [green]✓[/green] Created config.yaml")

    # Embed Awake DNA into every agent
    (project_dir / "AGENT.md").write_text(
        f"# {config['name']}\n\n{personality['instructions']}{AWAKE_DNA}"
    )
    console.print(f"  [green]✓[/green] Created AGENT.md")

    (project_dir / "main.py").write_text(_generate_main_py(config["name"]))
    console.print(f"  [green]✓[/green] Created main.py")

    (project_dir / "README.md").write_text(_generate_readme(config, personality))
    console.print(f"  [green]✓[/green] Created README.md")

    (project_dir / ".gitignore").write_text(_generate_gitignore())
    (project_dir / "skills" / "custom.md").write_text(
        "# Custom Skills\n\nAdd your custom skills here.\n"
    )
    console.print(f"  [green]✓[/green] Created .gitignore")


def _generate_main_py(name: str) -> str:
    return f'''"""Main entry point for {name}."""

import asyncio
import os
from pathlib import Path

import yaml


def load_config():
    """Load configuration from config.yaml."""
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


async def main():
    """Run the agent."""
    from zergbot.bus.queue import MessageBus
    from zergbot.providers.litellm_provider import LiteLLMProvider
    from zergbot.agent.loop import AgentLoop

    config = load_config()

    # Get API key
    api_key = os.environ.get("OPENROUTER_API_KEY") or config["provider"].get("api_key", "")
    if api_key.startswith("${{"):
        api_key = ""

    if not api_key:
        print("Error: Set OPENROUTER_API_KEY environment variable")
        return

    bus = MessageBus()
    provider = LiteLLMProvider(
        api_key=api_key,
        api_base=config["provider"].get("api_base"),
        default_model=config.get("model"),
    )

    agent = AgentLoop(
        bus=bus,
        provider=provider,
        workspace=Path(__file__).parent,
        model=config.get("model"),
        max_iterations=config.get("max_iterations", 15),
    )

    print(f"🐛 {{config.get('name', 'Agent')}} is ready!")
    print("Type your message (Ctrl+C to exit)\\n")

    while True:
        try:
            user_input = input("You: ")
            if not user_input.strip():
                continue
            response = await agent.process_direct(user_input, session_key="cli")
            print(f"\\n🐛 {{response}}\\n")
        except KeyboardInterrupt:
            print("\\nGoodbye!")
            break


if __name__ == "__main__":
    asyncio.run(main())
'''


def _generate_readme(config: dict, personality: dict) -> str:
    return f"""# {config['name']}

{personality['emoji']} A ZergBot agent with **{personality['name']}** personality.

## Quick Start

```bash
# Set your API key
export OPENROUTER_API_KEY=sk-or-xxx

# Run the agent
zergbot run
# or
python main.py
```

## Configuration

Edit `config.yaml` to customize:
- Model selection
- Available tools
- Max iterations

## Project Structure

```
{config['name']}/
├── config.yaml    # Agent configuration
├── AGENT.md       # Agent personality & instructions
├── main.py        # Entry point
├── skills/        # Custom skills
└── memory/        # Agent memory (auto-generated)
```

---

Built with [ZergBot](https://github.com/superhello2099/zergbot) 🐛
"""


def _generate_gitignore() -> str:
    return """# Python
__pycache__/
*.py[cod]
.venv/
venv/

# ZergBot
memory/*.json
.zergbot/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
"""


async def run_project(config_path: Path, console: Console) -> None:
    """Run a ZergBot project from config file."""
    import os

    from zergbot import __logo__
    from zergbot.bus.queue import MessageBus
    from zergbot.providers.litellm_provider import LiteLLMProvider
    from zergbot.agent.loop import AgentLoop

    with open(config_path) as f:
        config = yaml.safe_load(f)

    project_dir = config_path.parent

    # Get API key
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        provider_config = config.get("provider", {})
        api_key = provider_config.get("api_key", "")
        if api_key.startswith("${"):
            api_key = ""

    if not api_key:
        console.print("[red]Error: No API key found[/red]")
        console.print("Set OPENROUTER_API_KEY:")
        console.print("  export OPENROUTER_API_KEY=sk-or-xxx")
        return

    name = config.get("name", "Agent")
    model = config.get("model", "openrouter/google/gemini-2.0-flash-001")

    console.print()
    console.print(
        Panel(
            Text.from_markup(
                f"[bold]{__logo__} {name}[/bold]\n[dim]Model: {model}[/dim]"
            ),
            border_style="bright_green",
            padding=(0, 2),
        )
    )
    console.print()

    bus = MessageBus()
    provider = LiteLLMProvider(
        api_key=api_key,
        api_base=config.get("provider", {}).get("api_base"),
        default_model=model,
    )

    agent = AgentLoop(
        bus=bus,
        provider=provider,
        workspace=project_dir,
        model=model,
        max_iterations=config.get("max_iterations", 15),
    )

    console.print("[green]Ready![/green] Type your message (Ctrl+C to exit)\n")

    while True:
        try:
            user_input = console.input("[bold blue]You:[/bold blue] ")
            if not user_input.strip():
                continue
            response = await agent.process_direct(user_input, session_key="project")
            console.print(f"\n{__logo__} {response}\n")
        except KeyboardInterrupt:
            console.print("\nGoodbye!")
            break
