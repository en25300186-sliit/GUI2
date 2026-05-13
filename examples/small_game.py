"""Small game example built with GUI2 Object/ObjectGroup primitives.

Run:
    python examples/small_game.py
"""

from __future__ import annotations

from gui2 import STATUS_ACTIVE, Object, ObjectGroup


def intersects(a: Object, b: Object) -> bool:
    ax = float(a.get_meta("x", 0.0))
    ay = float(a.get_meta("y", 0.0))
    aw = float(a.get_meta("width", 0.0))
    ah = float(a.get_meta("height", 0.0))

    bx = float(b.get_meta("x", 0.0))
    by = float(b.get_meta("y", 0.0))
    bw = float(b.get_meta("width", 0.0))
    bh = float(b.get_meta("height", 0.0))

    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def run() -> None:
    viewport_x, viewport_y, viewport_width, viewport_height = 0, 0, 20, 10
    coin_x = viewport_x + viewport_width - 5
    coin_y_positions = (1, 8)

    world = ObjectGroup().set_viewport(viewport_x, viewport_y, viewport_width, viewport_height)

    player = Object().set_size(1, 1).set_position(1, 5)
    coin = Object().set_size(1, 1).set_position(coin_x, 5)
    world.add(player).add(coin)

    score = 0

    @player.on_collide()
    def on_player_collide(other: Object) -> None:
        nonlocal score
        if other is coin:
            score += 1
            coin.set_position(coin_x, coin_y_positions[score % 2])

    print("Small Game: reach the coin (C) with the player (P).")
    print("Controls: a=left, d=right, w=up, s=down, q=quit")

    while True:
        px = int(player.get_meta("x"))
        py = int(player.get_meta("y"))
        cx = int(coin.get_meta("x"))
        cy = int(coin.get_meta("y"))
        print(f"Player=({px},{py}) Coin=({cx},{cy}) Score={score}")

        move = input("move> ").strip().lower()
        if move == "q":
            print("Bye!")
            break

        dx, dy = 0, 0
        if move == "a":
            dx = -1
        elif move == "d":
            dx = 1
        elif move == "w":
            dy = -1
        elif move == "s":
            dy = 1
        else:
            print("Invalid input.")
            continue

        nx = max(viewport_x, min(viewport_x + viewport_width - 1, px + dx))
        ny = max(viewport_y, min(viewport_y + viewport_height - 1, py + dy))
        player.set_position(nx, ny)

        # This example performs collision checks in the loop, then triggers callbacks.
        if player.status == STATUS_ACTIVE and intersects(player, coin):
            player.trigger_collide(coin)


if __name__ == "__main__":
    run()
