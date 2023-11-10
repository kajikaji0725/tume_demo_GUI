import numpy as np
from skimage import io
from skimage.color import rgb2gray
from skimage.feature import local_binary_pattern
from tqdm import tqdm
from PIL import Image
from pyzbar.pyzbar import decode
import cv2
import threading
import time
import os
import qrcode
import random
import glob
import re

camera = None


def write_now_temp_number(temp_number):
    path = f"{os.path.normpath(os.getcwd())}"
    with open(f"{path}/temp_number.txt", "w") as f:
        f.write(temp_number.__str__())


def read_now_temp_number():
    path = f"{os.path.normpath(os.getcwd())}"
    try:
        with open(f"{path}/temp_number.txt", "r") as f:
            return int(f.read())
    except FileNotFoundError:
        return None


def write_now_auth_number(auth_number):
    path = f"{os.path.normpath(os.getcwd())}"
    with open(f"{path}/auth_number.txt", "w") as f:
        f.write(auth_number.__str__())


def read_now_auth_number():
    path = f"{os.path.normpath(os.getcwd())}"
    try:
        with open(f"{path}/auth_number.txt", "r") as f:
            return int(f.read())
    except FileNotFoundError:
        return None


def get_dir_username(username):
    dir = os.path.normpath(os.getcwd()).split(os.sep)[-1]
    path = "./"
    print(dir, username)
    if not dir == "tume_data" or dir in username:
        path = "../"
    username = os.listdir(path)
    return username


def check_current_dir(username):
    dir_user_name = os.path.normpath(os.getcwd())
    dir_user_name = dir_user_name.split(os.sep)
    if dir_user_name[len(dir_user_name) - 1] in username:
        os.chdir("../")


def move_dir(dir):
    print("遷移前",os.getcwd())
    os.chdir(f"{dir}")
    print("遷移後",os.getcwd())


def reading_qrcode_for_png():
    img = Image.open("qrcode.png")
    codes = decode(img)
    inputX = codes[0][0].decode("utf-8", "ignore")
    read_result = inputX.split(":")
    numcode = ascii2num(read_result[1])
    ns = numcode
    ns_org = numcode
    time.sleep(0.5)
    return ns, ns_org


def jen_rand(a, b):
    ns = list(range(a, b + 1))
    random.shuffle(ns)
    return ns


def num2ascii(num_list):
    newlist = ""
    for i in num_list:
        bin_num = bin(i)
        bin_num = bin_num[2:]
        zero_num = bin_num.zfill(5)
        newlist = newlist + str(zero_num)

    v = [newlist[i : i + 7] for i in range(0, len(newlist), 7)]
    acode_list = ""

    for i in range(len(v)):
        num5 = int(str(v[i]), 2)
        asc = chr(num5)
        acode_list = acode_list + asc

    return acode_list


def edit_contrast(image, gamma):
    """コントラスト調整"""
    look_up_table = [
        np.uint8(255.0 / (1 + np.exp(-gamma * (i - 128.0) / 255.0))) for i in range(256)
    ]
    result_image = np.array(
        [look_up_table[value] for value in image.flat], dtype=np.uint8
    )
    result_image = result_image.reshape(image.shape)
    return result_image


def ascii2num(acode_list):
    t = [acode_list[i : i + 1] for i in range(0, len(acode_list), 1)]

    num_code = ""
    for j in range(len(t)):
        num = ord(t[j])
        num2 = bin(num)[2:]
        num3 = num2.zfill(7)

        if j == len(t) - 1:
            if int(str(num3)[0]) == 0:
                num3 = num3[1:]
        num_code = num_code + str(num3)
    k = [num_code[i : i + 5] for i in range(0, len(num_code), 5)]

    res_list = []

    for i in range(len(k)):
        num_int = int(k[i], 2)
        res_list.append(num_int)

    print(res_list)
    return res_list


def convert_file(in_filename):
    radius = 3
    point = 22 * radius
    method = "default"

    # LBP変換
    image = io.imread(in_filename)
    image = rgb2gray(image)
    lbp = local_binary_pattern(image, point, radius, method=method)
    cv2.imwrite("./input/sample.png", lbp)

    return lbp


def crop_center(img, cropx, cropy):  # グレースケール用
    y, x = img.shape
    startx = x // 2 - (cropx // 2)
    starty = y // 2 - (cropy // 2) + 50
    return img[starty : starty + cropy, startx : startx + cropx]


def ImgSplit(img):
    height = 60
    width = 60
    buff = []
    # 縦の分割枚数
    for h1 in range(5):
        # 横の分割枚数
        for w1 in range(5):
            w2 = w1 * width
            h2 = h1 * height
            img2 = img[h2 : height + h2, w2 : width + w2]
            buff.append(img2)
    return buff


def rand_auth2(ns, q):
    new_list2 = []
    for l in enumerate(ns):
        new_list2.append(q[l[1] - 1])
        # new_list.append(p[l])
    result = list(split_list(new_list2, 5))
    return result


def split_list(l, n):
    for idx in range(0, len(l), n):
        yield l[idx : idx + n]


def concat_tile(im_list_2d):
    return cv2.vconcat([cv2.hconcat(im_list_h) for im_list_h in im_list_2d])


def crop_center2(img, cropx, cropy):  # 3チャンネル用→カラー
    y, x, z = img.shape
    startx = x // 2 - (cropx // 2)
    starty = y // 2 - (cropy // 2) + 50
    return img[starty : starty + cropy, startx : startx + cropx]


def liveness_detection(img):
    imgArray = np.array(img)
    tmp = np.where(imgArray >= 215, 0, imgArray)
    l_R = np.where(tmp[:, :, 0] > 150, True, False)
    l_G = np.where(tmp[:, :, 1] > 150, True, False)
    l_B = np.where(tmp[:, :, 2] > 150, True, False)
    n_R = np.count_nonzero(l_B == True)
    n_B = np.count_nonzero(l_G == True)
    n_G = np.count_nonzero(l_R == True)

    red_rate = n_R / (n_B + n_R + n_G)

    return red_rate


def create_user(username):
    if not os.path.exists(str(username)):  # ディレクトリがなかったら
        os.makedirs(str(username))
        # os.makedirs("./"+str(ans)+"./input")
        os.makedirs(str(username) + "./input/liveness_detection")
    else:
        return False
    dirc = str(username)
    os.chdir(dirc)
    print("現在のディレクトリ",os.getcwd())

    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=2,
        border=4,
    )

    ns_org = jen_rand(1, 25)
    ns = ns_org
    with open("./input/ID_backup.txt", mode="a", encoding="shift_jis") as f:
        f.write(str(ns_org))

    print("ns_org",ns_org)
    asc = num2ascii(ns_org)

    qr.add_data(str(username) + ":")

    qr.add_data(str(asc))
    # qr.add_data(str(ns_res))
    qr.make()
    img = qr.make_image()
    img.save("./qrcode.png")

    return True


def template_matching_zncc2(auth, temp):
    score = 0

    # 認証画像の平均画素値
    mu_r = np.mean(auth)

    # 認証画像 - 認証画像の平均
    auth = auth - mu_r

    # ZNCCの計算式
    num = np.sum(auth * temp)
    den = np.sqrt(np.sum(auth**2)) * np.sqrt(np.sum(temp**2))

    if den == 0:
        score = 0

    score = num / den
    return score


def template_matching_zncc(temp_file, auth_counter, ns):
    # 入力画像とテンプレート画像をで取得
    highscore = 0
    count = 0

    print("認証を行います\n\n")
    auth_before = False

    # ----------LBP処理-----------------
    auth_file = convert_file("./input/auth" + str(auth_counter) + ".png")
    # ----------------------------------

    auth_file[auth_file < 0] = 0
    auth_file[auth_file > 255] = 255
    auth_file = np.asarray(auth_file, dtype=np.uint8)
    cv2.imwrite("./input/convert_auth.png", auth_file)

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

    with open("./input/matching_result.txt", mode="a", encoding="shift_jis") as f:
        f.write(str(highscore) + "\n")
    print("matching score is " + str(highscore))
    if highscore >= 0.04:
        print("認証成功です")
    else:
        print("認証失敗です")


def ld_overall(camera, red_rate1):
    # 生体検知
    dx_list = []
    ld_list = []

    link_validation_flag = False

    org_position = cv2.imread("./input/liveness_detection/ld_before.png")
    org_position = cv2.cvtColor(org_position, cv2.COLOR_RGB2GRAY)

    print("生体検知を行います")
    print("指をもう少し前に押しこんでください")
    time.sleep(0.2)
    detect_counter = 0
    after_score = 1

    ta = time.time()
    for i in tqdm(range(25)):
        frame = camera.get_image_not_base64()
        cv2.imwrite(
            "./input/liveness_detection/liveness_detection"
            + str(detect_counter)
            + ".png",
            frame,
        )
        detect_counter += 1

        # 位置ずれ計算用
        current_position = frame
        current_position = cv2.cvtColor(current_position, cv2.COLOR_RGB2GRAY)
        current_center = crop_center(current_position, 300, 300)
        match = cv2.matchTemplate(current_center, org_position, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_pt = cv2.minMaxLoc(match)
        pt = max_pt
        with open(
            "./input/liveness_detection/ld_result.txt", mode="a", encoding="utf-8"
        ) as f:
            f.write("dx = " + str(pt[1] - 140) + " : ")
        dx_list.append(pt[1] - 140)

        # R値割合計算用
        crop_image = crop_center2(frame, 300, 300)
        current_redrate = liveness_detection(crop_image)
        with open(
            "./input/liveness_detection/ld_result.txt", mode="a", encoding="utf-8"
        ) as f:
            f.write("red_rate = " + str(current_redrate) + "\n")
        ld_list.append(current_redrate)
        if after_score > current_redrate:
            after_score = current_redrate
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.imwrite("./input/liveness_detection/detection_after.png", frame)

    with open(
        "./input/liveness_detection/ld_result.txt", mode="a", encoding="shift_jis"
    ) as f:
        f.write("red_rate1 = " +str(red_rate1) + "\n")
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
        "./input/liveness_detection/ld_result.txt", mode="a", encoding="shift_jis"
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
        "./input/liveness_detection/ld_result.txt", mode="a", encoding="shift_jis"
    ) as f:
        f.write("link_validation = " + str(link_counter / len(ld_result_list)) + "\n")

    with open(
        "./input/liveness_detection/ld_result.txt", mode="a", encoding="shift_jis"
    ) as f:
        f.write("\n")

    if red_rate1 - after_score >= 0.02 and link_validation_flag == True:
        print("生体検知成功です\n\n")
    elif red_rate1 - after_score >= 0.02 and link_validation_flag == False:
        print("生体検知失敗です(リンク検証失敗)\n\n")
    elif red_rate1 - after_score < 0.02 and link_validation_flag == True:
        print("生体検知失敗です(閾値未満)\n\n")
    else:
        print("生体検知失敗です(リンク検証失敗＆閾値未満)\n\n")


def save_template(frame, temp_counter, ns_org):
    
    print("save_template",temp_counter)
    write_now_temp_number(temp_counter)
    cv2.imwrite("./input/temp" + str(temp_counter) + ".png", frame)

    temp_file = convert_file("./input/temp" + str(temp_counter) + ".png")
    temp_file_center = crop_center(temp_file, 300, 300)

    # 今回は，時系列ではなく，爪で認証できるかが重要．たぶん，保存ファイル先は関係ない(そもそもwriteしたファイルを読み込まない)
    # cv2.imwrite("./input/temp0_center.png", temp_file_center)

    cv2.imwrite(f"./input/temp_center.png", temp_file_center)

    # ----------tempファイル分割--------------
    p = []
    for number, ig in enumerate(ImgSplit(temp_file_center), 1):
        p.append(ig)
        # 保存先フォルダの指定
    # ---------------------------------------

    # ------並び替え順序作成------------------
    im_temp_list = rand_auth2(ns_org, p)  # ←分割ブロックの数を入力
    print("ns_org",ns_org)
    # --------------------------------------

    # ------結合ファイル作成--------------------
    res_temp_file = concat_tile(im_temp_list)
    cv2.imwrite("./input/result_temp" + str(temp_counter) + ".png", res_temp_file)
    # --------------------------------------


def save_certification(frame, temp_counter, auth_counter, ns, camera):
    
    write_now_auth_number(auth_counter)
    cv2.imwrite("./input/auth" + str(auth_counter) + ".png", frame)

    temp = cv2.imread("./input/result_temp" + str(temp_counter) + ".png")
    
    print(f"対象テンプレート画像No {temp_counter}")

    cv2.imwrite("./input/liveness_detection/ld_before.png", frame)

    ld_cropped = crop_center2(frame, 300, 300)
    cv2.imwrite("input/liveness_detection/ld_before_cropped.png", ld_cropped)
    red_rate1 = liveness_detection(ld_cropped)
    with open(
        "./input/liveness_detection/ld_result.txt", mode="a", encoding="shift_jis"
    ) as f:
        f.write("before = " + str(red_rate1) + "\n")

    thread1 = threading.Thread(
        target=template_matching_zncc, args=(temp, auth_counter, ns)
    )
    thread2 = threading.Thread(target=ld_overall, args=(camera, red_rate1))

    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
