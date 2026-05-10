"""
Программа подбора совместимых комплектующих для ПК
Веб-версия для Streamlit Cloud
"""

import streamlit as st
import math

# ========== База комплектующих с поисковыми ссылками ==========
DATABASE = {
    "cpu": [
        {"model": "Intel Core i3-12100F", "socket": "LGA1700", "tdp": 60, "price": 8500,
         "source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Intel+Core+i3-12100F",
         "purpose": "office", "in_stock": True},
        {"model": "Intel Core i5-12400F", "socket": "LGA1700", "tdp": 117, "price": 15000,
         "source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=Intel+Core+i5-12400F",
         "purpose": "gaming", "in_stock": True},
        {"model": "Intel Core i5-13400F", "socket": "LGA1700", "tdp": 148, "price": 21000,
         "source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Intel+Core+i5-13400F",
         "purpose": "gaming", "in_stock": True},
        {"model": "Intel Core i7-12700KF", "socket": "LGA1700", "tdp": 190, "price": 31000,
         "source": "Регард", "url": "https://www.regard.ru/catalog/?search=Intel+Core+i7-12700KF",
         "purpose": "gaming", "in_stock": True},
        {"model": "AMD Ryzen 5 5500", "socket": "AM4", "tdp": 65, "price": 9500,
         "source": "OZON", "url": "https://www.ozon.ru/search/?text=AMD+Ryzen+5+5500",
         "purpose": "office", "in_stock": True},
        {"model": "AMD Ryzen 5 5600", "socket": "AM4", "tdp": 65, "price": 12000,
         "source": "DNS", "url": "https://www.dns-shop.ru/search/?q=AMD+Ryzen+5+5600",
         "purpose": "gaming", "in_stock": True},
        {"model": "AMD Ryzen 5 7600", "socket": "AM5", "tdp": 105, "price": 19000,
         "source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=AMD+Ryzen+5+7600",
         "purpose": "gaming", "in_stock": True},
        {"model": "AMD Ryzen 7 7700X", "socket": "AM5", "tdp": 170, "price": 32000,
         "source": "DNS", "url": "https://www.dns-shop.ru/search/?q=AMD+Ryzen+7+7700X",
         "purpose": "gaming", "in_stock": False},
        {"model": "Intel Celeron G6900", "socket": "LGA1700", "tdp": 46, "price": 4000,
         "source": "Регард", "url": "https://www.regard.ru/catalog/?search=Intel+Celeron+G6900",
         "purpose": "office", "in_stock": True},
        {"model": "AMD Ryzen 9 7950X", "socket": "AM5", "tdp": 230, "price": 55000,
         "source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=AMD+Ryzen+9+7950X",
         "purpose": "gaming", "in_stock": True},
    ],
    "motherboard": [
        {"model": "MSI PRO B760M-P DDR4", "socket": "LGA1700", "form_factor": "mATX", "ram_type": "DDR4",
         "price": 8500, "source": "DNS", "url": "https://www.dns-shop.ru/search/?q=MSI+PRO+B760M-P+DDR4",
         "in_stock": True},
        {"model": "ASRock B550M-HDV", "socket": "AM4", "form_factor": "mATX", "ram_type": "DDR4",
         "price": 6500, "source": "Регард", "url": "https://www.regard.ru/catalog/?search=ASRock+B550M-HDV",
         "in_stock": True},
        {"model": "Gigabyte B650M K", "socket": "AM5", "form_factor": "mATX", "ram_type": "DDR5",
         "price": 11000, "source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=Gigabyte+B650M+K",
         "in_stock": True},
        {"model": "MSI MAG B760 TOMAHAWK WIFI DDR4", "socket": "LGA1700", "form_factor": "ATX", "ram_type": "DDR4",
         "price": 17000, "source": "DNS", "url": "https://www.dns-shop.ru/search/?q=MSI+MAG+B760+TOMAHAWK+WIFI",
         "in_stock": False},
        {"model": "ASRock B650M Pro RS", "socket": "AM5", "form_factor": "mATX", "ram_type": "DDR5",
         "price": 13500, "source": "OZON", "url": "https://www.ozon.ru/search/?text=ASRock+B650M+Pro+RS",
         "in_stock": True},
        {"model": "Gigabyte B550M AORUS ELITE", "socket": "AM4", "form_factor": "mATX", "ram_type": "DDR4",
         "price": 9500, "source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Gigabyte+B550M+AORUS+ELITE",
         "in_stock": True},
        {"model": "MSI PRO H610M-G DDR4", "socket": "LGA1700", "form_factor": "mATX", "ram_type": "DDR4",
         "price": 6000, "source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=MSI+PRO+H610M-G+DDR4",
         "in_stock": True},
        {"model": "ASUS TUF GAMING B650-PLUS WIFI", "socket": "AM5", "form_factor": "ATX", "ram_type": "DDR5",
         "price": 21000, "source": "DNS", "url": "https://www.dns-shop.ru/search/?q=ASUS+TUF+GAMING+B650-PLUS+WIFI",
         "in_stock": True},
        {"model": "ASRock H610M-HVS", "socket": "LGA1700", "form_factor": "mATX", "ram_type": "DDR4",
         "price": 5200, "source": "Регард", "url": "https://www.regard.ru/catalog/?search=ASRock+H610M-HVS",
         "in_stock": True},
        {"model": "Gigabyte Z790 AORUS ELITE AX", "socket": "LGA1700", "form_factor": "ATX", "ram_type": "DDR5",
         "price": 29000, "source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=Gigabyte+Z790+AORUS+ELITE+AX",
         "in_stock": True},
    ],
    "ram": [
        {"model": "Kingston Fury Beast DDR4 16GB 3200MHz", "type": "DDR4", "size": 16, "price": 4200,
         "source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Kingston+Fury+Beast+DDR4+16GB+3200MHz",
         "in_stock": True},
        {"model": "Kingston Fury Beast DDR5 16GB 5200MHz", "type": "DDR5", "size": 16, "price": 5800,
         "source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=Kingston+Fury+Beast+DDR5+16GB+5200MHz",
         "in_stock": True},
        {"model": "G.Skill Ripjaws V DDR4 32GB 3600MHz", "type": "DDR4", "size": 32, "price": 9500,
         "source": "Регард", "url": "https://www.regard.ru/catalog/?search=G.Skill+Ripjaws+V+DDR4+32GB+3600MHz",
         "in_stock": True},
        {"model": "Corsair Vengeance RGB DDR5 32GB 6000MHz", "type": "DDR5", "size": 32, "price": 14000,
         "source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Corsair+Vengeance+RGB+DDR5+32GB+6000MHz",
         "in_stock": True},
        {"model": "Kingston ValueRAM DDR4 8GB 2666MHz", "type": "DDR4", "size": 8, "price": 2200,
         "source": "OZON", "url": "https://www.ozon.ru/search/?text=Kingston+ValueRAM+DDR4+8GB+2666MHz",
         "in_stock": True},
        {"model": "Team Group T-Force Delta RGB DDR5 16GB 6400MHz", "type": "DDR5", "size": 16, "price": 7500,
         "source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Team+Group+T-Force+Delta+RGB+DDR5+16GB",
         "in_stock": True},
        {"model": "Patriot Viper Steel DDR4 16GB 3600MHz", "type": "DDR4", "size": 16, "price": 4800,
         "source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=Patriot+Viper+Steel+DDR4+16GB+3600MHz",
         "in_stock": True},
        {"model": "ADATA XPG Lancer DDR5 32GB 6000MHz", "type": "DDR5", "size": 32, "price": 13500,
         "source": "Регард", "url": "https://www.regard.ru/catalog/?search=ADATA+XPG+Lancer+DDR5+32GB+6000MHz",
         "in_stock": True},
    ],
    "gpu": [
        {"model": "NVIDIA GeForce GT 1030 2GB", "tdp": 30, "price": 7000,
         "source": "DNS", "url": "https://www.dns-shop.ru/search/?q=GeForce+GT+1030+2GB",
         "purpose": "office", "in_stock": True},
        {"model": "NVIDIA GeForce RTX 3060 12GB", "tdp": 170, "price": 28000,
         "source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=GeForce+RTX+3060+12GB",
         "purpose": "gaming", "in_stock": True},
        {"model": "AMD Radeon RX 6600 8GB", "tdp": 132, "price": 22000,
         "source": "Регард", "url": "https://www.regard.ru/catalog/?search=Radeon+RX+6600+8GB",
         "purpose": "gaming", "in_stock": True},
        {"model": "NVIDIA GeForce RTX 4060 8GB", "tdp": 115, "price": 32000,
         "source": "DNS", "url": "https://www.dns-shop.ru/search/?q=GeForce+RTX+4060+8GB",
         "purpose": "gaming", "in_stock": True},
        {"model": "AMD Radeon RX 7800 XT 16GB", "tdp": 263, "price": 65000,
         "source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=Radeon+RX+7800+XT+16GB",
         "purpose": "gaming", "in_stock": False},
        {"model": "Intel UHD Graphics (встроено)", "tdp": 0, "price": 0,
         "source": "—", "url": "",
         "purpose": "office", "in_stock": True},
        {"model": "NVIDIA GeForce RTX 4070 12GB", "tdp": 200, "price": 58000,
         "source": "OZON", "url": "https://www.ozon.ru/search/?text=GeForce+RTX+4070+12GB",
         "purpose": "gaming", "in_stock": True},
        {"model": "AMD Radeon RX 7600 8GB", "tdp": 165, "price": 27000,
         "source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Radeon+RX+7600+8GB",
         "purpose": "gaming", "in_stock": True},
    ],
    "psu": [
        {"model": "Be Quiet! System Power 10 450W", "power": 450, "price": 4000,
         "source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Be+Quiet+System+Power+10+450W",
         "in_stock": True},
        {"model": "Cooler Master MWE 650W V2 Bronze", "power": 650, "price": 5500,
         "source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=Cooler+Master+MWE+650W+V2+Bronze",
         "in_stock": True},
        {"model": "Corsair RM750e 750W Gold", "power": 750, "price": 9500,
         "source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Corsair+RM750e+750W+Gold",
         "in_stock": True},
        {"model": "DeepCool PF600 600W", "power": 600, "price": 4500,
         "source": "OZON", "url": "https://www.ozon.ru/search/?text=DeepCool+PF600+600W",
         "in_stock": True},
        {"model": "Thermaltake Toughpower GF3 850W Gold", "power": 850, "price": 12000,
         "source": "Регард", "url": "https://www.regard.ru/catalog/?search=Thermaltake+Toughpower+GF3+850W",
         "in_stock": True},
        {"model": "XPG Pylon 550W Bronze", "power": 550, "price": 4200,
         "source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=XPG+Pylon+550W+Bronze",
         "in_stock": True},
        {"model": "Be Quiet! Pure Power 12 M 1000W Gold", "power": 1000, "price": 15500,
         "source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Be+Quiet+Pure+Power+12+M+1000W",
         "in_stock": True},
    ],
    "case": [
        {"model": "AeroCool CS-101 mATX Black", "form_factor": "mATX", "price": 2500,
         "source": "DNS", "url": "https://www.dns-shop.ru/search/?q=AeroCool+CS-101+mATX+Black",
         "in_stock": True},
        {"model": "DeepCool MACUBE 110 mATX White", "form_factor": "mATX", "price": 3500,
         "source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=DeepCool+MACUBE+110+mATX+White",
         "in_stock": True},
        {"model": "Zalman S2 ATX Black", "form_factor": "ATX", "price": 3000,
         "source": "OZON", "url": "https://www.ozon.ru/search/?text=Zalman+S2+ATX+Black",
         "in_stock": True},
        {"model": "Corsair 4000D Airflow ATX Black", "form_factor": "ATX", "price": 8500,
         "source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Corsair+4000D+Airflow+ATX+Black",
         "in_stock": True},
        {"model": "Cooler Master MasterBox Q300L mATX", "form_factor": "mATX", "price": 4200,
         "source": "Регард", "url": "https://www.regard.ru/catalog/?search=Cooler+Master+MasterBox+Q300L",
         "in_stock": True},
        {"model": "Fractal Design Pop Air ATX Black", "form_factor": "ATX", "price": 7500,
         "source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=Fractal+Design+Pop+Air+ATX+Black",
         "in_stock": True},
        {"model": "AeroCool Cylon mATX Black", "form_factor": "mATX", "price": 2800,
         "source": "DNS", "url": "https://www.dns-shop.ru/search/?q=AeroCool+Cylon+mATX+Black",
         "in_stock": True},
    ]
}

# Инициализация состояний сессии
if 'pc' not in st.session_state:
    st.session_state.pc = None
if 'step' not in st.session_state:
    st.session_state.step = 'input'
if 'budget' not in st.session_state:
    st.session_state.budget = 0
if 'purpose' not in st.session_state:
    st.session_state.purpose = 'gaming'


def check_compatibility(cpu, mb, ram, gpu, psu, case):
    msgs = []
    if cpu["socket"] != mb["socket"]:
        msgs.append(f"❌ Несовпадение сокета: CPU {cpu['socket']} ↔ Плата {mb['socket']}")
    if ram["type"] != mb["ram_type"]:
        msgs.append(f"❌ Тип RAM {ram['type']} несовместим с платой ({mb['ram_type']})")
    if case["form_factor"] != mb["form_factor"]:
        msgs.append(f"❌ Форм-фактор корпуса ({case['form_factor']}) не подходит плате ({mb['form_factor']})")
    total_tdp = cpu["tdp"] + gpu["tdp"] + 50
    if psu["power"] < total_tdp * 1.3:
        msgs.append(f"❌ БП ({psu['power']} Вт) слабоват, нужно ~{math.ceil(total_tdp * 1.3)} Вт")
    if not msgs:
        msgs.append("✅ Все компоненты совместимы")
    return msgs


def smart_pick(items, max_budget, prefer_cheaper=True):
    affordable = sorted(
        [item for item in items if item["price"] <= max_budget],
        key=lambda x: x["price"]
    )
    if not affordable:
        return None
    n = len(affordable)
    if n == 1:
        return affordable[0]
    if prefer_cheaper:
        idx = min(n - 1, int(n * 0.5))
    else:
        idx = max(0, int(n * 0.4))
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
    quotas = {
        "cpu": 0.28,
        "motherboard": 0.15,
        "ram": 0.08,
        "gpu": 0.32,
        "psu": 0.07,
        "case": 0.05,
    }
    remaining = budget
    pc = {}
    error_msg = None

    # CPU
    cpu_budget = budget * quotas["cpu"]
    cpu_list = [c for c in DATABASE["cpu"] if c.get("purpose") == purpose_key]
    cpu = smart_pick(cpu_list, min(remaining, cpu_budget * 1.2), prefer_cheaper=False)
    if not cpu:
        error_msg = "❌ Не найден процессор."
    else:
        pc["cpu"] = cpu
        remaining -= cpu["price"]

    # MB
    if not error_msg:
        mb_budget = budget * quotas["motherboard"]
        mb_list = [m for m in DATABASE["motherboard"] if m["socket"] == cpu["socket"]]
        mb = smart_pick(mb_list, min(remaining, mb_budget * 1.3), prefer_cheaper=True)
        if not mb:
            error_msg = "❌ Нет материнской платы."
        else:
            pc["motherboard"] = mb
            remaining -= mb["price"]

    # RAM
    if not error_msg:
        ram_budget = budget * quotas["ram"]
        ram_list = [r for r in DATABASE["ram"] if r["type"] == mb["ram_type"]]
        ram = smart_pick(ram_list, min(remaining, ram_budget * 1.2), prefer_cheaper=True)
        if not ram:
            error_msg = "❌ Нет ОЗУ."
        else:
            pc["ram"] = ram
            remaining -= ram["price"]

    # GPU
    if not error_msg:
        gpu_budget = budget * quotas["gpu"]
        gpu_list = [g for g in DATABASE["gpu"] if g.get("purpose") == purpose_key]
        gpu = smart_pick(gpu_list, min(remaining, gpu_budget * 1.2), prefer_cheaper=False)
        if not gpu:
            error_msg = "❌ Нет видеокарты."
        else:
            pc["gpu"] = gpu
            remaining -= gpu["price"]

    # PSU
    if not error_msg:
        required_watt = math.ceil((cpu["tdp"] + gpu["tdp"] + 50) * 1.3)
        psu_budget = budget * quotas["psu"]
        psu_list = [p for p in DATABASE["psu"] if p["power"] >= required_watt]
        psu = smart_pick(psu_list, min(remaining, psu_budget * 1.5), prefer_cheaper=True)
        if not psu:
            error_msg = f"❌ Нет БП ({required_watt} Вт)."
        else:
            pc["psu"] = psu
            remaining -= psu["price"]

    # Case
    if not error_msg:
        case_list = sorted(
            [c for c in DATABASE["case"] if c["form_factor"] == mb["form_factor"] and c["price"] <= remaining],
            key=lambda x: x["price"]
        )
        case_ = case_list[0] if case_list else None
        if not case_:
            error_msg = "❌ Нет корпуса."
        else:
            pc["case"] = case_
            remaining -= case_["price"]

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
    st.header("Шаг 2. Сборка (можно заменить любую позицию)")

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
        st.subheader(label)
        stock_icon = "✅" if current.get("in_stock", True) else "❌ Нет в наличии"
        st.write(f"**{current['model']}** — {current['price']} руб. | {current.get('source', '')} | {stock_icon}")
        if current.get("url"):
            st.markdown(f"🔗 [Открыть в магазине]({current['url']})")
        if key == "cpu":
            st.write(f"Сокет: {current['socket']} | TDP: {current['tdp']} Вт")
        elif key == "psu":
            st.write(f"Мощность: {current['power']} Вт")

        all_options = DATABASE[key]
        options_str = [
            f"{'✅' if o.get('in_stock', True) else '❌'} {o['model']} — {o['price']} руб. ({o.get('source', '')})"
            for o in all_options
        ]
        current_str = f"{'✅' if current.get('in_stock', True) else '❌'} {current['model']} — {current['price']} руб. ({current.get('source', '')})"
        idx = options_str.index(current_str) if current_str in options_str else 0
        selected_str = st.selectbox("🔄 Заменить:", options_str, index=idx, key=key)
        if selected_str.startswith(("✅", "❌")):
            selected_model = selected_str.split(" ", 1)[1].split(" — ")[0]
        else:
            selected_model = selected_str.split(" — ")[0]
        for opt in all_options:
            if opt["model"] == selected_model:
                pc[key] = opt
                break
        st.markdown("---")

    new_total = sum(pc[k]["price"] for k in ["cpu", "motherboard", "ram", "gpu", "psu", "case"])
    pc["total"] = new_total
    pc["remaining"] = st.session_state.budget - new_total
    pc["compatibility"] = check_compatibility(pc["cpu"], pc["motherboard"], pc["ram"],
                                              pc["gpu"], pc["psu"], pc["case"])

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("💰 Итого", f"{pc['total']} руб.")
    col_b.metric("💵 Остаток", f"{pc['remaining']} руб.")
    col_c.metric("⚡ Треб. БП", f"{math.ceil((pc['cpu']['tdp'] + pc['gpu']['tdp'] + 50) * 1.3)} Вт")

    st.subheader("🔍 Совместимость")
    for msg in pc["compatibility"]:
        if "❌" in msg:
            st.error(msg)
        else:
            st.success(msg)

    if st.button("✅ Подтвердить сборку"):
        st.session_state.step = "final"
        st.rerun()

# ---------- Шаг 3: Финал со ссылками ----------
if st.session_state.step == "final" and st.session_state.pc is not None:
    pc = st.session_state.pc
    st.header("🏁 Итоговая сборка — ссылки на покупку")
    st.info("Нажмите на ссылку, чтобы перейти к поиску товара в магазине.")

    items = [
        ("🧠 Процессор", "cpu"),
        ("🖥️ Материнская плата", "motherboard"),
        ("🧮 Оперативная память", "ram"),
        ("🎮 Видеокарта", "gpu"),
        ("⚡ Блок питания", "psu"),
        ("🏠 Корпус", "case"),
    ]

    for label, key in items:
        comp = pc[key]
        in_stock = comp.get("in_stock", True)
        st.markdown(f"### {label}")
        if in_stock:
            st.success(f"✅ **{comp['model']}** — {comp['price']} руб. — В НАЛИЧИИ")
        else:
            st.error(f"❌ **{comp['model']}** — {comp['price']} руб. — ОТСУТСТВУЕТ")

        if comp.get("url"):
            st.markdown(f"🔗 [Открыть поиск на {comp['source']}]({comp['url']})")
        else:
            st.write(f"Источник: {comp.get('source', '—')}")

        # Замена отсутствующего товара
        if not in_stock:
            st.write("🔽 Выберите замену из доступных аналогов:")
            alternatives = [o for o in DATABASE[key] if o.get("in_stock", True)]
            if alternatives:
                alt_str = [f"{o['model']} — {o['price']} руб. ({o['source']})" for o in alternatives]
                chosen = st.selectbox(f"Замена для {label}", alt_str, key=f"replace_{key}")
                chosen_model = chosen.split(" — ")[0]
                for o in alternatives:
                    if o["model"] == chosen_model:
                        pc[key] = o
                        break
                if pc[key].get("url"):
                    st.markdown(f"🔗 [Купить замену на {pc[key]['source']}]({pc[key]['url']})")
            else:
                st.warning("Нет аналогов в наличии.")
        st.write("")

    new_total = sum(pc[k]["price"] for k in ["cpu", "motherboard", "ram", "gpu", "psu", "case"])
    pc["total"] = new_total

    st.markdown("---")
    st.metric("💰 Итого к оплате", f"{pc['total']} руб.")
    st.info("Спасибо! Для нового подбора обновите страницу (F5).")