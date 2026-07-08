from typing import Optional
from commands.command import Command
from commands.click_command import ClickCommand
from commands.jump_command import JumpCommand
from commands.wait_command import WaitCommand
from commands.print_command import PrintCommand


class CommandFactory:

    def __init__(self, move_validator, move_factory, move_scheduler):
        self._validator = move_validator
        self._factory = move_factory
        self._scheduler = move_scheduler

    def parse(self, line: str) -> Optional[Command]:
        parts = line.split()
        if not parts:
            return None

        name = parts[0]

        if name == "click":
            return ClickCommand(parts, self._validator, self._factory)
        if name == "jump":
            return JumpCommand(parts)
        if name == "wait":
            return WaitCommand(parts, self._scheduler)
        if name == "print" and len(parts) > 1 and parts[1] == "board":
            return PrintCommand()

        return None
