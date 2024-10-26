import tkinter as tk
from tkinter import ttk
from pymongo import MongoClient

# Kết nối đến MongoDB
client = MongoClient('mongodb+srv://scjan123:vgbyostAaTl3Uttq@cluster0.aahzt.mongodb.net/')  # Thay đổi địa chỉ và port nếu cần
db = client['nhandienkhuonmat1']  # Tên database
collection = db['sukien']  # Tên collection

# Kiểm tra kết nối và in ra một document
event_data = collection.find_one({"mask": "12DHTH13"})  # Thay thế ID chính xác

if event_data:
    print("Kết nối thành công và dữ liệu được tìm thấy:")
    print(event_data)
else:
    print("Không tìm thấy dữ liệu hoặc kết nối thất bại.")

# Hàm lấy dữ liệu sinh viên từ MongoDB
def get_student_data():
    event_data = collection.find_one({"mask": "12DHTH13"})  # Thay ID sự kiện bằng giá trị thực
    if event_data and 'dssinhvien_thamgia' in event_data:
        return event_data['dssinhvien_thamgia']
    return []

# Tạo giao diện với Tkinter
class StudentForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Thông Tin Sinh Viên Tham Gia Sự Kiện")
        self.geometry("700x400")

        # Tiêu đề bảng
        columns = ('mssv', 'hoten', 'lop', 'tgiancheck_in', 'tgiancheck_out', 'trangthai')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')

        # Đặt tiêu đề cột
        self.tree.heading('mssv', text='MSSV')
        self.tree.heading('hoten', text='Họ Tên')
        self.tree.heading('lop', text='Lớp')
        self.tree.heading('tgiancheck_in', text='Check-in')
        self.tree.heading('tgiancheck_out', text='Check-out')
        self.tree.heading('trangthai', text='Trạng Thái')

        # Kích thước cột
        self.tree.column('mssv', width=100)
        self.tree.column('hoten', width=200)
        self.tree.column('lop', width=100)
        self.tree.column('tgiancheck_in', width=100)
        self.tree.column('tgiancheck_out', width=100)
        self.tree.column('trangthai', width=100)

        # Đặt bảng vào giao diện
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Lấy dữ liệu và hiển thị
        self.load_data()

    def load_data(self):
        student_data = get_student_data()

        # Xóa các dòng cũ (nếu có)
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Thêm dữ liệu mới vào bảng
        for student in student_data:
            self.tree.insert('', tk.END, values=(
                student.get('mssv', ''),
                student.get('hoten', ''),
                student.get('lop', ''),
                student.get('tgiancheck_in', 'Chưa check-in'),
                student.get('tgiancheck_out', 'Chưa check-out'),
                student.get('trangthai', 'Chưa cập nhật')
            ))

# Chạy ứng dụng Tkinter
if __name__ == "__main__":
    app = StudentForm()
    app.mainloop()
