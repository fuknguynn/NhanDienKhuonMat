import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from pymongo import MongoClient
import subprocess

# --- Kết nối MongoDB ---
def connect_to_db():
    client = MongoClient('mongodb+srv://scjan123:vgbyostAaTl3Uttq@cluster0.aahzt.mongodb.net/')
    db = client['nhandienkhuonmat']
    return db

# Lấy dữ liệu sự kiện
def fetch_event_data():
    db = connect_to_db()
    collection = db['sukien']
    data = {}
    for event in collection.find():
        tensk = event.get("tensk", "Không rõ")
        sl_thamgia = event.get("slthamgia", 0)
        sl_comat = int(event.get("slcomat", 0))
        sl_vang = sl_thamgia - sl_comat
        data[tensk] = {"thamgia": sl_thamgia, "comat": sl_comat, "vang": sl_vang}
    return data

# Hiển thị biểu đồ
def display_chart(chart_type="thamgia"):
    data = fetch_event_data()
    events = list(data.keys())
    if chart_type == "thamgia":
        values = [event["thamgia"] for event in data.values()]
        title = "Số lượng tham gia các sự kiện"
        ylabel = "Số lượng tham gia"
    elif chart_type == "comat_vang":
        values_comat = [event["comat"] for event in data.values()]
        values_vang = [event["vang"] for event in data.values()]
        title = "Số lượng có mặt và vắng các sự kiện"
        ylabel = "Số lượng người"
    elif chart_type == "percent":
        values = [
            (event["comat"] / event["thamgia"] * 100 if event["thamgia"] > 0 else 0)
            for event in data.values()
        ]
        title = "Tỉ lệ phần trăm có mặt trong các sự kiện"
        ylabel = "Phần trăm (%)"

    # Clear frame trước khi thêm chart
    for widget in content_frame.winfo_children():
        widget.destroy()

    # Tạo biểu đồ
    fig, ax = plt.subplots(figsize=(7, 5))

    if chart_type == "comat_vang":
        ax.bar(events, values_comat, label="Có mặt", color="green")
        ax.bar(events, values_vang, bottom=values_comat, label="Vắng", color="red")
        ax.legend()
    else:
        ax.bar(events, values, color="skyblue")

    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Tên sự kiện")
    ax.tick_params(axis="x", rotation=45)

    # Tích hợp biểu đồ vào content_frame
    canvas = FigureCanvasTkAgg(fig, master=content_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=ctk.BOTH, expand=True)
    canvas.draw()

# Các hàm thực thi chương trình của các button
def manage_events():
    subprocess.run(["python", r"D:\DoAn\NhanDienKhuonMat\QLSK.py"])

def statistics_events():
    subprocess.run(["python", r"D:\DoAn\NhanDienKhuonMat\ThongKeSuKien.py"])

def get_face_data():
    subprocess.run(["python", r"D:\DoAn\NhanDienKhuonMat\LayDuLieuKhuonMat.py"])

def train_model():
    subprocess.run(["python", r"D:\DoAn\NhanDienKhuonMat\HuanLuyenMoHinh.py"])

def check_in():
    subprocess.run(["python", r"D:\DoAn\NhanDienKhuonMat\Checkin.py"])

def check_out():
    subprocess.run(["python", r"D:\DoAn\NhanDienKhuonMat\Checkout.py"])

# --- Main GUI ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.geometry(f"{1000}x{700}")
root.title("Ứng dụng điểm danh sự kiện bằng khuôn mặt")

# Menu Frame
menu_frame = ctk.CTkFrame(master=root, width=200)
menu_frame.pack(side=ctk.LEFT, fill=ctk.Y)

# Content Frame
content_frame = ctk.CTkFrame(master=root)
content_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True)

# --- Radio Button cho biểu đồ ---
chart_type_var = ctk.StringVar(value="thamgia")

def on_chart_type_change():
    display_chart(chart_type_var.get())

ctk.CTkLabel(menu_frame, text="Chọn loại biểu đồ:").pack(pady=10)
ctk.CTkRadioButton(
    master=menu_frame, text="Số lượng tham gia", variable=chart_type_var, value="thamgia", command=on_chart_type_change
).pack(pady=5, anchor="w")
ctk.CTkRadioButton(
    master=menu_frame, text="Có mặt và vắng", variable=chart_type_var, value="comat_vang", command=on_chart_type_change
).pack(pady=5, anchor="w")
ctk.CTkRadioButton(
    master=menu_frame, text="Tỉ lệ phần trăm có mặt", variable=chart_type_var, value="percent", command=on_chart_type_change
).pack(pady=5, anchor="w")

# --- Các nút chức năng ---
ctk.CTkButton(menu_frame, text="Quản lý Sự Kiện", command=manage_events).pack(pady=10, padx=10, fill=ctk.X)
ctk.CTkButton(menu_frame, text="Thống kê Sự Kiện", command=statistics_events).pack(pady=10, padx=10, fill=ctk.X)
ctk.CTkButton(menu_frame, text="Lấy dữ liệu khuôn mặt", command=get_face_data).pack(pady=10, padx=10, fill=ctk.X)
ctk.CTkButton(menu_frame, text="Huấn luyện mô hình", command=train_model).pack(pady=10, padx=10, fill=ctk.X)
ctk.CTkButton(menu_frame, text="Check-in", command=check_in).pack(pady=10, padx=10, fill=ctk.X)
ctk.CTkButton(menu_frame, text="Check-out", command=check_out).pack(pady=10, padx=10, fill=ctk.X)
ctk.CTkButton(menu_frame, text="Thoát", command=root.destroy).pack(pady=10, padx=10, fill=ctk.X)

# Hiển thị biểu đồ mặc định
display_chart("thamgia")

root.mainloop()
