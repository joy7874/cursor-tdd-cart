"""Entity 계약 테스트 — INV-1, INV-3, INV-4 (doc/test-plan.md)"""

import pytest

from src.cart import calculate_final, subtotal


# --- INV-1: subtotal(items) == Σ(price × qty) ---


@pytest.mark.entity
def test_subtotal_single_item_inv1_t01():
    assert subtotal([(12000, 3)]) == 36000  # INV-1-T01


@pytest.mark.entity
def test_subtotal_multiple_items_inv1_t02():
    assert subtotal([(12000, 3), (30000, 1)]) == 66000  # INV-1-T02


@pytest.mark.entity
def test_subtotal_boundary_sum_inv1_t03():
    assert subtotal([(10000, 1), (20000, 2)]) == 50000  # INV-1-T03


@pytest.mark.entity
def test_subtotal_no_discount_case_inv1_t04():
    assert subtotal([(48000, 1)]) == 48000  # INV-1-T04


# --- INV-3: 문턱 → VIP, VIP면 round(×0.95) ---


@pytest.mark.entity
def test_final_threshold_only_inv3_t01():
    assert calculate_final([(12000, 3), (30000, 1)], is_vip=False) == 59400  # INV-3-T01


@pytest.mark.entity
def test_final_vip_after_threshold_inv3_t02():
    assert calculate_final([(12000, 3), (30000, 1)], is_vip=True) == 56430  # INV-3-T02


@pytest.mark.entity
def test_final_vip_below_threshold_inv3_t03():
    assert calculate_final([(48000, 1)], is_vip=True) == 45600  # INV-3-T03


@pytest.mark.entity
def test_final_order_1107_inv3_t04():
    assert calculate_final([(60000, 1)], is_vip=False) == 54000  # INV-3-T04


@pytest.mark.entity
def test_vip_applied_after_threshold_not_before_inv3_t05():
    result = calculate_final([(12000, 3), (30000, 1)], is_vip=True)
    assert result != round(66000 * 0.95)  # INV-3-T05


# --- INV-4: 0 ≤ final_total ≤ subtotal ---


@pytest.mark.parametrize(
    "items,is_vip",
    [
        ([(12000, 3), (30000, 1)], False),  # INV-3-T01
        ([(12000, 3), (30000, 1)], True),   # INV-3-T02
        ([(48000, 1)], False),              # #1042
        ([(60000, 1)], False),              # INV-3-T04
    ],
)
@pytest.mark.entity
def test_final_within_bounds_inv4_t01(items, is_vip):
    st = subtotal(items)
    final = calculate_final(items, is_vip=is_vip)
    assert 0 <= final <= st  # INV-4-T01
    assert final <= st


@pytest.mark.entity
def test_final_zero_lower_bound_inv4_t02():
    items = [(0, 0)]
    st = subtotal(items)
    final = calculate_final(items, is_vip=False)
    assert final == 0  # INV-4-T02
    assert final <= st


@pytest.mark.entity
def test_final_at_threshold_subtotal_inv4_t03():
    items = [(50000, 1)]
    st = subtotal(items)
    final = calculate_final(items, is_vip=True)
    assert final <= st  # INV-4-T03


@pytest.mark.entity
def test_final_strictly_below_subtotal_when_discounted_inv4_t04():
    items = [(100000, 1)]
    st = subtotal(items)
    final = calculate_final(items, is_vip=False)
    assert final < st  # INV-4-T04
