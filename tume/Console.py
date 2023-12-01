import flet as ft
from .Camera import Camera
import cv2
import numpy as np
import threading
import time
from .utils import (
    write_now_auth_number,
    write_now_temp_number,
    convert_file,
    crop_center,
    ImgSplit,
    rand_auth2,
    concat_tile,
    crop_center2,
    liveness_detection,
    template_matching_zncc2,
)


class Console(ft.UserControl):
    def __init__(self, page: ft.Page, camera: Camera) -> None:
        super().__init__()
        self.page = page
        self.camera = camera
        self.method = ""
        self.console = ft.Column(
            spacing=ft.alignment.center,
            height=350,
            width=1300,
            scroll=ft.ScrollMode.ALWAYS,
            auto_scroll=True,
        )

    def build(self):
        return ft.Row(controls=[ft.Container(content=ft.Column(
            controls=[self.console],
            spacing=ft.alignment.center,
        ), bgcolor="black", border_radius=10, padding=ft.padding.only(left=10, top=10, bottom=20))], alignment=ft.MainAxisAlignment.CENTER)

    def set_method(self, method):
        self.method = method

    def append_cnosole(self, text):
        self.console.controls.append(
            ft.Text(value=text, size=15, selectable=True, color="white")
        )
        self.page.update()
        self.update()

    def append_console_Text(self, text):
        self.console.controls.append(text)
        self.page.update()
        self.update()

    def ld_overall(self, camera, red_rate1):
        # 生体検知
        dx_list = []
        ld_list = []

        link_validation_flag = False
        text = ft.Text(color="white", selectable=True)
        Text_ld = ft.Text(color="white", selectable=True)

        org_position = cv2.imread(
            f"./{self.method}/input/liveness_detection/ld_before.png")
        org_position = cv2.cvtColor(org_position, cv2.COLOR_RGB2GRAY)
        self.append_cnosole("生体検知を行います\n指をもう少し前に押しこんでください")
        self.append_console_Text(text)
        self.append_console_Text(Text_ld)
        self.update()
        print("生体検知を行います")
        print("指をもう少し前に押しこんでください")
        time.sleep(0.2)
        detect_counter = 0
        after_score = 1
        ta = time.time()
        for i in range(25):
            bar = "#"*i + " "*(25-i-1)
            text.value = f"[{bar}] {i+1}/25"
            # text.value = f"bar + "]", "{}/{}"".format(i+1, 25)
            self.update()
            frame = camera.get_image_not_base64()
            cv2.imwrite(
                f"./{self.method}/input/liveness_detection/liveness_detection"
                + str(detect_counter)
                + ".png",
                frame,
            )
            detect_counter += 1

            # 位置ずれ計算用
            current_position = frame
            current_position = cv2.cvtColor(
                current_position, cv2.COLOR_RGB2GRAY)
            current_center = crop_center(current_position, 300, 300)
            match = cv2.matchTemplate(
                current_center, org_position, cv2.TM_CCOEFF_NORMED)
            _, _, _, max_pt = cv2.minMaxLoc(match)
            pt = max_pt
            with open(
                f"./{self.method}/input/liveness_detection/ld_result.txt", mode="a", encoding="utf-8"
            ) as f:
                f.write("dx = " + str(pt[1] - 140) + " : ")
            dx_list.append(pt[1] - 140)

            # R値割合計算用
            crop_image = crop_center2(frame, 300, 300)
            current_redrate = liveness_detection(crop_image)
            with open(
                f"./{self.method}/input/liveness_detection/ld_result.txt", mode="a", encoding="utf-8"
            ) as f:
                f.write("red_rate = " + str(current_redrate) + "\n")
            ld_list.append(current_redrate)
            if after_score > current_redrate:
                after_score = current_redrate
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cv2.imwrite(
            f"./{self.method}/input/liveness_detection/detection_after.png", frame)

        with open(
            f"./{self.method}/input/liveness_detection/ld_result.txt", mode="a", encoding="shift_jis"
        ) as f:
            f.write("red_rate1 = " + str(red_rate1) + "\n")
            f.write("after = " + str(after_score) + "\n")

        ld_result_list = []
        dx_result_list = []
        ld_result = True
        dx_result = True
        link_counter = 0

        for i in range(len(ld_list) - 3):  # R値割合が減少すればTrueを返す
            if ld_list[i + 3] - ld_list[i + 2] < 0:
                ld_result = True
            else:
                ld_result = False
            ld_result_list.append(ld_result)

            if dx_list[i + 3] - dx_list[i + 2] > 0:  # ズレ値が増加すればTrueを返す
                dx_result = True
            else:
                dx_result = False
            dx_result_list.append(dx_result)

        with open(
            f"./{self.method}/input/liveness_detection/ld_result.txt", mode="a", encoding="shift_jis"
        ) as f:
            f.write("ld_list = " + str(ld_result_list) + "\n")
            f.write("dx_list = " + str(dx_result_list) + "\n")

        for i in range(len(ld_result_list)):
            if ld_result_list[i] == dx_result_list[i]:
                link_counter += 1
        print(link_counter)
        print(len(ld_result_list))

        if link_counter / len(ld_result_list) > 0.7:
            link_validation_flag = True

        with open(
            f"./{self.method}/input/liveness_detection/ld_result.txt", mode="a", encoding="shift_jis"
        ) as f:
            f.write("link_validation = " +
                    str(link_counter / len(ld_result_list)) + "\n")

        with open(
            f"./{self.method}/input/liveness_detection/ld_result.txt", mode="a", encoding="shift_jis"
        ) as f:
            f.write("\n")

        if red_rate1 - after_score >= 0.02 and link_validation_flag == True:
            Text_ld.value = f"生体検知成功です"
            print("生体検知成功です\n\n")
        elif red_rate1 - after_score >= 0.02 and link_validation_flag == False:
            Text_ld.value = f"生体検知失敗です(リンク検証失敗)"
            print("生体検知失敗です(リンク検証失敗)\n\n")
        elif red_rate1 - after_score < 0.02 and link_validation_flag == True:
            Text_ld.value = f"生体検知失敗です(閾値未満)"
            print("生体検知失敗です(閾値未満)\n\n")
        else:
            Text_ld.value = f"生体検知失敗です(リンク検証失敗＆閾値未満)"
            print("生体検知失敗です(リンク検証失敗＆閾値未満)\n\n")
        self.update()

    def template_matching_zncc(self, temp_file, auth_counter, ns):
        # 入力画像とテンプレート画像をで取得
        highscore = 0
        count = 0
        Text_auth = ft.Text(color="white", selectable=True)
        self.append_cnosole("-----------------------------------\n認証を行います")
        self.append_console_Text(Text_auth)
        self.update()
        print("認証を行います\n\n")
        auth_before = False

        # ----------LBP処理-----------------
        auth_file = convert_file(
            f"./{self.method}/input/auth" + str(auth_counter) + ".png", self.method)
        # ----------------------------------

        auth_file[auth_file < 0] = 0
        auth_file[auth_file > 255] = 255
        auth_file = np.asarray(auth_file, dtype=np.uint8)
        cv2.imwrite(f"./{self.method}/input/convert_auth.png", auth_file)

        temp = cv2.cvtColor(temp_file, cv2.COLOR_RGB2GRAY)

        # テンプレート画像の平均画素値
        mu_t = np.mean(temp)
        # テンプレート画像 - 認証画像の平均
        temp = temp - mu_t

        for i in range(45):  # 探索するyのピクセル数
            for k in range(120):  # 探索するxのピクセル数
                left = 120 + k  # 画像左辺x座標
                right = 420 + k  # 画像右辺x座標
                top = 120 + i  # 画像上辺y座標
                bottom = 420 + i  # 画像下辺y座標

                q = []

                # ---------マッチングする認証画像のクロッピング-------------
                img2 = auth_file[top:bottom, left:right]
                # -------------------------------------------------
                # -----------クロッピングした画像の分割処理-------------
                for _, ig in enumerate(ImgSplit(img2), 1):
                    q.append(ig)
                # ------------------------------------------------
                # ----------分割した画像を並び替えて結合処理------------
                im_auth_list = rand_auth2(ns, q)
                res_auth_file = concat_tile(im_auth_list)
                # -------------------------------------------------

                max_value = template_matching_zncc2(res_auth_file, temp)

                if max_value > highscore:
                    highscore = max_value

                count = count + 1
                if auth_before == False:
                    auth_before = True

        with open(f"./{self.method}/input/matching_result.txt", mode="a", encoding="shift_jis") as f:
            f.write(str(highscore) + "\n")
        Text_auth.value = f"matching score is {highscore}"
        print("matching score is " + str(highscore))
        if highscore >= 0.1:
            Text_auth.value = f"{Text_auth.value}\n 認証成功です"
            print("認証成功です")
        else:
            Text_auth.value = f"{Text_auth.value}\n 認証失敗です"
            print("認証失敗です")
        self.update()

    def save_template(self, frame, temp_counter, ns_org):
        # self.append_cnosole(f"save_template, {temp_counter}")

        print("save_template", temp_counter)
        write_now_temp_number(temp_counter,self.method)
        cv2.imwrite(f"./{self.method}/input/temp" +
                    str(temp_counter) + ".png", frame)

        temp_file = convert_file(
            f"./{self.method}/input/temp" + str(temp_counter) + ".png", self.method)
        temp_file_center = crop_center(temp_file, 300, 300)

        # 今回は，時系列ではなく，爪で認証できるかが重要．たぶん，保存ファイル先は関係ない(そもそもwriteしたファイルを読み込まない)
        # cv2.imwrite("./input/temp0_center.png", temp_file_center)

        cv2.imwrite(f"./{self.method}/input/temp_center.png", temp_file_center)

        # ----------tempファイル分割--------------
        p = []
        for number, ig in enumerate(ImgSplit(temp_file_center), 1):
            p.append(ig)
            # 保存先フォルダの指定
        # ---------------------------------------

        # ------並び替え順序作成------------------
        im_temp_list = rand_auth2(ns_org, p)  # ←分割ブロックの数を入力
        # self.append_cnosole(f"ns_org {ns_org}")
        print("ns_org", ns_org)
        # --------------------------------------

        # ------結合ファイル作成--------------------
        res_temp_file = concat_tile(im_temp_list)
        cv2.imwrite(f"./{self.method}/input/result_temp" +
                    str(temp_counter) + ".png", res_temp_file)
        # --------------------------------------

    def save_certification(self, frame, temp_counter, auth_counter, ns, camera):

        write_now_auth_number(auth_counter,self.method)
        cv2.imwrite(f"./{self.method}/input/auth" +
                    str(auth_counter) + ".png", frame)

        temp = cv2.imread(
            f"./{self.method}/input/result_temp" + str(temp_counter) + ".png")

        # self.append_cnosole(f"対象テンプレート画像No {temp_counter}")
        # self.append_cnosole(f"ns : {ns}")
        print(f"対象テンプレート画像No {temp_counter}")
        print(f"ns : {ns}")

        cv2.imwrite(
            f"./{self.method}/input/liveness_detection/ld_before.png", frame)

        ld_cropped = crop_center2(frame, 300, 300)
        cv2.imwrite(
            f"./{self.method}/input/liveness_detection/ld_before_cropped.png", ld_cropped)
        red_rate1 = liveness_detection(ld_cropped)
        with open(
            f"./{self.method}/input/liveness_detection/ld_result.txt", mode="a", encoding="shift_jis"
        ) as f:
            f.write("before = " + str(red_rate1) + "\n")

        thread1 = threading.Thread(
            target=self.template_matching_zncc, args=(temp, auth_counter, ns)
        )
        thread2 = threading.Thread(
            target=self.ld_overall, args=(camera, red_rate1))

        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        self.append_cnosole("---------------------------\n\n")
