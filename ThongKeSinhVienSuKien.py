import sys
import pandas as pd
from tkinter import filedialog
from tkinter import Tk, Label, Entry, Button, ttk, messagebox, StringVar
from tkinter.ttk import Combobox
from pymongo import MongoClient



class ThongKeSinhVienSuKien:
    def __init__(self, ma_su_kien):
        self.ma_su_kien = ma_su_kien
        self.root = Tk()
        self.root.title("Thống kê sinh viên sự kiện")
        self.root.geometry("1200x700")

        # MongoDB connection
        self.client = MongoClient("mongodb+srv://scjan123:vgbyostAaTl3Uttq@cluster0.aahzt.mongodb.net/")
        self.db = self.client["nhandienkhuonmat"]  # Cập nhật tên database
        self.collection = self.db["sukien"]   # Cập nhật tên collection

        # Variables
        self.var_mssv = StringVar()
        self.var_hoten = StringVar()
        self.var_khoa = StringVar(value="Tất cả")
        self.var_chuyennganh = StringVar(value="Tất cả")
        self.var_trangthai = StringVar(value="Tất cả")

        # Header
        Label(self.root, text=f"Mã Sự Kiện: {self.ma_su_kien}", font=("Arial", 16)).pack(pady=10)

        # Search Fields
        frame_search = ttk.Frame(self.root)
        frame_search.pack(pady=10, fill="x", padx=10)

        Label(frame_search, text="MSSV:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        Entry(frame_search, textvariable=self.var_mssv, width=20).grid(row=0, column=1, padx=5, pady=5)

        Label(frame_search, text="Họ Tên:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        Entry(frame_search, textvariable=self.var_hoten, width=20).grid(row=0, column=3, padx=5, pady=5)

        Label(frame_search, text="Khoa:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        Combobox(frame_search, textvariable=self.var_khoa, values=[
            "Tất cả", "Khoa Công Nghệ Thông Tin", "Khoa công nghệ thực phẩm",
            "Khoa sinh học và môi trường", "Khoa công nghệ hóa học", "Khoa công nghệ điện - điện tử",
            "Khoa may - thiết kế thời trang", "Khoa công nghệ cơ khí"
        ], state="readonly").grid(row=0, column=5, padx=5, pady=5)

        Label(frame_search, text="Chuyên Ngành:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        Combobox(frame_search, textvariable=self.var_chuyennganh, values=[
            "Tất cả", "Công nghệ thông tin", "An toàn thông tin", "Công nghệ kỹ thuật điện, điện tử",
            "Công nghệ điều khiển và tự động hoá", "Công nghệ kỹ thuật cơ điện tử", "Công nghệ chế tạo máy",
            "Công nghệ kỹ thuật hóa học", "Công nghệ thực phẩm", "Đảm bảo chất lượng & an toàn thực phẩm",
            "Khoa học dinh dưỡng và ẩm thực", "Khoa học nấu ăn", "Công nghệ chế biến thủy sản",
            "Công nghệ sinh học", "Công nghệ kỹ thuật môi trường", "Quản lý tài nguyên và môi trường",
            "Công nghệ dệt may", "Quản trị dịch vụ du lịch lữ hành", "Quản trị dịch vụ nhà hàng ăn uống",
            "Quản trị khách sạn", "Kế toán", "Tài chính ngân hàng", "Công nghệ tài chính",
            "Quản trị kinh doanh", "Marketing", "Kinh doanh quốc tế", "Thương mại điện tử",
            "Ngôn ngữ Anh", "Ngôn ngữ Trung Quốc", "Luật kinh tế", "Kỹ thuật nhiệt", "Khoa học dữ liệu",
            "Kinh doanh may, thời trang", "Quản trị kinh doanh thực phẩm", "Logistics và chuỗi cung ứng"
        ], state="readonly").grid(row=1, column=1, padx=5, pady=5)

        Label(frame_search, text="Trạng Thái:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        Combobox(frame_search, textvariable=self.var_trangthai, values=[
            "Tất cả", "Chưa Check-out", "Không điểm danh", "Đã điểm danh"
        ], state="readonly").grid(row=1, column=3, padx=5, pady=5)

        Button(frame_search, text="Tìm Kiếm", command=self.search).grid(row=1, column=4, padx=5, pady=5)
        Button(frame_search, text="In Danh Sách", command=self.export_list).grid(row=1, column=5, padx=5, pady=5)
        Button(frame_search, text="Thống Kê Lưu Lượng", command=self.statistical_summary).grid(row=1, column=6, padx=5,                                                                                           pady=5)
        Button(frame_search, text="Trở Về", command=self.root.destroy).grid(row=1, column=7, padx=5, pady=5)

        # Treeview
        self.tree = ttk.Treeview(self.root, columns=("STT", "MSSV", "Họ Tên", "Lớp", "Chuyên Ngành",
                                                     "Check In", "Check Out", "Trạng Thái"), show="headings")
        self.tree.heading("STT", text="STT")
        self.tree.heading("MSSV", text="MSSV")
        self.tree.heading("Họ Tên", text="Họ Tên")
        self.tree.heading("Lớp", text="Lớp")
        self.tree.heading("Chuyên Ngành", text="Chuyên Ngành")
        self.tree.heading("Check In", text="Check In")
        self.tree.heading("Check Out", text="Check Out")
        self.tree.heading("Trạng Thái", text="Trạng Thái")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Resize handling
        self.root.bind("<Configure>", self.on_resize)
        # Load data automatically
        self.load_data()

        self.root.mainloop()

    def load_data(self):
        """Load data from MongoDB."""
        try:
            event = self.collection.find_one({"mask": self.ma_su_kien})
            if not event:
                messagebox.showerror("Lỗi", "Không tìm thấy sự kiện")
                return

            self.populate_tree(event.get("dssinhvien_thamgia", []))

        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {str(e)}")

    def search(self):
        """Search and filter data based on user input."""
        try:
            # Lấy dữ liệu sự kiện từ MongoDB
            event = self.collection.find_one({"mask": self.ma_su_kien})
            if not event:
                messagebox.showerror("Lỗi", "Không tìm thấy sự kiện")
                return

            # Lấy danh sách sinh viên từ dữ liệu sự kiện
            students = event.get("dssinhvien_thamgia", [])

            # Lọc dữ liệu theo các điều kiện tìm kiếm
            filtered_students = []
            for sv in students:
                # Điều kiện MSSV
                if self.var_mssv.get() and self.var_mssv.get() not in sv.get("mssv", ""):
                    continue
                # Điều kiện Họ Tên
                if self.var_hoten.get() and self.var_hoten.get().lower() not in sv.get("hoten", "").lower():
                    continue
                # Điều kiện Khoa
                if self.var_khoa.get() != "Tất cả" and self.var_khoa.get() != sv.get("khoa", "Không rõ"):
                    continue
                # Điều kiện Chuyên Ngành
                if self.var_chuyennganh.get() != "Tất cả" and self.var_chuyennganh.get() != sv.get("nganh", "Không rõ"):
                    continue
                # Điều kiện Trạng Thái
                if self.var_trangthai.get() != "Tất cả" and self.var_trangthai.get() != sv.get("trangthai", "Không rõ"):
                    continue

                filtered_students.append(sv)

            # Hiển thị kết quả lọc lên TreeView
            self.populate_tree(filtered_students)

            # Thông báo nếu không có kết quả
            if not filtered_students:
                messagebox.showinfo("Thông báo", "Không tìm thấy kết quả phù hợp.")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {str(e)}")

    def export_list(self):
        """Export the list of students to a file."""
        try:
            # Lấy dữ liệu từ TreeView
            data = []
            for child in self.tree.get_children():
                values = self.tree.item(child, "values")
                data.append(values)

            if not data:
                messagebox.showinfo("Thông báo", "Không có dữ liệu để xuất!")
                return

            # Tạo DataFrame từ dữ liệu
            columns = ["STT", "MSSV", "Họ Tên", "Lớp", "Chuyên Ngành", "Check In", "Check Out", "Trạng Thái"]
            df = pd.DataFrame(data, columns=columns)

            # Hộp thoại chọn nơi lưu trữ
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Chọn nơi lưu trữ và nhập tên file"
            )

            # Nếu người dùng hủy hộp thoại, không làm gì cả
            if not file_path:
                return

            # Ghi DataFrame ra file Excel
            df.to_excel(file_path, index=False)

            # Thông báo thành công
            messagebox.showinfo("Thành công", f"Danh sách đã được xuất ra file: {file_path}")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi xuất file: {str(e)}")

    def populate_tree(self, students):
        """Populate Treeview with student data."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for idx, sv in enumerate(students, start=1):
            self.tree.insert("", "end", values=(
                idx,
                sv.get("mssv", ""),
                sv.get("hoten", ""),
                sv.get("lop", ""),
                sv.get("nganh", ""),
                sv.get("tgiancheck_in", ""),
                sv.get("tgiancheck_out", ""),
                sv.get("trangthai", "Chưa cập nhật")
            ))

    def statistical_summary(self):
        """Show statistical summary."""
        try:
            event = self.collection.find_one({"mask": self.ma_su_kien})
            if not event:
                messagebox.showerror("Lỗi", "Không tìm thấy sự kiện")
                return

            students = event.get("dssinhvien_thamgia", [])
            total = len(students)
            checked_in = len([s for s in students if s.get("trangthai") == "Đã điểm danh"])
            not_checked_in = total - checked_in

            messagebox.showinfo(
                "Thống Kê Lưu Lượng",
                f"Tổng số sinh viên: {total}\n"
                f"Số sinh viên đã điểm danh: {checked_in}\n"
                f"Số sinh viên chưa điểm danh: {not_checked_in}"
            )
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {str(e)}")

    def on_resize(self, event):
        """Adjust layout on resize."""
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

if __name__ == "__main__":
    # Lấy mã sự kiện từ tham số command line
    ma_su_kien = sys.argv[1] if len(sys.argv) > 1 else "12DHTH13"
    ThongKeSinhVienSuKien(ma_su_kien)
