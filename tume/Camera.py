import cv2
import base64
import datetime
import time
import os
from .utils import edit_contrast, ascii2num
from pyzbar.pyzbar import decode


class Camera:
    def __init__(self):
        # OpenCVのカメラオブジェクトを作成
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        self._is_capture = True
        self.dir_flag = True

    def get_image(self):
        # カメラから画像を取得
        _, self.frame = self.cap.read()
        img = self._cv_to_base64(self.frame)
        # img = self.frame
        return img

    def get_image_not_base64(self):
        _, frame = self.cap.read()
        return frame

    def start_cam(self, e):
        """画像取得開始時の処理"""
        self._is_capture = True

    def end_cam(self, e):
        """画像取得終了時の処理"""
        self._is_capture = False

    def save_image(self, e):
        """画像を保存する"""
        filename = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")
        cv2.imwrite(f"{filename}.jpg", self.frame)

    def qrcode_reader(self):
        frame = self.get_image_not_base64()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (7, 7), 0)
        image = edit_contrast(blur, 5)
        codes = decode(image)
        if len(codes) > 0:
            inputX = codes[0][0].decode("utf-8", "ignore")
            print("読み取り成功です")
            read_result = inputX.split(":")
            if self.dir_flag == True:
                os.chdir(str(read_result[0]))  # ディレクトリの移動
                print(os.getcwd())
                self.dir_flag = False
            numcode = ascii2num(read_result[1])
            ns = numcode
            ns_org = numcode
            user_name = str(read_result[0])
            time.sleep(0.5)
            return ns, ns_org, user_name
        else:
            return None, None, None

    @property
    def is_capture(self) -> bool:
        """画像取得を行うかのフラグ
        Returns:
            bool: 画像取得を行う場合True
        """
        return self._is_capture

    def _cv_to_base64(self, img):
        _, encoded = cv2.imencode(".jpg", img)
        img_str = base64.b64encode(encoded).decode("ascii")
        return img_str

    def __del__(self):
        # カメラを終了
        self.cap.release()
