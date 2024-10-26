import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from pymongo import MongoClient
import csv
from datetime import datetime
from keras_facenet import FaceNet
from mtcnn import MTCNN
from scipy.spatial.distance import cosine
import threading
import pygame
import time

# Kết nối tới MongoDB
client = MongoClient('mongodb+srv://scjan123:vgbyostAaTl3Uttq@cluster0.aahzt.mongodb.net/')
db = client['nhandienkhuonmat1']
students = db['sinhvien']
events = db['sukien']
# Load embedding vectors từ file
student_embeddings = np.load('embeddings.npy', allow_pickle=True).item()

# Khởi tạo mô hình FaceNet và MTCNN
embedder = FaceNet()
detector = MTCNN()

# Biến toàn cục cho treeview và danh sách đã điểm danh
treeview = None
recognized_students = set()
attendance_data = []

def create_embedding(face_img):
    """Tạo embedding vector từ ảnh khuôn mặt."""
    face_img_resized = cv2.resize(face_img, (160, 160))
    return embedder.embeddings([face_img_resized])[0]

def update_attendance(mssv, time_check_in, trang_thai):
    """Cập nhật thông tin điểm danh vào cơ sở dữ liệu."""
    result = db.sukien.update_one(
        {'mask': '12DHTH13'},
        {
            '$set': {
                f'dssinhvien_thamgia.$[elem].tgiancheck_in': time_check_in,
                f'dssinhvien_thamgia.$[elem].trangthai_chkin': trang_thai
            }
        },
        array_filters=[{'elem.mssv': mssv}]
    )
    if result.modified_count > 0:
        print("Cập nhật thành công")
    else:
        print("Không tìm thấy hoặc không cần cập nhật")

# Hàm cập nhật thời gian hiện tại
def update_time():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    label_time.config(text=f"{current_time}")
    root.after(1000, update_time)


# Hàm load thông tin từ MSSV và cập nhật label
# Biến để lưu thời gian hiển thị và khuôn mặt đang hiển thị
display_timer = None
current_mssv = None

def load_data_by_mssv(mssv):
    global recognized_students, label_name, label_mssv, student_image_label, display_timer, current_mssv

    # Kiểm tra nếu khuôn mặt mới và khác mssv đang hiển thị
    if mssv in recognized_students and mssv == current_mssv:
        return  # Nếu MSSV đã được nhận diện, không cần cập nhật lại
    
    # Cập nhật MSSV hiện tại và nhận diện sinh viên mới
    current_mssv = mssv
    student = students.find_one({"mssv": mssv})
    
    if student:
        # Hiện thông tin sinh viên
        label_name.config(text=f"Họ tên: {student['hoten']}")
        label_mssv.config(text=f"MSSV: {student['mssv']}")
        
        # Load và hiển thị ảnh sinh viên
        image_path = os.path.join("dataset", mssv, f"{mssv}_5.jpg")
        if os.path.exists(image_path):
            img = Image.open(image_path).resize((150, 150))
            imgtk = ImageTk.PhotoImage(img)
            student_image_label.imgtk = imgtk  # Giữ ảnh tránh bị xóa
            student_image_label.config(image=imgtk)
        else:
            student_image_label.config(image="")  # Xóa ảnh nếu không tìm thấy
        
        # Hiện khung info_frame và đặt lại hiển thị sau 2 giây
        info_frame.pack(side=tk.RIGHT, padx=40, pady=10)
        if display_timer:
            root.after_cancel(display_timer)  # Hủy bỏ bộ đếm cũ nếu có
        display_timer = root.after(3000, lambda: info_frame.pack_forget())
        
        # Cập nhật database, thêm vào danh sách đã điểm danh
        check_in_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        update_attendance(mssv, check_in_time, 'Đã điểm danh vào')

        # Thông tin đầy đủ được lưu trữ và cập nhật vào TreeView
        date, time = check_in_time.split()
        save_attendance(student['hoten'], student['lop'], student['mssv'], date, time, "Đã điểm danh vào")

        recognized_students.add(mssv)
        play_sound(moivao_sound)  # Phát âm thanh "mở vào"
    else:
        messagebox.showwarning("Cảnh báo", "Không tìm thấy sinh viên với MSSV này")


# Hàm lưu thông tin điểm danh
def save_attendance(hoten, lop, mssv, date, time, status):
    global attendance_data
    # Tìm vị trí của sinh viên trong attendance_data
    for i, data in enumerate(attendance_data):
        if data[2] == mssv:
            attendance_data[i] = (hoten, lop, mssv, date, time, status)
            break
    else:
        # Nếu không tìm thấy, thêm dòng mới
        attendance_data.append((hoten, lop, mssv, date, time, status))


# Hàm mở cửa sổ chứa Treeview
def open_attendance_window():
    attendance_window = tk.Toplevel(root)
    attendance_window.title("Thông tin sinh viên đã điểm danh")
    attendance_window.geometry("1200x500")

    global treeview
    treeview = ttk.Treeview(attendance_window, columns=("Họ tên", "Lớp", "MSSV", "Ngày vào", "Giờ vào", "Trạng thái"),
                            show="headings")
    treeview.heading("Họ tên", text="Họ tên")
    treeview.heading("Lớp", text="Lớp")
    treeview.heading("MSSV", text="MSSV")
    treeview.heading("Ngày vào", text="Ngày vào")
    treeview.heading("Giờ vào", text="Giờ vào")
    treeview.heading("Trạng thái", text="Trạng thái")
    treeview.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Hiển thị số lượng sinh viên đã checkin
    total_students = students.count_documents({})
    checked_in_students = len(recognized_students)
    label_attendance_info = ttk.Label(attendance_window,
                                      text=f"Số sinh viên đã điểm danh: {checked_in_students}/{total_students}")
    label_attendance_info.pack(pady=5)

    # Lấy dữ liệu điểm danh từ database
    attendance_data = []
    for event in events.find():
        if event['mask'] == '12DHTH13':
            for student in event['dssinhvien_thamgia']:
                if student['tgiancheck_in']:
                    date, time = student['tgiancheck_in'].split()
                    attendance_data.append((student['hoten'], student['lop'], student['mssv'], date, time, student['trangthai_chkin']))

    # Hiển thị dữ liệu vào TreeView
    for data in attendance_data:
        treeview.insert("", "end", values=data)

    # Tạo nút "Xuất file"
    export_button = ttk.Button(attendance_window, text="Xuất file",
                               command=lambda: root.after(10, export_attendance_to_csv))
    export_button.pack(pady=10)

    # Tạo nút "Thêm sinh viên vắng"
    add_absent_button = ttk.Button(attendance_window, text="Xong", command=add_absent_students)
    add_absent_button.pack(pady=5)


# Hàm xuất thông tin điểm danh ra file CSV
def export_attendance_to_csv():
    global treeview
    if not attendance_data:
        messagebox.showwarning("Cảnh báo", "Chưa có thông tin điểm danh để xuất!")
        return

    try:
        with open("diemdanh_data.csv", "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Họ tên", "Lớp", "MSSV", "Ngày vào", "Giờ vào", "Trạng thái"])
            for item in treeview.get_children():
                values = treeview.item(item, 'values')
                writer.writerow(values)
        messagebox.showinfo("Thông báo", "Xuất file thành công!")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi xuất file: {e}")


# Hàm thêm sinh viên vắng vào TreeView
def add_absent_students():
    global treeview, attendance_data
    for student in students.find():
        if student['mssv'] not in recognized_students:
            # Thêm sinh viên vào TreeView nếu chưa có
            current_date = datetime.now().strftime('%Y-%m-%d')
            treeview.insert("", "end",
                            values=(student['hoten'], student['lop'], student['mssv'], current_date, None, "Vắng"))
            attendance_data.append((student['hoten'], student['lop'], student['mssv'], current_date, None, "Vắng"))


# Hàm nhận diện khuôn mặt
def recognize_face():
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    last_unknown_sound_time = time.time()

    def update_frame(last_unknown_sound_time):
        global recognized_students, label_name, label_mssv
        ret, frame = cap.read()
        if not ret:
            return

        # Chuyển đổi sang ảnh màu
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Phát hiện khuôn mặt
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            # Tạo embedding cho khuôn mặt
            face_img = gray[y:y + h, x:x + w]
            face_embedding = create_embedding(face_img)

            # Tìm sinh viên có embedding gần nhất
            best_match = None
            min_distance = float('inf')
            for mssv, known_embedding in student_embeddings.items():
                distance = cosine(face_embedding, known_embedding)
                if distance < min_distance:
                    min_distance = distance
                    best_match = mssv

            # Kiểm tra độ tin cậy
            if min_distance < 0.2:
                load_data_by_mssv(best_match)  # Cập nhật nhãn thông tin sinh viên
                # Vẽ khung chữ nhật và MSSV lên hình
                cv2.putText(frame, f"MSSV: {best_match}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            else:
                current_time = time.time()
                if current_time - last_unknown_sound_time >= 3:  # Kiểm tra khoảng cách thời gian
                    play_sound(khongxacdinh_sound)  # Phát âm thanh "không xác định"
                    last_unknown_sound_time = current_time  # Cập nhật thời gian phát âm thanh cuối cùng

                # Vẽ khung chữ nhật và "Unknown" lên hình
                cv2.putText(frame, f"Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        imgtk = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)))
        camera_label.imgtk = imgtk
        camera_label.config(image=imgtk)
        camera_label.after(10, lambda: update_frame(last_unknown_sound_time))

    update_frame(last_unknown_sound_time)


# Hàm để đóng chương trình
def close_app():
    root.quit()
    root.destroy()


# Khởi tạo pygame
pygame.mixer.init()

# Đường dẫn đến file âm thanh
moivao_sound = os.path.join("Audio", "moivao.mp3")
khongxacdinh_sound = os.path.join("Audio", "khongxacdinh.mp3")


# Hàm phát âm thanh
def play_sound(sound_file):
    try:
        sound = pygame.mixer.Sound(sound_file)
        sound.play()
    except pygame.error as e:
        print(f"Lỗi phát âm thanh: {e}")


# Cửa sổ chính của ứng dụng
root = tk.Tk()
root.title("Smart Attendance Tracker")
root.geometry("1000x800")

# Thay đổi biểu tượng cửa sổ
root.iconbitmap("static\logo-byme.ico")  # Đường dẫn đến tệp .ico

def load_icon(image_path, size=(40, 40)):
    """Tải và điều chỉnh kích thước biểu tượng."""
    icon = Image.open(image_path)
    icon = icon.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(icon)

# Tải biểu tượng cho nút
close_icon_image_tk = load_icon("static/close.png")
icon_image_tk = load_icon("static/list.png")

# Tải hình nền
background_image_path = os.path.join("static", "background.png")  # Đường dẫn tới hình nền
background_image = Image.open(background_image_path)
background_image = background_image.resize((1000, 800), Image.LANCZOS)  # Đảm bảo kích thước phù hợp
background_image_tk = ImageTk.PhotoImage(background_image)

# Tạo Label với hình nền
background_label = tk.Label(root, image=background_image_tk)
background_label.place(relwidth=1, relheight=1)  # Đặt Label chiếm toàn bộ diện tích cửa sổ

# Frame chính
# Tiêu đề ứng dụng
logo = tk.PhotoImage(file="static\logo-byme.png")
title_label = tk.Label(root, font=("Arial", 16, "bold"),image=logo)
title_label.pack()

main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=100)

# Phần camera
camera_frame = tk.Frame(main_frame)
camera_frame.pack(side=tk.LEFT, padx=5, pady=5)

# Thiết lập kích thước mong muốn cho camera
camera_width = 440  # Chiều rộng mong muốn
camera_height = 480  # Chiều cao mong muốn

camera_label = tk.Label(camera_frame, width=camera_width, height=camera_height)
camera_label.pack()


# Phần bên phải: Hiển thị thông tin sinh viên với khung

# Tạo Frame Info
info_frame = ttk.LabelFrame(main_frame, padding=(10, 5))

# Label cho trạng thái
header_image_path = os.path.join("static", "check.png")  # Thay đổi tên file cho đúng
header_image = Image.open(header_image_path)
header_image_tk = ImageTk.PhotoImage(header_image)
top_image_label = ttk.Label(info_frame, image=header_image_tk)
top_image_label.grid(row=0, column=0, padx=0, pady=0)

# Hiển thị hình ảnh sinh viên
student_image_label = ttk.Label(info_frame)
student_image_label.grid(row=1, column=0, padx=5, pady=5)

# Hiển thị MSSV và Họ tên
label_name = ttk.Label(info_frame, text="Họ tên: ", font=('Arial', 12))
label_name.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)

label_mssv = ttk.Label(info_frame, text="MSSV: ", font=('Arial', 12))
label_mssv.grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)

# Nút đóng chương trình
close_button = ttk.Button(root, command=close_app, image=close_icon_image_tk)
close_button.pack(side=tk.RIGHT, padx=30, pady=10)

# Nút mở cửa sổ điểm danh
attendance_button = ttk.Button(root, command=open_attendance_window, image=icon_image_tk)
attendance_button.pack(side=tk.LEFT, padx=30, pady=10)

# Bắt đầu nhận diện khuôn mặt
recognize_thread = threading.Thread(target=recognize_face)
recognize_thread.daemon = True
recognize_thread.start()

# Hiển thị thời gian hiện tại
label_time = tk.Label(root, font=("Arial", 16, "bold"), fg="black")
label_time.pack()
update_time()

# Chạy vòng lặp giao diện
root.mainloop()