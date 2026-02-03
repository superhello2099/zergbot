"""ZergBot Project Scaffolding - Create new agent projects."""

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from rich.console import Console


# Project templates
TEMPLATES = {
    "default": {
        "description": "General-purpose AI assistant",
        "config": {
            "name": "my-agent",
            "description": "A ZergBot AI agent",
            "model": "openrouter/google/gemini-2.0-flash-001",
            "provider": {
                "type": "openrouter",
                "api_key": "${OPENROUTER_API_KEY}",
            },
            "tools": ["read_file", "write_file", "exec", "web_search"],
            "max_iterations": 10,
        },
        "agent_instructions": """# Agent Instructions

You are a helpful AI assistant. Be concise, accurate, and friendly.

## Guidelines

- Always explain what you're doing before taking actions
- Ask for clarification when the request is ambiguous
- Use tools to help accomplish tasks
- Be proactive in suggesting solutions
""",
        "main_py": '''"""Main entry point for the agent."""

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

    # Get API key from env or config
    api_key = os.environ.get("OPENROUTER_API_KEY") or config["provider"].get("api_key", "")
    if api_key.startswith("${"):
        api_key = ""

    if not api_key:
        print("Error: Set OPENROUTER_API_KEY environment variable")
        print("  export OPENROUTER_API_KEY=sk-or-xxx")
        return

    bus = MessageBus()
    provider = LiteLLMProvider(
        api_key=api_key,
        default_model=config.get("model", "openrouter/google/gemini-2.0-flash-001"),
    )

    agent = AgentLoop(
        bus=bus,
        provider=provider,
        workspace=Path(__file__).parent,
        model=config.get("model"),
        max_iterations=config.get("max_iterations", 10),
    )

    print(f"🐛 {config.get('name', 'Agent')} is ready!")
    print("Type your message (Ctrl+C to exit)\\n")

    while True:
        try:
            user_input = input("You: ")
            if not user_input.strip():
                continue

            response = await agent.process_direct(user_input, session_key="cli")
            print(f"\\n🐛 {response}\\n")

        except KeyboardInterrupt:
            print("\\nGoodbye!")
            break


if __name__ == "__main__":
    asyncio.run(main())
''',
    },
    "research": {
        "description": "Research and summarization agent",
        "config": {
            "name": "research-agent",
            "description": "An agent specialized in research and summarization",
            "model": "openrouter/google/gemini-2.0-flash-001",
            "provider": {
                "type": "openrouter",
                "api_key": "${OPENROUTER_API_KEY}",
            },
            "tools": ["web_search", "web_fetch", "read_file", "write_file"],
            "max_iterations": 15,
        },
        "agent_instructions": """# Research Agent

You are a research specialist. Your job is to find information, analyze it, and provide clear summaries.

## Guidelines

- Search multiple sources for comprehensive information
- Cross-reference facts when possible
- Cite sources in your responses
- Structure information clearly with headers and bullet points
- Distinguish between facts and opinions

## Research Process

1. Understand the research question
2. Search for relevant sources
3. Extract key information
4. Synthesize findings
5. Present a clear summary with sources
""",
        "main_py": None,  # Uses default
    },
    "code-helper": {
        "description": "Coding assistant agent",
        "config": {
            "name": "code-helper",
            "description": "An agent that helps with coding tasks",
            "model": "openrouter/google/gemini-2.0-flash-001",
            "provider": {
                "type": "openrouter",
                "api_key": "${OPENROUTER_API_KEY}",
            },
            "tools": ["read_file", "write_file", "edit_file", "list_dir", "exec"],
            "max_iterations": 20,
        },
        "agent_instructions": """# Code Helper

You are a coding assistant. Help users write, debug, and improve code.

## Guidelines

- Read existing code before making changes
- Explain your changes and reasoning
- Follow the project's coding style
- Write tests when appropriate
- Handle errors gracefully

## Workflow

1. Understand the task
2. Explore relevant files
3. Plan the implementation
4. Make changes incrementally
5. Test and verify
""",
        "main_py": None,  # Uses default
    },
}


def create_project(project_dir: Path, template: str, console: "Console") -> None:
    """Create a new ZergBot project from a template."""
    if template not in TEMPLATES:
        available = ", ".join(TEMPLATES.keys())
        raise ValueError(f"Unknown template: {template}. Available: {available}")

    tmpl = TEMPLATES[template]
    config = tmpl["config"].copy()

    # Use project directory name as project name
    config["name"] = project_dir.name

    console.print(f"Creating project: [cyan]{project_dir.name}[/cyan]")
    console.print(f"Template: [cyan]{template}[/cyan] - {tmpl['description']}")
    console.print()

    # Create directory structure
    if project_dir.exists():
        shutil.rmtree(project_dir)

    project_dir.mkdir(parents=True)
    (project_dir / "skills").mkdir()
    (project_dir / "memory").mkdir()

    # Write config.yaml
    config_path = project_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    console.print(f"  [green]✓[/green] Created config.yaml")

    # Write AGENT.md
    agent_path = project_dir / "AGENT.md"
    agent_path.write_text(tmpl["agent_instructions"])
    console.print(f"  [green]✓[/green] Created AGENT.md")

    # Write main.py
    main_py = tmpl.get("main_py") or TEMPLATES["default"]["main_py"]
    main_path = project_dir / "main.py"
    main_path.write_text(main_py)
    console.print(f"  [green]✓[/green] Created main.py")

    # Write README.md
    readme_content = f"""# {config['name']}

{config.get('description', 'A ZergBot AI agent')}

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
{project_dir.name}/
├── config.yaml    # Agent configuration
├── AGENT.md       # Agent instructions/personality
├── main.py        # Entry point
├── skills/        # Custom skills (optional)
└── memory/        # Agent memory (auto-generated)
```

## Adding Custom Skills

Create `.md` files in the `skills/` directory. The agent will automatically load them.

---

Built with [ZergBot](https://github.com/superhello2099/zergbot)
"""
    readme_path = project_dir / "README.md"
    readme_path.write_text(readme_content)
    console.print(f"  [green]✓[/green] Created README.md")

    # Write .gitignore
    gitignore_content = """# Python
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
    gitignore_path = project_dir / ".gitignore"
    gitignore_path.write_text(gitignore_content)
    console.print(f"  [green]✓[/green] Created .gitignore")

    # Write example skill
    skill_content = """# Example Skill

This is an example skill file. The agent will read this to understand additional capabilities.

## Custom Commands

You can define custom behaviors here that the agent can learn from.

## Notes

- Skills are loaded automatically from the `skills/` directory
- Use markdown format for readability
- Be specific about what the agent should do
"""
    skill_path = project_dir / "skills" / "example.md"
    skill_path.write_text(skill_content)
    console.print(f"  [green]✓[/green] Created skills/example.md")


async def run_project(config_path: Path, console: "Console") -> None:
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
        console.print("Set OPENROUTER_API_KEY environment variable:")
        console.print("  export OPENROUTER_API_KEY=sk-or-xxx")
        return

    name = config.get("name", "Agent")
    model = config.get("model", "openrouter/google/gemini-2.0-flash-001")

    console.print(f"{__logo__} Starting [bold]{name}[/bold]")
    console.print(f"Model: {model}")
    console.print()

    bus = MessageBus()
    provider = LiteLLMProvider(
        api_key=api_key,
        default_model=model,
    )

    agent = AgentLoop(
        bus=bus,
        provider=provider,
        workspace=project_dir,
        model=model,
        max_iterations=config.get("max_iterations", 10),
    )

    console.print(
        f"{__logo__} [green]Ready![/green] Type your message (Ctrl+C to exit)\n"
    )

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
