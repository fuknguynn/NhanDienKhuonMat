import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from datetime import datetime
from pymongo import MongoClient
# import csv # Không cần sử dụng thư viện csv nữa
from tkcalendar import Calendar

# Kết nối đến MongoDB
client = MongoClient('mongodb://localhost:27017/')  
db = client['nhandienkhuonmat']  # Tên database
collection = db['sukien']  # Tên collection

# Kiểm tra kết nối MongoDB
try:
    client.admin.command('ping')
    print("Kết nối MongoDB thành công!")
except Exception as e:
    print(f"Lỗi kết nối MongoDB: {e}")

# Hàm tạo sự kiện
def create_event():
    mask = mask_entry.get()
    tensk = tensk_entry.get()

    # Kiểm tra dữ liệu đầu vào
    if not mask or not tensk:
        tk.messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")
        return

    try:
        slthamgia = int(slthamgia_entry.get())  # Kiểm tra nếu slthamgia có phải là số
    except ValueError:
        tk.messagebox.showerror("Lỗi", "Số lượng sinh viên tham gia phải là số nguyên.")
        return

    # Kiểm tra thời gian bắt đầu và kết thúc
    try:
        # Chuyển ngày từ chuỗi thành đối tượng datetime.date
        thoigianbd_date = datetime.strptime(thoigianbd_calendar.get_date(), "%m/%d/%y").date()
        thoigiankt_date = datetime.strptime(thoigiankt_calendar.get_date(), "%m/%d/%y").date()

        # Chuyển thời gian từ chuỗi thành đối tượng datetime.time
        thoigianbd_time_obj = datetime.strptime(thoigianbd_time.get(), "%H:%M").time()
        thoigiankt_time_obj = datetime.strptime(thoigiankt_time.get(), "%H:%M").time()

        # Kết hợp ngày và giờ thành datetime
        thoigianbd_datetime = datetime.combine(thoigianbd_date, thoigianbd_time_obj)
        thoigiankt_datetime = datetime.combine(thoigiankt_date, thoigiankt_time_obj)
    except Exception as e:
        tk.messagebox.showerror("Lỗi", f"Lỗi khi xử lý thời gian: {e}")
        return

    if thoigiankt_datetime <= thoigianbd_datetime:
        tk.messagebox.showerror("Lỗi", "Thời gian kết thúc phải sau thời gian bắt đầu.")
        return

    # Xử lý danh sách sinh viên
    dssinhvien_thamgia = []
    for student_data in student_listbox.get(0, tk.END):
        try:
            mssv, hoten, lop, nganh = student_data.split("|")  # Giả sử dữ liệu trong listbox được lưu theo format "mssv|hoten|lop|nganh"
            dssinhvien_thamgia.append({
                "mssv": mssv.strip(),
                "hoten": hoten.strip(),
                "lop": lop.strip(),
                "nganh": nganh.strip(),
                "tgiancheck_in": None,
                "tgiancheck_out": None,
                "trangthai_chkin": None,
                "trangthai_chkout": None,
                "trangthai": None
            })
        except Exception as e:
            tk.messagebox.showerror("Lỗi", f"Lỗi khi xử lý sinh viên: {e}")
            return

    # Tạo dữ liệu sự kiện
    new_event = {
        "mask": mask,
        "tensk": tensk,
        "slthamgia": slthamgia,
        "slcomat": 0,  # Khởi tạo số lượng sinh viên có mặt là 0
        "trangthai": "Chưa diễn ra",
        "thoigianbd": thoigianbd_datetime,
        "thoigiankt": thoigiankt_datetime,
        "dssinhvien_thamgia": dssinhvien_thamgia
    }

    # Thêm sự kiện vào MongoDB (với xử lý lỗi)
    try:
        collection.insert_one(new_event)
        tk.messagebox.showinfo("Thành công", f"Sự kiện {tensk} đã được tạo thành công!")
    except Exception as e:
        tk.messagebox.showerror("Lỗi", f"Lỗi khi thêm sự kiện vào database: {e}")

# Hàm import danh sách sinh viên từ file txt
def import_student_list():
    file_path = filedialog.askopenfilename(
        initialdir="/",
        title="Chọn file TXT",
        filetypes=(("TXT files", "*.txt"), ("all files", "*.*"))
    )
    if file_path:
        student_listbox.delete(0, tk.END)
        try:
            with open(file_path, 'r', encoding='utf-8') as txtfile:
                # Bỏ qua dòng đầu tiên (dòng header)
                next(txtfile)
                for line in txtfile:
                    # Loại bỏ các ký tự khoảng trắng ở đầu và cuối dòng
                    line = line.strip()
                    # Tách dữ liệu từ dòng, sử dụng dấu phẩy "," làm dấu phân cách
                    mssv, hoten, lop, nganh = line.split(",")  
                    # Loại bỏ các dấu ngoặc kép
                    mssv = mssv.replace('"', '')
                    hoten = hoten.replace('"', '')
                    lop = lop.replace('"', '')
                    nganh = nganh.replace('"', '')
                    # Tạo chuỗi student_data
                    student_data = f"{mssv}|{hoten}|{lop}|{nganh}"
                    # Thêm dữ liệu vào listbox
                    student_listbox.insert(tk.END, student_data)
                    # In dữ liệu ra terminal
                    print(f"MSSV: {mssv}, Họ tên: {hoten}, Lớp: {lop}, Ngành: {nganh}")  
        except Exception as e:
            tk.messagebox.showerror("Lỗi", f"Lỗi khi đọc file TXT: {e}")

# Tạo giao diện với Tkinter
root = tk.Tk()
root.title("Tạo Sự Kiện")
root.geometry("850x600")  # Điều chỉnh kích thước cửa sổ

# Tạo các nhãn và hộp nhập liệu
mask_label = tk.Label(root, text="Mã sự kiện:")
mask_label.grid(row=0, column=0, padx=5, pady=5)
mask_entry = tk.Entry(root)
mask_entry.grid(row=0, column=1, padx=5, pady=5)

tensk_label = tk.Label(root, text="Tên sự kiện:")
tensk_label.grid(row=0, column=2, padx=5, pady=5)
tensk_entry = tk.Entry(root)
tensk_entry.grid(row=0, column=3, padx=5, pady=5)

slthamgia_label = tk.Label(root, text="Số lượng sinh viên tham gia:")
slthamgia_label.grid(row=1, column=0, padx=5, pady=5)
slthamgia_entry = tk.Entry(root)
slthamgia_entry.grid(row=1, column=1, padx=5, pady=5)

# Tạo các widget cho ngày và giờ bắt đầu
thoigianbd_label = tk.Label(root, text="Thời gian bắt đầu:")
thoigianbd_label.grid(row=2, column=0, padx=5, pady=5)

thoigianbd_calendar = Calendar(root, selectmode='day', year=2024, month=10, day=1)
thoigianbd_calendar.grid(row=3, column=0, padx=5, pady=5)

thoigianbd_time = ttk.Combobox(root, values=[f"{hour:02d}:{minute:02d}" for hour in range(24) for minute in range(0, 60, 30)])
thoigianbd_time.current(0)
thoigianbd_time.grid(row=3, column=1, padx=5, pady=5)

# Tạo các widget cho ngày và giờ kết thúc
thoigiankt_label = tk.Label(root, text="Thời gian kết thúc:")
thoigiankt_label.grid(row=2, column=2, padx=5, pady=5)

thoigiankt_calendar = Calendar(root, selectmode='day', year=2024, month=10, day=1)
thoigiankt_calendar.grid(row=3, column=2, padx=5, pady=5)

thoigiankt_time = ttk.Combobox(root, values=[f"{hour:02d}:{minute:02d}" for hour in range(24) for minute in range(0, 60, 30)])
thoigiankt_time.current(0)
thoigiankt_time.grid(row=3, column=3, padx=5, pady=5)

# Tạo listbox để hiển thị danh sách sinh viên
student_listbox_label = tk.Label(root, text="Danh sách sinh viên:")
student_listbox_label.grid(row=4, column=0, columnspan=4, padx=5, pady=5)
student_listbox = tk.Listbox(root, width=50, height=10)
student_listbox.grid(row=5, column=0, columnspan=4, padx=5, pady=5)

# Tạo nút import file CSV 
import_button = tk.Button(root, text="Import danh sách", command=import_student_list)
import_button.grid(row=6, column=0, columnspan=4, padx=5, pady=10)

# Tạo nút hoàn thành
create_button = tk.Button(root, text="Hoàn thành", command=create_event, width=15)  # Điều chỉnh kích thước nút
create_button.grid(row=7, column=0, columnspan=4, padx=5, pady=10)

root.mainloop()