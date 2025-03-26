import cv2
import mediapipe as mp
import pyautogui
import time

# Khởi tạo MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Biến trạng thái cho chức năng Alt+Tab
alt_tab_active = False
prev_index_x = None
threshold_x = 200


def detect_hand_state(lm_list):
    """
    Hàm xác định trạng thái tay:
      - "open": Tay mở (với các ngón trỏ, giữa, áp út, út được duỗi ra)
      - "closed": Tay nắm (các ngón tay gập lại)
    """
    if lm_list:
        # Kiểm tra các ngón: nếu tip của index, middle, ring, pinky có y nhỏ hơn PIP thì tay mở
        open_cond = (lm_list[8][2] < lm_list[6][2] and
                     lm_list[12][2] < lm_list[10][2] and
                     lm_list[16][2] < lm_list[14][2] and
                     lm_list[20][2] < lm_list[18][2])
        closed_cond = (lm_list[8][2] > lm_list[6][2] and
                       lm_list[12][2] > lm_list[10][2] and
                       lm_list[16][2] > lm_list[14][2] and
                       lm_list[20][2] > lm_list[18][2])
        # Với thumb, chúng ta dùng so sánh x để phân biệt (giả sử tay phải)
        thumb_cond = lm_list[4][1] > lm_list[2][1]  # thumb mở nếu tip bên phải
        if open_cond and thumb_cond:
            return "open"
        elif closed_cond:
            return "closed"
    return None


def execute_alt_tab(frame, lm_list):
    """Thực hiện chức năng chuyển đổi cửa sổ (Alt+Tab)"""
    global alt_tab_active, prev_index_x, threshold_x
    # Lấy vị trí X của ngón trỏ (point id 8)
    x_index = lm_list[8][1]
    # Vẽ đường phân cách (cho trực quan)
    cv2.line(frame, (threshold_x, 0), (threshold_x, frame.shape[0]), (0, 255, 0), 2)

    hand_state = detect_hand_state(lm_list)
    if hand_state == "open" and not alt_tab_active:
        print("Alt+Tab: Bắt đầu chuyển (giữ Alt + nhấn Tab)")
        pyautogui.keyDown("alt")
        pyautogui.press("tab")
        alt_tab_active = True
    elif hand_state == "closed" and alt_tab_active:
        print("Alt+Tab: Chọn ứng dụng (nhấn Enter và thả Alt)")
        pyautogui.press("enter")
        time.sleep(0.5)
        pyautogui.keyUp("alt")
        alt_tab_active = False

    # Kiểm tra chuyển động vuốt ngang (nếu ngón trỏ vượt qua ngưỡng)
    if prev_index_x is not None and alt_tab_active:
        if prev_index_x < threshold_x and x_index >= threshold_x:
            print("Alt+Tab: Vuốt sang phải -> Nhấn Tab")
            pyautogui.press("tab")
    prev_index_x = x_index


def execute_volume_control(gesture):
    """Thực hiện tăng/giảm âm lượng dựa trên gesture:
       [1,1,0,0,0] : Tăng âm lượng
       [0,1,0,0,0] : Giảm âm lượng
    """
    if gesture == [1, 1, 0, 0, 0]:
        print("Tăng âm lượng")
        pyautogui.press("volumeup")
    elif gesture == [0, 1, 0, 0, 0]:
        print("Giảm âm lượng")
        pyautogui.press("volumedown")


def execute_close_tab():
    """Thực hiện đóng tab hiện tại bằng hotkey Ctrl+W"""
    print("Đóng tab hiện tại")
    pyautogui.hotkey("ctrl", "w")


# Mở webcam
cap = cv2.VideoCapture(0)
prev_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    lm_list = []
    gesture = None

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
            for id, lm in enumerate(handLms.landmark):
                lm_list.append([id, int(lm.x * w), int(lm.y * h)])

            # Xác định trạng thái từng ngón (dạng nhị phân, 0 hoặc 1)
            # Thumb: dựa trên x (cho tay phải)
            if lm_list[4][1] > lm_list[2][1]:
                thumb = 1
            else:
                thumb = 0
            # Các ngón còn lại: nếu tip có y nhỏ hơn PIP (ngón duỗi ra)
            index_finger = 1 if lm_list[8][2] < lm_list[6][2] else 0
            middle_finger = 1 if lm_list[12][2] < lm_list[10][2] else 0
            ring_finger = 1 if lm_list[16][2] < lm_list[14][2] else 0
            pinky = 1 if lm_list[20][2] < lm_list[18][2] else 0

            gesture = [thumb, index_finger, middle_finger, ring_finger, pinky]
            cv2.putText(frame, f"Gesture: {gesture}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 0, 255), 2)

    # Kiểm tra gesture và gọi chức năng tương ứng
    if lm_list:
        # Chuyển đổi cửa sổ (Alt+Tab) khi gesture là [0,1,1,1,1]
        if gesture == [0, 1, 1, 1, 1]:
            execute_alt_tab(frame, lm_list)
        # Đóng tab hiện tại khi gesture là [0,0,0,0,1]
        elif gesture == [0, 0, 0, 0, 1]:
            execute_close_tab()
        # Điều chỉnh âm lượng: nếu gesture là [1,1,0,0,0] (volume up) hoặc [0,1,0,0,0] (volume down)
        elif gesture in ([1, 1, 0, 0, 0], [0, 1, 0, 0, 0]):
            execute_volume_control(gesture)

    # Tính FPS
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
    prev_time = curr_time
    cv2.putText(frame, f"FPS: {int(fps)}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX,
                1, (255, 0, 0), 2)

    cv2.imshow("Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('x'):
        break

cap.release()
cv2.destroyAllWindows()
