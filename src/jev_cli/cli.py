from __future__ import annotations

import typer

from jev_cli.commands.ask import ask
from jev_cli.commands.auth import status as auth_status
from jev_cli.commands.models import models
from jev_cli.commands.oneshot import choice, noul, score
from jev_cli.commands.smoke import smoke

app = typer.Typer(
    name="jev",
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_enable=False,
    help="CLI for TypeSafe System One (Jev). Typed judgments, not chat.",
)

auth_app = typer.Typer(no_args_is_help=True, help="Authentication helpers")
auth_app.command("status")(auth_status)
app.add_typer(auth_app, name="auth")

app.command("ask")(ask)
app.command("noul")(noul)
app.command("choice")(choice)
app.command("score")(score)
app.command("models")(models)
app.command("smoke")(smoke)
