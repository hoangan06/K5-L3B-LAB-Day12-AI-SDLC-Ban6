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
            stove.update(state="idle", dish=None, cook_ticks_left=0, ready_ticks=0)
