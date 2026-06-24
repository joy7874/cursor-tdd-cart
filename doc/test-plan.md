# Test Plan — INV-1 · INV-3 · INV-4

| 항목 | 내용 |
|------|------|
| **프로젝트** | cursor-tdd-cart (장바구니 할인 계산기) |
| **계층** | Entity (`src/cart.py`) |
| **테스트 파일** | `tests/test_cart.py` |
| **현재 단계** | RED 준비 |
| **근거 문서** | [README.md](../README.md) |

계약 ID에 없는 동작은 테스트·구현 모두 **작성하지 않는다.**

---

## 1. 범위

본 테스트 플랜은 아래 계약만 다룬다.

| ID | 계약 | 근거 레벨 |
|----|------|-----------|
| INV-1 | `subtotal(items) == Σ(price × qty)` | — |
| INV-3 | `final = 문턱할인 적용 후, VIP면 round(×0.95)`. 순서 문턱→VIP 고정 | L2 |
| INV-4 | 모든 입력에서 `0 ≤ final_total ≤ subtotal`. 할인은 금액을 늘리지 않는다 | L3 |

> **INV-3 의존성:** 문턱 할인 단계는 [INV-2](../README.md)가 정의한다. INV-3 테스트는 문턱 단계 결과를 전제로 하며, INV-2 구현·테스트가 선행되거나 테스트 픽스처로 문턱 결과를 고정한다.

---

## 2. 공통 규칙

- 테스트 함수명·주석에 계약 ID를 명시한다. 예: `test_subtotal_sums_line_totals_inv1`
- `pytest` 마커: `@pytest.mark.entity`
- RED 단계: `tests/`만 수정, `src/cart.py`는 건드리지 않는다.
- 입력 형식(가정): `items`는 `(price, qty)` 튜플의 리스트. 계약에 없는 필드(품목명 등)는 사용하지 않는다.

---

## 3. INV-1 — `subtotal(items) == Σ(price × qty)`

### 3.1 목표

각 품목 `price × qty`의 합이 `subtotal` 반환값과 같음을 검증한다.

### 3.2 테스트 케이스

| # | 케이스 ID | 입력 `items` | 기대 `subtotal` | 비고 |
|---|-----------|--------------|-----------------|------|
| 1 | INV-1-T01 | `[(12000, 3)]` | `36000` | 단일 품목 |
| 2 | INV-1-T02 | `[(12000, 3), (30000, 1)]` | `66000` | 복수 품목 (인터뷰 2024-03-12) |
| 3 | INV-1-T03 | `[(10000, 1), (20000, 2)]` | `50000` | 경계 소계 (INV-2 연계용) |
| 4 | INV-1-T04 | `[(48000, 1)]` | `48000` | 할인 없음 소계 (#1042) |

### 3.3 RED 테스트 스케치

```python
@pytest.mark.entity
def test_subtotal_single_item_inv1():
    assert subtotal([(12000, 3)]) == 36000  # INV-1

@pytest.mark.entity
def test_subtotal_multiple_items_inv1():
    assert subtotal([(12000, 3), (30000, 1)]) == 66000  # INV-1
```

### 3.4 구현 대상 (GREEN)

- `subtotal(items)` — `src/cart.py`

---

## 4. INV-3 — 문턱 → VIP 순서, VIP 시 `round(×0.95)`

### 4.1 목표

1. 최종 금액은 **문턱 할인 적용 후** 값에서 계산한다.
2. VIP이면 `round(문턱결과 × 0.95)`를 적용한다.
3. 비VIP이면 문턱 단계 결과가 최종 금액이다.
4. VIP 5%는 문턱 **이전** 소계에 직접 적용하지 않는다 (순서 검증).

### 4.2 테스트 케이스

| # | 케이스 ID | 소계 | VIP | 기대 `final` | 근거 |
|---|-----------|------|-----|--------------|------|
| 1 | INV-3-T01 | `66000` | `False` | `59400` | 문턱만: `round(66000×0.9)` |
| 2 | INV-3-T02 | `66000` | `True` | `56430` | 문턱 후 VIP: `round(59400×0.95)` (엑셀 검산) |
| 3 | INV-3-T03 | `48000` | `True` | `45600` | 문턱 없음 후 VIP: `round(48000×0.95)` |
| 4 | INV-3-T04 | `60000` | `False` | `54000` | #1107 |
| 5 | INV-3-T05 | `66000` | `True` | ≠ `62700` | **순서 검증:** `round(66000×0.95)`가 아님 |

### 4.3 RED 테스트 스케치

```python
@pytest.mark.entity
def test_final_vip_after_threshold_inv3():
    # items → subtotal 66000, is_vip=True
    assert calculate_final([(12000, 3), (30000, 1)], is_vip=True) == 56430  # INV-3

@pytest.mark.entity
def test_final_non_vip_skips_vip_discount_inv3():
    assert calculate_final([(12000, 3), (30000, 1)], is_vip=False) == 59400  # INV-3

@pytest.mark.entity
def test_vip_applied_after_threshold_not_before_inv3():
    result = calculate_final([(12000, 3), (30000, 1)], is_vip=True)
    assert result != round(66000 * 0.95)  # INV-3 순서 고정
```

### 4.4 구현 대상 (GREEN)

- `calculate_final(items, is_vip)` (또는 동등 API) — `src/cart.py`
- 내부 호출 순서: `subtotal` → 문턱(INV-2) → VIP 조건부(INV-3)

---

## 5. INV-4 — `0 ≤ final_total ≤ subtotal`

### 5.1 목표

유효 입력( E-1·E-2를 통과한 `items` )에 대해 최종 금액이 항상 소계 이하·0 이상임을 검증한다. 할인으로 금액이 증가하지 않음을 확인한다.

### 5.2 테스트 케이스

| # | 케이스 ID | 입력 | 검증 조건 | 비고 |
|---|-----------|------|-----------|------|
| 1 | INV-4-T01 | INV-3-T01~T04 각 케이스 | `0 ≤ final ≤ subtotal` | 통합 불변식 |
| 2 | INV-4-T02 | `[(0, 0)]` | `final == 0`, `final ≤ subtotal` | 하한 0 |
| 3 | INV-4-T03 | `[(50000, 1)]`, VIP `True` | `final ≤ 50000` | 경계 소계 |
| 4 | INV-4-T04 | `[(100000, 1)]`, VIP `False` | `final < subtotal` | 할인 시 엄격 부등호 |

### 5.3 RED 테스트 스케치

```python
@pytest.mark.parametrize("items,is_vip", [
    ([(12000, 3), (30000, 1)], False),
    ([(12000, 3), (30000, 1)], True),
    ([(48000, 1)], False),
    ([(60000, 1)], False),
])
@pytest.mark.entity
def test_final_within_bounds_inv4(items, is_vip):
    st = subtotal(items)
    final = calculate_final(items, is_vip=is_vip)
    assert 0 <= final <= st  # INV-4
    assert final <= st       # 할인은 금액을 늘리지 않는다
```

### 5.4 구현 대상 (GREEN)

- `calculate_final` 반환값이 INV-4를 항상 만족하도록 보장 — `src/cart.py`

---

## 6. RED 작성 순서 (권장)

```text
INV-1 (subtotal)
  ↓
INV-3 (calculate_final — INV-2 문턱 로직 포함 또는 픽스처)
  ↓
INV-4 (범위 불변식 — parametrize로 INV-3 케이스 재사용)
```

---

## 7. 실행

```bash
pytest tests/test_cart.py -q -m entity
```

전체:

```bash
pytest -q
```

---

## 8. Out of Scope (본 플랜 미포함)

- INV-2 단독 문턱 경계 상세 (별도 플랜 또는 README 계약 표 참조)
- E-1 (`items is None`), E-2 (음수 price/qty)
- 쿠폰, 배송비, 세금, 포인트
- UI, API, DB

---

*본 문서는 doc/test-plan.md — INV-1 · INV-3 · INV-4 Entity 계약 테스트 플랜입니다.*
