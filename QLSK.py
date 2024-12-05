import tkinter as tk
from tkinter import ttk, messagebox
import pymongo
from datetime import datetime
from tkcalendar import DateEntry

# Cấu hình cơ sở dữ liệu
MONGO_URI = "mongodb+srv://scjan123:vgbyostAaTl3Uttq@cluster0.aahzt.mongodb.net/"
DATABASE_NAME = "nhandienkhuonmat"
COLLECTION_NAME = "sukien"

# Biến toàn cục
client = None
db = None
collection = None

def connect_to_mongodb():
    global client, db, collection
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        return True
    except pymongo.errors.ConnectionFailure as e:
        messagebox.showerror("Lỗi kết nối", f"Không thể kết nối đến MongoDB: {e}")
        return False

def disconnect_from_mongodb():
    global client
    if client:
        client.close()

def load_events():
    try:
        return list(collection.find({}))
    except pymongo.errors.PyMongoError as e:
        messagebox.showerror("Lỗi truy vấn", f"Lỗi khi lấy dữ liệu từ MongoDB: {e}")
        return []

def validate_dates(ngaytochuc, ngayketthuc):
    today = datetime.now()
    try:
        ngaytochuc_date = datetime.strptime(ngaytochuc, "%Y-%m-%d")
        ngayketthuc_date = datetime.strptime(ngayketthuc, "%Y-%m-%d")
        if ngaytochuc_date < today or ngayketthuc_date < today:
            raise ValueError("Ngày bắt đầu và ngày kết thúc phải lớn hơn hoặc bằng ngày hiện tại.")
        if ngaytochuc_date > ngayketthuc_date:
            raise ValueError("Ngày bắt đầu không được sau ngày kết thúc.")
    except ValueError as e:
        raise ValueError(f"Lỗi ngày tháng: {e}")

def create_fullscreen_window(window):
    window.state("zoomed")
    window.protocol("WM_DELETE_WINDOW", lambda: window.destroy())
# Xem thông tin chi tiết sự kiện
def view_event_details():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Lỗi", "Vui lòng chọn một sự kiện để xem chi tiết.")
        return

    event = tree.item(selected_item[0])["values"]
    event_data = collection.find_one({"mask": event[0]})

    detail_window = tk.Toplevel(root)
    detail_window.title("Thông tin chi tiết sự kiện")
    create_fullscreen_window(detail_window)

    # Header thông tin sự kiện
    header_frame = tk.Frame(detail_window, padx=20, pady=10)
    header_frame.pack(fill=tk.BOTH)

    tk.Label(header_frame, text="Thông tin sự kiện", font=("Arial", 20, "bold"), anchor="center").pack()

    info_labels = {
        "Mã sự kiện": event_data.get("mask", ""),
        "Tên sự kiện": event_data.get("tensk", ""),
        "Ngày tổ chức": event_data.get("ngaytochuc", ""),
        "Thời gian bắt đầu": event_data.get("tgianbatdau", ""),
        "Ngày kết thúc": event_data.get("ngayketthuc", ""),
        "Thời gian kết thúc": event_data.get("tgianketthuc", ""),
        "Số lượng tham gia": event_data.get("slthamgia", 0),
        "Số lượng có mặt": event_data.get("slcomat", 0),
        "Trạng thái": event_data.get("trangthai", "Chưa rõ")
    }

    for label, value in info_labels.items():
        frame = tk.Frame(header_frame)
        frame.pack(fill=tk.X, pady=5)
        tk.Label(frame, text=f"{label}:", font=("Arial", 14), anchor="w", width=20).pack(side=tk.LEFT)
        tk.Label(frame, text=str(value), font=("Arial", 14), anchor="w").pack(side=tk.LEFT)

    # Danh sách sinh viên tham gia
    student_frame = tk.Frame(detail_window, padx=20, pady=10)
    student_frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(student_frame, text="Danh sách sinh viên tham gia", font=("Arial", 16, "bold"), anchor="center").pack()

    student_tree = ttk.Treeview(student_frame, columns=("MSSV", "Họ tên", "Lớp", "Ngành", "Check-in", "Check-out"), show="headings")
    student_tree.pack(fill=tk.BOTH, expand=True)

    student_tree.heading("MSSV", text="MSSV")
    student_tree.heading("Họ tên", text="Họ tên")
    student_tree.heading("Lớp", text="Lớp")
    student_tree.heading("Ngành", text="Ngành")
    student_tree.heading("Check-in", text="Thời gian check-in")
    student_tree.heading("Check-out", text="Thời gian check-out")

    student_tree.column("MSSV", width=100, anchor="center")
    student_tree.column("Họ tên", width=200, anchor="w")
    student_tree.column("Lớp", width=100, anchor="center")
    student_tree.column("Ngành", width=200, anchor="w")
    student_tree.column("Check-in", width=150, anchor="center")
    student_tree.column("Check-out", width=150, anchor="center")

    # Hiển thị danh sách sinh viên
    for student in event_data.get("dssinhvien_thamgia", []):
        student_tree.insert("", "end", values=(
            student.get("mssv", ""),
            student.get("hoten", ""),
            student.get("lop", ""),
            student.get("nganh", ""),
            student.get("tgiancheck_in", "Chưa check-in"),
            student.get("tgiancheck_out", "Chưa check-out")
        ))

    # Nút thoát
    tk.Button(detail_window, text="Đóng", font=("Arial", 14), command=detail_window.destroy).pack(pady=10)

# Thêm sự kiện
def add_event():
    def save_event():
        try:
            # Thu thập và xử lý dữ liệu từ các trường
            event_data = {
                "mask": fields["mask"].get().strip(),
                "tensk": fields["tensk"].get().strip(),
                "slthamgia": int(fields["slthamgia"].get().strip()) if fields["slthamgia"].get().strip() else 0,
                "slcomat": int(fields["slcomat"].get().strip()) if fields["slcomat"].get().strip() else 0,
                "hocki": fields["hocki"].get().strip(),
                "namhoc": fields["namhoc"].get().strip(),
                "vitri": fields["vitri"].get().strip(),
                "ngaytochuc": fields["Ngày tổ chức"].get_date().strftime("%Y-%m-%d"),
                "ngayketthuc": fields["Ngày kết thúc"].get_date().strftime("%Y-%m-%d"),
                "tgianbatdau": f"{fields['Giờ bắt đầu'].get()}:{fields['Phút bắt đầu'].get()}",
                "tgianketthuc": f"{fields['Giờ kết thúc'].get()}:{fields['Phút kết thúc'].get()}",
                "trangthai": "Chưa diễn ra",
                "dssinhvien_thamgia": []
            }

            # Kiểm tra dữ liệu đầu vào
            if not event_data["mask"] or not event_data["tensk"]:
                raise ValueError("Mã sự kiện và tên sự kiện không được để trống.")
            if collection.find_one({"mask": event_data["mask"]}):
                raise ValueError("Mã sự kiện đã tồn tại.")
            validate_dates(event_data["ngaytochuc"], event_data["ngayketthuc"])

            # Chèn dữ liệu vào MongoDB
            collection.insert_one(event_data)
            refresh_table()
            messagebox.showinfo("Thành công", "Thêm sự kiện thành công!")
            add_window.destroy()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))
        except pymongo.errors.PyMongoError as e:
            messagebox.showerror("Lỗi", f"Lỗi cơ sở dữ liệu: {e}")

    add_window = tk.Toplevel(root)
    add_window.title("Thêm sự kiện mới")
    create_fullscreen_window(add_window)

    container = tk.Frame(add_window, padx=20, pady=20)
    container.pack(fill=tk.BOTH, expand=True)

    fields = {
        "mask": tk.StringVar(),
        "tensk": tk.StringVar(),
        "slthamgia": tk.StringVar(),
        "slcomat": tk.StringVar(),
        "hocki": tk.StringVar(),
        "namhoc": tk.StringVar(),
        "vitri": tk.StringVar()
    }

    for i, (label, var) in enumerate(fields.items()):
        tk.Label(container, text=label.capitalize(), font=("Arial", 14), anchor="w").grid(row=i, column=0, sticky="w", pady=5)
        tk.Entry(container, textvariable=var, font=("Arial", 14)).grid(row=i, column=1, sticky="ew", pady=5)

    # Thêm Date Picker và các trường thời gian
    tk.Label(container, text="Ngày tổ chức", font=("Arial", 14), anchor="w").grid(row=len(fields), column=0, sticky="w", pady=5)
    fields["Ngày tổ chức"] = DateEntry(container, date_pattern="yyyy-MM-dd", font=("Arial", 14))
    fields["Ngày tổ chức"].grid(row=len(fields), column=1, sticky="ew", pady=5)

    tk.Label(container, text="Ngày kết thúc", font=("Arial", 14), anchor="w").grid(row=len(fields) + 1, column=0, sticky="w", pady=5)
    fields["Ngày kết thúc"] = DateEntry(container, date_pattern="yyyy-MM-dd", font=("Arial", 14))
    fields["Ngày kết thúc"].grid(row=len(fields) + 1, column=1, sticky="ew", pady=5)

    time_frame = tk.Frame(container)
    time_frame.grid(row=len(fields) + 2, column=0, columnspan=2, sticky="ew", pady=10)

    tk.Label(time_frame, text="Thời gian bắt đầu", font=("Arial", 14), anchor="w").grid(row=0, column=0, pady=5)
    fields["Giờ bắt đầu"] = ttk.Combobox(time_frame, values=[f"{i:02d}" for i in range(24)], width=5, font=("Arial", 14))
    fields["Giờ bắt đầu"].grid(row=0, column=1, padx=5)
    fields["Phút bắt đầu"] = ttk.Combobox(time_frame, values=[f"{i:02d}" for i in range(0, 60, 5)], width=5, font=("Arial", 14))
    fields["Phút bắt đầu"].grid(row=0, column=2, padx=5)

    tk.Label(time_frame, text="Thời gian kết thúc", font=("Arial", 14), anchor="w").grid(row=1, column=0, pady=5)
    fields["Giờ kết thúc"] = ttk.Combobox(time_frame, values=[f"{i:02d}" for i in range(24)], width=5, font=("Arial", 14))
    fields["Giờ kết thúc"].grid(row=1, column=1, padx=5)
    fields["Phút kết thúc"] = ttk.Combobox(time_frame, values=[f"{i:02d}" for i in range(0, 60, 5)], width=5, font=("Arial", 14))
    fields["Phút kết thúc"].grid(row=1, column=2, padx=5)

    container.grid_columnconfigure(1, weight=1)
    tk.Button(add_window, text="Lưu", font=("Arial", 14), command=save_event).pack(pady=10)


# Xóa sự kiện
def delete_event():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Lỗi", "Vui lòng chọn một sự kiện để xóa.")
        return

    event = tree.item(selected_item[0])["values"]
    if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa sự kiện '{event[1]}' không?"):
        try:
            collection.delete_one({"mask": event[0]})
            refresh_table()
            messagebox.showinfo("Thành công", "Xóa sự kiện thành công!")
        except pymongo.errors.PyMongoError as e:
            messagebox.showerror("Lỗi", f"Lỗi cơ sở dữ liệu: {e}")

# Sửa sự kiện
def edit_event():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Lỗi", "Vui lòng chọn một sự kiện để sửa.")
        return

    event = tree.item(selected_item[0])["values"]
    event_data = collection.find_one({"mask": event[0]})

    def save_edit():
        try:
            # Thu thập và xử lý dữ liệu từ các trường
            updated_data = {
                "mask": event_data["mask"],  # Không thay đổi mã sự kiện
                "tensk": fields["tensk"].get().strip(),
                "slthamgia": int(fields["slthamgia"].get().strip()) if fields["slthamgia"].get().strip() else 0,
                "slcomat": int(fields["slcomat"].get().strip()) if fields["slcomat"].get().strip() else 0,
                "hocki": fields["hocki"].get().strip(),
                "namhoc": fields["namhoc"].get().strip(),
                "vitri": fields["vitri"].get().strip(),
                "ngaytochuc": fields["Ngày tổ chức"].get_date().strftime("%Y-%m-%d"),
                "ngayketthuc": fields["Ngày kết thúc"].get_date().strftime("%Y-%m-%d"),
                "tgianbatdau": f"{fields['Giờ bắt đầu'].get()}:{fields['Phút bắt đầu'].get()}",
                "tgianketthuc": f"{fields['Giờ kết thúc'].get()}:{fields['Phút kết thúc'].get()}",
                "trangthai": event_data.get("trangthai", "Chưa diễn ra"),
                "dssinhvien_thamgia": event_data.get("dssinhvien_thamgia", [])
            }

            # Kiểm tra dữ liệu đầu vào
            if not updated_data["tensk"]:
                raise ValueError("Tên sự kiện không được để trống.")
            validate_dates(updated_data["ngaytochuc"], updated_data["ngayketthuc"])

            # Cập nhật dữ liệu vào MongoDB
            collection.update_one({"mask": event_data["mask"]}, {"$set": updated_data})
            refresh_table()
            messagebox.showinfo("Thành công", "Sửa sự kiện thành công!")
            edit_window.destroy()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))
        except pymongo.errors.PyMongoError as e:
            messagebox.showerror("Lỗi", f"Lỗi cơ sở dữ liệu: {e}")

    edit_window = tk.Toplevel(root)
    edit_window.title("Sửa sự kiện")
    create_fullscreen_window(edit_window)

    container = tk.Frame(edit_window, padx=20, pady=20)
    container.pack(fill=tk.BOTH, expand=True)

    # Định nghĩa các trường
    fields = {
        "mask": tk.StringVar(value=event_data.get("mask", "")),
        "tensk": tk.StringVar(value=event_data.get("tensk", "")),
        "slthamgia": tk.StringVar(value=str(event_data.get("slthamgia", ""))),
        "slcomat": tk.StringVar(value=str(event_data.get("slcomat", ""))),
        "hocki": tk.StringVar(value=event_data.get("hocki", "")),
        "namhoc": tk.StringVar(value=event_data.get("namhoc", "")),
        "vitri": tk.StringVar(value=event_data.get("vitri", "")),
    }

    # Tạo các trường nhập liệu
    for i, (label, var) in enumerate(fields.items()):
        tk.Label(container, text=label.capitalize(), font=("Arial", 14), anchor="w").grid(row=i, column=0, sticky="w", pady=5)
        tk.Entry(container, textvariable=var, font=("Arial", 14)).grid(row=i, column=1, sticky="ew", pady=5)

    # Thêm Date Picker
    tk.Label(container, text="Ngày tổ chức", font=("Arial", 14), anchor="w").grid(row=len(fields), column=0, sticky="w", pady=5)
    fields["Ngày tổ chức"] = DateEntry(container, date_pattern="yyyy-MM-dd", font=("Arial", 14))
    fields["Ngày tổ chức"].set_date(event_data.get("ngaytochuc", ""))
    fields["Ngày tổ chức"].grid(row=len(fields), column=1, sticky="ew", pady=5)

    tk.Label(container, text="Ngày kết thúc", font=("Arial", 14), anchor="w").grid(row=len(fields) + 1, column=0, sticky="w", pady=5)
    fields["Ngày kết thúc"] = DateEntry(container, date_pattern="yyyy-MM-dd", font=("Arial", 14))
    fields["Ngày kết thúc"].set_date(event_data.get("ngayketthuc", ""))
    fields["Ngày kết thúc"].grid(row=len(fields) + 1, column=1, sticky="ew", pady=5)

    # Thêm các trường thời gian
    time_frame = tk.Frame(container)
    time_frame.grid(row=len(fields) + 2, column=0, columnspan=2, sticky="ew", pady=10)

    tk.Label(time_frame, text="Thời gian bắt đầu (HH:MM)", font=("Arial", 14), anchor="w").grid(row=0, column=0, pady=5)
    fields["Giờ bắt đầu"] = ttk.Combobox(time_frame, values=[f"{i:02d}" for i in range(24)], width=5, font=("Arial", 14))
    fields["Giờ bắt đầu"].grid(row=0, column=1, padx=5)
    fields["Giờ bắt đầu"].set(event_data.get("tgianbatdau", "").split(":")[0])  # Giờ bắt đầu từ dữ liệu cũ

    fields["Phút bắt đầu"] = ttk.Combobox(time_frame, values=[f"{i:02d}" for i in range(0, 60, 5)], width=5, font=("Arial", 14))
    fields["Phút bắt đầu"].grid(row=0, column=2, padx=5)
    fields["Phút bắt đầu"].set(event_data.get("tgianbatdau", "").split(":")[1])  # Phút bắt đầu từ dữ liệu cũ

    tk.Label(time_frame, text="Thời gian kết thúc (HH:MM)", font=("Arial", 14), anchor="w").grid(row=1, column=0, pady=5)
    fields["Giờ kết thúc"] = ttk.Combobox(time_frame, values=[f"{i:02d}" for i in range(24)], width=5, font=("Arial", 14))
    fields["Giờ kết thúc"].grid(row=1, column=1, padx=5)
    fields["Giờ kết thúc"].set(event_data.get("tgianketthuc", "").split(":")[0])  # Giờ kết thúc từ dữ liệu cũ

    fields["Phút kết thúc"] = ttk.Combobox(time_frame, values=[f"{i:02d}" for i in range(0, 60, 5)], width=5, font=("Arial", 14))
    fields["Phút kết thúc"].grid(row=1, column=2, padx=5)
    fields["Phút kết thúc"].set(event_data.get("tgianketthuc", "").split(":")[1])  # Phút kết thúc từ dữ liệu cũ

    container.grid_columnconfigure(1, weight=1)

    tk.Button(edit_window, text="Lưu", font=("Arial", 14), command=save_edit).pack(pady=10)



# Cập nhật danh sách sự kiện
def refresh_table():
    for item in tree.get_children():
        tree.delete(item)

    events = load_events()
    for event in events:
        tree.insert("", tk.END, values=(event["mask"], event["tensk"], event["trangthai"]))

# Giao diện chính
root = tk.Tk()
root.title("Quản lý sự kiện")
create_fullscreen_window(root)

title_label = tk.Label(root, text="QUẢN LÝ SỰ KIỆN", font=("Arial", 24, "bold"), anchor="center")
title_label.pack(pady=10)

frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True, pady=10)

tree = ttk.Treeview(frame, columns=("mask", "tensk", "trangthai"), show="headings", style="Treeview")
tree.heading("mask", text="Mã sự kiện")
tree.heading("tensk", text="Tên sự kiện")
tree.heading("trangthai", text="Trạng thái")
tree.pack(fill=tk.BOTH, expand=True)

button_frame = tk.Frame(root)
button_frame.pack(pady=20)

ttk.Button(button_frame, text="Thêm sự kiện", command=add_event).pack(side=tk.LEFT, padx=10)
ttk.Button(button_frame, text="Xóa sự kiện", command=delete_event).pack(side=tk.LEFT, padx=10)
ttk.Button(button_frame, text="Sửa sự kiện", command=edit_event).pack(side=tk.LEFT, padx=10)
ttk.Button(button_frame, text="Chi tiết sự kiện", command=view_event_details).pack(side=tk.LEFT, padx=10)
ttk.Button(button_frame, text="Thoát", command=root.quit).pack(side=tk.LEFT, padx=10)

if connect_to_mongodb():
    refresh_table()

    root.mainloop()
    disconnect_from_mongodb()
