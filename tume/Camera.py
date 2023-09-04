import cv2
import base64
import datetime

class Camera():
    def __init__(self):
        # OpenCVのカメラオブジェクトを作成
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) 
        self.cap.set(cv2.CAP_PROP_FPS,60)
        self._is_capture = True
    def get_image(self):
        # カメラから画像を取得
        _ , self.frame = self.cap.read()
        img = self._cv_to_base64(self.frame)
        # img = self.frame
        return img
    def get_image_not_base64(self):
        _,self.frame = self.cap.read()
        return self.frame
    def start_cam(self,e):
        """画像取得開始時の処理
        """
        self._is_capture = True
    def end_cam(self,e):
        """画像取得終了時の処理
        """
        self._is_capture = False
    def save_image(self,e):
        """画像を保存する
        """
        filename=datetime.strftime(datetime.now(),"%Y%m%d%H%M%S")
        cv2.imwrite(f"{filename}.jpg",self.frame)
    @property
    def is_capture(self)->bool:
        """画像取得を行うかのフラグ
        Returns:
            bool: 画像取得を行う場合True
        """
        return self._is_capture
    def _cv_to_base64(self,img):
        _, encoded = cv2.imencode(".jpg", img)
        img_str = base64.b64encode(encoded).decode("ascii")
        return img_str
    def __del__(self):
        # カメラを終了
        self.cap.release()