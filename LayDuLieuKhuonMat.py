import customtkinter as ctk
import cv2
import tkinter as tk
import os
from pymongo import MongoClient
from gtts import gTTS
import time
import pygame
from tkinter import messagebox

# --- Cấu hình ---
DATABASE_NAME = 'nhandienkhuonmat'
COLLECTION_NAME = 'sinhvien'
DATASET_DIR = 'dataset'
AUDIO_DIR = 'Audio'

# --- Kết nối MongoDB ---
try:
    client = MongoClient('mongodb+srv://scjan123:vgbyostAaTl3Uttq@cluster0.aahzt.mongodb.net/')
    db = client[DATABASE_NAME]
    students = db[COLLECTION_NAME]
except Exception as e:
    messagebox.showerror("Lỗi", f"Kết nối CSDL thất bại! ({e})")
    exit()

# --- Tạo thư mục dataset và audio ---
os.makedirs(DATASET_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# --- Hàm phát âm thanh ---
def speak(text, filename):
    try:
        tts = gTTS(text=text, lang='vi')
        filepath = os.path.join(AUDIO_DIR, f"{filename}.mp3")
        tts.save(filepath)
        pygame.mixer.init()
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.quit()
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi phát âm thanh: {e}")

# --- Hàm reset form ---
def reset_form():
    mssv_entry.delete(0, ctk.END)
    hoten_entry.configure(state="normal"); hoten_entry.delete(0, ctk.END); hoten_entry.configure(state="disabled")
    lop_entry.configure(state="normal"); lop_entry.delete(0, ctk.END); lop_entry.configure(state="disabled")

# --- Hàm kiểm tra MSSV ---
def check_student():
    mssv = mssv_entry.get()
    if len(mssv) != 10:
        messagebox.showerror("Lỗi", "MSSV phải có 10 ký tự!"); reset_form(); return
    try:
        student = students.find_one({"mssv": mssv})
        if student:
            hoten_entry.configure(state="normal"); hoten_entry.delete(0, ctk.END); hoten_entry.insert(0, student["hoten"]); hoten_entry.configure(state="disabled")
            lop_entry.configure(state="normal"); lop_entry.delete(0, ctk.END); lop_entry.insert(0, student["lop"]); lop_entry.configure(state="disabled")
        else:
            messagebox.showerror("Lỗi", "Sinh viên không tồn tại!"); reset_form()
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi truy vấn CSDL: {e}")

# --- Hàm chụp ảnh ---
def capture_images():
    mssv = mssv_entry.get()
    if not mssv:
        messagebox.showerror("Lỗi", "Vui lòng nhập MSSV!"); return

    student_images_dir = os.path.join(DATASET_DIR, mssv)
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
        speak("Bắt đầu chụp ảnh", "batdau")

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

                # Phát giọng nói cho các khoảng ảnh
                if current_images == 10:
                    speak("Nhìn lên", "nhinlen")
                elif current_images == 20:
                    speak("Nhìn xuống", "nhinxuong")
                elif current_images == 30:
                    speak("Nhìn trái", "nhintrai")
                elif current_images == 40:
                    speak("Nhìn phải", "nhinphai")

            cv2.imshow('Thu thập dữ liệu', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break

        cap.release(); cv2.destroyAllWindows()
        speak("Hoàn thành việc chụp ảnh", "hoanthanh")
        messagebox.showinfo("Hoàn tất", f"Đã lưu {current_images} ảnh cho {mssv}."); reset_form()

    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")

# --- Giao diện ---
ctk.set_appearance_mode("System")  # Cài đặt chế độ giao diện hệ thống (sáng/tối)
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Thu thập dữ liệu khuôn mặt")
root.geometry("800x700")

try:
    img = tk.PhotoImage(file='static/huitBG.png')
    img_label = tk.Label(root, image=img)
    img_label.image = img
    img_label.pack(pady=40)
except Exception as e:
    print(f"Lỗi tải ảnh: {e}")
    messagebox.showerror("Lỗi", "Không tải được ảnh!")

# --- Cấu hình font và chiều rộng ---
FONT = ("Arial", 20)
WIDTH = 35  # Đặt chiều rộng đồng đều cho tất cả các thành phần

mssv_label = ctk.CTkLabel(root, text="MSSV:", font=FONT)
mssv_label.pack(side=ctk.TOP, anchor="w", padx=30, pady=15)
mssv_entry = ctk.CTkEntry(root, font=FONT, width=WIDTH)
mssv_entry.pack(side=ctk.TOP, fill=ctk.X, padx=30, pady=10)

check_button = ctk.CTkButton(root, text="Kiểm tra", font=FONT, command=check_student, fg_color="#BA8E23", hover_color="#9e7015", width=WIDTH * 4)
check_button.pack(side=ctk.TOP, padx=30, pady=15)

hoten_label = ctk.CTkLabel(root, text="Họ tên:", font=FONT)
hoten_label.pack(side=ctk.TOP, anchor="w", padx=30, pady=15)
hoten_entry = ctk.CTkEntry(root, font=FONT, state="disabled", width=WIDTH)
hoten_entry.pack(side=ctk.TOP, fill=ctk.X, padx=30, pady=10)

lop_label = ctk.CTkLabel(root, text="Lớp:", font=FONT)
lop_label.pack(side=ctk.TOP, anchor="w", padx=30, pady=15)
lop_entry = ctk.CTkEntry(root, font=FONT, state="disabled", width=WIDTH)
lop_entry.pack(side=ctk.TOP, fill=ctk.X, padx=30, pady=10)

capture_button = ctk.CTkButton(root, text="Chụp ảnh", font=FONT, command=capture_images, fg_color="#4CAF50", hover_color="#3c8c41", width=WIDTH * 4)
capture_button.pack(side=ctk.TOP, padx=30, pady=30)

root.mainloop()
