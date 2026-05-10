"""
Программа подбора совместимых комплектующих для ПК
Веб-версия для Streamlit Cloud
База загружается из components.json
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

# Инициализация состояний сессии
if 'pc' not in st.session_state:
    st.session_state.pc = None
if 'step' not in st.session_state:
    st.session_state.step = 'input'
if 'budget' not in st.session_state:
    st.session_state.budget = 0
if 'purpose' not in st.session_state:
    st.session_state.purpose = 'gaming'


def get_price(item):
    if not item.get("shops"):
        return item.get("price", 0)
    return min(shop["price"] for shop in item["shops"])


def get_best_shop(item):
    if not item.get("shops"):
        return None
    return min(item["shops"], key=lambda s: s["price"])


def check_compatibility(cpu, mb, ram, gpu, psu, case):
    """Возвращает список причин несовместимости (пустой = всё ОК)."""
    msgs = []

    if cpu["socket"] != mb["socket"]:
        msgs.append(f"Разные сокеты: у процессора «{cpu['socket']}», у платы «{mb['socket']}» — физически несовместимы, нужна плата с сокетом {cpu['socket']}")

    if ram["type"] != mb["ram_type"]:
        msgs.append(f"Разный тип памяти: ОЗУ — «{ram['type']}», плата поддерживает только «{mb['ram_type']}» — модуль не войдёт в разъём")

    if case["form_factor"] != mb["form_factor"]:
        msgs.append(f"Корпус ({case['form_factor']}) не подходит плате ({mb['form_factor']}). Плата просто не поместится в корпус — нужен корпус {mb['form_factor']}")

    total_tdp = cpu["tdp"] + gpu["tdp"] + 50
    required = math.ceil(total_tdp * 1.3)
    if psu["power"] < required:
        msgs.append(f"Недостаточно мощности БП: системе нужно ~{required} Вт, а установленный БП даёт только {psu['power']} Вт")

    return msgs


def get_compatibility_status(category, item, pc):
    """Проверяет совместимость одного товара с остальной сборкой. Возвращает (ok, причины)."""
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


def smart_pick(items, max_budget, prefer_cheaper=True):
    affordable = sorted(
        [item for item in items if get_price(item) <= max_budget],
        key=lambda x: get_price(x)
    )
    if not affordable:
        return None
    n = len(affordable)
    if n == 1:
        return affordable[0]
    idx = min(n - 1, int(n * 0.5)) if prefer_cheaper else max(0, int(n * 0.4))
    return affordable[idx]


# ====================== ИНТЕРФЕЙС ======================
st.set_page_config(page_title="Подбор ПК", layout="wide")
st.title("🖥️ Подбор комплектующих ПК с проверкой совместимости")

# ---------- Шаг 1: Ввод ----------
st.header("Шаг 1. Параметры")
col1, col2 = st.columns(2)
with col1:
    budget = st.number_input("💰 Ваш бюджет (руб.)", min_value=10000, max_value=500000, value=80000, step=5000)
with col2:
    purpose = st.selectbox("🎯 Назначение", ["Офисные задачи", "Игры и графика"])

if st.button("🔍 Подобрать сборку", type="primary"):
    st.session_state.step = "review"
    st.session_state.budget = budget
    purpose_key = "office" if purpose == "Офисные задачи" else "gaming"
    st.session_state.purpose = purpose_key
    quotas = {"cpu": 0.28, "motherboard": 0.15, "ram": 0.08, "gpu": 0.32, "psu": 0.07, "case": 0.05}
    remaining = budget
    pc = {}
    error_msg = None

    cpu_list = [c for c in DATABASE["cpu"] if c.get("purpose") == purpose_key]
    cpu = smart_pick(cpu_list, min(remaining, budget * quotas["cpu"] * 1.2), prefer_cheaper=False)
    if not cpu: error_msg = "❌ Не найден процессор."
    else: pc["cpu"] = cpu; remaining -= get_price(cpu)

    if not error_msg:
        mb_list = [m for m in DATABASE["motherboard"] if m["socket"] == cpu["socket"]]
        mb = smart_pick(mb_list, min(remaining, budget * quotas["motherboard"] * 1.3), prefer_cheaper=True)
        if not mb: error_msg = "❌ Нет материнской платы."
        else: pc["motherboard"] = mb; remaining -= get_price(mb)

    if not error_msg:
        ram_list = [r for r in DATABASE["ram"] if r["type"] == mb["ram_type"]]
        ram = smart_pick(ram_list, min(remaining, budget * quotas["ram"] * 1.2), prefer_cheaper=True)
        if not ram: error_msg = "❌ Нет ОЗУ."
        else: pc["ram"] = ram; remaining -= get_price(ram)

    if not error_msg:
        gpu_list = [g for g in DATABASE["gpu"] if g.get("purpose") == purpose_key]
        gpu = smart_pick(gpu_list, min(remaining, budget * quotas["gpu"] * 1.2), prefer_cheaper=False)
        if not gpu: error_msg = "❌ Нет видеокарты."
        else: pc["gpu"] = gpu; remaining -= get_price(gpu)

    if not error_msg:
        required_watt = math.ceil((cpu["tdp"] + gpu["tdp"] + 50) * 1.3)
        psu_list = [p for p in DATABASE["psu"] if p["power"] >= required_watt]
        psu = smart_pick(psu_list, min(remaining, budget * quotas["psu"] * 1.5), prefer_cheaper=True)
        if not psu: error_msg = f"❌ Нет БП ({required_watt} Вт)."
        else: pc["psu"] = psu; remaining -= get_price(psu)

    if not error_msg:
        case_list = sorted(
            [c for c in DATABASE["case"] if c["form_factor"] == mb["form_factor"] and get_price(c) <= remaining],
            key=lambda x: get_price(x)
        )
        case_ = case_list[0] if case_list else None
        if not case_: error_msg = "❌ Нет корпуса."
        else: pc["case"] = case_; remaining -= get_price(case_)

    if error_msg:
        st.error(error_msg)
    else:
        pc["total"] = budget - remaining
        pc["remaining"] = remaining
        pc["compatibility"] = check_compatibility(cpu, mb, ram, gpu, psu, case_)
        st.session_state.pc = pc

# ---------- Шаг 2: Просмотр и замена ----------
if st.session_state.step == "review" and st.session_state.pc is not None:
    pc = st.session_state.pc
    st.header("Шаг 2. Сборка — проверьте и при необходимости замените компоненты")

    # Единый блок с важной информацией перед всей сборкой
    with st.container(border=True):
        st.markdown("### 📌 Важная информация")
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.info("💡 **Рекомендация:** выбирайте в списках замены товары **без пометки «⚠️»** — они гарантированно совместимы с остальными компонентами. Товары с пометкой «⚠️» и описанием причины лучше не выбирать — они могут не подойти.")
        with col_info2:
            st.warning("💰 **Внимание:** цены в программе являются ориентировочными и собраны на основе данных из открытых источников. Реальные цены в магазинах могут отличаться — переходите по ссылкам на финальном шаге для уточнения.")

    st.markdown("---")

    # Показываем проблемы совместимости (если есть)
    compat_issues = check_compatibility(pc["cpu"], pc["motherboard"], pc["ram"], pc["gpu"], pc["psu"], pc["case"])
    if compat_issues:
        st.error("⚠️ Обнаружены проблемы совместимости в текущей сборке:")
        for msg in compat_issues:
            st.write(f"- {msg}")
        st.markdown("---")

    # Легенда значков
    st.caption("✅ — товар в наличии | ❌ — товар отсутствует в магазине")

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

        st.subheader(label)
        stock_icon = "✅" if current.get("in_stock", True) else "❌ Нет в наличии"
        st.write(f"**{current['model']}** — {current_price} руб. | {stock_icon}")

        # Характеристики
        if key == "cpu":
            st.write(f"🔹 Сокет: **{current['socket']}** | Ядер: {current.get('cores', '—')} | Потоков: {current.get('threads', '—')} | Базовая частота: {current.get('base_clock', '—')} | Турбо: {current.get('turbo_clock', '—')} | TDP: {current['tdp']} Вт")
        elif key == "motherboard":
            st.write(f"🔹 Сокет: **{current['socket']}** | Чипсет: {current.get('chipset', '—')} | RAM: {current['ram_type']} | Слотов RAM: {current.get('ram_slots', '—')} | Макс RAM: {current.get('max_ram', '—')} ГБ | Форм-фактор: **{current['form_factor']}**")
        elif key == "ram":
            st.write(f"🔹 Тип: **{current['type']}** | Объём: {current['size']} ГБ | Частота: {current.get('freq', '—')} МГц | Планок: {current.get('sticks', '—')}")
        elif key == "gpu":
            st.write(f"🔹 Видеопамять: {current.get('vram', '—')} ГБ | TDP: {current['tdp']} Вт")
        elif key == "psu":
            st.write(f"🔹 Мощность: {current['power']} Вт | Сертификат: {current.get('cert', '—')}")
        elif key == "case":
            st.write(f"🔹 Форм-фактор: **{current['form_factor']}** | Вентиляторов в комплекте: {current.get('fans', '—')}")

        # Выпадающий список замены
        all_options = DATABASE[key]

        # Формируем список опций
        options_display = []
        compatible_options = []
        for o in all_options:
            o_price = get_price(o)
            stock = "✅" if o.get("in_stock", True) else "❌"
            ok, reasons = get_compatibility_status(key, o, pc)
            if ok:
                options_display.append(f"{stock} {o['model']} — {o_price} руб.")
                compatible_options.append(o)
            else:
                reason_text = "; ".join(reasons)
                options_display.append(f"{stock} {o['model']} — {o_price} руб. ⚠️ {reason_text}")

        # Находим индекс текущего элемента
        idx = 0
        for i, disp in enumerate(options_display):
            if current['model'] in disp:
                idx = i
                break

        selected_display = st.selectbox(
            "🔄 Заменить:",
            options_display,
            index=idx,
            key=f"select_{key}",
            label_visibility="collapsed"
        )

        # Обработка выбора
        selected_model = selected_display.split(" — ")[0].split(" ", 1)[1] if " " in selected_display.split(" — ")[0] else selected_display.split(" — ")[0]
        for opt in all_options:
            if opt["model"] == selected_model and opt["model"] != current["model"]:
                pc[key] = opt
                break

        st.markdown("---")

    # Пересчёт итогов
    new_total = sum(get_price(pc[k]) for k in ["cpu", "motherboard", "ram", "gpu", "psu", "case"])
    pc["total"] = new_total
    pc["remaining"] = st.session_state.budget - new_total
    pc["compatibility"] = check_compatibility(pc["cpu"], pc["motherboard"], pc["ram"],
                                              pc["gpu"], pc["psu"], pc["case"])

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("💰 Итого", f"{pc['total']} руб.")
    col_b.metric("💵 Остаток бюджета", f"{pc['remaining']} руб.")
    col_c.metric("⚡ Требуемая мощность БП",
                 f"{math.ceil((pc['cpu']['tdp'] + pc['gpu']['tdp'] + 50) * 1.3)} Вт")

    if st.button("✅ Подтвердить сборку", type="primary"):
        st.session_state.step = "final"
        st.rerun()

# ---------- Шаг 3: Финал ----------
if st.session_state.step == "final" and st.session_state.pc is not None:
    pc = st.session_state.pc
    st.header("🏁 Итоговая сборка — ссылки на покупку")
    st.info("Ниже — полный список компонентов с лучшими ценами и прямыми ссылками.")

    # Предупреждение о ценах
    st.warning("💰 **Внимание:** цены являются ориентировочными. Реальные цены могут отличаться — переходите по ссылкам для уточнения актуальной стоимости.")

    items = [
        ("🧠 Процессор", "cpu"),
        ("🖥️ Материнская плата", "motherboard"),
        ("🧮 Оперативная память", "ram"),
        ("🎮 Видеокарта", "gpu"),
        ("⚡ Блок питания", "psu"),
        ("🏠 Корпус", "case"),
    ]

    total_price = 0
    for label, key in items:
        comp = pc[key]
        price = get_price(comp)
        total_price += price
        best_shop = get_best_shop(comp)
        in_stock = comp.get("in_stock", True)

        st.markdown(f"### {label}")
        if in_stock:
            st.success(f"✅ **{comp['model']}** — {price} руб. — В НАЛИЧИИ")
        else:
            st.error(f"❌ **{comp['model']}** — {price} руб. — ОТСУТСТВУЕТ")

        # Характеристики
        if key == "cpu":
            st.write(f"🔹 Сокет: {comp['socket']} | Ядер: {comp.get('cores', '—')} | Потоков: {comp.get('threads', '—')} | Базовая частота: {comp.get('base_clock', '—')} | Турбо: {comp.get('turbo_clock', '—')} | TDP: {comp['tdp']} Вт")
        elif key == "motherboard":
            st.write(f"🔹 Сокет: {comp['socket']} | Чипсет: {comp.get('chipset', '—')} | RAM: {comp['ram_type']} | Слотов RAM: {comp.get('ram_slots', '—')} | Макс RAM: {comp.get('max_ram', '—')} ГБ | Форм-фактор: {comp['form_factor']}")
        elif key == "ram":
            st.write(f"🔹 Тип: {comp['type']} | Объём: {comp['size']} ГБ | Частота: {comp.get('freq', '—')} МГц | Планок: {comp.get('sticks', '—')}")
        elif key == "gpu":
            st.write(f"🔹 Видеопамять: {comp.get('vram', '—')} ГБ | TDP: {comp['tdp']} Вт")
        elif key == "psu":
            st.write(f"🔹 Мощность: {comp['power']} Вт | Сертификат: {comp.get('cert', '—')}")
        elif key == "case":
            st.write(f"🔹 Форм-фактор: {comp['form_factor']} | Вентиляторов: {comp.get('fans', '—')}")

        # Ссылки на магазины
        if comp.get("shops"):
            st.write("**🛒 Где купить:**")
            for shop in comp["shops"]:
                if shop == best_shop:
                    st.markdown(f"- 🏆 **{shop['source']} — {shop['price']} руб. (лучшая цена!)** [Открыть]({shop['url']})")
                else:
                    st.markdown(f"- {shop['source']} — {shop['price']} руб. [Открыть]({shop['url']})")

        # Замена отсутствующего
        if not in_stock:
            st.write("🔽 Выберите замену из доступных аналогов:")
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
            else:
                st.warning("Нет аналогов в наличии.")
        st.write("")

    # Итоги
    st.markdown("---")
    st.subheader("📊 Характеристики сборки")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Итого", f"{total_price} руб.")
        st.write(f"**Процессор:** {pc['cpu']['model']}")
        st.write(f"**Видеокарта:** {pc['gpu']['model']}")
    with col2:
        total_tdp = pc['cpu']['tdp'] + pc['gpu']['tdp'] + 50
        st.metric("⚡ Энергопотребление", f"{total_tdp} Вт")
        st.write(f"**ОЗУ:** {pc['ram']['size']} ГБ {pc['ram']['type']}")
        st.write(f"**БП:** {pc['psu']['power']} Вт ({pc['psu'].get('cert', '—')})")
    with col3:
        st.metric("📅 Дата подбора", datetime.now().strftime("%d.%m.%Y"))
        st.write(f"**Платформа:** {pc['cpu']['socket']} + {pc['motherboard'].get('chipset', '—')}")
        st.write(f"**Корпус:** {pc['case']['form_factor']}")

    st.info("Спасибо за использование программы! Для нового подбора обновите страницу (F5).")
