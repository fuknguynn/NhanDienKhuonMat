import os
import numpy as np
from keras_facenet import FaceNet
from mtcnn import MTCNN
import cv2
import customtkinter as ctk
from tkinter import messagebox

# Đường dẫn đến folder chứa ảnh sinh viên, mỗi folder là MSSV của sinh viên
dataset_path = "dataset"

# Khởi tạo mô hình FaceNet và MTCNN
embedder = FaceNet()
detector = MTCNN()

# Hàm tạo embedding vector từ ảnh
def create_embedding(face_img):
    face_img_resized = cv2.resize(face_img, (160, 160))
    return embedder.embeddings([face_img_resized])[0]

# Tạo dictionary lưu các embedding của từng sinh viên
student_embeddings = {}

# Giao diện Tkinter
root = ctk.CTk()
root.title("Tiến trình tạo embedding")
root.geometry("800x600")  # Tăng kích thước cửa sổ

# Label và Progressbar (tiến trình tổng thể)
progress_label = ctk.CTkLabel(root, text="Nhấn bắt đầu để tạo embedding", font=("Arial", 18))
progress_label.pack(pady=20)

# Khởi tạo ProgressBar với giá trị ban đầu là 0
progressbar = ctk.CTkProgressBar(root, width=600, mode='determinate', height=30)  
progressbar.pack(pady=20)

# Dòng hiển thị số lượng tiến trình tổng thể
progress_text = ctk.CTkLabel(root, text="0/0", font=("Arial", 14))
progress_text.pack(pady=10)

# Progress bar cho từng vòng lặp (xử lý sinh viên)
progress_label_detail = ctk.CTkLabel(root, text="Tiến trình xử lý từng sinh viên", font=("Arial", 16))
progress_label_detail.pack(pady=20)

# Khởi tạo ProgressBar cho từng vòng lặp
progressbar_detail = ctk.CTkProgressBar(root, width=600, mode='determinate', height=30)  
progressbar_detail.pack(pady=20)

# Dòng hiển thị số lượng tiến trình chi tiết
progress_text_detail = ctk.CTkLabel(root, text="0/0", font=("Arial", 14))
progress_text_detail.pack(pady=10)

# Hàm để cập nhật tiến trình tổng thể
def update_progress(progress, processed_folders, total_folders):
    progressbar.set(progress / 100)  # Sử dụng set() thay vì configure(progress=...)
    progress_text.configure(text=f"{processed_folders}/{total_folders}")
    root.update_idletasks()

# Hàm để cập nhật tiến trình chi tiết (từng ảnh trong một folder)
def update_progress_detail(progress, processed_images, total_images):
    progressbar_detail.set(progress / 100)  # Sử dụng set() thay vì configure(progress=...)
    progress_text_detail.configure(text=f"{processed_images}/{total_images}")
    root.update_idletasks()

# Hàm tạo embedding và cập nhật tiến trình
def create_embeddings():
    total_folders = len(os.listdir(dataset_path))
    processed_folders = 0
    print("Bắt đầu tạo embedding cho sinh viên...")

    # Cập nhật lại label khi bắt đầu quá trình
    progress_label.configure(text="Đang tạo embedding cho sinh viên...")

    # Đặt lại giá trị thanh tiến trình về 0 khi bắt đầu
    progressbar.set(0)
    progressbar_detail.set(0)

    for mssv in os.listdir(dataset_path):
        student_folder = os.path.join(dataset_path, mssv)

        # Đảm bảo rằng mỗi folder chỉ chứa các file ảnh
        if os.path.isdir(student_folder):
            embeddings = []
            print(f"Đang xử lý folder: {mssv}")

            total_images = len(os.listdir(student_folder))  # Tổng số ảnh trong mỗi folder
            processed_images = 0  # Số ảnh đã xử lý

            # Duyệt qua từng ảnh trong folder của sinh viên
            for img_file in os.listdir(student_folder):
                img_path = os.path.join(student_folder, img_file)
                img = cv2.imread(img_path)

                if img is not None:
                    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    faces = detector.detect_faces(rgb_img)

                    if faces:
                        # Giả sử mỗi ảnh chỉ có 1 khuôn mặt
                        x, y, w, h = faces[0]['box']
                        face_img = rgb_img[y:y+h, x:x+w]
                        embedding = create_embedding(face_img)
                        embeddings.append(embedding)
                        print(f"Đã tạo embedding cho ảnh: {img_file}")

                processed_images += 1
                # Cập nhật tiến trình chi tiết (từng ảnh trong folder)
                progress_detail = int((processed_images / total_images) * 100)
                update_progress_detail(progress_detail, processed_images, total_images)

            if embeddings:
                # Lấy trung bình của các embedding nếu có nhiều ảnh
                mean_embedding = np.mean(embeddings, axis=0)
                student_embeddings[mssv] = mean_embedding
                print(f"Đã lưu embedding cho sinh viên: {mssv} (Tổng số ảnh: {len(embeddings)})")
            else:
                print(f"Không tìm thấy khuôn mặt trong folder: {mssv}")

        processed_folders += 1
        # Cập nhật tiến trình tổng thể (từng folder)
        progress = int((processed_folders / total_folders) * 100)
        update_progress(progress, processed_folders, total_folders)

    print("Đã hoàn tất việc tạo embedding cho tất cả sinh viên.")

    # Lưu lại embedding vectors vào file
    np.save('embeddings.npy', student_embeddings)
    print("Đã lưu embedding vectors vào file embeddings.npy.")

    messagebox.showinfo("Hoàn tất", "Đã tạo xong và lưu embedding.")

# Button để bắt đầu quá trình tạo embedding
start_button = ctk.CTkButton(root, text="Bắt đầu", font=("Arial", 16), width=200, height=40, command=create_embeddings)  
start_button.pack(pady=30)

root.mainloop()
