"""Scratch-like scripting layer for high-level gameplay logic."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Block:
    opcode: str
    args: tuple[object, ...] = ()


@dataclass
class ScriptBuilder:
    blocks: list[Block] = field(default_factory=list)

    def add_block(self, opcode: str, *args: object) -> "ScriptBuilder":
        self.blocks.append(Block(opcode=opcode, args=args))
        return self

    def move_steps(self, steps: float) -> "ScriptBuilder":
        return self.add_block("motion_move_steps", steps)

    def turn_right_degrees(self, degrees: float) -> "ScriptBuilder":
        return self.add_block("motion_turn_right", degrees)

    def say(self, message: str) -> "ScriptBuilder":
        return self.add_block("looks_say", message)

    def wait_seconds(self, seconds: float) -> "ScriptBuilder":
        return self.add_block("control_wait", seconds)


@dataclass
class Stage:
    scripts_by_event: dict[str, list[ScriptBuilder]] = field(default_factory=dict)

    def when_flag_clicked(self) -> ScriptBuilder:
        script = ScriptBuilder()
        self.scripts_by_event.setdefault("event_whenflagclicked", []).append(script)
        return script
