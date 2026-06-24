"""장바구니 할인 계산 — Entity 계층."""

from typing import Sequence

Item = tuple[int, int]  # (price, qty)


def subtotal(items: Sequence[Item]) -> int:
    return sum(price * qty for price, qty in items)  # INV-1


def _apply_threshold(amount: int) -> int:
    if amount >= 50000:  # INV-2
        return round(amount * 0.9)
    return amount  # INV-2


def calculate_final(items: Sequence[Item], is_vip: bool = False) -> int:
    after_threshold = _apply_threshold(subtotal(items))  # INV-2, INV-3
    if is_vip:
        return round(after_threshold * 0.95)  # INV-3
    return after_threshold  # INV-3, INV-4
