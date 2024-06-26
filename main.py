import os
import pyautogui
import pytesseract
from PIL import Image
import cv2
import numpy as np
import time

time.sleep(5)

# Đường dẫn đến tesseract.exe (cập nhật đường dẫn nếu cần)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Đặt biến môi trường TESSDATA_PREFIX
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR'

# Hàm xử lý ảnh để tăng chất lượng nhận diện văn bản
def preprocess_image(image):
    # Chuyển đổi ảnh sang grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Điều chỉnh độ tương phản và độ sáng
    # gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
    
    # Tăng độ tương phản và làm mịn ảnh bằng ngưỡng Otsu
    gray = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    return gray

def tauhoanhapma():
    try:
        while pyautogui.locateOnScreen('img\khacchetamma.png', confidence=0.8) is not None:
            pyautogui.click(pyautogui.locateOnScreen('img\khacchetamma.png', confidence=0.8))
            time.sleep(0.1)
    except Exception as e:
        print(f"Error: {e}")

def loivaotiengioi(location):
    time.sleep(2)
    pyautogui.click(location)
    time.sleep(2)
    pyautogui.click(pyautogui.locateOnScreen('img\clicktiengioi.png', confidence=0.8))
    time.sleep(2)
    pyautogui.click(pyautogui.locateOnScreen('img\clickdituluyen.png', confidence=0.8))


# Hàm tìm và nhấp vào hình ảnh trên màn hình
def click_image(target_image_path, confidence=0.8):
    try:
        location = pyautogui.locateOnScreen(target_image_path, confidence=confidence)
        if location:
            if 'phieuluu.png' in target_image_path:
                for target_text in target_texts:
                    if click_text(target_text):   
                        break   
            elif 'tauhoa.png' in target_image_path:
                pyautogui.click(location)
                tauhoanhapma()
            elif 'loivaotiengioi.png' in target_image_path:
                loivaotiengioi(location)
            else:
                pyautogui.click(location)
                print(f"Clicked on image {target_image_path} at location: {location}")
            return True
        else:
            # print("Image not found on screen.")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# Hàm tìm và nhấp vào văn bản trên màn hình
def click_text(target_text, region=None):
    try:
        # Chụp ảnh màn hình
        screenshot = pyautogui.screenshot(region=region)
        screenshot_np = np.array(screenshot)
        
        # Xử lý ảnh
        preprocessed_image = preprocess_image(screenshot_np)
        # Lưu ảnh đã xử lý vào file
        cv2.imwrite('preprocessed_image.png', preprocessed_image)
        
        # Sử dụng Tesseract để nhận dạng văn bản trên ảnh màn hình
        text_data = pytesseract.image_to_data(preprocessed_image, output_type=pytesseract.Output.DICT, lang='eng')  # Sử dụng ngôn ngữ tiếng Việt
        text_data['text'] = [text.encode('ascii', 'ignore').decode('utf-8') for text in text_data['text']]
        with open('text_data.txt', 'w', encoding='utf-8') as file:
            file.write(str(text_data))

        for i, text in enumerate(text_data['text']):
            # Kiểm tra để tránh truy cập ngoài mảng
            if i + 1 < len(text_data['text']):
                # Nối văn bản hiện tại và văn bản tiếp theo với một khoảng trắng giữa chúng
                concatenated_text = text + ' ' + text_data['text'][i+1]
                # Kiểm tra xem target_text có nằm trong chuỗi nối này không
                if target_text.lower() in concatenated_text.lower():
                    x, y, w, h = text_data['left'][i], text_data['top'][i], text_data['width'][i], text_data['height'][i]
                    center_x, center_y = x + w // 2, y + h // 2
                    # Sử dụng PyAutoGUI để click vào vị trí trung tâm
                    pyautogui.click(center_x, center_y)
                    print(f"Clicked on text '{target_text}' at location: ({center_x}, {center_y})")
                    # time.sleep(5)
                    return True

        # print(f"Text '{target_text}' not found on screen.")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# Đọc danh sách văn bản mục tiêu từ tệp
with open('target_text_en.txt', 'r', encoding='utf-8') as file:
    target_texts = [line.strip().replace(',', '') for line in file if line.strip()]

# Thư mục chứa các hình ảnh mục tiêu
image_folder = 'img'
# image_question_folder = 'img/question'

# Sử dụng vòng lặp vô hạn để kiểm tra liên tục
while True:
    # Thử nhấp vào một hình ảnh
    for image_file in os.listdir(image_folder):
        if image_file.endswith(('.png', '.jpg', '.jpeg')):
            if click_image(os.path.join(image_folder, image_file)):
                break

    # Chờ một chút trước khi thử lại
    # time.sleep(0.5)
