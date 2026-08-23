import streamlit as st
import sxtwl
from datetime import datetime, timedelta, timezone, date
import warnings

warnings.filterwarnings('ignore')
st.set_page_config(page_title="Ngọa Long Kỳ Môn", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 1. DỮ LIỆU CƠ BẢN & HẰNG SỐ CHÂN TRUYỀN
# ==========================================
thien_can = "甲乙丙丁戊己庚辛壬癸"
dia_chi = "子丑寅卯辰巳午未申酉戌亥"
luc_nghi = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]

WOLONG_OUTER_PALACES = [4, 9, 2, 7, 6, 1, 8, 3] 
WOLONG_FLYING_PATH = [5, 6, 7, 8, 9, 1, 2, 3, 4] 
WOLONG_NUM_TO_STEM = {1: "癸", 2: "丁", 3: "丙", 4: "乙", 5: "戊", 6: "己", 7: "庚", 8: "辛", 9: "壬", 0: "甲"}
WOLONG_ORIGINAL_GATES = {1: "休门", 8: "生门", 3: "伤门", 4: "杜门", 9: "景门", 2: "死门", 7: "惊门", 6: "开门"}
WOLONG_CLOCKWISE_GATES = ["景门", "死门", "惊门", "开门", "休门", "生门", "伤门", "杜门"]

ORIGINAL_STARS = {1: "天蓬", 2: "天芮", 3: "天冲", 4: "天辅", 5: "天禽", 6: "天心", 7: "天柱", 8: "天任", 9: "天英"}
DEITIES = ["值符", "螣蛇", "太阴", "六合", "勾陈", "朱雀", "九地", "九天"] 

solar_term_ju = {
    "冬至":[1,7,4], "小寒":[2,8,5], "大寒":[3,9,6], "立春":[8,5,2], "雨水":[9,6,3], "惊蛰":[1,7,4],
    "春分":[3,9,6], "清明":[4,1,7], "谷雨":[5,2,8], "立夏":[4,1,7], "小满":[5,2,8], "芒种":[6,3,9],
    "夏至":[9,3,6], "小暑":[8,2,5], "大暑":[7,1,4], "立秋":[2,5,8], "处暑":[1,4,7], "白露":[9,3,6],
    "秋分":[7,1,4], "寒露":[6,9,3], "霜降":[5,8,2], "立冬":[6,9,3], "小雪":[5,8,2], "大雪":[4,7,1]
}
wolong_jq_order = ["大雪", "冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种", "夏至", "小暑", "大暑", "立秋", "处暑", "白露", "秋分", "寒露", "霜降", "立冬", "小雪"]

GATE_TO_TRIGRAM = {"休门": "地", "生门": "雷", "伤门": "火", "杜门": "泽", "景门": "天", "死门": "风", "惊门": "水", "开门": "山"}
TIEN_THIEN_MAP = {9: "天", 1: "地", 3: "火", 7: "水", 6: "山", 2: "风", 8: "雷", 4: "泽"}

TRIGRAM_BIN = {"地": [0,0,0], "山": [0,0,1], "水": [0,1,0], "风": [0,1,1], "雷": [1,0,0], "火": [1,0,1], "泽": [1,1,0], "天": [1,1,1]}
BIN_TO_TRIGRAM = {tuple(v): k for k, v in TRIGRAM_BIN.items()}
TRIGRAM_UNICODE = {"天": "☰", "泽": "☱", "火": "☲", "雷": "☳", "风": "☴", "水": "☵", "山": "☶", "地": "☷"}

EVAL_DICT = {
    "风": {"泽":"〇", "天":"△", "风":"✕", "火":"〇", "水":"△", "雷":"〇", "地":"✕", "山":"〇"},
    "天": {"泽":"✕", "天":"△", "风":"✕", "火":"〇", "水":"✕", "雷":"△", "地":"✕", "山":"✕"},
    "水": {"泽":"✕", "天":"✕", "风":"✕", "火":"〇", "水":"✕", "雷":"✕", "地":"〇", "山":"〇"},
    "泽": {"泽":"△", "天":"✕", "风":"✕", "火":"✕", "水":"✕", "雷":"✕", "地":"〇", "山":"〇"},
    "山": {"泽":"△", "天":"〇", "风":"✕", "火":"✕", "水":"✕", "雷":"〇", "地":"✕", "山":"✕"},
    "火": {"泽":"✕", "天":"〇", "风":"〇", "火":"✕", "水":"✕", "雷":"△", "地":"〇", "山":"✕"},
    "地": {"泽":"〇", "天":"〇", "风":"〇", "火":"✕", "水":"✕", "雷":"〇", "地":"△", "山":"△"},
    "雷": {"泽":"✕", "天":"△", "风":"〇", "火":"〇", "水":"〇", "雷":"△", "地":"〇", "山":"✕"}
}

HEX_NAME_DICT = {
    ("天","天"): "Càn", ("地","地"): "Khôn", ("水","雷"): "Truân", ("山","水"): "Mông",
    ("水","天"): "Nhu", ("天","水"): "Tụng", ("地","水"): "Sư", ("水","地"): "Tỷ",
    ("风","天"): "Tiểu Súc", ("天","泽"): "Lý", ("地","天"): "Thái", ("天","地"): "Bĩ",
    ("天","火"): "Đ.Nhân", ("火","天"): "Đại Hữu", ("地","山"): "Khiêm", ("雷","地"): "Dự",
    ("泽","雷"): "Tùy", ("山","风"): "Cổ", ("地","泽"): "Lâm", ("风","地"): "Quan",
    ("火","雷"): "Phệ Hạp", ("山","火"): "Bí", ("山","地"): "Bác", ("地","雷"): "Phục",
    ("天","雷"): "Vô Vọng", ("山","天"): "Đại Súc", ("山","雷"): "Di", ("泽","风"): "Đại Quá",
    ("水","水"): "Khảm", ("火","火"): "Ly", ("泽","山"): "Hàm", ("雷","风"): "Hằng",
    ("天","山"): "Độn", ("雷","天"): "Đ.Tráng", ("火","地"): "Tấn", ("地","火"): "Minh Di",
    ("风","火"): "Gia Nhân", ("火","泽"): "Khuê", ("水","山"): "Kiển", ("雷","水"): "Giải",
    ("山","泽"): "Tổn", ("风","雷"): "Ích", ("泽","天"): "Quải", ("天","风"): "Cấu",
    ("泽","地"): "Tụy", ("地","风"): "Thăng", ("泽","水"): "Khốn", ("水","风"): "Tỉnh",
    ("泽","火"): "Cách", ("火","风"): "Đỉnh", ("雷","雷"): "Chấn", ("山","山"): "Cấn",
    ("风","山"): "Tiệm", ("雷","泽"): "Quy Muội", ("雷","火"): "Phong", ("火","山"): "Lữ",
    ("风","风"): "Tốn", ("泽","泽"): "Đoài", ("风","水"): "Hoán", ("水","泽"): "Tiết",
    ("风","泽"): "T.Phu", ("雷","山"): "Tiểu Quá", ("水","火"): "Ký Tế", ("火","水"): "Vị Tế"
}

# ==========================================
# 2. LOGIC LỊCH
# ==========================================
def calculate_correct_ju(nguyen, can_gio, chi_gio, tiet_khi):
    base_ju_dict = {"夏至":9,"小暑":7,"大暑":6,"立秋":5,"处暑":6,"白露":5,"秋分":4,"寒露":9,"霜降":8,"立冬":7,"小雪":2,"大雪":1,"冬至":1,"小寒":3,"大寒":4,"立春":5,"雨水":4,"惊蛰":5,"春分":6,"清明":1,"谷雨":2,"立夏":3,"小满":8,"芒种":9}
    yin_dun_terms = ["夏至", "小暑", "大暑", "立秋", "处暑", "白露", "秋分", "寒露", "霜降", "立冬", "小雪", "大雪"]
    dun_type = -1 if tiet_khi in yin_dun_terms else 1
    tuan_index = ((thien_can.index(can_gio) - dia_chi.index(chi_gio)) % 12) // 2
    nguyen_multiplier = 0 if nguyen == "上" else 1 if nguyen == "中" else 2
    raw_ju = base_ju_dict[tiet_khi] + (dun_type * (tuan_index + 6 * nguyen_multiplier))
    return (raw_ju - 1) % 9 + 1

def get_wushu_dun(day_stem, hour_branch):
    return thien_can[((thien_can.index(day_stem) % 5) * 2 + dia_chi.index(hour_branch)) % 10]

def get_xun_leader(can, chi):
    return {"子":"戊", "戌":"己", "申":"庚", "午":"辛", "辰":"壬", "寅":"癸"}[dia_chi[(dia_chi.index(chi) - thien_can.index(can)) % 12]]

def get_wolong_calendar_data(lunar_month, lunar_day):
    abs_day = ((lunar_month - 11) % 12) * 30 + (lunar_day - 1)
    wl_jieqi = wolong_jq_order[abs_day // 15 % 24]
    day_in_jq = abs_day % 15
    wl_yuan = "上" if day_in_jq < 5 else "中" if day_in_jq < 10 else "下"
    wl_dun = "阳遁" if 1 <= (abs_day // 15 % 24) <= 12 else "阴遁"
    return thien_can[(45 + abs_day) % 10], dia_chi[(45 + abs_day) % 12], wl_jieqi, wl_yuan, wl_dun

def get_hour_nine_star(day_branch, hour_branch, dun_type):
    hb_idx = dia_chi.index(hour_branch) 
    start_star = 1 if day_branch in ["子","午","卯","酉"] else (4 if day_branch in ["辰","戌","丑","未"] else 7)
    if dun_type == "阴遁": start_star = 7 if day_branch in ["辰","戌","丑","未"] else (4 if day_branch in ["寅","申","巳","亥"] else 1)
    res = (start_star + hb_idx) % 9 if dun_type == "阳遁" else (start_star - hb_idx) % 9
    return 9 if res == 0 else res

# ==========================================
# 3. LẬP BÀN TOÁN HỌC
# ==========================================
def lap_que_wolong(can_gio, chi_gio, dun_type, ju_num, chi_ngay):
    cung_data = {i: {'dia': '', 'mon': '', 'thien': '', 'sao': '', 'than': '', 'hour_star': ''} for i in range(1, 10)}
    
    current_val = (10 - ju_num) if dun_type == "阳遁" else ju_num
    step_dir = 1 if dun_type == "阳遁" else -1
    dia_ban = {}
    for cung in WOLONG_FLYING_PATH:
        can = WOLONG_NUM_TO_STEM.get(current_val, "")
        dia_ban[cung] = can
        cung_data[cung]['dia'] = can
        current_val += step_dir
        if current_val > 9: current_val = 1
        elif current_val < 1: current_val = 9

    luc_nghi_gio = get_xun_leader(can_gio, chi_gio)
    
    p_circle_list = [c for c, can in dia_ban.items() if can == luc_nghi_gio] 
    p_circle = p_circle_list[0] if p_circle_list else 5

    target_stem = luc_nghi_gio if can_gio == '甲' else can_gio
    p_hour_stem_list = [c for c, can in dia_ban.items() if can == target_stem]
    p_hour_stem = p_hour_stem_list[0] if p_hour_stem_list else 5

    if p_circle == 5:
        for i in WOLONG_OUTER_PALACES: cung_data[i]['thien'] = dia_ban[i] 
        if p_hour_stem != 5: cung_data[p_hour_stem]['thien'] = luc_nghi_gio 
        cung_data[5]['thien'] = can_gio 
    elif p_hour_stem == 5:
        for i in WOLONG_OUTER_PALACES: cung_data[i]['thien'] = dia_ban[i] 
        cung_data[p_circle]['thien'] = can_gio 
        cung_data[5]['thien'] = luc_nghi_gio 
    else:
        idx_source = WOLONG_OUTER_PALACES.index(p_circle)
        idx_target = WOLONG_OUTER_PALACES.index(p_hour_stem)
        offset = (idx_target - idx_source) % 8
        for i in range(8):
            cung_data[WOLONG_OUTER_PALACES[i]]['thien'] = dia_ban[WOLONG_OUTER_PALACES[(i - offset) % 8]]
        cung_data[5]['thien'] = dia_ban[5] 

    # BÁT MÔN (Lưu p_land để dùng cho Ngọc Nữ Thủ Môn)
    p_land = 5
    if p_circle != 5:
        s_steps = thien_can.index(can_gio) + 1
        seq = [1,2,3,4,5,6,7,8,9] if dun_type == "阳遁" else [9,8,7,6,5,4,3,2,1]
        p_land = seq[(seq.index(p_circle) + s_steps - 1) % 9]

    if p_circle == 5:
        for p, door in WOLONG_ORIGINAL_GATES.items(): cung_data[p]['mon'] = door
    else:
        g_start = WOLONG_ORIGINAL_GATES[p_circle]
        if p_land == 5:
            for p, door in WOLONG_ORIGINAL_GATES.items(): cung_data[p]['mon'] = door
        else:
            idx_land = WOLONG_OUTER_PALACES.index(p_land)
            idx_gate = WOLONG_CLOCKWISE_GATES.index(g_start)
            for i in range(8):
                cung_data[WOLONG_OUTER_PALACES[(idx_land + i) % 8]]['mon'] = WOLONG_CLOCKWISE_GATES[(idx_gate + i) % 8]

    # Khóa cứng Trung Cung (Cung 5) tạo Hạ Quái Đoài/Cấn theo chuẩn Lập Hướng
    cung_data[5]['mon'] = "惊门" if dun_type == "阳遁" else "生门"

    curr_star = get_hour_nine_star(chi_ngay, chi_gio, dun_type)
    for cung in WOLONG_FLYING_PATH:
        cung_data[cung]['hour_star'] = curr_star
        curr_star = 1 if curr_star == 9 else curr_star + 1

    luoshu_9 = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    idx_base_star = luoshu_9.index(p_circle)
    idx_target_star = luoshu_9.index(p_hour_stem)
    shift_for_star = (idx_target_star - idx_base_star) % 9
    for i in range(1, 10):
        idx_new = (luoshu_9.index(i) + shift_for_star) % 9
        cung_data[luoshu_9[idx_new]]['sao'] = ORIGINAL_STARS[i]
    cung_data[5]['sao'] = "" 

    anchor_palace = p_hour_stem
    if anchor_palace == 5:
        anchor_palace = 8 if dun_type == "阳遁" else 7
        
    idx_anchor = WOLONG_OUTER_PALACES.index(anchor_palace)
    for i in range(8):
        if dun_type == "阳遁":
            cung_data[WOLONG_OUTER_PALACES[(idx_anchor + i) % 8]]['than'] = DEITIES[i]
        else:
            cung_data[WOLONG_OUTER_PALACES[(idx_anchor - i) % 8]]['than'] = DEITIES[i]
    cung_data[5]['than'] = ""

    # Trích xuất cung_phi_tinh (Cung hạ cánh Lạc Thư vào Trung cung) để soi Địa (Hạ Quái)
    cung_phi_tinh = cung_data[5]['hour_star']

    return cung_data, p_circle, cung_phi_tinh, p_land

# ==========================================
# 4. MODULE PHÂN TÍCH CÁCH CỤC
# ==========================================
def qimen_analyzer_hojo(cung_data, can_tuan, p_land):
    FORMATION_RANKS = {
        "天遁": 1, "地遁": 1, "人遁": 1, "神遁": 1, "鬼遁": 1,
        "大格": 1, "小格": 1, "刑格": 1, "戦格": 1, "飛宮格": 1, "伏宮格": 1, 
        "青竜逃走": 1, "白虎猖狂": 1, "熒惑入白": 1, "太白入熒": 1, "朱雀投江": 1, "螣蛇妖嬌": 1,
        "青竜返首": 2, "飛鳥跌穴": 2, "玉女守門": 2, "乙奇得使": 2, "丙奇得使": 2, "丁奇得使": 2, 
        "竜遁": 2, "虎遁": 2, "風遁": 2, "雲遁": 2, 
        "乙奇入墓": 2, "丙奇入墓": 2, "丁奇入墓": 2,
        "干伏吟": 2, "干反吟": 2, 
        "乙奇昇殿": 3, "丙奇昇殿": 3, "丁奇昇殿": 3,
        "星門伏吟": 3, "星門反吟": 3, "八門受制": 3, "六儀撃刑": 3
    }
    
    cung_status = {i: [] for i in range(1, 10)}
    can_can_data = {'甲':{'甲':'吉','乙':'吉','丙':'吉','丁':'吉','戊':'凶','己':'吉','庚':'大凶','辛':'凶','壬':'凶','癸':'吉'}, '乙':{'甲':'吉','乙':'凶','丙':'吉','丁':'吉','戊':'吉','己':'吉','庚':'凶','辛':'大凶','壬':'吉','癸':'凶'}, '丙':{'甲':'吉','乙':'吉','丙':'凶','丁':'吉','戊':'吉','己':'吉','庚':'大凶','辛':'吉','壬':'吉','癸':'凶'}, '丁':{'甲':'吉','乙':'吉','丙':'吉','丁':'吉','戊':'吉','己':'凶','庚':'吉','辛':'凶','壬':'吉','癸':'大凶'}, '戊':{'甲':'凶','乙':'吉','丙':'吉','丁':'吉','戊':'凶','己':'凶','庚':'凶','辛':'凶','壬':'吉','癸':'凶'}, '己':{'甲':'凶','乙':'吉','丙':'凶','丁':'凶','戊':'吉','己':'凶','庚':'凶','辛':'凶','壬':'凶','癸':'凶'}, '庚':{'甲':'大凶','乙':'凶','丙':'大凶','丁':'吉','戊':'凶','己':'大凶','庚':'大凶','辛':'凶','壬':'大凶','癸':'大凶'}, '辛':{'甲':'凶','乙':'大凶','丙':'凶','丁':'吉','戊':'凶','己':'凶','庚':'凶','辛':'凶','壬':'凶','癸':'凶'}, '壬':{'甲':'凶','乙':'凶','丙':'凶','丁':'吉','戊':'吉','己':'凶','庚':'凶','辛':'吉','壬':'凶','癸':'凶'}, '癸':{'甲':'吉','乙':'凶','丙':'吉','丁':'大凶','戊':'吉','己':'凶','庚':'大凶','辛':'凶','壬':'凶','癸':'凶'}}

    def get_actual(can): return '甲' if can == can_tuan else can

    for p, d in cung_data.items():
        if p == 5: continue 
        
        raw_t = d['thien']
        raw_d = d['dia']
        if not raw_t or not raw_d: continue

        t_can = get_actual(raw_t)
        d_can = get_actual(raw_d)
        
        mon, sao, than = d['mon'], d['sao'], d['than']

        if t_can == '甲' and d_can == '丙': cung_status[p].append(("青竜返首", "#CC0000"))
        if t_can == '丙' and d_can == '甲': cung_status[p].append(("飛鳥跌穴", "#CC0000"))
        # Ngọc Nữ Thủ Môn: Căn cứ vào điểm hạ cánh của Trực Sử (p_land)
        if t_can == '丁' and p == p_land: cung_status[p].append(("玉女守門", "#CC0000"))
        
        if t_can == '乙' and p == 3: cung_status[p].append(("乙奇昇殿", "#CC0000"))
        if t_can == '丙' and p == 9: cung_status[p].append(("丙奇昇殿", "#CC0000"))
        if t_can == '丁' and p == 7: cung_status[p].append(("丁奇昇殿", "#CC0000")) 
        
        if t_can == '乙' and d_can == '己': cung_status[p].append(("乙奇得使", "#CC0000"))
        if t_can == '丙' and d_can == '戊': cung_status[p].append(("丙奇得使", "#CC0000"))
        if t_can == '丁' and d_can == '壬': cung_status[p].append(("丁奇得使", "#CC0000"))
        
        if t_can == '丙' and d_can == '戊' and mon == "生门": cung_status[p].append(("天遁", "#CC0000"))
        if t_can == '乙' and d_can == '己' and mon == "开门": cung_status[p].append(("地遁", "#CC0000"))
        if t_can == '丁' and mon == "休门" and than == "太阴": cung_status[p].append(("人遁", "#CC0000"))
        if t_can == '丙' and mon == "生门" and than == "九天": cung_status[p].append(("神遁", "#CC0000"))
        if t_can == '丁' and mon == "开门" and than == "九地": cung_status[p].append(("鬼遁", "#CC0000"))
        if (t_can == '乙' and mon == "开门") or (t_can == '乙' and p == 6 and mon in ["休门", "生门"]): cung_status[p].append(("竜遁", "#CC0000"))
        if (t_can == '乙' and mon == "生门") or (t_can == '乙' and p == 8 and mon in ["休门", "开门"]): cung_status[p].append(("虎遁", "#CC0000"))
        if t_can == '乙' and p == 4 and mon in ["休门", "生门", "开门"]: cung_status[p].append(("風遁", "#CC0000"))
        if t_can == '乙' and p == 2 and mon in ["休门", "生门", "开门"]: cung_status[p].append(("雲遁", "#CC0000"))

        if (t_can == '己' and p == 2) or (t_can == '辛' and p == 9) or (t_can == '壬' and p == 4) or (t_can == '癸' and p == 4) or (t_can == '戊' and p == 3) or (t_can == '庚' and p == 8): 
            cung_status[p].append(("六儀撃刑", "#000000"))
            
        if t_can == '乙' and p == 2: cung_status[p].append(("乙奇入墓", "#000000"))
        if t_can == '丙' and p == 6: cung_status[p].append(("丙奇入墓", "#000000"))
        if t_can == '丁' and p == 6: cung_status[p].append(("丁奇入墓", "#000000"))
        
        if t_can == '庚' and d_can == '癸': cung_status[p].append(("大格", "#000000"))
        if t_can == '庚' and d_can == '壬': cung_status[p].append(("小格", "#000000"))
        if t_can == '庚' and d_can == '己': cung_status[p].append(("刑格", "#000000"))
        if t_can == '庚' and d_can == '庚': cung_status[p].append(("戦格", "#000000"))
        
        if t_can == '庚' and d_can == '甲': cung_status[p].append(("伏宮格", "#000000"))
        if t_can == '甲' and d_can == '庚': cung_status[p].append(("飛宮格", "#000000"))
        
        if t_can == '乙' and d_can == '辛': cung_status[p].append(("青竜逃走", "#000000"))
        if t_can == '辛' and d_can == '乙': cung_status[p].append(("白虎猖狂", "#000000"))
        if t_can == '丙' and d_can == '庚': cung_status[p].append(("熒惑入白", "#000000"))
        if t_can == '庚' and d_can == '丙': cung_status[p].append(("太白入熒", "#000000"))
        if t_can == '丁' and d_can == '癸': cung_status[p].append(("朱雀投江", "#000000"))
        if t_can == '癸' and d_can == '丁': cung_status[p].append(("螣蛇妖嬌", "#000000"))

        if (mon == "休门" and p == 9) or (mon == "景门" and p == 7) or (mon == "生门" and p == 1) or (mon == "开门" and p == 3):
            cung_status[p].append(("八門受制", "#000000"))

        if t_can == d_can and t_can not in ['甲', '丁']: cung_status[p].append(("干伏吟", "#000000"))
        if (t_can, d_can) in [('戊','辛'), ('辛','戊'), ('己','壬'), ('壬','己'), ('庚','癸'), ('癸','庚')]:
            cung_status[p].append(("干反吟", "#000000"))

        sao_mon_goc = {"天蓬":"休门", "天芮":"死门", "天冲":"伤门", "天辅":"杜门", "天心":"开门", "天柱":"惊门", "天任":"生门", "天英":"景门"}
        mon_doi_xung = {"休门":"景门", "死门":"生门", "伤门":"惊门", "杜门":"开门", "开门":"杜门", "惊门":"伤门", "生门":"死门", "景门":"休门"}
        
        if sao in sao_mon_goc:
            if mon == sao_mon_goc[sao]: cung_status[p].append(("星門伏吟", "#000000"))
            elif mon == mon_doi_xung[sao_mon_goc[sao]]: cung_status[p].append(("星門反吟", "#000000"))

    stem_colors = {i: "#000000" for i in range(1, 10)} 
    for p in range(1, 10):
        if p == 5 or p not in cung_data: continue
        t_can = '甲' if cung_data[p]['thien'] == can_tuan else cung_data[p]['thien']
        d_can = '甲' if cung_data[p]['dia'] == can_tuan else cung_data[p]['dia']
        if t_can in can_can_data and d_can in can_can_data[t_can]:
            eval_res = can_can_data[t_can][d_can]
            stem_colors[p] = "#000000" if "凶" in eval_res else "#CC0000"

    for p in cung_status:
        cung_status[p].sort(key=lambda x: FORMATION_RANKS.get(x[0], 99))
        formatted_list = []
        for raw_name, color in cung_status[p]:
            rank = FORMATION_RANKS.get(raw_name)
            if rank == 3: continue 
            if rank: display_name = f"<span style='font-size: 0.8em; font-weight: normal; color: #666;'>({rank})</span> {raw_name}"
            else: display_name = raw_name
            formatted_list.append((display_name, color))
        cung_status[p] = formatted_list

    return cung_status, stem_colors

# ==========================================
# 5. GIAO DIỆN HTML RENDER 
# ==========================================
def render_html_table(cung_data, cung_status, stem_colors, can_tuan, cung_phi_tinh, user_birth_star):
    
    # "地" (HẠ QUÁI) ĐƯỢC XÁC ĐỊNH BỞI TỌA ĐỘ CỬU CUNG PHI TINH
    global_lower_gate = cung_data[cung_phi_tinh]['mon']
    global_lower_tri = GATE_TO_TRIGRAM.get(global_lower_gate, "天")

    luoi_lac_thu = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
    html = """
    <style>
        .qmdj-table { border-collapse: collapse; width: 100%; max-width: 510px; min-width: 400px; height: 430px; table-layout: fixed; font-family: sans-serif; margin: 0 auto; background: #fff;}
        .qmdj-td { border: 1px solid #aaa; width: 33.33%; position: relative; vertical-align: top; padding: 10px; }
        .cell-main {
            display: grid; grid-template-columns: auto auto 1fr; grid-template-rows: 22px 22px 22px;   
            column-gap: 15px; row-gap: 6px; height: 100%; min-height: 85px; align-content: start; margin-top: 5px; margin-left: 5px; 
        }
        /* THẦN - TINH - MÔN: Màu XÁM NHẸ */
        .item-than  { grid-column: 1 / span 2; grid-row: 1; font-size: 15px; color: #999999; text-align: left; }
        .item-tinh  { grid-column: 1; grid-row: 2; font-size: 15px; color: #999999; text-align: left; }
        .item-mon   { grid-column: 1; grid-row: 3; font-size: 15px; color: #999999; text-align: left; }
        
        .bottom-left-phitinh { position: absolute; bottom: 3px; left: 5px; font-size: 15px; color: #555; font-weight: bold; }
        .star-highlight { display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; border: 2px solid #0000FF; border-radius: 50%; color: #0000FF; background-color: rgba(0,0,255,0.05); }
        
        /* CÁCH CỤC CHUYỂN LÊN GÓC TRÊN PHẢI */
        .top-right-panel { position: absolute; top: 4px; right: 5px; display: flex; flex-direction: column; align-items: flex-end; text-align: right; font-size: 11px;}
        .formation-item { margin-top: 1px; font-weight: bold; letter-spacing: 1px; color: #000; }
        
        /* QUẺ DỊCH CHUYỂN XUỐNG GÓC DƯỚI PHẢI, SÁT LỀ, ĐỘ RỘNG CỐ ĐỊNH ĐỂ CĂN TÊN */
        .bottom-right-hex { position: absolute; bottom: 5px; right: 2px; display: flex; flex-direction: column; align-items: center; width: 44px; }
    </style>
    <table class="qmdj-table">
    """

    for row in luoi_lac_thu:
        html += "<tr>"
        for p in row:
            d = cung_data[p]
            
            # Vòng tròn xanh Giờ Sinh
            h_star_val = d['hour_star']
            if h_star_val == user_birth_star:
                phi_tinh_html = f"<div class='bottom-left-phitinh'><span class='star-highlight'>{h_star_val}</span></div>"
            else:
                phi_tinh_html = f"<div class='bottom-left-phitinh'>{h_star_val}</div>"

            # XỬ LÝ MÀU CAN & GẠCH CHÂN GIÁP
            t_can, d_can = d.get('thien', ''), d.get('dia', '')
            base_color = stem_colors.get(p, "#000000") 
            
            t_decor = "underline" if t_can == can_tuan else "none"
            d_decor = "underline" if d_can == can_tuan else "none"
            
            t_style = f"font-weight: bold; color: {base_color}; font-size: 16px; text-decoration: {t_decor}; text-underline-offset: 4px; text-decoration-thickness: 2px;"
            d_style = f"font-weight: bold; color: {base_color}; font-size: 16px; text-decoration: {d_decor}; text-underline-offset: 4px; text-decoration-thickness: 2px;"

            if p == 5:
                html += f"""
                <td class="qmdj-td" style="background-color: transparent; text-align: center;">
                    {phi_tinh_html}
                    <div style="position: absolute; bottom: 30px; right: 6px; {t_style}">{t_can}</div>
                    <div style="position: absolute; bottom: 6px; right: 6px; {d_style}">{d_can}</div>
                </td>"""
            else:
                out_upper_tri = TIEN_THIEN_MAP[p]
                out_lower_tri = global_lower_tri 
                
                out_eval = EVAL_DICT.get(out_upper_tri, {}).get(out_lower_tri, "△")
                
                # --- PHÂN LOẠI MÀU SẮC QUẺ DỊCH 3 CẤP ĐỘ ---
                if out_eval == "〇":
                    out_hex_color = "#CC0000"  # Cát: Màu Đỏ
                elif out_eval == "△":
                    out_hex_color = "#B8860B"  # Bình hòa: Màu Vàng Nâu (Dark Goldenrod)
                else:
                    out_hex_color = "#000000"  # Hung: Màu Đen
                # -------------------------------------------
                out_hex_name = HEX_NAME_DICT.get((out_upper_tri, out_lower_tri), "Không rõ")
                
                # Quẻ ở dưới phải (Căn giữa width 44px để thẳng mép)
                outer_hex_html = f"""
                <div class="bottom-right-hex">
                    <div style="font-size:26px; line-height:0.85; color:{out_hex_color}; margin-bottom: 2px; text-align: center;">
                        {TRIGRAM_UNICODE[out_upper_tri]}<br>{TRIGRAM_UNICODE[out_lower_tri]}
                    </div>
                    <div style="width: 100%; font-size:10px; font-weight:normal; color:#999999; letter-spacing: -0.5px; text-align: center;">{out_hex_name}</div>
                </div>
                """

                # Cách cục ở trên phải
                form_html = "".join([f"<div class='formation-item' style='color:{f_color};'>{f_name}</div>" for f_name, f_color in cung_status[p]])
                top_right_html = f"<div class='top-right-panel'>{form_html}</div>"
                
                html += f"""
                <td class="qmdj-td" style="background-color: transparent;">
                    {phi_tinh_html}
                    {top_right_html}
                    {outer_hex_html}
                    <div class="cell-main">
                        <div class="item-than">{d['than']}</div>
                        <div class="item-tinh">{d['sao']}</div>
                        <div class="item-mon"><span>{d['mon']}</span></div>
                        <div style="grid-column: 2; grid-row: 2; text-align: left; display: flex; align-items: center; {t_style}">{t_can}</div>
                        <div style="grid-column: 2; grid-row: 3; text-align: left; display: flex; align-items: center; {d_style}">{d_can}</div>
                    </div>
                </td>"""
        html += "</tr>"
    html += "</table>"
    return html

# ==========================================
# 6. STREAMLIT APP MAIN
# ==========================================
def get_current_vn_time(): return datetime.now(timezone(timedelta(hours=7)))
if "init_dt" not in st.session_state: st.session_state.init_dt = get_current_vn_time()

col1, col2, col3, col4, col5, col6 = st.columns([1, 0.8, 0.8, 1, 0.8, 0.8])
with col1: selected_date = st.date_input("Ngày Xem", value=st.session_state.init_dt.date(), min_value=date(1900, 1, 1), max_value=date(2100, 12, 31))
with col2: selected_hour = st.selectbox("Giờ Xem", options=list(range(24)), index=st.session_state.init_dt.hour)
with col3: selected_minute = st.selectbox("Phút Xem", options=list(range(60)), index=st.session_state.init_dt.minute)
with col4: birth_date = st.date_input("Ngày Sinh", value=date(1993, 1, 7), min_value=date(1900, 1, 1), max_value=date(2100, 12, 31))
with col5: birth_hour = st.selectbox("Giờ Sinh", options=list(range(24)), index=8)
with col6: birth_minute = st.selectbox("Phút Sinh", options=list(range(60)), index=15)

hoa_giap_60 = [thien_can[i%10] + dia_chi[i%12] for i in range(60)]
cuc_so_list = [f"阳遁{i}局" for i in range(1, 10)] + [f"阴遁{i}局" for i in range(1, 10)]

st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
_, col_opt1, col_opt2, _ = st.columns([3, 2.5, 2.5, 3])
with col_opt1: 
    manual_hoagiap = st.selectbox("Hoa Giáp", options=["Tùy Chọn"] + hoa_giap_60)
with col_opt2: 
    manual_cucso = st.selectbox("Cục Số", options=["Tùy Chọn"] + cuc_so_list)

user_dt = datetime.combine(selected_date, datetime.min.time()).replace(hour=selected_hour, minute=selected_minute)
actual_date = user_dt.date() + timedelta(days=1) if user_dt.hour >= 23 else user_dt.date()
chi_gio_idx = 0 if user_dt.hour >= 23 else (user_dt.hour + 1) // 2 % 12
chi_gio = dia_chi[chi_gio_idx]

day_obj = sxtwl.fromSolar(actual_date.year, actual_date.month, actual_date.day)
lunar_m = day_obj.getLunarMonth()
lunar_d = day_obj.getLunarDay()

wl_can, wl_chi, wl_jieqi, wl_yuan, wl_dun = get_wolong_calendar_data(lunar_m, lunar_d)
can_gio = get_wushu_dun(wl_can, chi_gio)
hoa_giap_hien_tai = can_gio + chi_gio

wl_ju = calculate_correct_ju(wl_yuan, can_gio, chi_gio, wl_jieqi)

b_dt = datetime.combine(birth_date, datetime.min.time()).replace(hour=birth_hour, minute=birth_minute)
b_actual_date = b_dt.date() + timedelta(days=1) if b_dt.hour >= 23 else b_dt.date()
b_chi_idx = 0 if b_dt.hour >= 23 else (b_dt.hour + 1) // 2 % 12
b_chi_gio = dia_chi[b_chi_idx]
b_day_obj = sxtwl.fromSolar(b_actual_date.year, b_actual_date.month, b_actual_date.day)
b_lunar_m = b_day_obj.getLunarMonth()
b_wl_can, b_wl_chi, _, _, b_wl_dun = get_wolong_calendar_data(b_lunar_m, b_day_obj.getLunarDay())
user_birth_star = get_hour_nine_star(b_wl_chi, b_chi_gio, b_wl_dun)

if manual_hoagiap != "Tùy Chọn":
    can_gio = manual_hoagiap[0]
    chi_gio = manual_hoagiap[1]
    hoa_giap_hien_tai = manual_hoagiap

if manual_cucso != "Tùy Chọn":
    wl_dun = "阳遁" if "阳" in manual_cucso else "阴遁"
    wl_ju = int(manual_cucso.replace("阳遁", "").replace("阴遁", "").replace("局", ""))

# TÍNH TOÁN BÀN LÕI
data, p_circle, cung_phi_tinh, p_land = lap_que_wolong(can_gio, chi_gio, wl_dun, wl_ju, wl_chi)

# XỬ LÝ CÁCH CỤC
can_tuan = get_xun_leader(can_gio, chi_gio)
cung_st, stem_colors = qimen_analyzer_hojo(data, can_tuan, p_land)

bazi_chuoi = f"农历 {lunar_m}月 {lunar_d}日 | {wl_can}{wl_chi} | {wl_jieqi} {wl_yuan}元"
title = f"<h3 style='margin-bottom:8px; font-family:sans-serif; color: #1a1a1a; font-weight: normal; font-size: 18px; text-align: center;'>{bazi_chuoi}</h3>"
sub_title = f"<h4 style='margin-top:0px; margin-bottom:15px; font-family:sans-serif; color: #555; font-weight: normal; font-size: 16px; text-align: center;'>{hoa_giap_hien_tai}时 | {wl_dun}{wl_ju}局</h4>"

qimen_board_html = render_html_table(data, cung_st, stem_colors, can_tuan, cung_phi_tinh, user_birth_star)

combined_html = f"""<div style="display: flex; flex-direction: column; align-items: center; width: 100%; padding-top: 10px;"><div style="display: flex; flex-direction: column; align-items: center; width: 100%; max-width: 510px;">{title}{sub_title}{qimen_board_html}</div></div>"""
st.components.v1.html(combined_html, height=550, scrolling=True)


# ==========================================
# 7. MODULE SCAN: DỤNG SỰ (TÌM KIẾM)
# ==========================================
st.markdown("---")
st.markdown("<h3 style='text-align: center; color: #333; font-family: sans-serif; margin-bottom: 20px;'>DỤNG SỰ</h3>", unsafe_allow_html=True)

FORMATION_RANKS_LOCAL = {
    "天遁": 1, "地遁": 1, "人遁": 1, "神遁": 1, "鬼遁": 1,
    "大格": 1, "小格": 1, "刑格": 1, "戦格": 1, "飛宮格": 1, "伏宮格": 1, 
    "青竜逃走": 1, "白虎猖狂": 1, "熒惑入白": 1, "太白入熒": 1, "朱雀投江": 1, "螣蛇妖嬌": 1,
    "青竜返首": 2, "飛鳥跌穴": 2, "玉女守門": 2, "乙奇得使": 2, "丙奇得使": 2, "丁奇得使": 2, 
    "竜遁": 2, "虎遁": 2, "風遁": 2, "雲遁": 2, 
    "乙奇入墓": 2, "丙奇入墓": 2, "丁奇入墓": 2,
    "干伏吟": 2, "干反吟": 2, 
    "乙奇昇殿": 3, "丙奇昇殿": 3, "丁奇昇殿": 3,
    "星門伏吟": 3, "星門反吟": 3, "八门受制": 3, "六儀撃刑": 3
}

def format_ui_list(raw_list):
    valid_items = [x for x in raw_list if x != ""]
    valid_items.sort(key=lambda x: (FORMATION_RANKS_LOCAL.get(x, 99), x))
    res = [""]
    for x in valid_items:
        rank = FORMATION_RANKS_LOCAL.get(x)
        if rank: res.append(f"({rank}) {x}")
        else: res.append(x)
    return res

def extract_raw_name(ui_name):
    if not ui_name: return ""
    return ui_name.split(") ")[1] if ") " in ui_name else ui_name

huong_list = {"": None, "坎 (345 - 15)": 1, "艮 (15 - 75)": 8, "震 (75 - 105)": 3, "巽 (105 - 165)": 4, "離 (165 - 195)": 9, "坤 (195 - 255)": 2, "兌 (255 - 285)": 7, "乾 (285 - 345)": 6}
can_list = ["", "甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
mon_list = ["", "休门", "生门", "伤门", "杜门", "景门", "死门", "惊门", "开门"]
tinh_list = ["", "天蓬", "天芮", "天冲", "天辅", "天禽", "天心", "天柱", "天任", "天英"]
than_list = ["", "值符", "螣蛇", "太阴", "六合", "勾陈", "朱雀", "九地", "九天"]
cat_cach_list = format_ui_list(["青竜返首", "飛鳥跌穴", "玉女守門", "乙奇昇殿", "丙奇昇殿", "丁奇昇殿", "天遁", "地遁", "人遁", "神遁", "鬼遁", "竜遁", "虎遁", "風遁", "雲遁"])

TRAN_HUNG_DICT = {
    "大格": (["地遁"], ["乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"]),
    "小格": (["地遁"], ["乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"]),
    "刑格": (["地遁"], ["乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"]),
    "戦格": (["地遁"], ["乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"]),
    "伏宮格": (["地遁"], ["乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"]),
    "太白入熒": (["地遁"], ["乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"]),
    "飛宮格": (["人遁", "鬼遁"], ["玉女守門", "天盤丙", "乙奇得使", "丁奇得使"]),
    "青竜逃走": (["人遁", "鬼遁"], ["玉女守門", "天盤丙", "乙奇得使", "丁奇得使"]),
    "白虎猖狂": (["天遁", "神遁"], ["飛鳥跌穴", "丙奇得使"]),
    "螣蛇妖嬌": (["天遁", "地遁", "神遁"], ["飛鳥跌穴", "乙奇得使", "丙奇得使", "竜遁", "虎遁", "風遁", "雲遁"]),
    "乙奇入墓": (["人遁", "鬼遁", "玉女守門", "丁奇得使"], ["丁奇昇殿"]),
    "干伏吟": (["青竜返首"], []), "干反吟": (["青竜返首"], []),
    "熒惑入白": ([], []), "朱雀投江": ([], []), "丙奇入墓": ([], []), "丁奇入墓": ([], [])
}

THOI_CAT_DICT = {
    "青竜返首": (["青竜返首"], []), "乙奇得使": (["青竜返首"], []),
    "地遁": (["青竜返首"], []), "竜遁": (["青竜返首"], []), "虎遁": (["青竜返首"], []),
    "風遁": (["青竜返首"], []), "雲遁": (["青竜返首"], []),
    "飛鳥跌穴": (["地遁", "乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"], ["乙奇昇殿"]),
    "玉女守門": (["地遁", "青竜返首", "乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"], ["乙奇昇殿"]),
    "丙奇得使": (["地遁", "乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"], ["乙奇昇殿"]),
    "丁奇得使": (["地遁", "青竜返首", "乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"], ["乙奇昇殿"]),
    "天遁": (["地遁"], ["乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"]),
    "神遁": (["地遁"], ["乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"]),
    "人遁": (["地遁"], ["青竜返首", "乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"]),
    "鬼遁": (["地遁"], ["青竜返首", "乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"])
}

tran_hung_list = format_ui_list(list(TRAN_HUNG_DICT.keys()))
thoi_cat_list = format_ui_list(list(THOI_CAT_DICT.keys()))

with st.container():
    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    loc_huong = c1.selectbox("方向 (Hướng)", options=list(huong_list.keys()))
    loc_thien_can = c2.selectbox("天盤 (Thiên Bàn)", options=can_list)
    loc_dia_can = c3.selectbox("地盤 (Địa Bàn)", options=can_list)
    loc_mon = c4.selectbox("八门 (Bát Môn)", options=mon_list)
    loc_tinh = c5.selectbox("九星 (Cửu Tinh)", options=tinh_list)
    loc_than = c6.selectbox("八神 (Bát Thần)", options=than_list)
    loc_cat_cach = c7.selectbox("吉格 (Cát Cách)", options=cat_cach_list)
    
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    c9, c10, c11, c12 = st.columns(4)
    loc_tran_hung = c9.selectbox("鎮凶 (Trấn Hung)", options=tran_hung_list)
    loc_thoi_cat = c10.selectbox("催吉 (Thôi Cát)", options=thoi_cat_list)
    # 2 Mục lựa chọn mới
    loc_thien_thoi = c11.selectbox("天时 (Thiên Thời)", options=["", "Có"])
    loc_dia_loi = c12.selectbox("地利 (Địa Lợi)", options=["", "Có"])

def find_fulfilled_plan(plan_list, d_cung, status_cung, can_tuan_scan):
    for req in plan_list:
        if req == "天盤丙":
            t_chk = '甲' if d_cung['thien'] == can_tuan_scan else d_cung['thien']
            if t_chk == '丙': return "Thiên Bàn Bính"
        else:
            if any(req in item[0] for item in status_cung): return req
    return None

if st.button("TÌM KIẾM", use_container_width=True):
    val_tran_hung = extract_raw_name(loc_tran_hung)
    val_thoi_cat = extract_raw_name(loc_thoi_cat)
    
    if val_tran_hung and val_thoi_cat:
        st.error("Vui lòng không chọn cùng lúc Trấn Hung và Thôi Cát.")
    else:
        with st.spinner('Đang quét dữ liệu tương lai...'):
            mode = "NORMAL"
            if val_tran_hung: mode = "TRAN_HUNG"
            elif val_thoi_cat: mode = "THOI_CAT"
            
            results_normal, results_pa1, results_pa2 = [], [], []
            current_scan_dt = user_dt.replace(minute=0, second=0, microsecond=0)
            max_limit = 4320
            
            if mode == "TRAN_HUNG":
                pa1_reqs, pa2_reqs = TRAN_HUNG_DICT[val_tran_hung]
                if not pa1_reqs and not pa2_reqs: max_limit = 0
            elif mode == "THOI_CAT":
                pa1_reqs, pa2_reqs = THOI_CAT_DICT[val_thoi_cat]
                if not pa1_reqs and not pa2_reqs: max_limit = 0

            loops = 0
            while loops < max_limit: 
                if mode == "NORMAL" and len(results_normal) >= 10: break
                if mode in ["TRAN_HUNG", "THOI_CAT"]:
                    pa1_reqs, pa2_reqs = TRAN_HUNG_DICT[val_tran_hung] if mode == "TRAN_HUNG" else THOI_CAT_DICT[val_thoi_cat]
                    if (len(results_pa1) >= 5 or not pa1_reqs) and (len(results_pa2) >= 5 or not pa2_reqs): break

                loops += 1
                current_scan_dt += timedelta(hours=2) # Nhảy thời gian theo Giờ (2 tiếng)
                
                s_date = current_scan_dt.date() + timedelta(days=1) if current_scan_dt.hour >= 23 else current_scan_dt.date()
                c_gio_idx = 0 if current_scan_dt.hour >= 23 else (current_scan_dt.hour + 1) // 2 % 12
                c_gio_scan = dia_chi[c_gio_idx]
                
                s_obj = sxtwl.fromSolar(s_date.year, s_date.month, s_date.day)
                lm_scan = s_obj.getLunarMonth()
                ld_scan = s_obj.getLunarDay()
                
                wl_can_s, wl_chi_s, wl_jieqi_s, wl_yuan_s, wl_dun_s = get_wolong_calendar_data(lm_scan, ld_scan)
                can_gio_scan = get_wushu_dun(wl_can_s, c_gio_scan)
                wl_ju_s = calculate_correct_ju(wl_yuan_s, can_gio_scan, c_gio_scan, wl_jieqi_s)
                
                # CẬP NHẬT: Lấy biến cung_phi_tinh_scan từ hàm lap_que_wolong
                scan_data, p_circle_scan, cung_phi_tinh_scan, p_land_scan = lap_que_wolong(can_gio_scan, c_gio_scan, wl_dun_s, wl_ju_s, wl_chi_s)
                
                can_tuan_scan = get_xun_leader(can_gio_scan, c_gio_scan)
                
                # CẬP NHẬT: Lấy biến stem_colors_scan từ hàm qimen_analyzer_hojo
                cung_st_scan, stem_colors_scan = qimen_analyzer_hojo(scan_data, can_tuan_scan, p_land_scan)
                
                end_scan_dt = current_scan_dt + timedelta(hours=1, minutes=59)
                time_str = f"{current_scan_dt.strftime('%d/%m %H:%M')} - {end_scan_dt.strftime('%H:%M')}"
                c_str = f"{wl_dun_s} {wl_ju_s}局 | Giờ {can_gio_scan}{c_gio_scan}"
                
                target_palace = huong_list[loc_huong]

                if mode == "NORMAL":
                    is_match = False
                    val_cat_cach = extract_raw_name(loc_cat_cach)
                    def check_match(p):
                        d = scan_data[p]
                        t_chk = '甲' if d['thien'] == can_tuan_scan else d['thien']
                        d_chk = '甲' if d['dia'] == can_tuan_scan else d['dia']
                        if loc_thien_can and t_chk != loc_thien_can: return False
                        if loc_dia_can and d_chk != loc_dia_can: return False
                        if loc_mon and d['mon'] != loc_mon: return False
                        if loc_tinh and d['sao'] != loc_tinh: return False
                        if loc_than and d['than'] != loc_than: return False
                        if val_cat_cach:
                            if not any(val_cat_cach in item[0] for item in cung_st_scan[p]): return False
                            
                        # --- KIỂM TRA THIÊN THỜI ---
                        if loc_thien_thoi == "Có":
                            # "#000000" nghĩa là hung, "#CC0000" nghĩa là cát
                            if stem_colors_scan.get(p, "#000000") == "#000000":
                                return False
                                
                        # --- KIỂM TRA ĐỊA LỢI ---
                        if loc_dia_loi == "Có":
                            global_lower_gate = scan_data[cung_phi_tinh_scan]['mon']
                            global_lower_tri = GATE_TO_TRIGRAM.get(global_lower_gate, "天")
                            out_upper_tri = TIEN_THIEN_MAP.get(p, "天")
                            out_eval = EVAL_DICT.get(out_upper_tri, {}).get(global_lower_tri, "✕")
                            # Chỉ lấy Quẻ Cát (〇) hoặc Bình hòa (△)
                            if out_eval not in ["〇", "△"]:
                                return False
                                
                        return True

                    if target_palace:
                        if target_palace != 5: is_match = check_match(target_palace)
                    else:
                        for p in range(1, 10):
                            if p == 5: continue
                            if check_match(p):
                                is_match = True
                                target_palace = p
                                break
                                
                    if is_match:
                        ten_cung = [k for k, v in huong_list.items() if v == target_palace][0]
                        results_normal.append((time_str, c_str, ten_cung))

                else: 
                    palaces_to_scan = [target_palace] if target_palace else range(1, 10)
                    for p in palaces_to_scan:
                        if p == 5 or not p: continue
                        if len(results_pa1) < 5 and pa1_reqs:
                            found_pa1 = find_fulfilled_plan(pa1_reqs, scan_data[p], cung_st_scan[p], can_tuan_scan)
                            if found_pa1:
                                t_cung = [k for k, v in huong_list.items() if v == p][0]
                                results_pa1.append((time_str, c_str, t_cung, found_pa1))
                        
                        if len(results_pa2) < 5 and pa2_reqs:
                            found_pa2 = find_fulfilled_plan(pa2_reqs, scan_data[p], cung_st_scan[p], can_tuan_scan)
                            if found_pa2:
                                t_cung = [k for k, v in huong_list.items() if v == p][0]
                                results_pa2.append((time_str, c_str, t_cung, found_pa2))

            if mode == "NORMAL":
                if results_normal:
                    st.success(f"**TÌM THẤY {len(results_normal)} KẾT QUẢ:**")
                    for idx, (t_str, canchi_str, cung_str) in enumerate(results_normal):
                        h_text = f" | Hướng: {cung_str}" if cung_str else ""
                        st.write(f"{idx+1}. {t_str} | {canchi_str}{h_text}")
                else:
                    st.warning("Không tìm thấy thời điểm nào thỏa mãn điều kiện.")
            else:
                if not results_pa1 and not results_pa2 and max_limit > 0:
                    st.warning(f"Đã quét nhưng không tìm thấy thời điểm nào có thể xử lý.")
                if results_pa1:
                    st.success(f"**Phương án 1 (Tìm thấy {len(results_pa1)}):**")
                    for idx, (t_str, canchi_str, cung_str, dung_cach) in enumerate(results_pa1):
                        st.write(f"{idx+1}. Dùng **{dung_cach}** | {t_str} | {canchi_str} | Tại: {cung_str}")
                if results_pa2:
                    st.success(f"**Phương án 2 (Tìm thấy {len(results_pa2)}):**")
                    for idx, (t_str, canchi_str, cung_str, dung_cach) in enumerate(results_pa2):
                        st.write(f"{idx+1}. Dùng **{dung_cach}** | {t_str} | {canchi_str} | Tại: {cung_str}")
