import tkinter as tk
from tkinter import messagebox
import os
import cv2
from pymongo import MongoClient

# Kết nối MongoDB (bỏ qua nếu không dùng)
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['nhandienkhuonmat']
    students = db['sinhvien']
except Exception as e:
    print(f"Lỗi kết nối MongoDB: {e}")
    messagebox.showerror("Lỗi", "Kết nối CSDL thất bại!")
    exit()


dataset_dir = 'dataset'
os.makedirs(dataset_dir, exist_ok=True)


def reset_form():
    mssv_entry.delete(0, tk.END)
    hoten_entry.config(state="normal"); hoten_entry.delete(0, tk.END); hoten_entry.config(state="readonly")
    lop_entry.config(state="normal"); lop_entry.delete(0, tk.END); lop_entry.config(state="readonly")


def check_student():
    mssv = mssv_entry.get()
    if len(mssv) != 10:
        messagebox.showerror("Lỗi", "MSSV phải có 10 ký tự!"); reset_form(); return
    student = students.find_one({"mssv": mssv})
    if student:
        hoten_entry.config(state="normal"); hoten_entry.delete(0, tk.END); hoten_entry.insert(0, student["hoten"]); hoten_entry.config(state="readonly")
        lop_entry.config(state="normal"); lop_entry.delete(0, tk.END); lop_entry.insert(0, student["lop"]); lop_entry.config(state="readonly")
    else:
        messagebox.showerror("Lỗi", "Sinh viên không tồn tại!"); reset_form()


def capture_images():
    mssv = mssv_entry.get()
    if not mssv:
        messagebox.showerror("Lỗi", "Vui lòng nhập MSSV!"); return

    student_images_dir = os.path.join(dataset_dir, mssv)
    os.makedirs(student_images_dir, exist_ok=True)

    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Lỗi", "Không mở được camera!"); return

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        if face_cascade.empty():
            messagebox.showerror("Lỗi", "Không tải được bộ dò khuôn mặt!"); return

        total_images = 50; current_images = 0
        messagebox.showinfo("Thông báo", "Nhấn 'q' để dừng.")

        while current_images < total_images:
            ret, frame = cap.read()
            if not ret:
                messagebox.showerror("Lỗi", "Lỗi đọc ảnh từ camera!"); break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                current_images += 1
                face = gray[y:y + h, x:x + w]
                cv2.imwrite(os.path.join(student_images_dir, f'{mssv}_{current_images}.jpg'), face)
                cv2.putText(frame, f"Saving {current_images}/{total_images}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            cv2.imshow('Thu thập dữ liệu', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break

        cap.release(); cv2.destroyAllWindows()
        messagebox.showinfo("Hoàn tất", f"Đã lưu {current_images} ảnh cho {mssv}."); reset_form()

    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")


root = tk.Tk(); root.title("Thu thập dữ liệu khuôn mặt"); root.geometry("600x600")

try:
    img = tk.PhotoImage(file='static/LogoFinal.png')
    img_label = tk.Label(root, image=img)
    img_label.image = img
    img_label.pack(pady=20)
except Exception as e:
    print(f"Lỗi tải ảnh: {e}")
    messagebox.showerror("Lỗi", "Không tải được ảnh!")

FONT_LARGE = ("Arial", 16, "bold"); FONT_MEDIUM = ("Arial", 14)

mssv_label = tk.Label(root, text="MSSV:", font=FONT_LARGE); mssv_label.pack(side=tk.TOP, anchor=tk.W, padx=20, pady=5)
mssv_entry = tk.Entry(root, font=FONT_MEDIUM, width=25); mssv_entry.pack(side=tk.TOP, fill=tk.X, padx=20, pady=5)
check_button = tk.Button(root, text="Kiểm tra", font=FONT_MEDIUM, command=check_student, bg="#BA8E23", fg="white"); check_button.pack(side=tk.TOP, padx=20, pady=5)

hoten_label = tk.Label(root, text="Họ tên:", font=FONT_MEDIUM); hoten_label.pack(side=tk.TOP, anchor=tk.W, padx=20, pady=5)
hoten_entry = tk.Entry(root, font=FONT_MEDIUM, state="readonly", width=30); hoten_entry.pack(side=tk.TOP, fill=tk.X, padx=20, pady=5)

lop_label = tk.Label(root, text="Lớp:", font=FONT_MEDIUM); lop_label.pack(side=tk.TOP, anchor=tk.W, padx=20, pady=5)
lop_entry = tk.Entry(root, font=FONT_MEDIUM, state="readonly", width=30); lop_entry.pack(side=tk.TOP, fill=tk.X, padx=20, pady=5)

capture_button = tk.Button(root, text="Chụp ảnh", font=FONT_LARGE, command=capture_images, bg="#4CAF50", fg="white"); capture_button.pack(side=tk.TOP, padx=20, pady=20)

root.mainloop()