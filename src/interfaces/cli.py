"""
TARS CLI Interface
Beautiful command-line interface for interacting with TARS.
"""

import sys
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.live import Live
from rich.text import Text
import typer

# Add src to path for imports
sys.path.insert(0, str(__file__).rsplit('src', 1)[0])

from src.core import TARSEngine, get_tars_engine
from src.voice import VoiceInterface, create_voice_interface, VOICE_AVAILABLE
from src.utils.config import get_config


app = typer.Typer(
    name="tars",
    help="TARS: A sarcastic AI chatbot inspired by Interstellar",
    add_completion=False
)

console = Console()


def print_tars_header():
    """Print the TARS ASCII art header."""
    header = """
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   ████████╗ █████╗ ██████╗ ███████╗                           ║
║   ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝                           ║
║      ██║   ███████║██████╔╝███████╗                           ║
║      ██║   ██╔══██║██╔══██╗╚════██║                           ║
║      ██║   ██║  ██║██║  ██║███████║                           ║
║      ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝                           ║
║                                                                ║
║   Tactical AI Robot Sidekick | Humor: 60% | Honesty: 90%      ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"""
    console.print(header, style="cyan bold")


def print_greeting(engine: TARSEngine):
    """Print TARS greeting."""
    greeting = engine.get_greeting()
    console.print(Panel(
        greeting,
        title="[bold cyan]TARS[/bold cyan]",
        border_style="cyan",
        padding=(0, 2)
    ))


def print_response(response: str):
    """Print a TARS response with formatting."""
    console.print(Panel(
        Markdown(response),
        title="[bold cyan]TARS[/bold cyan]",
        border_style="cyan",
        padding=(0, 2)
    ))


def print_streaming_response(engine: TARSEngine, user_input: str):
    """Print a streaming response."""
    console.print("[bold cyan]TARS:[/bold cyan] ", end="")
    
    full_response = ""
    for chunk in engine.chat_stream(user_input):
        console.print(chunk, end="")
        full_response += chunk
    
    console.print()  # New line after response


def run_chat_loop(engine: TARSEngine, voice: VoiceInterface | None = None, stream: bool = False):
    """Run the main chat loop."""
    while True:
        try:
            # Get input
            if voice and voice.enabled:
                console.print("[dim]Listening...[/dim]")
                user_input = voice.listen()
                if user_input:
                    console.print(f"[bold green]You:[/bold green] {user_input}")
                else:
                    console.print("[yellow]Didn't catch that. Try again or type your message.[/yellow]")
                    user_input = Prompt.ask("[bold green]You[/bold green]")
            else:
                user_input = Prompt.ask("[bold green]You[/bold green]")
            
            if not user_input.strip():
                continue
            
            # Check for exit
            if user_input.lower() in ['bye', 'goodbye', 'exit', 'quit', 'q']:
                response = engine.chat(user_input)
                print_response(response)
                if voice and voice.enabled:
                    voice.speak(response)
                break
            
            # Check for special commands
            if user_input.startswith('/'):
                handle_command(user_input, engine)
                continue
            
            # Get response
            if stream:
                print_streaming_response(engine, user_input)
            else:
                response = engine.chat(user_input)
                print_response(response)
                
                if voice and voice.enabled:
                    voice.speak(response)
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Type 'bye' to exit properly.[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


def handle_command(command: str, engine: TARSEngine):
    """Handle CLI commands."""
    cmd = command.lower().strip()
    
    if cmd == '/help':
        help_text = """
## TARS Commands

| Command | Description |
|---------|-------------|
| `/help` | Show this help message |
| `/clear` | Clear conversation history |
| `/humor <value>` | Set humor level (0-100) |
| `/honesty <value>` | Set honesty level (0-100) |
| `/settings` | Show current settings |
| `/history` | Show conversation history |
| `bye` or `exit` | Exit TARS |

Type anything else to chat with TARS!
"""
        console.print(Panel(Markdown(help_text), title="Help", border_style="blue"))
    
    elif cmd == '/clear':
        engine.clear_memory()
        console.print("[green]Conversation history cleared.[/green]")
    
    elif cmd.startswith('/humor'):
        try:
            value = int(cmd.split()[1])
            settings = engine.update_personality(humor=value / 100)
            console.print(f"[green]Humor set to {settings['humor']}%[/green]")
        except (IndexError, ValueError):
            console.print("[red]Usage: /humor <0-100>[/red]")
    
    elif cmd.startswith('/honesty'):
        try:
            value = int(cmd.split()[1])
            settings = engine.update_personality(honesty=value / 100)
            console.print(f"[green]Honesty set to {settings['honesty']}%[/green]")
        except (IndexError, ValueError):
            console.print("[red]Usage: /honesty <0-100>[/red]")
    
    elif cmd == '/settings':
        config = get_config()
        settings_text = f"""
**Current TARS Settings:**
- Humor: {int(config.tars_humor_level * 100)}%
- Honesty: {int(config.tars_honesty_level * 100)}%
- Discretion: {int(config.tars_discretion_level * 100)}%
- LLM Provider: {config.llm_provider}
- Voice Enabled: {config.voice_enabled}
- RAG Enabled: {config.rag_enabled}
"""
        console.print(Panel(Markdown(settings_text), title="Settings", border_style="blue"))
    
    elif cmd == '/history':
        history = engine.get_conversation_history()
        if not history:
            console.print("[dim]No conversation history.[/dim]")
        else:
            for msg in history[-10:]:  # Show last 10 messages
                role = "You" if msg['role'] == 'user' else "TARS"
                style = "green" if msg['role'] == 'user' else "cyan"
                console.print(f"[bold {style}]{role}:[/bold {style}] {msg['content'][:100]}...")
    
    else:
        console.print(f"[yellow]Unknown command: {command}. Type /help for commands.[/yellow]")


@app.command()
def chat(
    voice: bool = typer.Option(False, "--voice", "-v", help="Enable voice input/output"),
    stream: bool = typer.Option(False, "--stream", "-s", help="Enable streaming responses"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="LLM provider (openai, gemini, lm_studio, ollama)"),
):
    """
    Start an interactive chat session with TARS.
    """
    print_tars_header()
    
    # Override provider if specified
    config = get_config()
    if provider:
        config.llm_provider = provider
    
    # Initialize engine
    try:
        engine = get_tars_engine()
    except Exception as e:
        console.print(f"[red]Failed to initialize TARS: {e}[/red]")
        console.print("[yellow]Make sure your LLM provider is running (e.g., LM Studio on localhost:1234)[/yellow]")
        raise typer.Exit(1)
    
    # Initialize voice if requested
    voice_interface = None
    if voice:
        if VOICE_AVAILABLE:
            voice_interface = create_voice_interface()
            if voice_interface:
                console.print("[green]Voice mode enabled[/green]")
            else:
                console.print("[yellow]Voice initialization failed, using text mode[/yellow]")
        else:
            console.print("[yellow]Voice packages not installed. Using text mode.[/yellow]")
    
    # Print greeting
    print_greeting(engine)
    
    # Run chat loop
    console.print("[dim]Type '/help' for commands, 'bye' to exit[/dim]\n")
    run_chat_loop(engine, voice_interface, stream)
    
    console.print("\n[cyan]TARS signing off. Until next time, slick![/cyan]")


@app.command()
def ask(
    question: str = typer.Argument(..., help="Question to ask TARS"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="LLM provider"),
):
    """
    Ask TARS a single question.
    """
    config = get_config()
    if provider:
        config.llm_provider = provider
    
    try:
        engine = get_tars_engine()
        response = engine.chat(question)
        console.print(Panel(
            Markdown(response),
            title="[bold cyan]TARS[/bold cyan]",
            border_style="cyan"
        ))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def settings():
    """
    Show current TARS settings.
    """
    config = get_config()
    console.print(Panel(
        f"""
[bold]TARS Configuration[/bold]

[cyan]Personality:[/cyan]
  Humor:     {int(config.tars_humor_level * 100)}%
  Honesty:   {int(config.tars_honesty_level * 100)}%
  Discretion: {int(config.tars_discretion_level * 100)}%

[cyan]LLM Provider:[/cyan] {config.llm_provider}
  LM Studio: {config.lm_studio_base_url}
  Model:     {config.lm_studio_model}

[cyan]Features:[/cyan]
  Voice:     {'Enabled' if config.voice_enabled else 'Disabled'}
  RAG:       {'Enabled' if config.rag_enabled else 'Disabled'}
        """,
        title="Settings",
        border_style="blue"
    ))


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
