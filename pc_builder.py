"""
Программа подбора совместимых комплектующих для ПК
Новый алгоритм: от самого дешёвого совместимого с автоулучшением
"""

import streamlit as st
import math
import json
from datetime import datetime

# Загрузка базы из JSON-файла
@st.cache_data
def load_database():
    with open("components.json", "r", encoding="utf-8") as f:
        return json.load(f)

DATABASE = load_database()

CATEGORY_LABELS = {
    "cpu": "Процессор",
    "motherboard": "Материнская плата",
    "ram": "Оперативная память",
    "gpu": "Видеокарта",
    "psu": "Блок питания",
    "case": "Корпус",
}

if 'pc' not in st.session_state:
    st.session_state.pc = None
if 'step' not in st.session_state:
    st.session_state.step = 'input'
if 'budget' not in st.session_state:
    st.session_state.budget = 0
if 'purpose' not in st.session_state:
    st.session_state.purpose = 'gaming'
if 'existing' not in st.session_state:
    st.session_state.existing = {}
if 'warnings' not in st.session_state:
    st.session_state.warnings = []


def get_price(item):
    if not item.get("shops"):
        return item.get("price", 0)
    return min(shop["price"] for shop in item["shops"])


def get_best_shop(item):
    if not item.get("shops"):
        return None
    return min(item["shops"], key=lambda s: s["price"])


def check_compatibility(cpu, mb, ram, gpu, psu, case):
    msgs = []
    if cpu["socket"] != mb["socket"]:
        msgs.append(f"Разные сокеты: у процессора «{cpu['socket']}», у платы «{mb['socket']}» — физически несовместимы, нужна плата с сокетом {cpu['socket']}")
    if ram["type"] != mb["ram_type"]:
        msgs.append(f"Разный тип памяти: ОЗУ — «{ram['type']}», плата поддерживает только «{mb['ram_type']}» — модуль не войдёт в разъём")
    if case["form_factor"] != mb["form_factor"]:
        msgs.append(f"Корпус ({case['form_factor']}) не подходит плате ({mb['form_factor']}). Нужен корпус {mb['form_factor']}")
    total_tdp = cpu["tdp"] + gpu["tdp"] + 50
    required = math.ceil(total_tdp * 1.3)
    if psu["power"] < required:
        msgs.append(f"Недостаточно мощности БП: системе нужно ~{required} Вт, а установленный БП выдает только {psu['power']} Вт")
    return msgs


def get_compatibility_status(category, item, pc):
    test_pc = pc.copy()
    test_pc[category] = item
    msgs = check_compatibility(
        test_pc.get("cpu", pc.get("cpu")),
        test_pc.get("motherboard", pc.get("motherboard")),
        test_pc.get("ram", pc.get("ram")),
        test_pc.get("gpu", pc.get("gpu")),
        test_pc.get("psu", pc.get("psu")),
        test_pc.get("case", pc.get("case"))
    )
    return len(msgs) == 0, msgs


# ====================== ИНТЕРФЕЙС ======================
st.set_page_config(page_title="Подбор ПК", layout="wide")
st.title("🖥️ Подбор комплектующих ПК с проверкой совместимости")

st.header("Шаг 1. Параметры")
col1, col2 = st.columns(2)
with col1:
    budget = st.number_input("💰 Ваш бюджет (руб.)", min_value=0, max_value=500000, value=80000, step=5000)
with col2:
    purpose = st.selectbox("🎯 Назначение", ["Офисные задачи", "Игры и графика"])

# Блок имеющихся комплектующих
with st.expander("🔧 У меня уже есть комплектующие", expanded=False):
    st.write("Выберите компоненты, которые уже есть. Программа подберёт только недостающие и учтёт совместимость.")
    existing = {}
    for key in ["cpu", "motherboard", "ram", "gpu", "psu", "case"]:
        all_items = DATABASE[key]
        item_labels = ["— Не выбрано —"] + [f"{item['model']} (~{get_price(item)} руб.)" for item in all_items]
        selected = st.selectbox(f"{CATEGORY_LABELS[key]}:", item_labels, key=f"existing_{key}")
        if selected != "— Не выбрано —":
            model_name = selected.split(" (~")[0]
            for item in all_items:
                if item["model"] == model_name:
                    existing[key] = item
                    break
    st.session_state.existing = existing
    if existing:
        st.success(f"✅ Учтено компонентов: {len(existing)} шт.")

if st.button("🔍 Подобрать сборку", type="primary"):
    st.session_state.step = "review"
    st.session_state.budget = budget
    purpose_key = "office" if purpose == "Офисные задачи" else "gaming"
    st.session_state.purpose = purpose_key
    existing = st.session_state.existing
    warnings = []
    pc = {}
    remaining = budget

    # --- НОВЫЙ АЛГОРИТМ: сначала всё самое дешёвое совместимое, потом улучшаем ---

    # 1. Выбираем CPU (самый дешёвый из подходящих по назначению)
    if "cpu" in existing:
        pc["cpu"] = existing["cpu"]
    else:
        candidates = sorted([c for c in DATABASE["cpu"] if c.get("purpose") == purpose_key], key=get_price)
        cpu = None
        for c in candidates:
            if get_price(c) <= remaining:
                cpu = c
                remaining -= get_price(c)
                break
        if cpu is None:
            st.error("❌ Ни один процессор не влезает в бюджет.")
            st.stop()
        pc["cpu"] = cpu

    # 2. Материнская плата (самая дешёвая совместимая)
    if "motherboard" in existing:
        pc["motherboard"] = existing["motherboard"]
    else:
        candidates = sorted([m for m in DATABASE["motherboard"] if m["socket"] == pc["cpu"]["socket"]], key=get_price)
        mb = None
        for m in candidates:
            if get_price(m) <= remaining:
                mb = m
                remaining -= get_price(m)
                break
        if mb is None:
            st.error("❌ Ни одна материнская плата не влезает в бюджет.")
            st.stop()
        pc["motherboard"] = mb

    # 3. ОЗУ (самая дешёвая совместимая)
    if "ram" in existing:
        pc["ram"] = existing["ram"]
    else:
        candidates = sorted([r for r in DATABASE["ram"] if r["type"] == pc["motherboard"]["ram_type"]], key=get_price)
        ram = None
        for r in candidates:
            if get_price(r) <= remaining:
                ram = r
                remaining -= get_price(r)
                break
        if ram is None:
            st.error("❌ Ни один модуль ОЗУ не влезает в бюджет.")
            st.stop()
        pc["ram"] = ram

    # 4. Видеокарта (самая дешёвая)
    if "gpu" in existing:
        pc["gpu"] = existing["gpu"]
    else:
        candidates = sorted([g for g in DATABASE["gpu"] if g.get("purpose") == purpose_key], key=get_price)
        gpu = None
        for g in candidates:
            if get_price(g) <= remaining:
                gpu = g
                remaining -= get_price(g)
                break
        if gpu is None:
            st.error("❌ Ни одна видеокарта не влезает в бюджет.")
            st.stop()
        pc["gpu"] = gpu

    # 5. Блок питания (самый дешёвый, но достаточный по мощности)
    if "psu" in existing:
        psu = existing["psu"]
        required_watt = math.ceil((pc["cpu"]["tdp"] + pc["gpu"]["tdp"] + 50) * 1.3)
        if psu["power"] < required_watt:
            warnings.append(f"⚠️ Ваш блок питания ({psu['power']} Вт) недостаточен для выбранных CPU+GPU. Требуется ~{required_watt} Вт. Рекомендуем заменить БП.")
            # Всё равно оставляем, но предупреждаем
        pc["psu"] = psu
    else:
        required_watt = math.ceil((pc["cpu"]["tdp"] + pc["gpu"]["tdp"] + 50) * 1.3)
        candidates = sorted([p for p in DATABASE["psu"] if p["power"] >= required_watt], key=get_price)
        psu = None
        for p in candidates:
            if get_price(p) <= remaining:
                psu = p
                remaining -= get_price(p)
                break
        if psu is None:
            # Предупреждаем, но не падаем — показываем самый дешёвый БП нужной мощности и говорим, сколько не хватает
            cheapest_compatible = candidates[0]
            shortfall = get_price(cheapest_compatible) - remaining
            warnings.append(f"⚠️ На блок питания ({cheapest_compatible['model']}, {cheapest_compatible['power']} Вт) не хватает {shortfall} руб. Показан самый дешёвый подходящий вариант.")
            psu = cheapest_compatible
            remaining -= get_price(psu)
        pc["psu"] = psu

    # 6. Корпус (самый дешёвый совместимый)
    if "case" in existing:
        pc["case"] = existing["case"]
    else:
        candidates = sorted([c for c in DATABASE["case"] if c["form_factor"] == pc["motherboard"]["form_factor"]], key=get_price)
        case_ = None
        for c in candidates:
            if get_price(c) <= remaining:
                case_ = c
                remaining -= get_price(c)
                break
        if case_ is None:
            cheapest_compatible = candidates[0]
            shortfall = get_price(cheapest_compatible) - remaining
            warnings.append(f"⚠️ На корпус ({cheapest_compatible['model']}) не хватает {shortfall} руб. Показан самый дешёвый совместимый вариант.")
            case_ = cheapest_compatible
            remaining -= get_price(case_)
        pc["case"] = case_

    # --- ФАЗА УЛУЧШЕНИЯ: если остались деньги, улучшаем компоненты по приоритету ---
    if remaining > 0:
        # Порядок улучшения: CPU → GPU → RAM → PSU → MB → Case
        upgrade_order = ["cpu", "gpu", "ram", "psu", "motherboard", "case"]
        for key in upgrade_order:
            if key in existing:
                continue
            current = pc[key]
            current_price = get_price(current)
            max_budget = current_price + remaining

            if key == "cpu":
                candidates = sorted([c for c in DATABASE["cpu"] if c.get("purpose") == purpose_key], key=get_price, reverse=True)
            elif key == "motherboard":
                candidates = sorted([m for m in DATABASE["motherboard"] if m["socket"] == pc["cpu"]["socket"]], key=get_price, reverse=True)
            elif key == "ram":
                candidates = sorted([r for r in DATABASE["ram"] if r["type"] == pc["motherboard"]["ram_type"]], key=get_price, reverse=True)
            elif key == "gpu":
                candidates = sorted([g for g in DATABASE["gpu"] if g.get("purpose") == purpose_key], key=get_price, reverse=True)
            elif key == "psu":
                required_watt = math.ceil((pc["cpu"]["tdp"] + pc["gpu"]["tdp"] + 50) * 1.3)
                candidates = sorted([p for p in DATABASE["psu"] if p["power"] >= required_watt], key=get_price, reverse=True)
            elif key == "case":
                candidates = sorted([c for c in DATABASE["case"] if c["form_factor"] == pc["motherboard"]["form_factor"]], key=get_price, reverse=True)

            for candidate in candidates:
                candidate_price = get_price(candidate)
                if candidate_price <= max_budget and candidate_price > current_price:
                    remaining -= (candidate_price - current_price)
                    pc[key] = candidate
                    break

    # Финальные проверки совместимости
    compat_issues = check_compatibility(pc["cpu"], pc["motherboard"], pc["ram"], pc["gpu"], pc["psu"], pc["case"])
    pc["total"] = budget - remaining
    pc["remaining"] = remaining
    pc["compatibility"] = compat_issues
    st.session_state.pc = pc
    st.session_state.warnings = warnings

# ---------- Шаг 2: Просмотр и замена ----------
if st.session_state.step == "review" and st.session_state.pc is not None:
    pc = st.session_state.pc
    existing = st.session_state.existing
    warnings = st.session_state.warnings

    st.header("Шаг 2. Сборка")

    # Важная информация
    with st.container(border=True):
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.info("💡 **Рекомендация:** выбирайте в списках замены товары **без пометки «⚠️»** — они гарантированно совместимы.")
        with col_info2:
            st.warning("💰 **Внимание:** цены ориентировочные. Реальные цены могут отличаться.")

    # Предупреждения
    if warnings:
        for w in warnings:
            st.warning(w)

    # Проблемы совместимости
    if pc["compatibility"]:
        st.error("⚠️ Обнаружены проблемы совместимости:")
        for msg in pc["compatibility"]:
            st.write(f"- {msg}")
        st.markdown("---")

    # Бюджет
    st.caption(f"Бюджет: {st.session_state.budget} руб. | Потрачено: {pc['total']} руб. | Остаток: {pc['remaining']} руб.")
    if pc["remaining"] < 0:
        st.error(f"⚠️ Превышение бюджета на {abs(pc['remaining'])} руб. Попробуйте увеличить бюджет или выбрать более дешёвые компоненты.")
    st.markdown("---")

    st.caption("✅ — товар в наличии | ❌ — отсутствует | 🔒 — уже есть у вас")

    labels = [
        ("🧠 Процессор", "cpu"),
        ("🖥️ Материнская плата", "motherboard"),
        ("🧮 Оперативная память", "ram"),
        ("🎮 Видеокарта", "gpu"),
        ("⚡ Блок питания", "psu"),
        ("🏠 Корпус", "case"),
    ]

    for label, key in labels:
        current = pc[key]
        current_price = get_price(current)
        is_owned = key in existing and existing[key]["model"] == current["model"]

        st.subheader(label)
        if is_owned:
            st.write(f"🔒 **{current['model']}** — УЖЕ ЕСТЬ")
        else:
            stock_icon = "✅" if current.get("in_stock", True) else "❌ Нет в наличии"
            st.write(f"**{current['model']}** — {current_price} руб. | {stock_icon}")

        # Характеристики
        if key == "cpu":
            st.write(f"Сокет: **{current['socket']}** | Ядер: {current.get('cores', '—')} | Потоков: {current.get('threads', '—')} | TDP: {current['tdp']} Вт")
        elif key == "motherboard":
            st.write(f"Сокет: **{current['socket']}** | Чипсет: {current.get('chipset', '—')} | RAM: {current['ram_type']} | Форм-фактор: {current['form_factor']}")
        elif key == "ram":
            st.write(f"Тип: **{current['type']}** | Объём: {current['size']} ГБ | Частота: {current.get('freq', '—')} МГц")
        elif key == "gpu":
            st.write(f"Видеопамять: {current.get('vram', '—')} ГБ | TDP: {current['tdp']} Вт")
        elif key == "psu":
            st.write(f"Мощность: {current['power']} Вт | Сертификат: {current.get('cert', '—')}")
        elif key == "case":
            st.write(f"Форм-фактор: **{current['form_factor']}** | Вентиляторов: {current.get('fans', '—')}")

        # Замена
        if is_owned:
            st.caption("🔒 Ваш компонент — замена не требуется")
        else:
            all_options = DATABASE[key]
            options_display = []
            for o in all_options:
                o_price = get_price(o)
                stock = "✅" if o.get("in_stock", True) else "❌"
                ok, reasons = get_compatibility_status(key, o, pc)
                if ok:
                    options_display.append(f"{stock} {o['model']} — {o_price} руб.")
                else:
                    options_display.append(f"{stock} {o['model']} — {o_price} руб. ⚠️ {'; '.join(reasons)}")

            idx = 0
            for i, disp in enumerate(options_display):
                if current['model'] in disp:
                    idx = i
                    break

            selected_display = st.selectbox("🔄 Заменить:", options_display, index=idx, key=f"select_{key}", label_visibility="collapsed")
            selected_model = selected_display.split(" — ")[0].split(" ", 1)[1] if " " in selected_display.split(" — ")[0] else selected_display.split(" — ")[0]
            for opt in all_options:
                if opt["model"] == selected_model and opt["model"] != current["model"]:
                    pc[key] = opt
                    break

        st.markdown("---")

    # Пересчёт
    new_total = sum(get_price(pc[k]) for k in ["cpu", "motherboard", "ram", "gpu", "psu", "case"] if k not in existing or existing[k]["model"] != pc[k]["model"])
    pc["total"] = new_total
    pc["remaining"] = st.session_state.budget - new_total

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("💰 К покупке", f"{pc['total']} руб.")
    col_b.metric("💵 Остаток", f"{pc['remaining']} руб.")
    total_tdp = pc['cpu']['tdp'] + pc['gpu']['tdp'] + 50
    col_c.metric("⚡ Треб. БП", f"{math.ceil(total_tdp * 1.3)} Вт")

    if st.button("✅ Подтвердить сборку", type="primary"):
        st.session_state.step = "final"
        st.rerun()

# ---------- Шаг 3: Финал ----------
if st.session_state.step == "final" and st.session_state.pc is not None:
    pc = st.session_state.pc
    existing = st.session_state.existing

    st.header("🏁 Итоговая сборка — ссылки на покупку")
    st.warning("💰 Цены ориентировочные. Переходите по ссылкам для уточнения.")

    items = [
        ("🧠 Процессор", "cpu"),
        ("🖥️ Материнская плата", "motherboard"),
        ("🧮 Оперативная память", "ram"),
        ("🎮 Видеокарта", "gpu"),
        ("⚡ Блок питания", "psu"),
        ("🏠 Корпус", "case"),
    ]

    total_to_buy = 0
    for label, key in items:
        comp = pc[key]
        price = get_price(comp)
        is_owned = key in existing and existing[key]["model"] == comp["model"]
        if not is_owned:
            total_to_buy += price

        st.markdown(f"### {label}")
        if is_owned:
            st.success(f"🔒 **{comp['model']}** — УЖЕ ЕСТЬ")
        else:
            in_stock = comp.get("in_stock", True)
            if in_stock:
                st.success(f"✅ **{comp['model']}** — {price} руб.")
            else:
                st.error(f"❌ **{comp['model']}** — {price} руб. — ОТСУТСТВУЕТ")

        if key == "cpu":
            st.write(f"Сокет: {comp['socket']} | Ядер: {comp.get('cores', '—')} | Потоков: {comp.get('threads', '—')} | TDP: {comp['tdp']} Вт")
        elif key == "motherboard":
            st.write(f"Сокет: {comp['socket']} | Чипсет: {comp.get('chipset', '—')} | RAM: {comp['ram_type']} | Форм-фактор: {comp['form_factor']}")
        elif key == "ram":
            st.write(f"Тип: {comp['type']} | Объём: {comp['size']} ГБ | Частота: {comp.get('freq', '—')} МГц")
        elif key == "gpu":
            st.write(f"Видеопамять: {comp.get('vram', '—')} ГБ | TDP: {comp['tdp']} Вт")
        elif key == "psu":
            st.write(f"Мощность: {comp['power']} Вт | Сертификат: {comp.get('cert', '—')}")
        elif key == "case":
            st.write(f"Форм-фактор: {comp['form_factor']} | Вентиляторов: {comp.get('fans', '—')}")

        if not is_owned and comp.get("shops"):
            st.write("**🛒 Где купить:**")
            best_shop = get_best_shop(comp)
            for shop in comp["shops"]:
                if shop == best_shop:
                    st.markdown(f"- 🏆 **{shop['source']} — {shop['price']} руб.** [Открыть]({shop['url']})")
                else:
                    st.markdown(f"- {shop['source']} — {shop['price']} руб. [Открыть]({shop['url']})")

        if not is_owned and not comp.get("in_stock", True):
            st.write("🔽 Замена:")
            alternatives = [o for o in DATABASE[key] if o.get("in_stock", True)]
            if alternatives:
                alt_str = [f"{o['model']} — {get_price(o)} руб." for o in alternatives]
                chosen = st.selectbox(f"Замена для {label}", alt_str, key=f"replace_{key}")
                chosen_model = chosen.split(" — ")[0]
                for o in alternatives:
                    if o["model"] == chosen_model:
                        pc[key] = o
                        break
                new_shop = get_best_shop(pc[key])
                if new_shop:
                    st.markdown(f"🛒 [Купить замену на {new_shop['source']}]({new_shop['url']}) — {new_shop['price']} руб.")

        st.write("")

    st.markdown("---")
    st.subheader("📊 Характеристики")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 К покупке", f"{total_to_buy} руб.")
    with col2:
        total_tdp = pc['cpu']['tdp'] + pc['gpu']['tdp'] + 50
        st.metric("⚡ Энергопотребление", f"{total_tdp} Вт")
    with col3:
        st.metric("📅 Дата подбора", datetime.now().strftime("%d.%m.%Y"))
    st.info("Спасибо! Для нового подбора обновите страницу (F5).")
