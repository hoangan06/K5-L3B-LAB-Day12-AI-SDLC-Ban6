from math import dist, floor

from .. import TICK_HZ
from ..ids import id_key, sort_by_id


def finish_cooking(sim, events: list) -> None:
    for stove in sort_by_id(sim.stoves):
        if stove["state"] == "cooking" and stove["cook_ticks_left"] == 0:
            stove.update(state="ready", ready_ticks=0)
            events.append(_stove_event("dish_ready", stove, stove["dish"]))


def interact(sim, events: list) -> None:
    targets = (
        (dist(sim.pos, entity["pos"]), is_table, id_key(entity["id"]), entity)
        for is_table, entities in ((False, sim.stoves), (True, sim.tables))
        for entity in entities
    )
    nearest = min(targets, key=lambda target: target[:3], default=None)
    if nearest is None:
        return

    distance, is_table, _, target = nearest
    if distance > sim.t["interact_radius"]:
        return

    if is_table:
        _serve(sim, target, events)
    elif target["state"] == "idle":
        _start_cooking(sim, target, events)
    elif target["state"] == "ready" and sim.hand is None:
        sim.hand = target["dish"]
        _clear_stove(target)
        events.append(_stove_event("dish_picked", target, sim.hand))


def pay_customer(sim, customer: dict, reason: str, events: list) -> None:
    base_price = customer["base_price"]
    tip = customer["tip"]
    amount = base_price + tip
    sim.money += amount
    sim.earned += amount
    sim.shift_earned += amount

    if tip > 0:
        reputation = sim.reputation + sim.t["tip_reputation"]
        sim.reputation = min(sim.t["reputation_max"], max(sim.t["reputation_min"], reputation))

    events.append((
        "paid",
        {
            "order_id": customer["id"],
            "table_id": customer["table_id"],
            "base_price": base_price,
            "tip": tip,
            "amount": amount,
            "reason": reason,
        },
    ))


def discard_order(sim, order_id: str) -> None:
    if sim.hand is not None and sim.hand["order_id"] == order_id:
        sim.hand = None

    for stove in sim.stoves:
        dish = stove["dish"]
        if dish is not None and dish["order_id"] == order_id:
            _clear_stove(stove)


def _start_cooking(sim, stove, events):
    orders = (
        customer for customer in sim.customers
        if customer["state"] == "waiting" and customer["order_status"] == "reserved"
    )
    customer = min(orders, key=lambda order: (order["order_tick"], id_key(order["table_id"])), default=None)
    if customer is None:
        return

    dish_id = customer["dish_id"]
    menu_item = sim.menu[dish_id]
    dish = {"order_id": customer["id"], "dish_id": dish_id, "base_price": menu_item["price"]}
    items = []
    for kind, count in sorted(customer["reserved"].items()):
        sim.stock[kind] -= count
        items.extend([kind] * count)

    customer.update(order_status="assigned", reserved={})
    stove.update(state="cooking", dish=dish, cook_ticks_left=round(menu_item["cook_s"] * TICK_HZ), ready_ticks=0)
    events.append(("cook_started", {"stove_id": stove["id"], **dish, "items": items}))


def _serve(sim, table, events):
    dish = sim.hand
    if dish is None:
        return
    customer = next((c for c in sim.customers if c["table_id"] == table["id"]), None)
    if (customer is None or customer["id"] != dish["order_id"]
            or customer["state"] != "waiting" or customer["order_status"] != "assigned"):
        return

    base_price = dish["base_price"]
    patience = customer["patience_ticks_left"]
    max_patience = round(sim.t["patience_s"] * TICK_HZ)
    tip = 0
    if patience / max_patience >= sim.t["tip_min_patience_ratio"]:
        tip = floor(base_price * sim.t["tip_rate"])

    customer.update(
        state="eating",
        order_status="served",
        eat_ticks_left=round(sim.t["eat_s"] * TICK_HZ),
        base_price=base_price,
        tip=tip,
    )
    sim.hand = None
    events.append(("served", {**dish, "table_id": table["id"], "patience_ticks_left": patience, "tip": tip}))


def _clear_stove(stove):
    stove.update(state="idle", dish=None, cook_ticks_left=0, ready_ticks=0)


def _stove_event(name, stove, dish):
    return name, {"stove_id": stove["id"], "order_id": dish["order_id"], "dish_id": dish["dish_id"]}
