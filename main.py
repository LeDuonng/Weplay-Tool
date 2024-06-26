import os
import pyautogui
import pytesseract
from PIL import Image
import cv2
import numpy as np
import time
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import keyboard

# Cài đặt đường dẫn cho Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Cài biến môi trường cho Tesseract
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR'

# Hàm xử lý hình ảnh trước khi nhận dạng
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return gray

# Hàm nhận dạng và đánh tẩu hỏa nhập ma
def tauhoanhapma():
    location = None
    while location is None:
        location = pyautogui.locateOnScreen('img/khacchetamma.png', confidence=0.8) 
    for _ in range(20):
        pyautogui.click(location)
        time.sleep(0.1)

# Hàm click vào hình ảnh trên màn hình
def click_image(target_image_path, confidence=0.8):
    try:
        location = pyautogui.locateOnScreen(target_image_path, confidence=confidence)
        if location:
            if 'phieuluu2.png' in target_image_path:
                os.system("start nofi.mp3")
                for target_text in target_texts:
                    if click_text(target_text):
                        break
                return False
            elif 'tauhoa.png' or 'tauhoa2.png' or 'tauhoa3.png' or 'tauhoa1.png' in target_image_path:
                pyautogui.click(location)
                tauhoanhapma()
            else:
                pyautogui.click(location)
                print(f"Clicked on image {target_image_path} at location: {location}")
            return True
        else:
            return False
    except Exception as e:
        print(f"Error image: {e}")
        return False

# Hàm nhận dạng và click vào văn bản trên màn hình
def click_text(target_text, region=None):
    try:
        screenshot = pyautogui.screenshot(region=region)
        screenshot_np = np.array(screenshot)
        preprocessed_image = preprocess_image(screenshot_np)
        # cv2.imwrite('preprocessed_image.png', preprocessed_image)
        text_data = pytesseract.image_to_data(preprocessed_image, output_type=pytesseract.Output.DICT, lang='eng')
        text_data['text'] = [text.encode('ascii', 'ignore').decode('utf-8') for text in text_data['text']]
        # with open('text_data.txt', 'w', encoding='utf-8') as file:
        #     file.write(str(text_data))

        for i, text in enumerate(text_data['text']):
            if i + 1 < len(text_data['text']):
                concatenated_text = text + ' ' + text_data['text'][i+1]
                if target_text.lower() in concatenated_text.lower():
                    x, y, w, h = text_data['left'][i], text_data['top'][i], text_data['width'][i], text_data['height'][i]
                    center_x, center_y = x + w // 2, y + h // 2
                    pyautogui.click(center_x, center_y)
                    print(f"Clicked on text '{target_text}' at location: ({center_x}, {center_y})")
                    return True

        return False
    except Exception as e:
        print(f"Error text: {e}")
        return False

# Hàm tự động click vào hình ảnh lì xì
def auto_click_lixi():
    global running 
    running = True
    while running:
        click_image('img/lixi/lixi.png')

# Hàm chạy script tự động
def start_script():
    global running, target_texts
    target_texts = []
    with open('target_text_en.txt', 'r', encoding='utf-8') as file:
        target_texts = [line.strip().replace(',', '') for line in file if line.strip()]

    running = True
    while running:
        for image_file in os.listdir('img'):
            if image_file.endswith(('.png', '.jpg', '.jpeg')):
                if click_image(os.path.join('img', image_file)):
                    break
        time.sleep(1)  # Prevent the script from running too fast

# Hàm dừng script tự động
def stop_script():
    global running
    running = False

# Hàm chạy script tự động trong một thread
def run_script_in_thread():
    stop_script()
    script_thread = threading.Thread(target=start_script)
    script_thread.start()

# Hàm chạy Lì xì trong một thread
def run_lixi_in_thread():
    stop_script()
    lixi_thread = threading.Thread(target=auto_click_lixi)
    lixi_thread.start()    

# Hàm tạo giao diện
def create_gui():
    window = tk.Tk()
    window.title("Weplay AutoTool")
    
    status_label = tk.Label(window, text="Status: Stopped", fg="red", font=("Arial", 16, "bold"))
    status_label.pack(pady=5)

    def update_status_label():
        global running
        while True:
            if running:
                status_label.config(text="Status: Running", fg="green", font=("Arial", 16, "bold"))
            else:
                status_label.config(text="Status: Stopped", fg="red", font=("Arial", 16, "bold"))
            time.sleep(0.1)
    

    status_thread = threading.Thread(target=update_status_label)
    status_thread.start()

    start_button = tk.Button(window, text="Auto Click (F9)", command=run_script_in_thread, padx=20, pady=10)
    start_button.pack(pady=5)
    keyboard.add_hotkey('f9', run_script_in_thread)

    start_button = tk.Button(window, text="Lì xì (F10)", command=run_lixi_in_thread, padx=20, pady=10)
    start_button.pack(pady=5)
    keyboard.add_hotkey('f10', run_lixi_in_thread)

    pause_button = tk.Button(window, text="Tạm dừng (F12)", command=stop_script, padx=20, pady=10)
    pause_button.pack(pady=5)
    keyboard.add_hotkey('f12', stop_script)

    exit_button = tk.Button(window, text="Thoát", command=window.quit, padx=20, pady=10)
    exit_button.pack(pady=5)

    window.geometry("+{}+{}".format(window.winfo_screenwidth() - window.winfo_reqwidth() - 150, window.winfo_screenheight() - window.winfo_reqheight() - 200))
    window.geometry("300x270")

    window.mainloop()

if __name__ == "__main__":
    running = False
    create_gui()
