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
    world = ObjectGroup().set_viewport(0, 0, 20, 10)

    player = Object().set_size(1, 1).set_position(1, 5)
    coin = Object().set_size(1, 1).set_position(15, 5)
    world.add(player).add(coin)

    score = {"value": 0}

    @coin.on_click()
    def collect_coin() -> None:
        score["value"] += 1
        coin.set_position(15, 1 if score["value"] % 2 == 0 else 8)

    print("Small Game: reach the C coin with P.")
    print("Controls: a=left, d=right, w=up, s=down, q=quit")

    while True:
        px = int(player.get_meta("x"))
        py = int(player.get_meta("y"))
        cx = int(coin.get_meta("x"))
        cy = int(coin.get_meta("y"))
        print(f"Player=({px},{py}) Coin=({cx},{cy}) Score={score['value']}")

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

        nx = max(0, min(19, px + dx))
        ny = max(0, min(9, py + dy))
        player.set_position(nx, ny)

        if player.status == STATUS_ACTIVE and intersects(player, coin):
            coin.trigger_click()


if __name__ == "__main__":
    run()
