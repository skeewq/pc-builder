import streamlit as st
import math
import json
from datetime import datetime

@st.cache_data
def load_database():
    with open("components.json", "r", encoding="utf-8") as f:
        return json.load(f)

DATABASE = load_database()

CATEGORY_LABELS = {
    "cpu": "Процессор", "motherboard": "Мат. плата",
    "ram": "ОЗУ", "gpu": "Видеокарта", "psu": "Блок питания", "case": "Корпус"
}

SORT_OPTIONS = ["Без сортировки", "По цене (возр.)", "По цене (убыв.)", "По названию (А-Я)"]

if 'pc' not in st.session_state: st.session_state.pc = None
if 'step' not in st.session_state: st.session_state.step = 'input'
if 'budget' not in st.session_state: st.session_state.budget = 0
if 'purpose' not in st.session_state: st.session_state.purpose = 'gaming'
if 'existing' not in st.session_state: st.session_state.existing = {}
if 'sort_order' not in st.session_state: st.session_state.sort_order = "Без сортировки"

def get_price(item):
    if not item.get("shops"): return item.get("price", 0)
    return min(shop["price"] for shop in item["shops"])

def get_best_shop(item):
    if not item.get("shops"): return None
    return min(item["shops"], key=lambda s: s["price"])

def check_compatibility(cpu, mb, ram, gpu, psu, case):
    msgs = []
    if cpu["socket"] != mb["socket"]:
        msgs.append(f"Сокеты: CPU={cpu['socket']}, плата={mb['socket']}")
    if ram["type"] != mb["ram_type"]:
        msgs.append(f"Память: ОЗУ={ram['type']}, плата={mb['ram_type']}")
    if case["form_factor"] != mb["form_factor"]:
        msgs.append(f"Корпус={case['form_factor']}, плата={mb['form_factor']}")
    if psu["power"] < math.ceil((cpu["tdp"] + gpu["tdp"] + 50) * 1.3):
        msgs.append(f"БП={psu['power']}Вт, нужно ~{math.ceil((cpu['tdp']+gpu['tdp']+50)*1.3)}Вт")
    return msgs

def sort_options(options, sort_key):
    if sort_key == "По цене (возр.)":
        return sorted(options, key=lambda x: get_price(x))
    elif sort_key == "По цене (убыв.)":
        return sorted(options, key=lambda x: get_price(x), reverse=True)
    elif sort_key == "По названию (А-Я)":
        return sorted(options, key=lambda x: x["model"])
    return options

# ====================== ИНТЕРФЕЙС ======================
st.set_page_config(page_title="Подбор ПК", layout="wide")
st.title("🖥️ Подбор комплектующих ПК")

st.header("Шаг 1. Параметры")
col1, col2 = st.columns(2)
with col1:
    budget = st.number_input("💰 Бюджет (руб.)", min_value=0, max_value=500000, value=80000, step=5000)
with col2:
    purpose = st.selectbox("🎯 Назначение", ["Офисные задачи", "Игры и графика"])

with st.expander("🔧 У меня уже есть комплектующие", expanded=False):
    existing = {}
    for key in ["cpu", "motherboard", "ram", "gpu", "psu", "case"]:
        items = DATABASE[key]
        labels_list = ["— Не выбрано —"] + [f"{it['model']} (~{get_price(it)} руб.)" for it in items]
        sel = st.selectbox(CATEGORY_LABELS[key], labels_list, key=f"ex_{key}")
        if sel != "— Не выбрано —":
            model = sel.split(" (~")[0]
            for it in items:
                if it["model"] == model:
                    existing[key] = it
                    break
    st.session_state.existing = existing
    if existing:
        st.success(f"Учтено: {len(existing)} шт.")

if st.button("🔍 Подобрать сборку", type="primary"):
    st.session_state.step = "review"
    st.session_state.budget = budget
    purpose_key = "office" if purpose == "Офисные задачи" else "gaming"
    st.session_state.purpose = purpose_key
    existing = st.session_state.existing
    remaining = budget
    pc = {}
    err = None

    if "cpu" in existing:
        pc["cpu"] = existing["cpu"]
    else:
        candidates = sorted([c for c in DATABASE["cpu"] if c.get("purpose") == purpose_key], key=get_price)
        for c in candidates:
            if get_price(c) <= remaining:
                pc["cpu"] = c; remaining -= get_price(c); break
        if "cpu" not in pc: err = "Нет процессора в бюджете"

    if not err:
        if "motherboard" in existing:
            pc["motherboard"] = existing["motherboard"]
        else:
            candidates = sorted([m for m in DATABASE["motherboard"] if m["socket"] == pc["cpu"]["socket"]], key=get_price)
            for m in candidates:
                if get_price(m) <= remaining:
                    pc["motherboard"] = m; remaining -= get_price(m); break
            if "motherboard" not in pc: err = "Нет материнской платы"

    if not err:
        if "ram" in existing:
            pc["ram"] = existing["ram"]
        else:
            candidates = sorted([r for r in DATABASE["ram"] if r["type"] == pc["motherboard"]["ram_type"]], key=get_price)
            for r in candidates:
                if get_price(r) <= remaining:
                    pc["ram"] = r; remaining -= get_price(r); break
            if "ram" not in pc: err = "Нет ОЗУ"

    if not err:
        if "gpu" in existing:
            pc["gpu"] = existing["gpu"]
        else:
            candidates = sorted([g for g in DATABASE["gpu"] if g.get("purpose") == purpose_key], key=get_price)
            for g in candidates:
                if get_price(g) <= remaining:
                    pc["gpu"] = g; remaining -= get_price(g); break
            if "gpu" not in pc: err = "Нет видеокарты"

    if not err:
        required = math.ceil((pc["cpu"]["tdp"] + pc["gpu"]["tdp"] + 50) * 1.3)
        if "psu" in existing:
            pc["psu"] = existing["psu"]
            if existing["psu"]["power"] < required:
                err = f"Ваш БП ({existing['psu']['power']}Вт) слаб для этой сборки, нужно {required}Вт"
        else:
            candidates = sorted([p for p in DATABASE["psu"] if p["power"] >= required], key=get_price)
            for p in candidates:
                if get_price(p) <= remaining:
                    pc["psu"] = p; remaining -= get_price(p); break
            if "psu" not in pc: err = f"Нет БП на {required}Вт"

    if not err:
        if "case" in existing:
            pc["case"] = existing["case"]
        else:
            candidates = sorted([c for c in DATABASE["case"] if c["form_factor"] == pc["motherboard"]["form_factor"]], key=get_price)
            for c in candidates:
                if get_price(c) <= remaining:
                    pc["case"] = c; remaining -= get_price(c); break
            if "case" not in pc: err = "Нет корпуса"

    if err:
        st.error(f"❌ {err}")
    else:
        pc["total"] = budget - remaining
        pc["remaining"] = remaining
        pc["compatibility"] = check_compatibility(pc["cpu"], pc["motherboard"], pc["ram"], pc["gpu"], pc["psu"], pc["case"])
        st.session_state.pc = pc

# ---------- Шаг 2 ----------
if st.session_state.step == "review" and st.session_state.pc is not None:
    pc = st.session_state.pc
    existing = st.session_state.existing
    st.header("Шаг 2. Сборка")

    with st.container(border=True):
        c1, c2 = st.columns(2)
        c1.info("💡 Выбирайте в списках замены товары без «⚠️» — они совместимы")
        c2.warning("💰 Цены ориентировочные")

    if pc["compatibility"]:
        st.error("⚠️ Проблемы совместимости:")
        for m in pc["compatibility"]:
            st.write(f"- {m}")
        st.markdown("---")

    sort_order = st.selectbox("🔽 Сортировка списков замены:", SORT_OPTIONS, key="sort_select")
    st.session_state.sort_order = sort_order
    st.caption("✅ в наличии | ❌ отсутствует | 🔒 ваш")
    st.markdown("---")

    labels = [("Процессор","cpu"),("Мат. плата","motherboard"),("ОЗУ","ram"),
              ("Видеокарта","gpu"),("БП","psu"),("Корпус","case")]

    for label, key in labels:
        cur = pc[key]
        owned = key in existing and existing[key]["model"] == cur["model"]
        
        # Компактная строка с информацией и кнопкой замены
        col_info, col_btn = st.columns([3, 1])
        with col_info:
            icon = "🔒" if owned else ("✅" if cur.get("in_stock", True) else "❌")
            st.write(f"{icon} **{cur['model']}** — {get_price(cur)} руб. {'(ваш)' if owned else ''}")
        with col_btn:
            if not owned:
                replace_clicked = st.button("🔄 Заменить", key=f"btn_{key}")
            else:
                replace_clicked = False
        
        # Если нажали "Заменить" — показываем popover со списком
        if replace_clicked:
            with st.container():
                st.markdown("---")
                st.write(f"**Замена для «{cur['model']}»:**")
                opts = DATABASE[key]
                opts = sort_options(opts, sort_order)
                disp = []
                for o in opts:
                    test_pc = pc.copy(); test_pc[key] = o
                    issues = check_compatibility(test_pc["cpu"], test_pc["motherboard"], test_pc["ram"], test_pc["gpu"], test_pc["psu"], test_pc["case"])
                    ok = len(issues) == 0
                    stock = "✅" if o.get("in_stock", True) else "❌"
                    if ok:
                        disp.append(f"{stock} {o['model']} — {get_price(o)} руб.")
                    else:
                        disp.append(f"{stock} {o['model']} — {get_price(o)} руб. ⚠️ {'; '.join(issues)}")
                idx = next((i for i, d in enumerate(disp) if cur['model'] in d), 0)
                sel = st.selectbox("Выберите:", disp, index=idx, key=f"sel_{key}")
                sel_model = sel.split(" — ")[0].split(" ", 1)[1] if " " in sel.split(" — ")[0] else sel.split(" — ")[0]
                for o in opts:
                    if o["model"] == sel_model and o["model"] != cur["model"]:
                        pc[key] = o
                        st.rerun()
                st.markdown("---")
        
        st.markdown("---")

    new_total = sum(get_price(pc[k]) for k in ["cpu","motherboard","ram","gpu","psu","case"] if k not in existing or existing[k]["model"] != pc[k]["model"])
    pc["total"] = new_total
    pc["remaining"] = st.session_state.budget - new_total

    ca, cb, cc = st.columns(3)
    ca.metric("💰 К покупке", f"{pc['total']} руб.")
    cb.metric("💵 Остаток", f"{pc['remaining']} руб.")
    cc.metric("⚡ Треб. БП", f"{math.ceil((pc['cpu']['tdp'] + pc['gpu']['tdp'] + 50) * 1.3)} Вт")

    if st.button("✅ Подтвердить", type="primary"):
        st.session_state.step = "final"
        st.rerun()

# ---------- Шаг 3 ----------
if st.session_state.step == "final" and st.session_state.pc is not None:
    pc = st.session_state.pc; existing = st.session_state.existing
    st.header("🏁 Итоговая сборка")
    st.warning("💰 Цены ориентировочные")
    total = 0
    for label, key in [("Процессор","cpu"),("Мат. плата","motherboard"),("ОЗУ","ram"),
                       ("Видеокарта","gpu"),("БП","psu"),("Корпус","case")]:
        comp = pc[key]; price = get_price(comp); owned = key in existing and existing[key]["model"] == comp["model"]
        if not owned: total += price
        st.markdown(f"### {label}")
        st.write(f"{'🔒' if owned else '✅'} **{comp['model']}** — {price} руб. {'(ваш)' if owned else ''}")
        if not owned and comp.get("shops"):
            best = get_best_shop(comp)
            for s in comp["shops"]:
                st.markdown(f"- {'🏆 ' if s==best else ''}{s['source']} — {s['price']} руб. [Ссылка]({s['url']})")
        st.write("")
    st.metric("💰 К покупке", f"{total} руб.")
    st.info("Спасибо! F5 — новый подбор.")
