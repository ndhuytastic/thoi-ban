import streamlit as st
import sxtwl
from datetime import datetime, timedelta, timezone
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Kỳ Môn Phi Bàn", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 1. HỆ THỐNG DỮ LIỆU CƠ BẢN (PHI BÀN)
# ==========================================
thien_can = "甲乙丙丁戊己庚辛壬癸"
dia_chi = "子丑寅卯辰巳午未申酉戌亥"
luc_nghi = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]

luoshu_9 = [1, 2, 3, 4, 5, 6, 7, 8, 9]

star_native = ["天蓬", "天芮", "天冲", "天辅", "天禽", "天心", "天柱", "天任", "天英"]
deity_9 = ["值符", "螣蛇", "太阴", "六合", "勾陈", "太常", "朱雀", "九地", "九天"]

jq_names = ["冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种", 
            "夏至", "小暑", "大暑", "立秋", "处暑", "白露", "秋分", "寒露", "霜降", "立冬", "小雪", "大雪"]
yang_terms = ["冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种"]

solar_term_ju = {
    "冬至":[1,7,4], "小寒":[2,8,5], "大寒":[3,9,6], "立春":[8,5,2], "雨水":[9,6,3], "惊蛰":[1,7,4],
    "春分":[3,9,6], "清明":[4,1,7], "谷雨":[5,2,8], "立夏":[4,1,7], "小满":[5,2,8], "芒种":[6,3,9],
    "夏至":[9,3,6], "小暑":[8,2,5], "大暑":[7,1,4], "立秋":[2,5,8], "处暑":[1,4,7], "白露":[9,3,6],
    "秋分":[7,1,4], "寒露":[6,9,3], "霜降":[5,8,2], "立冬":[6,9,3], "小雪":[5,8,2], "大雪":[4,7,1]
}

JIEQI_PALACE_MAP = {
    "冬至": 1, "小寒": 1, "大寒": 1,
    "立春": 8, "雨水": 8, "惊蛰": 8,
    "春分": 3, "清明": 3, "谷雨": 3,
    "立夏": 4, "小满": 4, "芒种": 4,
    "夏至": 9, "小暑": 9, "大暑": 9,
    "立秋": 2, "处暑": 2, "白露": 2,
    "秋分": 7, "寒露": 7, "霜降": 7,
    "立冬": 6, "小雪": 6, "大雪": 6
}

# ==========================================
# 2. THUẬT TOÁN ĐỊNH CỤC TRÍ NHUẬN KHÁM TRẠM
# ==========================================
def get_phu_dau(d_date):
    for i in range(20):
        check_date = d_date - timedelta(days=i)
        day_obj = sxtwl.fromSolar(check_date.year, check_date.month, check_date.day)
        tg = day_obj.getDayGZ().tg  
        dz = day_obj.getDayGZ().dz  
        if (tg == 0 or tg == 5) and (dz in [0, 3, 6, 9]):
            return check_date
    return d_date

def get_station(start_date, include_start=False):
    start_offset = 0 if include_start else 1
    for i in range(start_offset, 250): 
        check_date = start_date - timedelta(days=i)
        day_obj = sxtwl.fromSolar(check_date.year, check_date.month, check_date.day)
        if day_obj.hasJieQi():
            jq_idx = day_obj.getJieQi()
            if jq_names[jq_idx] in ["芒种", "大雪"]:
                return check_date, jq_names[jq_idx]
    return None, None

def run_trinhuan_algorithm(D, T_tram_date, T_tram_name, T_prev_tram_date):
    F_past = get_phu_dau(T_tram_date)
    chao_shen = (T_tram_date - F_past).days
    is_leap = False
    is_fake_tie_qi = False

    if chao_shen >= 9:
        F_prev_past = get_phu_dau(T_prev_tram_date)
        chao_shen_prev = (T_prev_tram_date - F_prev_past).days
        if chao_shen_prev >= 9: is_fake_tie_qi = True
        else: is_leap = True 

    Start_Line = F_past + timedelta(days=15) if is_fake_tie_qi else F_past

    if D < Start_Line:
        T_prev2_tram_date, _ = get_station(T_prev_tram_date, include_start=False)
        day_prev_obj = sxtwl.fromSolar(T_prev_tram_date.year, T_prev_tram_date.month, T_prev_tram_date.day)
        T_prev_tram_name = jq_names[day_prev_obj.getJieQi()]
        return run_trinhuan_algorithm(D, T_prev_tram_date, T_prev_tram_name, T_prev2_tram_date)

    delta_days = (D - Start_Line).days
    block_index = delta_days // 15
    nguyen_index = (delta_days % 15) // 5 
    station_idx = jq_names.index(T_tram_name)
    
    if is_leap:
        if block_index == 0 or block_index == 1: final_idx = station_idx
        else: final_idx = (station_idx + block_index - 1) % 24 
    else:
        final_idx = (station_idx + block_index) % 24

    final_term = jq_names[final_idx]
    is_nhuan_hien_tai = (is_leap and block_index == 1)
    return final_term, nguyen_index, is_nhuan_hien_tai

def get_zhirun_ju(actual_date):
    D = actual_date
    T_tram_date, T_tram_name = get_station(D, include_start=True)
    T_prev_tram_date, _ = get_station(T_tram_date, include_start=False)
    final_term, nguyen_index, is_nhuan = run_trinhuan_algorithm(D, T_tram_date, T_tram_name, T_prev_tram_date)
    loai_don = "阳遁" if final_term in yang_terms else "阴遁"
    so_cuc = solar_term_ju[final_term][nguyen_index]
    ji_palace = JIEQI_PALACE_MAP[final_term]
    return loai_don, so_cuc, final_term, ji_palace, is_nhuan

# ==========================================
# 2B. CÁC HÀM TÍNH TOÁN BỔ SUNG ĐỘC LẬP 
# ==========================================
def get_cung_phi_tinh(nhat_chi, thoi_chi, loai_don):
    col_map = {"子":0, "午":0, "卯":0, "酉":0, "丑":1, "未":1, "辰":1, "戌":1, "寅":2, "申":2, "巳":2, "亥":2}
    matrix = [
        [[1, 9], [4, 6], [7, 3]], [[2, 8], [5, 5], [8, 2]], [[3, 7], [6, 4], [9, 1]], 
        [[4, 6], [7, 3], [1, 9]], [[5, 5], [8, 2], [2, 8]], [[6, 4], [9, 1], [3, 7]], 
        [[7, 3], [1, 9], [4, 6]], [[8, 2], [2, 8], [5, 5]], [[9, 1], [3, 7], [6, 4]], 
        [[1, 9], [4, 6], [7, 3]], [[2, 8], [5, 5], [8, 2]], [[3, 7], [6, 4], [9, 1]]  
    ]
    c_idx = col_map[nhat_chi]
    r_idx = dia_chi.index(thoi_chi)
    vals = matrix[r_idx][c_idx]
    return vals[0] if loai_don == "阳遁" else vals[1]

def get_luc_than(can_gio, can_cung):
    if not can_cung: return ""
    element_map = {"甲":0, "乙":0, "丙":1, "丁":1, "戊":2, "己":2, "庚":3, "辛":3, "壬":4, "癸":4}
    b_e = element_map[can_gio]
    t_e = element_map[can_cung]
    diff_e = (t_e - b_e) % 5 
    if diff_e == 0: return "兄"    
    elif diff_e == 1: return "孙"   
    elif diff_e == 2: return "财"   
    elif diff_e == 3: return "官"   
    elif diff_e == 4: return "父"   
    return ""

def tinh_tuan_khong_gio(hoa_giap):
    idx_can, idx_chi = thien_can.index(hoa_giap[0]), dia_chi.index(hoa_giap[1])
    idx_tuan_dau = (idx_chi - idx_can) % 12
    chi_to_cung = {"子":1, "丑":8, "寅":8, "卯":3, "辰":4, "巳":4, "午":9, "未":2, "申":2, "酉":7, "戌":6, "亥":6}
    return [chi_to_cung[dia_chi[(idx_tuan_dau - 2) % 12]], chi_to_cung[dia_chi[(idx_tuan_dau - 1) % 12]]]

# ==========================================
# 3. THUẬT TOÁN PHI BÀN (TINH - MÔN - THẦN)
# ==========================================
def lap_que(hoa_giap_gio, nhat_chi, loai_don, so_cuc, ji_palace, can_thang, can_ngay, chi_thang):
    can_gio, chi_gio = hoa_giap_gio[0], hoa_giap_gio[1]
    loai = "阳" if loai_don == "阳遁" else "阴"
    
    idx_can, idx_chi = thien_can.index(can_gio), dia_chi.index(chi_gio)
    chi_tuan = dia_chi[(idx_chi - idx_can) % 12]
    can_tuan = {"子":"戊", "戌":"己", "申":"庚", "午":"辛", "辰":"壬", "寅":"癸"}[chi_tuan]

    cung_data = {i: {'dia': '', 'sao': '', 'mon': '', 'than': '', 'thien': '', 'ngua': '', 
                     'phi_tinh': 0, 'lt_thien': '', 'lt_dia': '',
                     'lt_thien_color': '#555', 'lt_thien_kichhinh': False, 'lt_thien_nhapkho': False} for i in range(1, 10)}

    # PHI TINH TRUNG CUNG - LUÔN PHI THUẬN
    center_num = get_cung_phi_tinh(nhat_chi, chi_gio, loai_don)
    quydo_luoshu = [5, 6, 7, 8, 9, 1, 2, 3, 4]
    curr_num = center_num
    for p in quydo_luoshu:
        cung_data[p]['phi_tinh'] = curr_num
        curr_num = (curr_num % 9) + 1

    # --- 1. ĐỊA BÀN ---
    dia_ban = {}
    for i, can in enumerate(luc_nghi):
        p = (so_cuc + i - 1) % 9 + 1 if loai == "阳" else (so_cuc - i - 1) % 9 + 1
        dia_ban[p] = can
    for i in range(1, 10): 
        cung_data[i]['dia'] = dia_ban[i]
        cung_data[i]['lt_dia'] = get_luc_than(can_gio, dia_ban[i]) 

    # --- TÌM MÃ ---
    map_ngua = {"子":"寅", "丑":"亥", "寅":"申", "卯":"巳", "辰":"寅", "巳":"亥", "午":"申", "未":"巳", "申":"寅", "酉":"亥", "戌":"申", "亥":"巳"}
    cung_data[{"寅":8, "巳":4, "申":2, "亥":6}[map_ngua[chi_gio]]]['ngua'] = "马"

    # --- 2. THIÊN BÀN TINH & CAN ---
    base_star_p = [k for k, v in dia_ban.items() if v == can_tuan][0]
    target_star_p = [k for k, v in dia_ban.items() if v == (can_tuan if can_gio == "甲" else can_gio)][0]
    
    star_path_forward = luoshu_9  
    idx_base_star_fwd = star_path_forward.index(base_star_p)
    idx_target_star_fwd = star_path_forward.index(target_star_p)
    shift_for_star = (idx_target_star_fwd - idx_base_star_fwd) % 9
    
    for i in range(9):
        p_star = star_path_forward[i]
        orig_idx_star = (i - shift_for_star) % 9
        orig_p_star = star_path_forward[orig_idx_star]
        cung_data[p_star]['sao'] = star_native[orig_p_star - 1]

    path_9 = luoshu_9 if loai == "阳" else list(reversed(luoshu_9))
    idx_base = path_9.index(base_star_p)
    idx_target = path_9.index(target_star_p)
    star_shift = (idx_target - idx_base) % 9
    
    for i in range(9):
        p = path_9[i]
        orig_idx = (i - star_shift) % 9
        orig_p = path_9[orig_idx]
        
        can_thien_bay_toi = dia_ban[orig_p]
        cung_data[p]['thien'] = can_thien_bay_toi
        cung_data[p]['lt_thien'] = get_luc_than(can_gio, can_thien_bay_toi) 

        combine_map = {'甲':('己','#8B4513'), '己':('甲','#8B4513'), '乙':('庚','#808080'), '庚':('乙','#808080'), '丙':('辛','#1E90FF'), '辛':('丙','#1E90FF'), '丁':('壬','#008000'), '壬':('丁','#008000'), '戊':('癸','#FF0000'), '癸':('戊','#FF0000')}
        target_can, hex_color = combine_map.get(can_thien_bay_toi, (None, '#555'))
        if target_can in [dia_ban[p], can_thang, can_ngay, can_gio]: cung_data[p]['lt_thien_color'] = hex_color

        # Tính Kích Hình
        kich_hinh_map = {'戊': 3, '己': 2, '庚': 8, '辛': 9, '壬': 4, '癸': 4}
        if kich_hinh_map.get(can_thien_bay_toi) == p: cung_data[p]['lt_thien_kichhinh'] = True
            
        # KHÔI PHỤC: Tính Nhập Mộ
        ruku_map = {'丙':('戌', 6), '丁':('戌', 6), '戊':('戌', 6), '己':('戌', 6), '庚':('丑', 8), '辛':('丑', 8), '壬':('辰', 4), '癸':('辰', 4), '甲':('未', 2), '乙':('未', 2)}
        if can_thien_bay_toi in ruku_map:
            kho_chi, kho_cung = ruku_map[can_thien_bay_toi]
            if p == kho_cung or chi_thang == kho_chi: cung_data[p]['lt_thien_nhapkho'] = True

    # --- 3. BÁT MÔN PHI BÀN ---
    door_native_dict = {1: "休门", 2: "死门", 3: "伤门", 4: "杜门", 6: "开门", 7: "惊门", 8: "生门", 9: "景门"}
    doors_cycle = ["休门", "死门", "伤门", "杜门", "开门", "惊门", "生门", "景门"]
    luoshu_8 = [1, 2, 3, 4, 6, 7, 8, 9]

    truc_su_door = door_native_dict[ji_palace] if base_star_p == 5 else door_native_dict[base_star_p]
    steps = (dia_chi.index(chi_gio) - dia_chi.index(chi_tuan)) % 12
    target_door_p = (so_cuc + steps - 1) % 9 + 1 if loai == "阳" else (so_cuc - steps - 1) % 9 + 1
    if target_door_p == 5: target_door_p = ji_palace
        
    idx_target_in_path8 = luoshu_8.index(target_door_p)
    shifted_palaces = luoshu_8[idx_target_in_path8:] + luoshu_8[:idx_target_in_path8]
    idx_truc_su = doors_cycle.index(truc_su_door)
    shifted_doors = doors_cycle[idx_truc_su:] + doors_cycle[:idx_truc_su]
    
    for p, door in zip(shifted_palaces, shifted_doors): cung_data[p]['mon'] = door

    # --- 4. CỬU THẦN ---
    for i in range(9):
        p = path_9[i]
        deity_idx = (i - idx_target) % 9
        cung_data[p]['than'] = deity_9[deity_idx]

    return cung_data

# ==========================================
# 4. MODULE ĐỘC LẬP: PHÂN TÍCH CÁCH CỤC
# ==========================================
def qimen_analyzer(cung_data, can_ngay, can_gio, can_tuan, truc_su_door=None):
    FORMATION_RANKS = {
        # Hạng 1 (Dưới cùng)
        "天遁": "1", "地遁": "1", "人遁": "1", "神遁": "1", "鬼遁": "1",
        "大格": "1", "小格": "1", "刑格": "1", "戦格": "1", "飛宮格": "1", 
        "伏宮格": "1", "青竜逃走": "1", "白虎猖狂": "1", "熒惑入白": "1", 
        "太白入熒": "1", "朱雀投江": "1", "螣蛇妖嬌": "1",
        
        # Hạng 2 (Nằm trên Hạng 1)
        "青竜返首": "2", "飛鳥跌穴": "2", "玉女守門": "2", "乙奇得使": "2", 
        "丙奇得使": "2", "丁奇得使": "2", "竜遁": "2", "虎遁": "2", 
        "風遁": "2", "雲遁": "2", 
        
        # Các cách cục đã được gọi tên chi tiết (Rank 2)
        "乙奇入墓": "2", "丙奇入墓": "2", "丁奇入墓": "2",
        "甲儀伏吟": "2", "乙奇伏吟": "2", "丙奇伏吟": "2", "丁奇伏吟": "2", "戊儀伏吟": "2", "己儀伏吟": "2", "庚儀伏吟": "2", "辛儀伏吟": "2", "壬儀伏吟": "2", "癸儀伏吟": "2",
        "戊儀反吟": "2", "己儀反吟": "2", "庚儀反吟": "2", "辛儀反吟": "2", "壬儀反吟": "2", "癸儀反吟": "2",
        
        # Hạng 3 (Nằm trên Hạng 2)
        "乙奇昇殿": "3", "丙奇昇殿": "3", "丁奇昇殿": "3",
        "九星伏吟": "3", "八门伏吟": "3", "九星反吟": "3", "八门反吟": "3"
    }

    toan_ban_status = []
    cung_status = {i: [] for i in range(1, 10)}
    cung_3_elements = {i: [] for i in range(1, 10)} 

    than_cung_data = {'值符':{1:'吉',2:'吉',3:'吉',4:'吉',5:'凶',6:'吉',7:'吉',8:'吉',9:'吉'}, '螣蛇':{1:'凶',2:'凶',3:'凶',4:'凶',5:'凶',6:'凶',7:'凶',8:'凶',9:'凶'}, '太阴':{1:'吉',2:'吉',3:'吉',4:'吉',5:'凶',6:'吉',7:'吉',8:'吉',9:'吉'}, '六合':{1:'吉',2:'吉',3:'吉',4:'吉',5:'凶',6:'吉',7:'吉',8:'吉',9:'吉'}, '勾陈':{1:'凶',2:'凶',3:'凶',4:'凶',5:'凶',6:'凶',7:'凶',8:'凶',9:'凶'}, '朱雀':{1:'凶',2:'凶',3:'凶',4:'凶',5:'凶',6:'凶',7:'凶',8:'凶',9:'凶'}, '九地':{1:'吉',2:'吉',3:'吉',4:'吉',5:'凶',6:'吉',7:'吉',8:'吉',9:'吉'}, '九天':{1:'吉',2:'吉',3:'吉',4:'吉',5:'凶',6:'吉',7:'吉',8:'吉',9:'吉'}, '太常':{1:'吉',2:'凶',3:'凶',4:'吉',5:'凶',6:'凶',7:'凶',8:'吉',9:'吉'}}
    mon_sao_data = {'休门':{'天蓬':'凶','天芮':'吉','天冲':'吉','天辅':'吉','天禽':'凶','天心':'吉','天柱':'吉','天任':'吉','天英':'凶'}, '生门':{'天蓬':'吉','天芮':'凶','天冲':'吉','天辅':'吉','天禽':'凶','天心':'吉','天柱':'吉','天任':'凶','天英':'吉'}, '伤门':{'天蓬':'凶','天芮':'凶','天冲':'凶','天辅':'凶','天禽':'凶','天心':'凶','天柱':'凶','天任':'凶','天英':'凶'}, '杜门':{'天蓬':'凶','天芮':'凶','天冲':'凶','天辅':'凶','天禽':'凶','天心':'凶','天柱':'凶','天任':'凶','天英':'凶'}, '景门':{'天蓬':'凶','天芮':'吉','天冲':'吉','天辅':'吉','天禽':'凶','天心':'吉','天柱':'吉','天任':'吉','天英':'凶'}, '死门':{'天蓬':'凶','天芮':'凶','天冲':'凶','天辅':'凶','天禽':'凶','天心':'凶','天柱':'凶','天任':'凶','天英':'凶'}, '惊门':{'天蓬':'凶','天芮':'凶','天冲':'凶','天辅':'凶','天禽':'凶','天心':'凶','天柱':'凶','天任':'凶','天英':'凶'}, '开门':{'天蓬':'吉','天芮':'吉','天冲':'吉','天辅':'凶','天禽':'凶','天心':'凶','天柱':'吉','天任':'吉','天英':'吉'}}
    can_can_data = {'甲':{'甲':'吉','乙':'吉','丙':'吉','丁':'吉','戊':'凶','己':'吉','庚':'大凶','辛':'凶','壬':'凶','癸':'吉'}, '乙':{'甲':'吉','乙':'凶','丙':'吉','丁':'吉','戊':'吉','己':'吉','庚':'凶','辛':'大凶','壬':'吉','癸':'凶'}, '丙':{'甲':'吉','乙':'吉','丙':'凶','丁':'吉','戊':'吉','己':'吉','庚':'大凶','辛':'吉','壬':'吉','癸':'凶'}, '丁':{'甲':'吉','乙':'吉','丙':'吉','丁':'吉','戊':'吉','己':'凶','庚':'吉','辛':'凶','壬':'吉','癸':'大凶'}, '戊':{'甲':'凶','乙':'吉','丙':'吉','丁':'吉','戊':'凶','己':'凶','庚':'凶','辛':'凶','壬':'吉','癸':'凶'}, '己':{'甲':'凶','乙':'吉','丙':'凶','丁':'凶','戊':'吉','己':'凶','庚':'凶','辛':'凶','壬':'凶','癸':'凶'}, '庚':{'甲':'大凶','乙':'凶','丙':'大凶','丁':'吉','戊':'凶','己':'大凶','庚':'大凶','辛':'凶','壬':'大凶','癸':'大凶'}, '辛':{'甲':'凶','乙':'大凶','丙':'凶','丁':'吉','戊':'凶','己':'凶','庚':'凶','辛':'凶','壬':'凶','癸':'凶'}, '壬':{'甲':'凶','乙':'凶','丙':'凶','丁':'吉','戊':'吉','己':'凶','庚':'凶','辛':'吉','壬':'凶','癸':'凶'}, '癸':{'甲':'吉','乙':'凶','丙':'吉','丁':'大凶','戊':'吉','己':'凶','庚':'大凶','辛':'凶','壬':'凶','癸':'凶'}}

    ngu_bat_ngo = {'甲':'庚', '乙':'辛', '丙':'壬', '丁':'癸', '戊':'甲', '己':'乙', '庚':'丙', '辛':'丁', '壬':'戊', '癸':'己'}
    if ngu_bat_ngo.get(can_ngay) == can_gio: toan_ban_status.append("五不遇时")

    sao_goc = {1:"天蓬", 2:"天芮", 3:"天冲", 4:"天辅", 5:"天禽", 6:"天心", 7:"天柱", 8:"天任", 9:"天英"}
    mon_goc = {1:"休门", 2:"死门", 3:"伤门", 4:"杜门", 6:"开门", 7:"惊门", 8:"生门", 9:"景门"}
    doi_xung = {1:9, 2:8, 3:7, 4:6, 6:4, 7:3, 8:2, 9:1}
    
    sao_phuc = sao_phan = mon_phuc = mon_phan = True
    for p in [1, 2, 3, 4, 6, 7, 8, 9]:
        d = cung_data[p]
        if d['sao'] != sao_goc[p]: sao_phuc = False
        if d['mon'] != mon_goc[p]: mon_phuc = False
        if d['sao'] != sao_goc[doi_xung[p]]: sao_phan = False
        if d['mon'] != mon_goc[doi_xung[p]]: mon_phan = False
    if sao_phuc: toan_ban_status.append("九星伏吟")
    if mon_phuc: toan_ban_status.append("八门伏吟")
    if sao_phan: toan_ban_status.append("九星反吟")
    if mon_phan: toan_ban_status.append("八门反吟")

    for p, d in cung_data.items():
        if p == 5: continue 
        
        # Lấy trực tiếp Thiên/Địa bàn thực tế (không quy đổi Giáp ẩn)
        t_can = d['thien']
        d_can = d['dia']
        mon, sao, than, phi_tinh = d['mon'], d['sao'], d['than'], d['phi_tinh']

        # XÉT CÁC CÁCH CỤC CÁT 
        if t_can == '戊' and d_can == '丙': cung_status[p].append(("青竜返首", "#CC0000"))
        if t_can == '丙' and d_can == '戊': cung_status[p].append(("飛鳥跌穴", "#CC0000"))
        
        if truc_su_door and t_can == '丁' and mon == truc_su_door: cung_status[p].append(("玉女守門", "#CC0000"))
        if t_can == '乙' and p == 3: cung_status[p].append(("乙奇昇殿", "#CC0000"))
        if t_can == '丙' and p == 9: cung_status[p].append(("丙奇昇殿", "#CC0000"))
        if t_can == '丁' and p == 9: cung_status[p].append(("丁奇昇殿", "#CC0000"))
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

        # XÉT CÁC CÁCH CỤC HUNG
        if (t_can == '戊' and p == 3) or (t_can == '己' and p == 2) or (t_can == '庚' and p == 8) or (t_can == '辛' and p == 9) or (t_can == '壬' and p == 4) or (t_can == '癸' and p == 4): cung_status[p].append(("六儀擊刑", "#000000"))
        
        # Tam Kỳ Nhập Mộ
        if t_can == '乙' and p == 2: cung_status[p].append(("乙奇入墓", "#000000"))
        if t_can == '丙' and p == 6: cung_status[p].append(("丙奇入墓", "#000000"))
        if t_can == '丁' and p == 6: cung_status[p].append(("丁奇入墓", "#000000"))
        
        if t_can == '庚' and d_can == '癸': cung_status[p].append(("大格", "#000000"))
        if t_can == '庚' and d_can == '壬': cung_status[p].append(("小格", "#000000"))
        if t_can == '庚' and d_can == '己': cung_status[p].append(("刑格", "#000000"))
        if t_can == '庚' and d_can == '庚': cung_status[p].append(("戦格", "#000000"))
        
        # Phục Cung và Phi Cung mới
        if t_can == '庚' and d_can == can_tuan: cung_status[p].append(("伏宮格", "#000000"))
        if t_can == can_tuan and d_can == '庚': cung_status[p].append(("飛宮格", "#000000"))
        
        if t_can == '乙' and d_can == '辛': cung_status[p].append(("青竜逃走", "#000000"))
        if t_can == '辛' and d_can == '乙': cung_status[p].append(("白虎猖狂", "#000000"))
        if t_can == '丙' and d_can == '庚': cung_status[p].append(("熒惑入白", "#000000"))
        if t_can == '庚' and d_can == '丙': cung_status[p].append(("太白入熒", "#000000"))
        if t_can == '丁' and d_can == '癸': cung_status[p].append(("朱雀投江", "#000000"))
        if t_can == '癸' and d_can == '丁': cung_status[p].append(("螣蛇妖嬌", "#000000"))

        # Chi tiết Can Phục Ngâm
        if t_can == d_can and t_can not in ['丁', '庚']:
            ten_ki_nghi = {'乙':'乙奇', '丙':'丙奇', '戊':'戊儀', '己':'己儀', '辛':'辛儀', '壬':'壬儀', '癸':'癸儀'}
            if t_can in ten_ki_nghi:
                cung_status[p].append((f"{ten_ki_nghi[t_can]}伏吟", "#000000"))

        # Chi tiết Can Phản Ngâm
        fan_yin_map = {('戊','辛'): '戊儀', ('辛','戊'): '辛儀', ('己','壬'): '己儀', ('壬','己'): '壬儀', ('庚','癸'): '庚儀', ('癸','庚'): '癸儀'}
        if (t_can, d_can) in fan_yin_map:
            prefix = fan_yin_map[(t_can, d_can)]
            cung_status[p].append((f"{prefix}反吟", "#000000"))
        
        mon_bach_rules = {"休门":[9], "景门":[6, 7], "生门":[1], "开门":[3, 4]}
        if p in mon_bach_rules.get(mon, []): cung_status[p].append(("门迫", "#000000"))

        # Bảng Cát Hung 10x10 sử dụng Can Thực (Bỏ qua Giáp ẩn)
        if t_can in can_can_data and d_can in can_can_data[t_can]: cung_3_elements[p].append(can_can_data[t_can][d_can])
        if mon in mon_sao_data and sao in mon_sao_data[mon]: cung_3_elements[p].append(mon_sao_data[mon][sao])
        if than in than_cung_data and phi_tinh in than_cung_data[than]: cung_3_elements[p].append(than_cung_data[than][phi_tinh])

    # --- THUẬT TOÁN TRỌNG SỐ ĐỂ SẮP XẾP ---
    def get_rank_weight(name):
        rank = FORMATION_RANKS.get(name)
        if rank == "1": return 4
        if rank == "2": return 3
        if rank == "3": return 2
        return 1

    toan_ban_status.sort(key=get_rank_weight)
    for i in range(len(toan_ban_status)):
        raw_name = toan_ban_status[i]
        if raw_name in FORMATION_RANKS:
            toan_ban_status[i] = f"<span style='font-size: 0.8em; font-weight: normal; color: #666;'>({FORMATION_RANKS[raw_name]})</span> {raw_name}"

    for p in cung_status:
        cung_status[p].sort(key=lambda x: get_rank_weight(x[0]))
        formatted_list = []
        for raw_name, color in cung_status[p]:
            if raw_name in FORMATION_RANKS:
                display_name = f"<span style='font-size: 0.8em; font-weight: normal; color: #666;'>({FORMATION_RANKS[raw_name]})</span> {raw_name}"
            else:
                display_name = raw_name
            formatted_list.append((display_name, color))
        cung_status[p] = formatted_list

    return toan_ban_status, cung_status, cung_3_elements

# ==========================================
# 5. GIAO DIỆN HTML RENDER
# ==========================================
def format_stem(stem_str): return stem_str if stem_str else ""
def format_sao(sao_str): return sao_str if sao_str else ""

def render_html_table(cung_data, tk_gio, toan_ban_status, cung_status, cung_3_elements):
    luoi_lac_thu = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]

    html = """
    <style>
        .qmdj-table { border-collapse: collapse; width: 100%; max-width: 510px; min-width: 400px; height: 430px; table-layout: fixed; font-family: sans-serif; margin: 0 auto; background: #fff;}
        .qmdj-td { border: 1px solid #aaa; width: 33.33%; position: relative; vertical-align: top; padding: 10px; }
        
        .cell-main {
            display: grid; grid-template-columns: auto auto 1fr; grid-template-rows: 22px 22px 22px;   
            column-gap: 15px; row-gap: 6px; height: 100%; min-height: 85px; align-content: start;
            margin-top: 5px; margin-left: 5px; 
        }

        .cell-center-left { display: flex; flex-direction: column; justify-content: flex-start; align-items: flex-start; margin-top: 33px; margin-left: 5px; gap: 6px; }
        
        .item-than  { grid-column: 1 / span 2; grid-row: 1; font-size: 15px; color: #222; text-align: left; }
        .item-tinh  { grid-column: 1; grid-row: 2; font-size: 15px; color: #222; text-align: left; }
        .item-mon   { grid-column: 1; grid-row: 3; font-size: 15px; color: #222; text-align: left; }
        .item-thien { grid-column: 2; grid-row: 2; font-size: 15px; color: #222; text-align: left; display: flex; align-items: center;}
        .item-dia   { grid-column: 2; grid-row: 3; font-size: 15px; color: #222; text-align: left; display: flex; align-items: center;}

        .luc-than-dia { font-size: 11px; color: #555; margin-left: 6px; font-weight: normal; }
        .luc-than-thien { font-size: 11px; margin-left: 6px; font-weight: normal; }
        
        .top-right-indicators { position: absolute; top: 3px; right: 4px; display: flex; flex-direction: row; align-items: center; justify-content: flex-end; gap: 4px; color: #444; }
        .horse-icon { font-size: 14px; font-weight: bold; }
        .void-icon { font-size: 20px; font-weight: normal; line-height: 0.8; margin-top: -2px; }
        .bottom-left-phitinh { position: absolute; bottom: 3px; left: 5px; font-size: 15px; color: #555; font-weight: bold; }

        .right-panel { position: absolute; right: 5px; top: 22px; display: flex; flex-direction: column; align-items: flex-end; text-align: right; font-size: 11px; font-family: sans-serif; }
        .bottom-right-panel { position: absolute; right: 5px; bottom: 3px; display: flex; flex-direction: column; align-items: flex-end; text-align: right; font-size: 11px; font-family: sans-serif; }
        
        .combo-item { color: #555; font-weight: 500; margin-bottom: 2px; }
        .formation-item { margin-top: 1px; font-weight: bold; letter-spacing: 1px; color: #000; }
    </style>
    <table class="qmdj-table">
    """

    for row in luoi_lac_thu:
        html += "<tr>"
        for p in row:
            d = cung_data[p]
            phi_tinh_html = f"<div class='bottom-left-phitinh'>{d['phi_tinh']}</div>"
            
            thien_css_styles = f"color: {d['lt_thien_color']};"
            if d['lt_thien_color'] != '#555':
                thien_css_styles += " font-weight: bold;"
                # ĐÃ SỬA: Nhận diện màu Xám #808080 (của hợp Kim) thay vì Đen #000000 để làm nét chữ đậm hơn
                if d['lt_thien_color'] == '#808080': thien_css_styles += " font-weight: 900;" 
            
            is_kh = d.get('lt_thien_kichhinh', False)
            is_nk = d.get('lt_thien_nhapkho', False) 
            
            if is_kh and is_nk: thien_css_styles += " text-decoration: underline double; text-underline-offset: 3px;"
            elif is_kh or is_nk: thien_css_styles += " text-decoration: underline; text-underline-offset: 3px;"
            
            lt_thien_html = f"<span class='luc-than-thien' style='{thien_css_styles}'>{d['lt_thien']}</span>" if d['lt_thien'] else ""
            lt_dia_html = f"<span class='luc-than-dia'>{d['lt_dia']}</span>" if d['lt_dia'] else ""
            thien_full = f"<span>{format_stem(d['thien'])}</span>{lt_thien_html}"
            dia_full = f"<span>{format_stem(d['dia'])}</span>{lt_dia_html}"
            
            if p == 5:
                toan_ban_html = "".join([f"<div class='formation-item'>{c}</div>" for c in toan_ban_status])
                # Cách cục ở trung cung dính góc dưới phải
                bottom_right_html = f"<div class='bottom-right-panel'>{toan_ban_html}</div>"
                html += f"""
                <td class="qmdj-td">
                    {phi_tinh_html}
                    {bottom_right_html}
                    <div class="cell-center-left">
                        <div class="item-thien">{thien_full}</div>
                        <div class="item-dia">{dia_full}</div>
                    </div>
                </td>"""
                continue
                
            indicators = []
            if d.get('ngua'): indicators.append("<span class='horse-icon'>马</span>")
            if p in tk_gio: indicators.append("<span class='void-icon'>○</span>")
            indicator_html = f"<div class='top-right-indicators'>{''.join(indicators)}</div>" if indicators else ""
            
            combos_html = "".join([f"<div class='combo-item'>{c}</div>" for c in cung_3_elements[p]])
            form_html = "".join([f"<div class='formation-item' style='color:{f_color};'>{f_name}</div>" for f_name, f_color in cung_status[p]])
            
            # 3 tổ hợp cát hung ở trên, cách cục ở dưới góc phải
            right_panel_html = f"<div class='right-panel'>{combos_html}</div>"
            bottom_right_html = f"<div class='bottom-right-panel'>{form_html}</div>"
            
            html += f"""
            <td class="qmdj-td">
                {indicator_html}
                {phi_tinh_html}
                {right_panel_html}
                {bottom_right_html}
                <div class="cell-main">
                    <div class="item-than">{d['than']}</div>
                    <div class="item-tinh">{format_sao(d['sao'])}</div>
                    <div class="item-mon"><span>{d['mon']}</span></div>
                    <div class="item-thien">{thien_full}</div>
                    <div class="item-dia">{dia_full}</div>
                </div>
            </td>"""
        html += "</tr>"
        
    html += "</table>"
    return html

# ==========================================
# 6. GIAO DIỆN STREAMLIT
# ==========================================
def get_current_vn_time(): return datetime.now(timezone(timedelta(hours=7)))

if "init_dt" not in st.session_state: st.session_state.init_dt = get_current_vn_time()

col1, col2 = st.columns(2)
with col1: selected_date = st.date_input("Ngày", value=st.session_state.init_dt.date(), min_value=datetime(1900, 1, 1).date(), max_value=datetime(2100, 12, 31).date())
with col2: selected_time = st.time_input("Giờ Phút", st.session_state.init_dt.time(), step=60)

user_dt = datetime.combine(selected_date, selected_time)

if user_dt.hour >= 23:
    actual_date = user_dt.date() + timedelta(days=1)
    chi_gio_idx = 0 
else:
    actual_date = user_dt.date()
    chi_gio_idx = (user_dt.hour + 1) // 2 % 12

chi_gio = dia_chi[chi_gio_idx]
day_obj = sxtwl.fromSolar(actual_date.year, actual_date.month, actual_date.day)

can_ngay_idx = day_obj.getDayGZ().tg
can_gio_idx = (can_ngay_idx % 5 * 2 + chi_gio_idx) % 10
hoa_giap_hien_tai = thien_can[can_gio_idx] + chi_gio

nhat_chi_hien_tai = dia_chi[day_obj.getDayGZ().dz] 
can_ngay_hien_tai = thien_can[day_obj.getDayGZ().tg]
can_thang_hien_tai = thien_can[day_obj.getMonthGZ().tg]
chi_thang_hien_tai = dia_chi[day_obj.getMonthGZ().dz]

bazi_dict = {'nam': thien_can[day_obj.getYearGZ().tg] + dia_chi[day_obj.getYearGZ().dz], 'thang': can_thang_hien_tai + chi_thang_hien_tai, 'ngay': can_ngay_hien_tai + nhat_chi_hien_tai}

don, cuc, jq_name, ji_palace, is_nhuan = get_zhirun_ju(actual_date)
nhuan_str = " - 闰奇" if is_nhuan else ""
chuoi_cuc = f"飞盘 | {jq_name}{nhuan_str} - {don}{cuc}局 | 寄宫: {ji_palace}"
bazi_chuoi = f"{bazi_dict['nam']}年 {bazi_dict['thang']}月 {bazi_dict['ngay']}日 {hoa_giap_hien_tai}时"

tk_gio = tinh_tuan_khong_gio(hoa_giap_hien_tai)
data = lap_que(hoa_giap_hien_tai, nhat_chi_hien_tai, don, cuc, ji_palace, can_thang_hien_tai, can_ngay_hien_tai, chi_thang_hien_tai)

# --- KHỐI TÍNH TOÁN CÁCH CỤC ---
can_gio_phai, chi_gio_phai = hoa_giap_hien_tai[0], hoa_giap_hien_tai[1]
idx_can, idx_chi = thien_can.index(can_gio_phai), dia_chi.index(chi_gio_phai)
chi_tuan = dia_chi[(idx_chi - idx_can) % 12]
can_tuan = {"子":"戊", "戌":"己", "申":"庚", "午":"辛", "辰":"壬", "寅":"癸"}[chi_tuan]

truc_su_door = None
for p, d in data.items():
    if p != 5 and d['dia'] == can_tuan:
        truc_su_door = d['mon']
        break
if not truc_su_door and ji_palace in data: truc_su_door = data[ji_palace]['mon']

toan_ban_st, cung_st, cung_3_el = qimen_analyzer(data, can_ngay_hien_tai, can_gio_phai, can_tuan, truc_su_door)
# -----------------------------------

title = f"<h3 style='margin-bottom:6px; font-family:sans-serif; color: #111; font-weight: 400; font-size: 18px; text-align: center;'>{bazi_chuoi}</h3>"
sub_title = f"<h4 style='margin-top:0px; margin-bottom:15px; font-family:sans-serif; color: #555; font-weight: 300; font-size: 15px; text-align: center;'>{chuoi_cuc}</h4>"

qimen_board_html = render_html_table(data, tk_gio, toan_ban_st, cung_st, cung_3_el)

combined_html = f"""
    <div style="display: flex; flex-direction: column; align-items: center; width: 100%; padding-top: 10px;">
        <div style="display: flex; flex-direction: column; align-items: center; width: 100%; max-width: 510px;">
            {title}
            {sub_title}
            {qimen_board_html}
        </div>
    </div>
"""

st.components.v1.html(combined_html, height=700, scrolling=True)

# ==========================================
# 7. MODULE SCAN: DỤNG SỰ (TÌM KIẾM THỜI ĐIỂM)
# ==========================================
st.markdown("---")
st.markdown("<h3 style='text-align: center; color: #333; font-family: sans-serif; margin-bottom: 20px;'>DỤNG SỰ</h3>", unsafe_allow_html=True)

# --- TỪ ĐIỂN RANK ĐỂ FORMAT GIAO DIỆN LỌC ---
FORMATION_RANKS_LOCAL = {
    "天遁": 1, "地遁": 1, "人遁": 1, "神遁": 1, "鬼遁": 1,
    "大格": 1, "小格": 1, "刑格": 1, "戦格": 1, "飛宮格": 1, "伏宮格": 1, 
    "青竜逃走": 1, "白虎猖狂": 1, "熒惑入白": 1, "太白入熒": 1, "朱雀投江": 1, "螣蛇妖嬌": 1,
    "青竜返首": 2, "飛鳥跌穴": 2, "玉女守門": 2, "乙奇得使": 2, "丙奇得使": 2, "丁奇得使": 2, 
    "竜遁": 2, "虎遁": 2, "風遁": 2, "雲遁": 2, 
    "乙奇入墓": 2, "丙奇入墓": 2, "丁奇入墓": 2,
    "甲儀伏吟": 2, "乙奇伏吟": 2, "丙奇伏吟": 2, "丁奇伏吟": 2, "戊儀伏吟": 2, "己儀伏吟": 2, "庚儀伏吟": 2, "辛儀伏吟": 2, "壬儀伏吟": 2, "癸儀伏吟": 2,
    "甲儀反吟": 2, "乙奇反吟": 2, "丙奇反吟": 2, "丁奇反吟": 2, "戊儀反吟": 2, "己儀反吟": 2, "庚儀反吟": 2, "辛儀反吟": 2, "壬儀反吟": 2, "癸儀反吟": 2,
    "乙奇昇殿": 3, "丙奇昇殿": 3, "丁奇昇殿": 3,
    "九星伏吟": 3, "八门伏吟": 3, "九星反吟": 3, "八门反吟": 3
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

# --- DATA BỘ LỌC CƠ BẢN ---
huong_list = {"": None, "坎 (337.5 - 22.5)": 1, "艮 (22.5 - 67.5)": 8, "震 (67.5 - 112.5)": 3, "巽 (112.5 - 157.5)": 4, 
              "離 (157.5 - 202.5)": 9, "坤 (202.5 - 247.5)": 2, "兌 (247.5 - 292.5)": 7, "乾 (292.5 - 337.5)": 6}
can_list = ["", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
mon_list = ["", "休门", "生门", "伤门", "杜门", "景门", "死门", "惊门", "开门"]
tinh_list = ["", "天蓬", "天芮", "天冲", "天辅", "天禽", "天心", "天柱", "天任", "天英"]
than_list = ["", "值符", "螣蛇", "太阴", "六合", "勾陈", "太常", "朱雀", "九地", "九天"]
cat_cach_list = format_ui_list(["青竜返首", "飛鳥跌穴", "玉女守門", "乙奇昇殿", "丙奇昇殿", "丁奇昇殿", "乙奇得使", "丙奇得使", "丁奇得使", "天遁", "地遁", "人遁", "神遁", "鬼遁", "竜遁", "虎遁", "風遁", "雲遁"])

# --- DATA TRẤN HUNG & THÔI CÁT ---
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
    "乙奇伏吟": (["人遁", "鬼遁", "玉女守門", "丁奇得使"], ["丁奇昇殿"]),
    "乙奇反吟": (["人遁", "鬼遁", "玉女守門", "丁奇得使"], ["丁奇昇殿"]),
    "戊儀伏吟": (["青竜返首"], []), "戊儀反吟": (["青竜返首"], []),
    "己儀伏吟": (["青竜返首"], []), "己儀反吟": (["青竜返首"], []),
    "庚儀伏吟": (["地遁", "乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"], ["乙奇昇殿"]),
    "庚儀反吟": (["地遁", "乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"], ["乙奇昇殿"]),
    "辛儀伏吟": (["天遁", "神遁", "飛鳥跌穴", "丙奇得使"], ["丙奇昇殿"]),
    "辛儀反吟": (["天遁", "神遁", "飛鳥跌穴", "丙奇得使"], ["丙奇昇殿"]),
    "壬儀伏吟": (["人遁", "鬼遁", "玉女守門", "丁奇得使"], ["丁奇昇殿"]),
    "壬儀反吟": (["人遁", "鬼遁", "玉女守門", "丁奇得使"], ["丁奇昇殿"]),
    "癸儀伏吟": (["天遁", "地遁", "神遁", "飛鳥跌穴", "乙奇得使", "丙奇得使", "竜遁", "虎遁", "風遁", "雲遁"], ["乙奇昇殿", "丙奇昇殿"]),
    "癸儀反吟": (["天遁", "地遁", "神遁", "飛鳥跌穴", "乙奇得使", "丙奇得使", "竜遁", "虎遁", "風遁", "雲遁"], ["乙奇昇殿", "丙奇昇殿"]),
    "熒惑入白": ([], []), "朱雀投江": ([], []), "丙奇入墓": ([], []), "丁奇入墓": ([], []), "丙奇伏吟": ([], []), "丙奇反吟": ([], [])
}

THOI_CAT_DICT = {
    "青竜返首": (["青竜返首"], []), "乙奇昇殿": (["青竜返首"], []), "乙奇得使": (["青竜返首"], []),
    "地遁": (["青竜返首"], []), "竜遁": (["青竜返首"], []), "虎遁": (["青竜返首"], []),
    "風遁": (["青竜返首"], []), "雲遁": (["青竜返首"], []),
    "飛鳥跌穴": (["地遁", "乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"], ["乙奇昇殿"]),
    "玉女守門": (["地遁", "青竜返首", "乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"], ["乙奇昇殿"]),
    "丙奇昇殿": (["地遁", "乙奇得使", "竜遁", "虎遁", "風遁", "雲遁", "乙奇昇殿"], []),
    "丁奇昇殿": (["地遁", "青竜返首", "乙奇得使", "竜遁", "虎遁", "風遁", "雲遁", "乙奇昇殿"], []),
    "丙奇得使": (["地遁", "乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"], ["乙奇昇殿"]),
    "丁奇得使": (["地遁", "青竜返首", "乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"], ["乙奇昇殿"]),
    "天遁": (["地遁"], ["乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"]),
    "神遁": (["地遁"], ["乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"]),
    "人遁": (["地遁"], ["青竜返首", "乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"]),
    "鬼遁": (["地遁"], ["青竜返首", "乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"])
}

tran_hung_list = format_ui_list(list(TRAN_HUNG_DICT.keys()))
thoi_cat_list = format_ui_list(list(THOI_CAT_DICT.keys()))

# --- GIAO DIỆN LỌC (Gộp lên 1 hàng) ---
with st.container():
    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    loc_huong = c1.selectbox("方向 (Hướng)", options=list(huong_list.keys()))
    loc_thien_can = c2.selectbox("天盤 (Thiên Bàn)", options=can_list)
    loc_dia_can = c3.selectbox("地盤 (Địa Bàn)", options=can_list)
    loc_mon = c4.selectbox("八門 (Bát Môn)", options=mon_list)
    loc_tinh = c5.selectbox("九星 (Cửu Tinh)", options=tinh_list)
    loc_than = c6.selectbox("九神 (Cửu Thần)", options=than_list)
    loc_cat_cach = c7.selectbox("吉格 (Cát Cách)", options=cat_cach_list)
    
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    # Chia đều 2 ô rộng ra giữa màn hình
    c9, c10 = st.columns(2)
    loc_tran_hung = c9.selectbox("鎮凶 (Trấn Hung)", options=tran_hung_list)
    loc_thoi_cat = c10.selectbox("催吉 (Thôi Cát)", options=thoi_cat_list)

# --- HÀM HỖ TRỢ LỌC ---
def get_shichen_start(dt):
    h = dt.hour
    start_h = h if h % 2 != 0 else h - 1
    if start_h < 0: return (dt - timedelta(days=1)).replace(hour=23, minute=0, second=0, microsecond=0)
    return dt.replace(hour=start_h, minute=0, second=0, microsecond=0)

def check_cung_match(d_cung, status_cung, f_thien, f_dia, f_mon, f_tinh, f_than, f_catcach):
    if f_thien and d_cung['thien'] != f_thien: return False
    if f_dia and d_cung['dia'] != f_dia: return False
    if f_mon and d_cung['mon'] != f_mon: return False
    if f_tinh and d_cung['sao'] != f_tinh: return False
    if f_than and d_cung['than'] != f_than: return False
    if f_catcach:
        if not any(f_catcach in item[0] for item in status_cung): return False
    return True

def find_fulfilled_plan(plan_list, d_cung, status_cung):
    for req in plan_list:
        if req == "天盤丙":
            if d_cung['thien'] == '丙': return "Thiên Bàn Bính"
        else:
            if any(req in item[0] for item in status_cung): return req
    return None

if st.button("TÌM KIẾM", use_container_width=True):
    val_tran_hung = extract_raw_name(loc_tran_hung)
    val_thoi_cat = extract_raw_name(loc_thoi_cat)
    
    # KIỂM TRA ĐIỀU KIỆN CHỌN ĐỒNG THỜI
    if val_tran_hung and val_thoi_cat:
        st.error("Không Có (Vui lòng không chọn cùng lúc Trấn Hung và Thôi Cát).")
    else:
        with st.spinner('Đang quét dữ liệu...'):
            mode = "NORMAL"
            if val_tran_hung: mode = "TRAN_HUNG"
            elif val_thoi_cat: mode = "THOI_CAT"
            
            results_normal = []
            results_pa1 = []
            results_pa2 = []
            
            current_scan_dt = get_shichen_start(user_dt)
            max_shichen_limit = 4320 
            loops = 0
            
            # Tiền kiểm tra: Tránh quét thừa nếu Không có phương án
            if mode == "TRAN_HUNG":
                pa1_reqs, pa2_reqs = TRAN_HUNG_DICT[val_tran_hung]
                if not pa1_reqs and not pa2_reqs:
                    st.info(f"Không có phương án nào để Trấn Hung cho cách cục [{val_tran_hung}].")
                    max_shichen_limit = 0
            elif mode == "THOI_CAT":
                pa1_reqs, pa2_reqs = THOI_CAT_DICT[val_thoi_cat]
                if not pa1_reqs and not pa2_reqs:
                    st.info(f"Không có phương án nào để Thôi Cát cho cách cục [{val_thoi_cat}].")
                    max_shichen_limit = 0

            # CACHE ngày để thuật toán siêu nhanh
            current_cached_date = None
            s_don, s_cuc, s_ji = None, None, None

            while loops < max_shichen_limit:
                if mode == "NORMAL" and len(results_normal) >= 10: break
                if mode in ["TRAN_HUNG", "THOI_CAT"]:
                    pa1_reqs, pa2_reqs = TRAN_HUNG_DICT[val_tran_hung] if mode == "TRAN_HUNG" else THOI_CAT_DICT[val_thoi_cat]
                    pa1_done = len(results_pa1) >= 5 or not pa1_reqs
                    pa2_done = len(results_pa2) >= 5 or not pa2_reqs
                    if pa1_done and pa2_done: break

                loops += 1
                current_scan_dt += timedelta(hours=2)
                
                if current_scan_dt.hour >= 23:
                    s_date = current_scan_dt.date() + timedelta(days=1)
                    c_gio_idx = 0 
                else:
                    s_date = current_scan_dt.date()
                    c_gio_idx = (current_scan_dt.hour + 1) // 2 % 12
                    
                c_gio = dia_chi[c_gio_idx]
                s_obj = sxtwl.fromSolar(s_date.year, s_date.month, s_date.day)
                
                c_ngay_idx = s_obj.getDayGZ().tg
                can_gio_idx_scan = (c_ngay_idx % 5 * 2 + c_gio_idx) % 10
                hg_gio_scan = thien_can[can_gio_idx_scan] + c_gio
                
                nc_scan = dia_chi[s_obj.getDayGZ().dz] 
                cn_scan = thien_can[s_obj.getDayGZ().tg]
                ct_scan = thien_can[s_obj.getMonthGZ().tg]
                cht_scan = dia_chi[s_obj.getMonthGZ().dz]
                
                # --- TỐI ƯU TỐC ĐỘ (CACHE) ---
                if s_date != current_cached_date:
                    cached_ju_data = get_zhirun_ju(s_date)
                    current_cached_date = s_date
                s_don, s_cuc, _, s_ji, _ = cached_ju_data
                
                scan_data = lap_que(hg_gio_scan, nc_scan, s_don, s_cuc, s_ji, ct_scan, cn_scan, cht_scan)
                
                idx_c_scan, idx_ch_scan = thien_can.index(hg_gio_scan[0]), dia_chi.index(hg_gio_scan[1])
                tuan_scan = dia_chi[(idx_ch_scan - idx_c_scan) % 12]
                can_tuan_scan = {"子":"戊", "戌":"己", "申":"庚", "午":"辛", "辰":"壬", "寅":"癸"}[tuan_scan]
                
                ts_door_scan = None
                for p, d in scan_data.items():
                    if p != 5 and d['dia'] == can_tuan_scan:
                        ts_door_scan = d['mon']
                        break
                if not ts_door_scan and s_ji in scan_data: ts_door_scan = scan_data[s_ji]['mon']
                
                _, cung_st, _ = qimen_analyzer(scan_data, cn_scan, hg_gio_scan[0], can_tuan_scan, ts_door_scan)
                
                end_scan_dt = current_scan_dt + timedelta(hours=2, minutes=-1)
                time_str = f"{current_scan_dt.strftime('%d/%m/%Y %H:00')} - {end_scan_dt.strftime('%H:59')}"
                can_chi_str = f"Ngày {cn_scan}{nc_scan} - Giờ {hg_gio_scan}"
                
                # --- XỬ LÝ LỌC BÌNH THƯỜNG ---
                if mode == "NORMAL":
                    is_match = False
                    target_palace = huong_list[loc_huong]
                    val_cat_cach = extract_raw_name(loc_cat_cach)
                    
                    if target_palace:
                        if target_palace != 5:
                            is_match = check_cung_match(scan_data[target_palace], cung_st[target_palace], loc_thien_can, loc_dia_can, loc_mon, loc_tinh, loc_than, val_cat_cach)
                    else:
                        for p in range(1, 10):
                            if p == 5: continue
                            if check_cung_match(scan_data[p], cung_st[p], loc_thien_can, loc_dia_can, loc_mon, loc_tinh, loc_than, val_cat_cach):
                                is_match = True
                                target_palace = p
                                break
                    if is_match:
                        ten_cung = [k for k, v in huong_list.items() if v == target_palace][0]
                        results_normal.append((time_str, can_chi_str, ten_cung))
                
                # --- XỬ LÝ TRẤN HUNG / THÔI CÁT ---
                else:
                    for p in range(1, 10):
                        if p == 5: continue
                        # Đi tìm Phương Án 1 / Phương Án 2 trực tiếp
                        
                        if len(results_pa1) < 5 and pa1_reqs:
                            found_pa1 = find_fulfilled_plan(pa1_reqs, scan_data[p], cung_st[p])
                            if found_pa1:
                                ten_cung = [k for k, v in huong_list.items() if v == p][0]
                                results_pa1.append((time_str, can_chi_str, ten_cung, found_pa1))
                        
                        if len(results_pa2) < 5 and pa2_reqs:
                            found_pa2 = find_fulfilled_plan(pa2_reqs, scan_data[p], cung_st[p])
                            if found_pa2:
                                ten_cung = [k for k, v in huong_list.items() if v == p][0]
                                results_pa2.append((time_str, can_chi_str, ten_cung, found_pa2))

            # --- HIỂN THỊ KẾT QUẢ ---
            if mode == "NORMAL":
                if results_normal:
                    st.write(f"**TÌM THẤY {len(results_normal)} KẾT QUẢ:**")
                    for idx, (t_str, c_str, cung_str) in enumerate(results_normal):
                        h_text = f" | Hướng: {cung_str}" if cung_str else ""
                        st.write(f"{idx+1}. {t_str} | {c_str}{h_text}")
                else:
                    st.write("Không tìm thấy kết quả nào trong vòng 1 năm tới.")
            
            else: # TRAN_HUNG / THOI_CAT
                if not results_pa1 and not results_pa2 and max_shichen_limit > 0:
                    st.write(f"Đã quét 1 năm nhưng không tìm thấy thời điểm nào có thể xử lý [{target_name}].")
                
                if results_pa1:
                    st.write(f"**Phương án 1 (Tìm thấy {len(results_pa1)}):**")
                    for idx, (t_str, c_str, cung_str, dung_cach) in enumerate(results_pa1):
                        st.write(f"{idx+1}. Dùng **{dung_cach}** | {t_str} | {c_str} | Tại: {cung_str}")
                
                if results_pa2:
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    st.write(f"**Phương án 2 (Tìm thấy {len(results_pa2)}):**")
                    for idx, (t_str, c_str, cung_str, dung_cach) in enumerate(results_pa2):
                        st.write(f"{idx+1}. Dùng **{dung_cach}** | {t_str} | {c_str} | Tại: {cung_str}")
