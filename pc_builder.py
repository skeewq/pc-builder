"""
Программа подбора совместимых комплектующих для ПК
Веб-версия для Streamlit Cloud
"""

import streamlit as st
import math
from datetime import datetime

# ========== Расширенная база комплектующих с несколькими магазинами ==========
DATABASE = {
    "cpu": [
        {"model": "Intel Core i3-12100F", "socket": "LGA1700", "tdp": 60, "cores": 4, "threads": 8,
         "price": 8500, "purpose": "office", "in_stock": True,
         "shops": [
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Intel+Core+i3-12100F", "price": 8500},
             {"source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=Intel+Core+i3-12100F", "price": 8700},
         ]},
        {"model": "Intel Core i5-12400F", "socket": "LGA1700", "tdp": 117, "cores": 6, "threads": 12,
         "price": 15000, "purpose": "gaming", "in_stock": True,
         "shops": [
             {"source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=Intel+Core+i5-12400F", "price": 15000},
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Intel+Core+i5-12400F", "price": 15500},
         ]},
        {"model": "Intel Core i5-13400F", "socket": "LGA1700", "tdp": 148, "cores": 10, "threads": 16,
         "price": 21000, "purpose": "gaming", "in_stock": True,
         "shops": [
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Intel+Core+i5-13400F", "price": 21000},
             {"source": "Регард", "url": "https://www.regard.ru/catalog/?search=Intel+Core+i5-13400F", "price": 21500},
         ]},
        {"model": "Intel Core i7-12700KF", "socket": "LGA1700", "tdp": 190, "cores": 12, "threads": 20,
         "price": 31000, "purpose": "gaming", "in_stock": True,
         "shops": [
             {"source": "Регард", "url": "https://www.regard.ru/catalog/?search=Intel+Core+i7-12700KF", "price": 31000},
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Intel+Core+i7-12700KF", "price": 32000},
         ]},
        {"model": "AMD Ryzen 5 5500", "socket": "AM4", "tdp": 65, "cores": 6, "threads": 12,
         "price": 9500, "purpose": "office", "in_stock": True,
         "shops": [
             {"source": "OZON", "url": "https://www.ozon.ru/search/?text=AMD+Ryzen+5+5500", "price": 9500},
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=AMD+Ryzen+5+5500", "price": 9800},
         ]},
        {"model": "AMD Ryzen 5 5600", "socket": "AM4", "tdp": 65, "cores": 6, "threads": 12,
         "price": 12000, "purpose": "gaming", "in_stock": True,
         "shops": [
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=AMD+Ryzen+5+5600", "price": 12000},
             {"source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=AMD+Ryzen+5+5600", "price": 12500},
         ]},
        {"model": "AMD Ryzen 5 7600", "socket": "AM5", "tdp": 105, "cores": 6, "threads": 12,
         "price": 19000, "purpose": "gaming", "in_stock": True,
         "shops": [
             {"source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=AMD+Ryzen+5+7600", "price": 19000},
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=AMD+Ryzen+5+7600", "price": 19500},
         ]},
        {"model": "AMD Ryzen 7 7700X", "socket": "AM5", "tdp": 170, "cores": 8, "threads": 16,
         "price": 32000, "purpose": "gaming", "in_stock": False,
         "shops": [
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=AMD+Ryzen+7+7700X", "price": 32000},
         ]},
        {"model": "Intel Celeron G6900", "socket": "LGA1700", "tdp": 46, "cores": 2, "threads": 2,
         "price": 4000, "purpose": "office", "in_stock": True,
         "shops": [
             {"source": "Регард", "url": "https://www.regard.ru/catalog/?search=Intel+Celeron+G6900", "price": 4000},
         ]},
        {"model": "AMD Ryzen 9 7950X", "socket": "AM5", "tdp": 230, "cores": 16, "threads": 32,
         "price": 55000, "purpose": "gaming", "in_stock": True,
         "shops": [
             {"source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=AMD+Ryzen+9+7950X", "price": 55000},
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=AMD+Ryzen+9+7950X", "price": 56000},
         ]},
    ],
    "motherboard": [
        {"model": "MSI PRO B760M-P DDR4", "socket": "LGA1700", "form_factor": "mATX", "ram_type": "DDR4",
         "ram_slots": 2, "price": 8500, "in_stock": True,
         "shops": [
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=MSI+PRO+B760M-P+DDR4", "price": 8500},
         ]},
        {"model": "ASRock B550M-HDV", "socket": "AM4", "form_factor": "mATX", "ram_type": "DDR4",
         "ram_slots": 2, "price": 6500, "in_stock": True,
         "shops": [
             {"source": "Регард", "url": "https://www.regard.ru/catalog/?search=ASRock+B550M-HDV", "price": 6500},
         ]},
        {"model": "Gigabyte B650M K", "socket": "AM5", "form_factor": "mATX", "ram_type": "DDR5",
         "ram_slots": 2, "price": 11000, "in_stock": True,
         "shops": [
             {"source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=Gigabyte+B650M+K", "price": 11000},
         ]},
        {"model": "MSI MAG B760 TOMAHAWK WIFI DDR4", "socket": "LGA1700", "form_factor": "ATX", "ram_type": "DDR4",
         "ram_slots": 4, "price": 17000, "in_stock": False,
         "shops": [
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=MSI+MAG+B760+TOMAHAWK+WIFI", "price": 17000},
         ]},
        {"model": "ASRock B650M Pro RS", "socket": "AM5", "form_factor": "mATX", "ram_type": "DDR5",
         "ram_slots": 4, "price": 13500, "in_stock": True,
         "shops": [
             {"source": "OZON", "url": "https://www.ozon.ru/search/?text=ASRock+B650M+Pro+RS", "price": 13500},
         ]},
        {"model": "Gigabyte B550M AORUS ELITE", "socket": "AM4", "form_factor": "mATX", "ram_type": "DDR4",
         "ram_slots": 4, "price": 9500, "in_stock": True,
         "shops": [
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Gigabyte+B550M+AORUS+ELITE", "price": 9500},
         ]},
        {"model": "MSI PRO H610M-G DDR4", "socket": "LGA1700", "form_factor": "mATX", "ram_type": "DDR4",
         "ram_slots": 2, "price": 6000, "in_stock": True,
         "shops": [
             {"source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=MSI+PRO+H610M-G+DDR4", "price": 6000},
         ]},
        {"model": "ASUS TUF GAMING B650-PLUS WIFI", "socket": "AM5", "form_factor": "ATX", "ram_type": "DDR5",
         "ram_slots": 4, "price": 21000, "in_stock": True,
         "shops": [
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=ASUS+TUF+GAMING+B650-PLUS+WIFI", "price": 21000},
         ]},
        {"model": "ASRock H610M-HVS", "socket": "LGA1700", "form_factor": "mATX", "ram_type": "DDR4",
         "ram_slots": 2, "price": 5200, "in_stock": True,
         "shops": [
             {"source": "Регард", "url": "https://www.regard.ru/catalog/?search=ASRock+H610M-HVS", "price": 5200},
         ]},
        {"model": "Gigabyte Z790 AORUS ELITE AX", "socket": "LGA1700", "form_factor": "ATX", "ram_type": "DDR5",
         "ram_slots": 4, "price": 29000, "in_stock": True,
         "shops": [
             {"source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=Gigabyte+Z790+AORUS+ELITE+AX", "price": 29000},
         ]},
    ],
    "ram": [
        {"model": "Kingston Fury Beast DDR4 16GB 3200MHz", "type": "DDR4", "size": 16, "freq": 3200,
         "price": 4200, "in_stock": True,
         "shops": [
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Kingston+Fury+Beast+DDR4+16GB+3200MHz", "price": 4200},
         ]},
        {"model": "Kingston Fury Beast DDR5 16GB 5200MHz", "type": "DDR5", "size": 16, "freq": 5200,
         "price": 5800, "in_stock": True,
         "shops": [
             {"source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=Kingston+Fury+Beast+DDR5+16GB+5200MHz", "price": 5800},
         ]},
        {"model": "G.Skill Ripjaws V DDR4 32GB 3600MHz", "type": "DDR4", "size": 32, "freq": 3600,
         "price": 9500, "in_stock": True,
         "shops": [
             {"source": "Регард", "url": "https://www.regard.ru/catalog/?search=G.Skill+Ripjaws+V+DDR4+32GB+3600MHz", "price": 9500},
         ]},
        {"model": "Corsair Vengeance RGB DDR5 32GB 6000MHz", "type": "DDR5", "size": 32, "freq": 6000,
         "price": 14000, "in_stock": True,
         "shops": [
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Corsair+Vengeance+RGB+DDR5+32GB+6000MHz", "price": 14000},
         ]},
        {"model": "Kingston ValueRAM DDR4 8GB 2666MHz", "type": "DDR4", "size": 8, "freq": 2666,
         "price": 2200, "in_stock": True,
         "shops": [
             {"source": "OZON", "url": "https://www.ozon.ru/search/?text=Kingston+ValueRAM+DDR4+8GB+2666MHz", "price": 2200},
         ]},
        {"model": "Team Group T-Force Delta RGB DDR5 16GB 6400MHz", "type": "DDR5", "size": 16, "freq": 6400,
         "price": 7500, "in_stock": True,
         "shops": [
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Team+Group+T-Force+Delta+RGB+DDR5+16GB", "price": 7500},
         ]},
        {"model": "Patriot Viper Steel DDR4 16GB 3600MHz", "type": "DDR4", "size": 16, "freq": 3600,
         "price": 4800, "in_stock": True,
         "shops": [
             {"source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=Patriot+Viper+Steel+DDR4+16GB+3600MHz", "price": 4800},
         ]},
        {"model": "ADATA XPG Lancer DDR5 32GB 6000MHz", "type": "DDR5", "size": 32, "freq": 6000,
         "price": 13500, "in_stock": True,
         "shops": [
             {"source": "Регард", "url": "https://www.regard.ru/catalog/?search=ADATA+XPG+Lancer+DDR5+32GB+6000MHz", "price": 13500},
         ]},
    ],
    "gpu": [
        {"model": "NVIDIA GeForce GT 1030 2GB", "tdp": 30, "vram": 2, "price": 7000,
         "purpose": "office", "in_stock": True,
         "shops": [
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=GeForce+GT+1030+2GB", "price": 7000},
         ]},
        {"model": "NVIDIA GeForce RTX 3060 12GB", "tdp": 170, "vram": 12, "price": 28000,
         "purpose": "gaming", "in_stock": True,
         "shops": [
             {"source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=GeForce+RTX+3060+12GB", "price": 28000},
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=GeForce+RTX+3060+12GB", "price": 29000},
         ]},
        {"model": "AMD Radeon RX 6600 8GB", "tdp": 132, "vram": 8, "price": 22000,
         "purpose": "gaming", "in_stock": True,
         "shops": [
             {"source": "Регард", "url": "https://www.regard.ru/catalog/?search=Radeon+RX+6600+8GB", "price": 22000},
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Radeon+RX+6600+8GB", "price": 23000},
         ]},
        {"model": "NVIDIA GeForce RTX 4060 8GB", "tdp": 115, "vram": 8, "price": 32000,
         "purpose": "gaming", "in_stock": True,
         "shops": [
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=GeForce+RTX+4060+8GB", "price": 32000},
             {"source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=GeForce+RTX+4060+8GB", "price": 32500},
         ]},
        {"model": "AMD Radeon RX 7800 XT 16GB", "tdp": 263, "vram": 16, "price": 65000,
         "purpose": "gaming", "in_stock": False,
         "shops": [
             {"source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=Radeon+RX+7800+XT+16GB", "price": 65000},
         ]},
        {"model": "Intel UHD Graphics (встроено)", "tdp": 0, "vram": 0, "price": 0,
         "purpose": "office", "in_stock": True,
         "shops": []},
        {"model": "NVIDIA GeForce RTX 4070 12GB", "tdp": 200, "vram": 12, "price": 58000,
         "purpose": "gaming", "in_stock": True,
         "shops": [
             {"source": "OZON", "url": "https://www.ozon.ru/search/?text=GeForce+RTX+4070+12GB", "price": 58000},
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=GeForce+RTX+4070+12GB", "price": 60000},
         ]},
        {"model": "AMD Radeon RX 7600 8GB", "tdp": 165, "vram": 8, "price": 27000,
         "purpose": "gaming", "in_stock": True,
         "shops": [
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Radeon+RX+7600+8GB", "price": 27000},
         ]},
    ],
    "psu": [
        {"model": "Be Quiet! System Power 10 450W", "power": 450, "cert": "80+ Bronze",
         "price": 4000, "in_stock": True,
         "shops": [
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Be+Quiet+System+Power+10+450W", "price": 4000},
         ]},
        {"model": "Cooler Master MWE 650W V2 Bronze", "power": 650, "cert": "80+ Bronze",
         "price": 5500, "in_stock": True,
         "shops": [
             {"source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=Cooler+Master+MWE+650W+V2+Bronze", "price": 5500},
         ]},
        {"model": "Corsair RM750e 750W Gold", "power": 750, "cert": "80+ Gold",
         "price": 9500, "in_stock": True,
         "shops": [
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Corsair+RM750e+750W+Gold", "price": 9500},
         ]},
        {"model": "DeepCool PF600 600W", "power": 600, "cert": "80+ Standard",
         "price": 4500, "in_stock": True,
         "shops": [
             {"source": "OZON", "url": "https://www.ozon.ru/search/?text=DeepCool+PF600+600W", "price": 4500},
         ]},
        {"model": "Thermaltake Toughpower GF3 850W Gold", "power": 850, "cert": "80+ Gold",
         "price": 12000, "in_stock": True,
         "shops": [
             {"source": "Регард", "url": "https://www.regard.ru/catalog/?search=Thermaltake+Toughpower+GF3+850W", "price": 12000},
         ]},
        {"model": "XPG Pylon 550W Bronze", "power": 550, "cert": "80+ Bronze",
         "price": 4200, "in_stock": True,
         "shops": [
             {"source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=XPG+Pylon+550W+Bronze", "price": 4200},
         ]},
        {"model": "Be Quiet! Pure Power 12 M 1000W Gold", "power": 1000, "cert": "80+ Gold",
         "price": 15500, "in_stock": True,
         "shops": [
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Be+Quiet+Pure+Power+12+M+1000W", "price": 15500},
         ]},
    ],
    "case": [
        {"model": "AeroCool CS-101 mATX Black", "form_factor": "mATX", "fans": 1,
         "price": 2500, "in_stock": True,
         "shops": [
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=AeroCool+CS-101+mATX+Black", "price": 2500},
         ]},
        {"model": "DeepCool MACUBE 110 mATX White", "form_factor": "mATX", "fans": 1,
         "price": 3500, "in_stock": True,
         "shops": [
             {"source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=DeepCool+MACUBE+110+mATX+White", "price": 3500},
         ]},
        {"model": "Zalman S2 ATX Black", "form_factor": "ATX", "fans": 3,
         "price": 3000, "in_stock": True,
         "shops": [
             {"source": "OZON", "url": "https://www.ozon.ru/search/?text=Zalman+S2+ATX+Black", "price": 3000},
         ]},
        {"model": "Corsair 4000D Airflow ATX Black", "form_factor": "ATX", "fans": 2,
         "price": 8500, "in_stock": True,
         "shops": [
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=Corsair+4000D+Airflow+ATX+Black", "price": 8500},
         ]},
        {"model": "Cooler Master MasterBox Q300L mATX", "form_factor": "mATX", "fans": 1,
         "price": 4200, "in_stock": True,
         "shops": [
             {"source": "Регард", "url": "https://www.regard.ru/catalog/?search=Cooler+Master+MasterBox+Q300L", "price": 4200},
         ]},
        {"model": "Fractal Design Pop Air ATX Black", "form_factor": "ATX", "fans": 3,
         "price": 7500, "in_stock": True,
         "shops": [
             {"source": "Ситилинк", "url": "https://www.citilink.ru/search/?text=Fractal+Design+Pop+Air+ATX+Black", "price": 7500},
         ]},
        {"model": "AeroCool Cylon mATX Black", "form_factor": "mATX", "fans": 1,
         "price": 2800, "in_stock": True,
         "shops": [
             {"source": "DNS", "url": "https://www.dns-shop.ru/search/?q=AeroCool+Cylon+mATX+Black", "price": 2800},
         ]},
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


def get_price(item):
    """Возвращает минимальную цену среди всех магазинов."""
    if not item.get("shops"):
        return item.get("price", 0)
    return min(shop["price"] for shop in item["shops"])


def get_best_shop(item):
    """Возвращает магазин с минимальной ценой."""
    if not item.get("shops"):
        return None
    return min(item["shops"], key=lambda s: s["price"])


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


def get_compatibility_with_current(category, item, pc):
    """Проверяет совместимость конкретного товара с остальной сборкой."""
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
    return msgs


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
        remaining -= get_price(cpu)

    # MB
    if not error_msg:
        mb_budget = budget * quotas["motherboard"]
        mb_list = [m for m in DATABASE["motherboard"] if m["socket"] == cpu["socket"]]
        mb = smart_pick(mb_list, min(remaining, mb_budget * 1.3), prefer_cheaper=True)
        if not mb:
            error_msg = "❌ Нет материнской платы."
        else:
            pc["motherboard"] = mb
            remaining -= get_price(mb)

    # RAM
    if not error_msg:
        ram_budget = budget * quotas["ram"]
        ram_list = [r for r in DATABASE["ram"] if r["type"] == mb["ram_type"]]
        ram = smart_pick(ram_list, min(remaining, ram_budget * 1.2), prefer_cheaper=True)
        if not ram:
            error_msg = "❌ Нет ОЗУ."
        else:
            pc["ram"] = ram
            remaining -= get_price(ram)

    # GPU
    if not error_msg:
        gpu_budget = budget * quotas["gpu"]
        gpu_list = [g for g in DATABASE["gpu"] if g.get("purpose") == purpose_key]
        gpu = smart_pick(gpu_list, min(remaining, gpu_budget * 1.2), prefer_cheaper=False)
        if not gpu:
            error_msg = "❌ Нет видеокарты."
        else:
            pc["gpu"] = gpu
            remaining -= get_price(gpu)

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
            remaining -= get_price(psu)

    # Case
    if not error_msg:
        case_list = sorted(
            [c for c in DATABASE["case"] if c["form_factor"] == mb["form_factor"] and get_price(c) <= remaining],
            key=lambda x: get_price(x)
        )
        case_ = case_list[0] if case_list else None
        if not case_:
            error_msg = "❌ Нет корпуса."
        else:
            pc["case"] = case_
            remaining -= get_price(case_)

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
        current_price = get_price(current)
        best_shop = get_best_shop(current)
        st.subheader(label)
        stock_icon = "✅" if current.get("in_stock", True) else "❌ Нет в наличии"
        st.write(f"**{current['model']}** — {current_price} руб. | {stock_icon}")
        if best_shop:
            st.markdown(f"🔗 [Купить на {best_shop['source']}]({best_shop['url']}) — {best_shop['price']} руб.")

        # Характеристики компонента
        if key == "cpu":
            st.write(f"Сокет: {current['socket']} | Ядер: {current.get('cores', '—')} | Потоков: {current.get('threads', '—')} | TDP: {current['tdp']} Вт")
        elif key == "motherboard":
            st.write(f"Сокет: {current['socket']} | RAM: {current['ram_type']} | Слотов RAM: {current.get('ram_slots', '—')} | Форм-фактор: {current['form_factor']}")
        elif key == "ram":
            st.write(f"Тип: {current['type']} | Объём: {current['size']} ГБ | Частота: {current.get('freq', '—')} МГц")
        elif key == "gpu":
            st.write(f"Видеопамять: {current.get('vram', '—')} ГБ | TDP: {current['tdp']} Вт")
        elif key == "psu":
            st.write(f"Мощность: {current['power']} Вт | Сертификат: {current.get('cert', '—')}")
        elif key == "case":
            st.write(f"Форм-фактор: {current['form_factor']} | Вентиляторов: {current.get('fans', '—')}")

        # Выпадающий список с учётом совместимости
        all_options = DATABASE[key]
        options_with_compat = []
        for o in all_options:
            o_price = get_price(o)
            o_shop = get_best_shop(o) or {"source": "—"}
            stock = "✅" if o.get("in_stock", True) else "❌"
            compat_msgs = get_compatibility_with_current(key, o, pc)
            is_compat = all("✅" in m for m in compat_msgs)
            if is_compat:
                options_with_compat.append(f"{stock} {o['model']} — {o_price} руб. ({o_shop['source']}) ✅ Совместим")
            else:
                issues = [m.split("❌ ")[1] for m in compat_msgs if "❌" in m]
                options_with_compat.append(f"{stock} {o['model']} — {o_price} руб. ({o_shop['source']}) ❌ {'; '.join(issues)}")

        current_str = f"{'✅' if current.get('in_stock', True) else '❌'} {current['model']} — {current_price} руб. ({best_shop['source'] if best_shop else '—'})"
        # Ищем текущий в списке (частичное совпадение)
        idx = 0
        for i, opt in enumerate(options_with_compat):
            if current['model'] in opt:
                idx = i
                break

        selected_str = st.selectbox("🔄 Заменить:", options_with_compat, index=idx, key=f"select_{key}")

        # Извлекаем модель из выбранной строки
        # Формат: "✅/❌ Модель — цена руб. (магазин) метка"
        parts = selected_str.split(" — ")
        model_part = parts[0].split(" ", 1)[1] if len(parts[0].split(" ", 1)) > 1 else parts[0]
        selected_model = model_part.strip()
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
    st.info("Для каждого компонента указана лучшая цена среди магазинов.")

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
            st.write(f"🔹 Сокет: {comp['socket']} | Ядер: {comp.get('cores', '—')} | Потоков: {comp.get('threads', '—')} | TDP: {comp['tdp']} Вт")
        elif key == "motherboard":
            st.write(f"🔹 Сокет: {comp['socket']} | RAM: {comp['ram_type']} | Слотов: {comp.get('ram_slots', '—')} | Форм-фактор: {comp['form_factor']}")
        elif key == "ram":
            st.write(f"🔹 Тип: {comp['type']} | Объём: {comp['size']} ГБ | Частота: {comp.get('freq', '—')} МГц")
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
                st.markdown(f"- [{shop['source']} — {shop['price']} руб.]({shop['url']})")

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
        st.write(f"Процессор: {pc['cpu']['model']}")
        st.write(f"Видеокарта: {pc['gpu']['model']}")
    with col2:
        total_tdp = pc['cpu']['tdp'] + pc['gpu']['tdp'] + 50
        st.metric("⚡ Энергопотребление", f"{total_tdp} Вт")
        st.write(f"ОЗУ: {pc['ram']['size']} ГБ {pc['ram']['type']}")
    with col3:
        st.metric("📅 Дата подбора", datetime.now().strftime("%d.%m.%Y"))
        st.write(f"Платформа: {pc['cpu']['socket']}")
        st.write(f"Корпус: {pc['case']['form_factor']}")

    st.info("Спасибо за использование программы! Для нового подбора обновите страницу (F5).")
