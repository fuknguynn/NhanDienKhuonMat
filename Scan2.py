import tkinter as tk
from tkinter import messagebox
import cv2
import os
from pymongo import MongoClient
from gtts import gTTS
import time
import pygame

# --- Cấu hình ---
MONGO_URI = 'mongodb://localhost:27017/'
DATABASE_NAME = 'nhandienkhuonmat'
COLLECTION_NAME = 'sinhvien'
DATASET_DIR = 'dataset'
AUDIO_DIR = 'Audio'

# --- Kết nối MongoDB ---
try:
    client = MongoClient(MONGO_URI)
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
    mssv_entry.delete(0, tk.END)
    hoten_entry.config(state="normal"); hoten_entry.delete(0, tk.END); hoten_entry.config(state="readonly")
    lop_entry.config(state="normal"); lop_entry.delete(0, tk.END); lop_entry.config(state="readonly")


# --- Hàm kiểm tra MSSV ---
def check_student():
    mssv = mssv_entry.get()
    if len(mssv) != 10:
        messagebox.showerror("Lỗi", "MSSV phải có 10 ký tự!"); reset_form(); return
    try:
        student = students.find_one({"mssv": mssv})
        if student:
            hoten_entry.config(state="normal"); hoten_entry.delete(0, tk.END); hoten_entry.insert(0, student["hoten"]); hoten_entry.config(state="readonly")
            lop_entry.config(state="normal"); lop_entry.delete(0, tk.END); lop_entry.insert(0, student["lop"]); lop_entry.config(state="readonly")
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