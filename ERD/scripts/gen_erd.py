#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sinh lai ERD.svg (va cac ERD phan he lien quan) tu dinh nghia schema dang du lieu Python.
Day la "nguon" moi cho ERD, thay the cho viec sua tay file SVG (Graphviz-generated, khong co
file .dot nguon trong repo)."""
import json
import os
import subprocess
import html

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ERD_DIR = os.path.dirname(SCRIPT_DIR)

CLUSTERS = {
    "DANH_MUC": {"label": "DANH MỤC DÙNG CHUNG", "color": "#dce6f1"},
    "YCGT": {"label": "TIẾP NHẬN &amp; XỬ LÝ YÊU CẦU GIẢI TRÌNH", "color": "#fbe5d6"},
    "VANBAN": {"label": "VĂN BẢN GIẢI TRÌNH &amp; CÔNG KHAI", "color": "#d8e4bc"},
    "PHKN": {"label": "PHẢN HỒI &amp; KHIẾU NẠI", "color": "#d9d2e9"},
    "DANHGIA": {"label": "ĐÁNH GIÁ THỰC HIỆN TNGT", "color": "#f2cfcf"},
    "GIAMSAT": {"label": "GIÁM SÁT, GIAO VIỆC &amp; BÁO CÁO", "color": "#c6e0e0"},
    "LUUTRU": {"label": "SỔ VĂN BẢN &amp; LƯU TRỮ", "color": "#e4e4c6"},
    "DUNGCHUNG": {"label": "BẢNG DÙNG CHUNG (POLYMORPHIC)", "color": "#ffe699"},
    "QUANTRI": {"label": "QUẢN TRỊ HỆ THỐNG", "color": "#d9d9d9"},
}

EXT_COLOR = "#dce6f1"  # bang mo rong 1-1 (can_bo/nguoi_dan/to_chuc)

entities = json.load(open(os.path.join(SCRIPT_DIR, "entities_base.json"), encoding="utf-8"))

# --- Fix du lieu 3 bang mo rong bi loi khi parse tu dong (thu tu cot / thieu truong) ---
entities["can_bo"] = [
    {"field": "id", "key": "PK/FK", "type": "BIGINT UNSIGNED", "note": "= nguoi_dung.id"},
    {"field": "ma_can_bo", "key": None, "type": "VARCHAR(30)"},
    {"field": "ho_ten", "key": None, "type": "VARCHAR(150)"},
    {"field": "don_vi_id", "key": "FK", "type": "BIGINT UNSIGNED"},
    {"field": "chuc_vu", "key": None, "type": "VARCHAR(100)"},
    {"field": "email", "key": None, "type": "VARCHAR(150)"},
    {"field": "so_dien_thoai", "key": None, "type": "VARCHAR(20)"},
]
entities["nguoi_dan"] = [
    {"field": "id", "key": "PK/FK", "type": "BIGINT UNSIGNED", "note": "= nguoi_dung.id"},
    {"field": "ho_ten", "key": None, "type": "VARCHAR(150)"},
    {"field": "ngay_sinh", "key": None, "type": "DATE"},
    {"field": "gioi_tinh", "key": None, "type": "TINYINT"},
    {"field": "dia_chi_thuong_tru", "key": None, "type": "VARCHAR(255)"},
    {"field": "email", "key": None, "type": "VARCHAR(150)"},
    {"field": "so_dien_thoai", "key": None, "type": "VARCHAR(20)"},
]
entities["to_chuc"] = [
    {"field": "id", "key": "PK/FK", "type": "BIGINT UNSIGNED", "note": "= nguoi_dung.id"},
    {"field": "ten_to_chuc", "key": None, "type": "VARCHAR(255)"},
    {"field": "ma_so_thue", "key": None, "type": "VARCHAR(30)"},
    {"field": "nguoi_dai_dien", "key": None, "type": "VARCHAR(150)"},
    {"field": "dia_chi", "key": None, "type": "VARCHAR(255)"},
    {"field": "email", "key": None, "type": "VARCHAR(150)"},
    {"field": "so_dien_thoai", "key": None, "type": "VARCHAR(20)"},
]

# ============ CAC DIEU CHINH THEO PHAN TICH GAP (uu tien CAO) ============

# 1) Gia han thoi han giai trinh: bo sung truong luu lich su gia han thay vi ghi de han_xu_ly
yc = entities["yeu_cau_giai_trinh"]
idx = next(i for i, f in enumerate(yc) if f["field"] == "han_xu_ly")
yc[idx+1:idx+1] = [
    {"field": "han_xu_ly_cu", "key": None, "type": "DATE", "new": True},
    {"field": "so_lan_gia_han", "key": None, "type": "TINYINT", "new": True},
    {"field": "ly_do_gia_han_id", "key": "FK", "type": "BIGINT UNSIGNED", "new": True},
    {"field": "ngay_gia_han_gan_nhat", "key": None, "type": "DATETIME", "new": True},
]

# 2) Phan biet loai van ban (chinh thuc/gia han/tam dinh chi/dinh chi/khoi phuc/thay the)
#    + tham chieu van ban duoc thay the
vb = entities["van_ban_giai_trinh"]
idx = next(i for i, f in enumerate(vb) if f["field"] == "yeu_cau_giai_trinh_id")
vb[idx+1:idx+1] = [
    {"field": "loai_van_ban", "key": None, "type": "ENUM", "new": True},
]
idx2 = next(i for i, f in enumerate(vb) if f["field"] == "trang_thai")
vb[idx2:idx2] = [
    {"field": "van_ban_thay_the_id", "key": "FK", "type": "BIGINT UNSIGNED", "new": True},
]

# Danh muc ly do (tu choi / gia han) - phuc vu FK moi o tren
entities["danh_muc_ly_do_giai_trinh"] = [
    {"field": "id", "key": "PK", "type": "BIGINT UNSIGNED", "new": True},
    {"field": "nhom_ly_do", "key": None, "type": "ENUM", "new": True},
    {"field": "noi_dung", "key": None, "type": "VARCHAR(255)", "new": True},
    {"field": "thu_tu", "key": None, "type": "TINYINT", "new": True},
    {"field": "trang_thai", "key": None, "type": "TINYINT", "new": True},
]

# 3) Chung thu so & thiet bi ky so (mucU - an toan thong tin cap do 3)
entities["chung_thu_so"] = [
    {"field": "id", "key": "PK", "type": "BIGINT UNSIGNED", "new": True},
    {"field": "can_bo_id", "key": "FK", "type": "BIGINT UNSIGNED", "new": True},
    {"field": "so_serial", "key": None, "type": "VARCHAR(100)", "new": True},
    {"field": "nha_cung_cap", "key": None, "type": "VARCHAR(255)", "new": True},
    {"field": "ngay_cap", "key": None, "type": "DATE", "new": True},
    {"field": "ngay_het_han", "key": None, "type": "DATE", "new": True},
    {"field": "trang_thai", "key": None, "type": "ENUM", "new": True},
    {"field": "ngay_thu_hoi", "key": None, "type": "DATETIME", "new": True},
    {"field": "ly_do_thu_hoi", "key": None, "type": "VARCHAR(255)", "new": True},
]
entities["thiet_bi_ky_so"] = [
    {"field": "id", "key": "PK", "type": "BIGINT UNSIGNED", "new": True},
    {"field": "chung_thu_so_id", "key": "FK", "type": "BIGINT UNSIGNED", "new": True},
    {"field": "loai_thiet_bi", "key": None, "type": "ENUM", "new": True},
    {"field": "ma_thiet_bi", "key": None, "type": "VARCHAR(100)", "new": True},
    {"field": "trang_thai", "key": None, "type": "ENUM", "new": True},
    {"field": "ngay_dang_ky", "key": None, "type": "DATE", "new": True},
]

# 4) Nhat ky he thong (audit log tong quat, da hinh) - mucJ
entities["nhat_ky_he_thong"] = [
    {"field": "id", "key": "PK", "type": "BIGINT UNSIGNED", "new": True},
    {"field": "doi_tuong_loai", "key": None, "type": "VARCHAR(50)", "new": True},
    {"field": "doi_tuong_id", "key": None, "type": "BIGINT UNSIGNED", "new": True},
    {"field": "hanh_dong", "key": None, "type": "ENUM", "new": True},
    {"field": "nguoi_thuc_hien_id", "key": "FK", "type": "BIGINT UNSIGNED", "new": True},
    {"field": "thoi_gian", "key": None, "type": "DATETIME", "new": True},
    {"field": "dia_chi_ip", "key": None, "type": "VARCHAR(45)", "new": True},
    {"field": "chi_tiet", "key": None, "type": "TEXT", "new": True},
]

# ============ Uu tien TRUNG BINH ============

# 5) So hoa du lieu (muc N) - ky so hoa theo tung dot, gan voi tep dinh kem
entities["ky_so_hoa"] = [
    {"field": "id", "key": "PK", "type": "BIGINT UNSIGNED", "new": True},
    {"field": "ten_ky", "key": None, "type": "VARCHAR(150)", "new": True},
    {"field": "loai_doi_tuong", "key": None, "type": "ENUM", "new": True},
    {"field": "tu_ngay", "key": None, "type": "DATE", "new": True},
    {"field": "den_ngay", "key": None, "type": "DATE", "new": True},
    {"field": "nguoi_phu_trach_id", "key": "FK", "type": "BIGINT UNSIGNED", "new": True},
    {"field": "trang_thai", "key": None, "type": "ENUM", "new": True},
]
tdk = entities["tep_dinh_kem"]
tdk.extend([
    {"field": "ky_so_hoa_id", "key": "FK", "type": "BIGINT UNSIGNED", "new": True},
    {"field": "da_so_hoa", "key": None, "type": "TINYINT", "new": True},
    {"field": "chat_luong_ocr", "key": None, "type": "VARCHAR(50)", "new": True},
])

# 6) Quan ly phien dang nhap / thiet bi dang nhap (muc U)
entities["phien_dang_nhap"] = [
    {"field": "id", "key": "PK", "type": "BIGINT UNSIGNED", "new": True},
    {"field": "nguoi_dung_id", "key": "FK", "type": "BIGINT UNSIGNED", "new": True},
    {"field": "thiet_bi", "key": None, "type": "VARCHAR(255)", "new": True},
    {"field": "dia_chi_ip", "key": None, "type": "VARCHAR(45)", "new": True},
    {"field": "thoi_gian_dang_nhap", "key": None, "type": "DATETIME", "new": True},
    {"field": "thoi_gian_dang_xuat", "key": None, "type": "DATETIME", "new": True},
    {"field": "trang_thai", "key": None, "type": "ENUM", "new": True},
]

# 7) Phieu danh gia - luan chuyen 2 chieu TTCP <-> Bo/nganh (muc I.III.2)
entities["phieu_danh_gia"] = [
    {"field": "id", "key": "PK", "type": "BIGINT UNSIGNED", "new": True},
    {"field": "ky_khao_sat_id", "key": "FK", "type": "BIGINT UNSIGNED", "new": True},
    {"field": "don_vi_id", "key": "FK", "type": "BIGINT UNSIGNED", "new": True},
    {"field": "nguoi_lap_id", "key": "FK", "type": "BIGINT UNSIGNED", "new": True},
    {"field": "trang_thai", "key": None, "type": "ENUM", "new": True,
     "note": "Nháp/Đã gửi/Yêu cầu bổ sung/Đã duyệt"},
    {"field": "ngay_gui", "key": None, "type": "DATETIME", "new": True},
    {"field": "ngay_duyet", "key": None, "type": "DATETIME", "new": True},
    {"field": "ghi_chu", "key": None, "type": "TEXT", "new": True},
]
kqks = entities["ket_qua_khao_sat"]
idx = next(i for i, f in enumerate(kqks) if f["field"] == "ky_khao_sat_id")
kqks[idx+1:idx+1] = [
    {"field": "phieu_danh_gia_id", "key": "FK", "type": "BIGINT UNSIGNED", "new": True},
]

# 8) Danh muc dung chung (muc K - ~35 danh muc dang bi thieu bang chua)
entities["danh_muc_dung_chung"] = [
    {"field": "id", "key": "PK", "type": "BIGINT UNSIGNED", "new": True},
    {"field": "loai_danh_muc", "key": None, "type": "VARCHAR(100)", "new": True,
     "note": "vd: linh_vuc_giai_trinh, loai_van_ban_lien_thong,..."},
    {"field": "ma", "key": None, "type": "VARCHAR(50)", "new": True},
    {"field": "ten", "key": None, "type": "VARCHAR(255)", "new": True},
    {"field": "thu_tu", "key": None, "type": "TINYINT", "new": True},
    {"field": "trang_thai", "key": None, "type": "TINYINT", "new": True},
]

# 9) Bo sung ghi chu gia tri "Da rut" cho ENUM trang_thai cua yeu_cau_giai_trinh
for f in entities["yeu_cau_giai_trinh"]:
    if f["field"] == "trang_thai":
        f["note"] = "...,Đã rút (bổ sung)"

ENTITY_CLUSTER = {
    "don_vi": "DANH_MUC", "vai_tro": "DANH_MUC", "nguoi_dung": "DANH_MUC",
    "nguoi_dung_vai_tro": "DANH_MUC", "bo_phan_tiep_nhan": "DANH_MUC",
    "lich_truc": "DANH_MUC", "noi_quy_quy_che": "DANH_MUC",
    "can_bo": "DANH_MUC", "nguoi_dan": "DANH_MUC", "to_chuc": "DANH_MUC",
    "danh_muc_ly_do_giai_trinh": "DANH_MUC", "danh_muc_dung_chung": "DANH_MUC",
    "phien_dang_nhap": "DANH_MUC",

    "nguoi_yeu_cau": "YCGT", "yeu_cau_giai_trinh": "YCGT",
    "phieu_yeu_cau_chuyen_mon": "YCGT", "nhiem_vu_giai_trinh": "YCGT",
    "ke_hoach_giai_trinh": "YCGT", "buoi_lam_viec": "YCGT",
    "bao_cao_thu_thap_du_lieu": "YCGT",

    "van_ban_giai_trinh": "VANBAN", "y_kien_phoi_hop": "VANBAN",
    "xu_ly_an_danh": "VANBAN", "cong_khai_van_ban": "VANBAN",
    "gui_van_ban_lien_thong": "VANBAN",

    "phan_hoi_van_ban": "PHKN", "quyet_dinh_thu_ly_phan_hoi": "PHKN",
    "don_khieu_nai": "PHKN", "quyet_dinh_thu_ly_khieu_nai": "PHKN",
    "xac_minh_khieu_nai": "PHKN",

    "tieu_chi_danh_gia": "DANHGIA", "ky_khao_sat": "DANHGIA",
    "ket_qua_khao_sat": "DANHGIA", "ket_qua_danh_gia": "DANHGIA",
    "phieu_danh_gia": "DANHGIA",

    "co_quan_giam_sat": "GIAMSAT", "cau_hinh_phan_quyen": "GIAMSAT",
    "nhat_ky_giam_sat": "GIAMSAT", "phieu_giao_viec": "GIAMSAT",
    "bao_cao_nhiem_vu": "GIAMSAT", "bao_cao_thong_ke": "GIAMSAT",
    "lich_su_xuat_bao_cao": "GIAMSAT",

    "ban_giao_ho_so": "LUUTRU", "phuong_an_luu_tru": "LUUTRU",
    "so_van_ban": "LUUTRU", "ho_so_luu_tru": "LUUTRU", "ky_so_hoa": "LUUTRU",

    "phe_duyet": "DUNGCHUNG", "tep_dinh_kem": "DUNGCHUNG",
    "thong_bao": "DUNGCHUNG", "lich_su_trang_thai": "DUNGCHUNG",
    "luot_tra_cuu": "DUNGCHUNG", "nhat_ky_he_thong": "DUNGCHUNG",

    "nhat_ky_cau_hinh_he_thong": "QUANTRI",
    "chung_thu_so": "QUANTRI", "thiet_bi_ky_so": "QUANTRI",
}

edges = json.load(open(os.path.join(SCRIPT_DIR, "edges_base.json"), encoding="utf-8"))
edges = [tuple(e) for e in edges]
NEW_EDGES = [
    ("yeu_cau_giai_trinh", "danh_muc_ly_do_giai_trinh"),
    ("van_ban_giai_trinh", "van_ban_giai_trinh"),
    ("chung_thu_so", "can_bo"),
    ("thiet_bi_ky_so", "chung_thu_so"),
    ("nhat_ky_he_thong", "nguoi_dung"),
    ("ky_so_hoa", "can_bo"),
    ("tep_dinh_kem", "ky_so_hoa"),
    ("phien_dang_nhap", "nguoi_dung"),
    ("phieu_danh_gia", "ky_khao_sat"),
    ("phieu_danh_gia", "don_vi"),
    ("phieu_danh_gia", "can_bo"),
    ("ket_qua_khao_sat", "phieu_danh_gia"),
]
edges = edges + NEW_EDGES

assert set(ENTITY_CLUSTER) == set(entities), set(ENTITY_CLUSTER) ^ set(entities)


def esc(s):
    return html.escape(str(s), quote=False)


def table_html(name, fields, header_color):
    rows = [f'<TR><TD COLSPAN="4" BGCOLOR="{header_color}"><FONT FACE="Consolas" POINT-SIZE="11"><B>{esc(name)}</B></FONT></TD></TR>']
    for f in fields:
        fname = esc(f["field"])
        key = f.get("key")
        ftype = f.get("type") or ""
        note = f.get("note")
        is_new = f.get("new")
        namecell = f'<B>{fname}</B>' if key else fname
        if is_new:
            namecell = f'<FONT COLOR="#c00000">{namecell}</FONT>'
        keycell = ""
        if key == "PK":
            keycell = '<FONT COLOR="#b8860b">PK</FONT>'
        elif key == "FK":
            keycell = '<FONT COLOR="#1f6fb2">FK</FONT>'
        elif key == "PK/FK":
            keycell = '<FONT COLOR="#b8860b">PK</FONT><FONT COLOR="#1f6fb2">/FK</FONT>'
        typecell = f'<FONT COLOR="#555555">{esc(ftype)}</FONT>'
        rows.append(
            f'<TR><TD ALIGN="LEFT"><FONT FACE="Consolas" POINT-SIZE="11">{namecell}</FONT></TD>'
            f'<TD ALIGN="LEFT">{keycell}</TD><TD></TD>'
            f'<TD ALIGN="LEFT">{typecell}</TD></TR>'
        )
        if note:
            rows.append(
                f'<TR><TD COLSPAN="4" ALIGN="LEFT"><FONT FACE="Consolas" POINT-SIZE="8" COLOR="#999999">= {esc(note)}</FONT></TD></TR>'
            )
    body = "".join(rows)
    return f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4">{body}</TABLE>>'


def build_dot(title, entity_subset, edge_subset, with_clusters=True):
    lines = []
    lines.append(f'digraph "{title}" {{')
    lines.append('rankdir=LR; splines=ortho; nodesep=0.4; ranksep=1.1;')
    lines.append('node [shape=plain];')
    lines.append(f'labelloc="t"; fontsize=22; fontname="Helvetica,sans-Serif"; label=<{esc(title)}>;')

    if with_clusters:
        by_cluster = {}
        for e in entity_subset:
            by_cluster.setdefault(ENTITY_CLUSTER[e], []).append(e)
        cidx = 0
        for cname, cinfo in CLUSTERS.items():
            if cname not in by_cluster:
                continue
            cidx += 1
            lines.append(f'subgraph cluster_{cidx}_{cname} {{')
            lines.append(f'label=<<FONT FACE="Helvetica,sans-Serif" POINT-SIZE="15"><B>{cinfo["label"]}</B></FONT>>;')
            lines.append(f'style=filled; color="{cinfo["color"]}"; fillcolor="{cinfo["color"]}55";')
            for e in by_cluster[cname]:
                header_color = EXT_COLOR if e in ("can_bo", "nguoi_dan", "to_chuc") else cinfo["color"]
                lines.append(f'{e} [label={table_html(e, entities[e], header_color)}];')
            lines.append('}')
    else:
        for e in entity_subset:
            header_color = EXT_COLOR if e in ("can_bo", "nguoi_dan", "to_chuc") else CLUSTERS[ENTITY_CLUSTER[e]]["color"]
            lines.append(f'{e} [label={table_html(e, entities[e], header_color)}];')

    for a, b in edge_subset:
        if a not in entity_subset or b not in entity_subset:
            continue
        style = ' [style=dashed]' if a == b else ''
        lines.append(f'{a} -> {b}{style} [color="#5578a8", arrowhead=none, arrowtail=none];')

    lines.append('}')
    return "\n".join(lines)


def render(name, entity_subset, edge_subset, title, with_clusters=True):
    dot_src = build_dot(title, entity_subset, edge_subset, with_clusters)
    dot_path = os.path.join(SCRIPT_DIR, f"{name}.dot")
    open(dot_path, "w", encoding="utf-8").write(dot_src)
    svg_path = os.path.join(ERD_DIR, f"{name}.svg")
    subprocess.run(["dot", "-Tsvg", dot_path, "-o", svg_path], check=True)
    print("rendered", svg_path)


ALL_ENTITIES = list(entities.keys())

render("ERD", ALL_ENTITIES, edges, "SƠ ĐỒ ERD CHI TIẾT - HỆ THỐNG QUẢN LÝ TRÁCH NHIỆM GIẢI TRÌNH (TNGT)")

# --- Sinh lai TOAN BO 9 file ERD phan he tu cung 1 nguon, dam bao nhat quan ---
DOMAIN_FILE = {
    "DANH_MUC": ("ERD_00_danh_muc", "DANH MỤC DÙNG CHUNG (đã bổ sung lý do, danh mục, phiên đăng nhập)"),
    "YCGT": ("ERD_01_tiep_nhan_ycgt", "TIẾP NHẬN & XỬ LÝ YÊU CẦU GIẢI TRÌNH (đã bổ sung gia hạn)"),
    "VANBAN": ("ERD_02_van_ban_cong_khai", "VĂN BẢN GIẢI TRÌNH & CÔNG KHAI (đã bổ sung loại văn bản & thay thế)"),
    "PHKN": ("ERD_03_phan_hoi_khieu_nai", "PHẢN HỒI & KHIẾU NẠI"),
    "DANHGIA": ("ERD_04_danh_gia_tngt", "ĐÁNH GIÁ THỰC HIỆN TNGT (đã bổ sung phiếu đánh giá 2 chiều)"),
    "GIAMSAT": ("ERD_05_giam_sat_giao_viec_bao_cao", "GIÁM SÁT, GIAO VIỆC & BÁO CÁO"),
    "LUUTRU": ("ERD_06_so_van_ban_luu_tru", "SỔ VĂN BẢN & LƯU TRỮ (đã bổ sung kỳ số hoá)"),
    "DUNGCHUNG": ("ERD_07_dung_chung", "BẢNG DÙNG CHUNG (POLYMORPHIC) - đã bổ sung nhật ký hệ thống"),
    "QUANTRI": ("ERD_08_quan_tri", "QUẢN TRỊ HỆ THỐNG - đã bổ sung chứng thư số & thiết bị ký số"),
}

for cname, (fname, title) in DOMAIN_FILE.items():
    core = {e for e, c in ENTITY_CLUSTER.items() if c == cname}
    if cname == "DANH_MUC":
        # DANH_MUC la hub duoc hau het bang khac tham chieu toi (don_vi, can_bo,
        # nguoi_dung...) -> khong ke neighbor de tranh so do bi roi, chi hien
        # cac bang thuoc chinh nhom danh muc.
        entity_subset = core
    else:
        neighbors = set()
        for a, b in edges:
            if a in core and b not in core:
                neighbors.add(b)
            if b in core and a not in core:
                neighbors.add(a)
        entity_subset = core | neighbors
    render(fname, sorted(entity_subset), edges, title, with_clusters=False)

print("DONE")
