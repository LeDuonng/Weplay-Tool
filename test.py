import pyautogui
import pytesseract
import cv2
import numpy as np
import time

# Cấu hình đường dẫn đến tesseract nếu cần
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Đọc nội dung từ file target_text.txt
with open('target_text_en.txt', 'r', encoding='utf-8') as file:
    target_texts = [line.strip() for line in file.read().split(',\n')]

def capture_screen():
    screenshot = pyautogui.screenshot()
    image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return image

def find_text_and_click(target_texts):
    while True:
        screen_image = capture_screen()
        gray = cv2.cvtColor(screen_image, cv2.COLOR_BGR2GRAY)
        custom_config = r'--oem 3 --psm 6 -l vie'
        detected_data = pytesseract.image_to_data(gray, config=custom_config, output_type=pytesseract.Output.DICT)
        detected_data['text'] = [text.encode('ascii', 'ignore').decode('utf-8') for text in detected_data['text']]
        with open('text_data.txt', 'w', encoding='utf-8') as file:
            file.write(''.join(detected_data['text']))

        for target_text in target_texts:
            if target_text in detected_data['text']:
                index = detected_data['text'].index(target_text)
                x, y, w, h = (detected_data['left'][index], detected_data['top'][index], 
                              detected_data['width'][index], detected_data['height'][index])
                center_x, center_y = x + w // 2, y + h // 2

                print(f'Phát hiện: {target_text}')
                pyautogui.click(center_x, center_y)
                print(f'Đã nhấp vào {target_text} tại {(center_x, center_y)}')
                return
        time.sleep(1)

while True:
    print('Bắt đầu tìm kiếm chữ trên màn hình...')
    find_text_and_click(target_texts)
