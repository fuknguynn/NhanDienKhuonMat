import sys
sys.path.append("D:\\DoAn\\NhanDienKhuonMat")
import customtkinter as ctk
from tkinter import ttk
from tkinter import filedialog
from tkcalendar import DateEntry
from pymongo import MongoClient
from datetime import datetime, timedelta
import pandas as pd
import subprocess
from ThongKeSinhVienSuKien import ThongKeSinhVienSuKien

# Kết nối MongoDB
client = MongoClient("mongodb+srv://scjan123:vgbyostAaTl3Uttq@cluster0.aahzt.mongodb.net/")  # Sửa địa chỉ theo hệ thống của bạn
db = client["nhandienkhuonmat"]  # Thay bằng tên cơ sở dữ liệu
collection = db["sukien"]  # Thay bằng tên collection

# Hàm xử lý hiển thị thời gian từ chuỗi
def format_time(time_str):
    try:
        if time_str:
            time_str = time_str.zfill(5)
            return datetime.strptime(time_str, "%H:%M").strftime("%I:%M %p")
        else:
            return "N/A"
    except ValueError:
        return "N/A"

# Hàm tải dữ liệu từ MongoDB
def load_data():
    results = collection.find()

    for item in tree.get_children():
        tree.delete(item)

    for idx, doc in enumerate(results, start=1):
        tree.insert("", "end", values=(
            idx,
            doc.get("mask", "N/A"),
            doc.get("tensk", "N/A"),
            doc.get("ngaytochuc", "N/A"),
            doc.get("vitri", "N/A"),
            doc.get("hocki", "N/A"),
            doc.get("tgianbatdau", ""),
            doc.get("tgianketthuc", ""),
            doc.get("slthamgia", 0),
            doc.get("slcomat", 0),
            doc.get("trangthai", "N/A")
        ))

# Hàm xuất dữ liệu từ Treeview ra Excel
def export_to_excel():
    # Mở hộp thoại chọn thư mục
    folder_selected = filedialog.askdirectory(title="Chọn thư mục lưu file Excel")

    if folder_selected:  # Kiểm tra nếu người dùng đã chọn thư mục
        # Mở hộp thoại nhập tên file
        file_name = filedialog.asksaveasfilename(
            initialdir=folder_selected,
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )

        if file_name:  # Kiểm tra nếu người dùng nhập tên file
            # Lấy dữ liệu từ Treeview
            data = []
            for item in tree.get_children():
                data.append(tree.item(item)["values"])

            # Chuyển dữ liệu thành DataFrame
            df = pd.DataFrame(data, columns=["STT", "Mã Sự Kiện", "Tên Sự Kiện", "Ngày Tổ Chức", "Vị Trí", "Học Kì",
                                             "Thời Gian Bắt Đầu", "Thời Gian Kết Thúc", "Số Lượng Tham Gia", "Số Lượng Có Mặt", "Trạng Thái"])

            # Xuất ra Excel
            df.to_excel(file_name, index=False, engine="openpyxl")
            print(f"Dữ liệu đã được xuất ra file {file_name}")
        else:
            print("Người dùng đã hủy chọn tên file.")
    else:
        print("Người dùng đã hủy chọn thư mục.")

# Hàm xử lý tìm kiếm
def tim_kiem():
    nam_hoc = combo_namhoc.get()
    hoc_ki = combo_hocki.get()
    vi_tri = combo_vitri.get()
    tu_ngay = entry_tungay.get_date().strftime("%Y-%m-%d")
    den_ngay = entry_denngay.get_date().strftime("%Y-%m-%d")
    ma_su_kien = entry_mask.get()
    trang_thai = combo_trangthai.get()

    query = {}
    if nam_hoc != "Tất cả":
        query["namhoc"] = nam_hoc
    if hoc_ki != "Tất cả":
        query["hocki"] = hoc_ki
    if vi_tri != "Tất cả":
        query["vitri"] = vi_tri
    if tu_ngay and den_ngay:
        query["ngaytochuc"] = {
            "$gte": tu_ngay,
            "$lte": den_ngay
        }
    elif tu_ngay:
        query["ngaytochuc"] = {"$gte": tu_ngay}
    elif den_ngay:
        query["ngaytochuc"] = {"$lte": den_ngay}
    if ma_su_kien:
        query["mask"] = {"$regex": ma_su_kien, "$options": "i"}
    if trang_thai != "Tất cả":
        query["trangthai"] = trang_thai

    results = collection.find(query)

    for item in tree.get_children():
        tree.delete(item)

    for idx, doc in enumerate(results, start=1):
        tree.insert("", "end", values=(
            idx,
            doc.get("mask", "N/A"),
            doc.get("tensk", "N/A"),
            doc.get("ngaytochuc", "N/A"),
            doc.get("vitri", "N/A"),
            doc.get("hocki", "N/A"),
            format_time(doc.get("tgianbatdau", "")),
            format_time(doc.get("tgianketthuc", "")),
            doc.get("slthamgia", 0),
            doc.get("slcomat", 0),
            doc.get("trangthai", "N/A")
        ))

def on_item_click(event):
    try:
        # Lấy dòng được chọn
        selected_item = tree.selection()[0]
        # Lấy mã sự kiện từ cột thứ hai
        ma_su_kien = tree.item(selected_item)["values"][1]
        print(f"Đã chọn Mã Sự Kiện: {ma_su_kien}")

        # Gọi subprocess để mở form ThongKeSinhVienSuKien.py
        subprocess.Popen([
            "python",
            "D:\\DoAn\\NhanDienKhuonMat\\ThongKeSinhVienSuKien.py",
            ma_su_kien
        ])
    except IndexError:
        print("Vui lòng chọn một dòng hợp lệ!")

def sort_treeview(tree, col):
    global reverse
    try:
        reverse = not reverse
    except:
        reverse = True

    l = [(tree.set(k, col), k) for k in tree.get_children('')]
    l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        tree.move(k, '', index)


# Giao diện chính
root = ctk.CTk()
root.title("Thống kê sự kiện")
root.geometry("1200x600")
root.resizable(True, True)

# Các trường tìm kiếm
ctk.CTkLabel(root, text="Năm học").grid(row=0, column=0, padx=15, pady=5)
combo_namhoc = ctk.CTkComboBox(root, values=["Tất cả", "2024-2025", "2023-2024", "2022-2023", "2020-2021"], state="readonly")
combo_namhoc.grid(row=0, column=1, padx=10, pady=5)
combo_namhoc.set("Tất cả")

ctk.CTkLabel(root, text="Học kì").grid(row=0, column=2, padx=10, pady=5)
combo_hocki = ctk.CTkComboBox(root, values=["Tất cả", "Học kì I", "Học kì II"], state="readonly")
combo_hocki.grid(row=0, column=3, padx=10, pady=5)
combo_hocki.set("Tất cả")

ctk.CTkLabel(root, text="Vị trí").grid(row=1, column=0, padx=10, pady=5)
combo_vitri = ctk.CTkComboBox(root, values=["Tất cả", "Tòa A", "Tòa B", "Tòa C", "Tòa D", "Tòa F", "Thư viện"], state="readonly")
combo_vitri.grid(row=1, column=1, padx=10, pady=5)
combo_vitri.set("Tất cả")

ctk.CTkLabel(root, text="Từ ngày").grid(row=1, column=2, padx=10, pady=5)
entry_tungay = DateEntry(root, date_pattern="dd/mm/yyyy")
entry_tungay.set_date(datetime.now() - timedelta(days=30))
entry_tungay.grid(row=1, column=3, padx=10, pady=5)

ctk.CTkLabel(root, text="Đến ngày").grid(row=1, column=4, padx=10, pady=5)
entry_denngay = DateEntry(root, date_pattern="dd/mm/yyyy")
entry_denngay.set_date(datetime.now())
entry_denngay.grid(row=1, column=5, padx=10, pady=5)

ctk.CTkLabel(root, text="Mã sự kiện").grid(row=2, column=0, padx=10, pady=5)
entry_mask = ctk.CTkEntry(root)
entry_mask.grid(row=2, column=1, padx=10, pady=5)

ctk.CTkLabel(root, text="Trạng thái").grid(row=2, column=2, padx=10, pady=5)
combo_trangthai = ctk.CTkComboBox(root, values=["Tất cả", "Đang diễn ra", "Đã kết thúc"], state="readonly")
combo_trangthai.grid(row=2, column=3, padx=10, pady=5)
combo_trangthai.set("Tất cả")

# Nút tìm kiếm và xuất Excel
button_tim_kiem = ctk.CTkButton(root, text="Tìm kiếm", command=tim_kiem)
button_tim_kiem.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

button_export = ctk.CTkButton(root, text="Xuất ra Excel", command=export_to_excel)
button_export.grid(row=3, column=2, columnspan=2, pady=10, padx=10, sticky="ew")

# Treeview để hiển thị kết quả
columns = ["STT", "Mã Sự Kiện", "Tên Sự Kiện", "Ngày Tổ Chức", "Vị Trí", "Học Kì",
           "Thời Gian Bắt Đầu", "Thời Gian Kết Thúc", "Số Lượng Tham Gia", "Số Lượng Có Mặt", "Trạng Thái"]

tree = ttk.Treeview(root, columns=columns, show="headings")
tree.grid(row=4, column=0, columnspan=6, padx=10, pady=10, sticky="nsew")

# Thêm header
for col in columns:
    tree.heading(col, text=col, command=lambda c=col: sort_treeview(tree, c))

# Điều chỉnh kích thước cột
for col in columns:
    tree.column(col, width=120, anchor="center")

# Thêm xử lý sự kiện khi nhấp vào dòng
tree.bind("<Double-1>", on_item_click)

# Cập nhật dữ liệu
load_data()

# Chạy giao diện chính
root.mainloop()