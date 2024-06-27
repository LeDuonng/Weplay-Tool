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

# Set the path to the Tesseract executable (update the path if needed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Set the TESSDATA_PREFIX environment variable
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR'

# Function to preprocess the image for better text recognition
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return gray

def tauhoanhapma():
    location = None
    while location is None:
        location = pyautogui.locateOnScreen('img/khacchetamma.png', confidence=0.8) 
    for _ in range(20):
        pyautogui.click(location)
        time.sleep(0.1)

# Function to click on an image on the screen
def click_image(target_image_path, confidence=0.8):
    try:
        location = pyautogui.locateOnScreen(target_image_path, confidence=confidence)
        if location:
            if 'phieuluu.png' in target_image_path:
                for target_text in target_texts:
                    if click_text(target_text):
                        break
            elif 'tauhoa.png' or 'tauhoa2.png' or 'tauhoa3.png' or 'tauhoa1.png' in target_image_path or 'tauhoa1.png' in target_image_path:
                pyautogui.click(location)
                tauhoanhapma()
            else:
                pyautogui.click(location)
                print(f"Clicked on image {target_image_path} at location: {location}")
            return True
        else:
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# Function to click on text on the screen
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
        print(f"Error: {e}")
        return False

def auto_click_lixi():
    global running 
    running = True
    while running:
        click_image('img/lixi/lixi.png')

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

def stop_script():
    global running
    running = False

def run_script_in_thread():
    script_thread = threading.Thread(target=start_script)
    script_thread.start()

def run_lixi_in_thread():
    lixi_thread = threading.Thread(target=auto_click_lixi)
    lixi_thread.start()    

# GUI setup
def create_gui():
    window = tk.Tk()
    window.title("Weplay AutoTool")
    
    status_label = tk.Label(window, text="Status: Stopped", fg="red")
    status_label.pack(pady=5)

    def update_status_label():
        global running
        while True:
            if running:
                status_label.config(text="Status: Running", fg="green")
            else:
                status_label.config(text="Status: Stopped", fg="red")
            time.sleep(0.1)

    status_thread = threading.Thread(target=update_status_label)
    status_thread.start()

    start_button = tk.Button(window, text="Auto Click", command=run_script_in_thread, padx=20, pady=10)
    start_button.pack(pady=5)

    start_button = tk.Button(window, text="Lì xì", command=run_lixi_in_thread, padx=20, pady=10)
    start_button.pack(pady=5)

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
