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
if 'custom_existing' not in st.session_state: st.session_state.custom_existing = {}
if 'sort_order' not in st.session_state: st.session_state.sort_order = "Без сортировки"
if 'show_replace' not in st.session_state: st.session_state.show_replace = {}

def get_price(item):
    if not item.get("shops"): return item.get("price", 0)
    return min(shop["price"] for shop in item["shops"])

def get_best_shop(item):
    if not item.get("shops"): return None
    return min(item["shops"], key=lambda s: s["price"])

def check_compatibility(cpu, mb, ram, gpu, psu, case):
    msgs = []
    if cpu.get("socket") != mb.get("socket"):
        msgs.append(f"Сокеты: CPU={cpu.get('socket')}, плата={mb.get('socket')}")
    if ram.get("type") != mb.get("ram_type"):
        msgs.append(f"Память: ОЗУ={ram.get('type')}, плата={mb.get('ram_type')}")
    if case.get("form_factor") != mb.get("form_factor"):
        msgs.append(f"Корпус={case.get('form_factor')}, плата={mb.get('form_factor')}")
    if psu.get("power", 0) < math.ceil((cpu.get("tdp", 0) + gpu.get("tdp", 0) + 50) * 1.3):
        msgs.append(f"БП={psu.get('power')}Вт, нужно ~{math.ceil((cpu.get('tdp',0)+gpu.get('tdp',0)+50)*1.3)}Вт")
    return msgs

def sort_options(options, sort_key):
    if sort_key == "По цене (возр.)":
        return sorted(options, key=lambda x: get_price(x))
    elif sort_key == "По цене (убыв.)":
        return sorted(options, key=lambda x: get_price(x), reverse=True)
    elif sort_key == "По названию (А-Я)":
        return sorted(options, key=lambda x: x["model"])
    return options

def display_characteristics(comp, key):
    if key == "cpu":
        st.write(f"🔹 Сокет: **{comp.get('socket','—')}** | Ядер: {comp.get('cores','—')} | Потоков: {comp.get('threads','—')} | Базовая частота: {comp.get('base_clock','—')} | Турбо: {comp.get('turbo_clock','—')} | TDP: {comp.get('tdp','—')} Вт")
    elif key == "motherboard":
        st.write(f"🔹 Сокет: **{comp.get('socket','—')}** | Чипсет: {comp.get('chipset','—')} | RAM: {comp.get('ram_type','—')} | Слотов RAM: {comp.get('ram_slots','—')} | Макс RAM: {comp.get('max_ram','—')} ГБ | Форм-фактор: **{comp.get('form_factor','—')}**")
    elif key == "ram":
        st.write(f"🔹 Тип: **{comp.get('type','—')}** | Объём: {comp.get('size','—')} ГБ | Частота: {comp.get('freq','—')} МГц | Планок: {comp.get('sticks','—')}")
    elif key == "gpu":
        st.write(f"🔹 Видеопамять: {comp.get('vram','—')} ГБ | TDP: {comp.get('tdp','—')} Вт")
    elif key == "psu":
        st.write(f"🔹 Мощность: **{comp.get('power','—')} Вт** | Сертификат: {comp.get('cert','—')}")
    elif key == "case":
        st.write(f"🔹 Форм-фактор: **{comp.get('form_factor','—')}** | Вентиляторов: {comp.get('fans','—')}")

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
    st.write("**Способ 1:** Выберите из списка")
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
    
    st.markdown("---")
    st.write("**Способ 2:** Или укажите характеристики вручную")
    custom_existing = st.session_state.custom_existing
    
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        custom_cpu_socket = st.selectbox("Сокет процессора", ["Не знаю", "LGA1700", "AM4", "AM5"], key="cust_cpu_sock")
        if custom_cpu_socket != "Не знаю":
            custom_existing["cpu_socket"] = custom_cpu_socket
    with cc2:
        custom_ram_type = st.selectbox("Тип памяти", ["Не знаю", "DDR4", "DDR5"], key="cust_ram_type")
        if custom_ram_type != "Не знаю":
            custom_existing["ram_type"] = custom_ram_type
    with cc3:
        custom_gpu_tdp = st.number_input("TDP видеокарты (Вт, примерно)", min_value=0, max_value=500, value=0, key="cust_gpu_tdp")
        if custom_gpu_tdp > 0:
            custom_existing["gpu_tdp"] = custom_gpu_tdp
    
    st.session_state.custom_existing = custom_existing
    if existing or custom_existing:
        st.success(f"Учтено: {len(existing)} из списка + {len(custom_existing)} характеристики вручную")

if st.button("🔍 Подобрать сборку", type="primary"):
    st.session_state.step = "review"
    st.session_state.budget = budget
    purpose_key = "office" if purpose == "Офисные задачи" else "gaming"
    st.session_state.purpose = purpose_key
    existing = st.session_state.existing
    custom = st.session_state.custom_existing
    remaining = budget
    pc = {}
    err = None

    # ---------- БАЗОВЫЙ ПОДБОР (самые дешёвые совместимые) ----------
    # CPU
    if "cpu" in existing:
        pc["cpu"] = existing["cpu"]
    else:
        socket_filter = custom.get("cpu_socket")
        candidates = [c for c in DATABASE["cpu"] if c.get("purpose") == purpose_key]
        if socket_filter:
            candidates = [c for c in candidates if c["socket"] == socket_filter]
        candidates = sorted(candidates, key=get_price)
        for c in candidates:
            if get_price(c) <= remaining:
                pc["cpu"] = c; remaining -= get_price(c); break
        if "cpu" not in pc: err = "Нет процессора"

    # MB
    if not err:
        if "motherboard" in existing:
            pc["motherboard"] = existing["motherboard"]
        else:
            candidates = sorted([m for m in DATABASE["motherboard"] if m["socket"] == pc["cpu"]["socket"]], key=get_price)
            for m in candidates:
                if get_price(m) <= remaining:
                    pc["motherboard"] = m; remaining -= get_price(m); break
            if "motherboard" not in pc: err = "Нет материнской платы"

    # RAM
    if not err:
        if "ram" in existing:
            pc["ram"] = existing["ram"]
        else:
            candidates = sorted([r for r in DATABASE["ram"] if r["type"] == pc["motherboard"]["ram_type"]], key=get_price)
            for r in candidates:
                if get_price(r) <= remaining:
                    pc["ram"] = r; remaining -= get_price(r); break
            if "ram" not in pc: err = "Нет ОЗУ"

    # GPU
    if not err:
        if "gpu" in existing:
            pc["gpu"] = existing["gpu"]
        else:
            candidates = sorted([g for g in DATABASE["gpu"] if g.get("purpose") == purpose_key], key=get_price)
            for g in candidates:
                if get_price(g) <= remaining:
                    pc["gpu"] = g; remaining -= get_price(g); break
            if "gpu" not in pc: err = "Нет видеокарты"

    # PSU
    if not err:
        required = math.ceil((pc["cpu"]["tdp"] + pc["gpu"]["tdp"] + 50) * 1.3)
        if "psu" in existing:
            pc["psu"] = existing["psu"]
            if existing["psu"]["power"] < required:
                err = f"Ваш БП ({existing['psu']['power']}Вт) слаб, нужно {required}Вт"
        else:
            candidates = sorted([p for p in DATABASE["psu"] if p["power"] >= required], key=get_price)
            for p in candidates:
                if get_price(p) <= remaining:
                    pc["psu"] = p; remaining -= get_price(p); break
            if "psu" not in pc: err = f"Нет БП на {required}Вт"

    # Case
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
        # ---------- ФАЗА УЛУЧШЕНИЯ: тратим оставшийся бюджет ----------
        # Порядок апгрейда: CPU → GPU → RAM → MB → PSU → Case
        upgrade_order = ["cpu", "gpu", "ram", "motherboard", "psu", "case"]
        upgraded = True
        while upgraded and remaining > 0:
            upgraded = False
            for key in upgrade_order:
                if key in existing:  # не меняем то, что уже есть у пользователя
                    continue
                current = pc[key]
                current_price = get_price(current)
                max_budget = current_price + remaining  # сколько можем потратить на этот компонент

                # Кандидаты: совместимые, дороже текущего, влезают в max_budget
                if key == "cpu":
                    candidates = [c for c in DATABASE["cpu"] if c.get("purpose") == purpose_key]
                    if socket_filter_cpu := custom.get("cpu_socket"):
                        candidates = [c for c in candidates if c["socket"] == socket_filter_cpu]
                elif key == "motherboard":
                    candidates = [m for m in DATABASE["motherboard"] if m["socket"] == pc["cpu"]["socket"]]
                elif key == "ram":
                    candidates = [r for r in DATABASE["ram"] if r["type"] == pc["motherboard"]["ram_type"]]
                elif key == "gpu":
                    candidates = [g for g in DATABASE["gpu"] if g.get("purpose") == purpose_key]
                elif key == "psu":
                    required_watt = math.ceil((pc["cpu"]["tdp"] + pc["gpu"]["tdp"] + 50) * 1.3)
                    candidates = [p for p in DATABASE["psu"] if p["power"] >= required_watt]
                elif key == "case":
                    candidates = [c for c in DATABASE["case"] if c["form_factor"] == pc["motherboard"]["form_factor"]]

                # Сортируем по убыванию цены, выбираем самый дорогой, который влезает
                candidates = sorted(candidates, key=lambda x: get_price(x), reverse=True)
                for candidate in candidates:
                    candidate_price = get_price(candidate)
                    if candidate_price > current_price and candidate_price <= max_budget:
                        # Проверяем совместимость с остальными компонентами
                        test_pc = pc.copy()
                        test_pc[key] = candidate
                        issues = check_compatibility(
                            test_pc["cpu"], test_pc["motherboard"], test_pc["ram"],
                            test_pc["gpu"], test_pc["psu"], test_pc["case"]
                        )
                        if len(issues) == 0:
                            # Улучшаем
                            remaining -= (candidate_price - current_price)
                            pc[key] = candidate
                            upgraded = True
                            break  # переходим к следующему компоненту
                if upgraded:
                    break  # начинаем цикл while заново, чтобы пересмотреть все компоненты с новым остатком
            # конец for, если не было улучшений, цикл while завершится

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
        c1.info("💡 В списках замены выбирайте товары без «⚠️» — они совместимы")
        c2.warning("💰 Цены ориентировочные")

    pc["compatibility"] = check_compatibility(pc["cpu"], pc["motherboard"], pc["ram"], pc["gpu"], pc["psu"], pc["case"])
    st.session_state.pc = pc

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
        
        st.subheader(f"{'🔒' if owned else ''} {label}")
        icon = "✅" if cur.get("in_stock", True) else "❌"
        st.write(f"{icon} **{cur['model']}** — {get_price(cur)} руб. {'(ваш)' if owned else ''}")
        display_characteristics(cur, key)
        
        if not owned:
            if st.button("🔄 Заменить", key=f"btn_{key}"):
                st.session_state.show_replace[key] = True
                st.rerun()
            
            if st.session_state.show_replace.get(key):
                st.write(f"**Замена для «{cur['model']}»:**")
                opts = DATABASE[key]
                opts = sort_options(opts, sort_order)
                disp = []
                for o in opts:
                    compat_pc = {
                        "cpu": pc["cpu"].copy(),
                        "motherboard": pc["motherboard"].copy(),
                        "ram": pc["ram"].copy(),
                        "gpu": pc["gpu"].copy(),
                        "psu": pc["psu"].copy(),
                        "case": pc["case"].copy()
                    }
                    compat_pc[key] = o
                    issues = check_compatibility(compat_pc["cpu"], compat_pc["motherboard"], compat_pc["ram"], 
                                                 compat_pc["gpu"], compat_pc["psu"], compat_pc["case"])
                    ok = len(issues) == 0
                    stock = "✅" if o.get("in_stock", True) else "❌"
                    if ok:
                        disp.append(f"{stock} {o['model']} — {get_price(o)} руб.")
                    else:
                        disp.append(f"{stock} {o['model']} — {get_price(o)} руб. ⚠️ {'; '.join(issues)}")
                idx = next((i for i, d in enumerate(disp) if cur['model'] in d), 0)
                sel = st.selectbox("Выберите замену:", disp, index=idx, key=f"sel_{key}")
                sel_model = sel.split(" — ")[0].split(" ", 1)[1] if " " in sel.split(" — ")[0] else sel.split(" — ")[0]
                for o in opts:
                    if o["model"] == sel_model and o["model"] != cur["model"]:
                        pc[key] = o
                        st.session_state.pc[key] = o
                        st.session_state.show_replace[key] = False
                        st.rerun()
                if st.button("Отмена", key=f"cancel_{key}"):
                    st.session_state.show_replace[key] = False
                    st.rerun()
        
        st.markdown("---")

    new_total = sum(get_price(pc[k]) for k in ["cpu","motherboard","ram","gpu","psu","case"] if k not in existing or existing[k]["model"] != pc[k]["model"])
    pc["total"] = new_total
    pc["remaining"] = st.session_state.budget - new_total
    pc["compatibility"] = check_compatibility(pc["cpu"], pc["motherboard"], pc["ram"], pc["gpu"], pc["psu"], pc["case"])
    st.session_state.pc = pc

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
    st.warning("💰 Цены ориентировочные — реальные цены могут отличаться")
    total = 0
    labels = [("🧠 Процессор","cpu"),("🖥️ Мат. плата","motherboard"),("🧮 ОЗУ","ram"),
              ("🎮 Видеокарта","gpu"),("⚡ Блок питания","psu"),("🏠 Корпус","case")]
    for label, key in labels:
        comp = pc[key]; price = get_price(comp); owned = key in existing and existing[key]["model"] == comp["model"]
        if not owned: total += price
        st.markdown(f"### {label}")
        icon = "🔒" if owned else ("✅" if comp.get("in_stock", True) else "❌")
        st.write(f"{icon} **{comp['model']}** — {price} руб. {'(ваш)' if owned else ''}")
        display_characteristics(comp, key)
        if not owned and comp.get("shops"):
            best = get_best_shop(comp)
            st.write("**🛒 Где купить:**")
            for s in comp["shops"]:
                st.markdown(f"- {'🏆 ' if s==best else ''}{s['source']} — {s['price']} руб. [Ссылка]({s['url']})")
        if not owned and not comp.get("in_stock", True):
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
    st.subheader("📊 Характеристики сборки")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 К покупке", f"{total} руб.")
        st.write(f"**CPU:** {pc['cpu']['model']}")
        st.write(f"**GPU:** {pc['gpu']['model']}")
    with col2:
        tdp = pc['cpu']['tdp'] + pc['gpu']['tdp'] + 50
        st.metric("⚡ Энергопотребление", f"{tdp} Вт")
        st.write(f"**RAM:** {pc['ram']['size']} ГБ {pc['ram']['type']}")
        st.write(f"**БП:** {pc['psu']['power']} Вт ({pc['psu'].get('cert','—')})")
    with col3:
        st.metric("📅 Дата подбора", datetime.now().strftime("%d.%m.%Y"))
        st.write(f"**Платформа:** {pc['cpu']['socket']} + {pc['motherboard'].get('chipset','—')}")
        st.write(f"**Корпус:** {pc['case']['form_factor']}")
    
    st.info("Спасибо! F5 — новый подбор.")
