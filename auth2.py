import numpy as np
import cv2
import pyws as m
import winxpgui
import sys
import msvcrt
import time
from datetime import datetime

from PIL import ImageGrab
from PIL import Image
from pathlib import Path
from pyzbar.pyzbar import decode

import os
import glob
import skimage

from skimage import io
from skimage.color import rgb2gray
from skimage.feature import local_binary_pattern


import random
import qrcode

from tqdm import tqdm

import threading

# ----------------------------------------------------------------
# inputフォルダの中にある画像をLBP変換してoutputフォルダに出力
# tempは透視変換して中央を保存
# ----------------------------------------------------------------

#LBP変換のポイント数，半径，メソッド（ここでパラメータ変更する）
radius = 3
point = 22 * radius
method = "default"

# テンプレートのパラメータ(中央tmpsize*tmpsizeのpixelを切り出して透視変換)
tmpsize = 256

#ファイル保存用連番変数
temp_counter = 0
auth_counter = 0


def crop_center(img, cropx, cropy):#グレースケール用
    y,x = img.shape
    startx = x//2-(cropx//2)
    starty = y//2-(cropy//2)+50
    return img[starty:starty+cropy,startx:startx+cropx]

def crop_center2(img, cropx, cropy):#3チャンネル用→カラー
    y,x,z = img.shape
    startx = x//2-(cropx//2)
    starty = y//2-(cropy//2)+50
    return img[starty:starty+cropy,startx:startx+cropx]


def concat_tile(im_list_2d):
  return cv2.vconcat([cv2.hconcat(im_list_h) for im_list_h in im_list_2d])

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
      img2 = img[h2: height + h2, w2: width + w2] 
      buff.append(img2)
  return buff

def split_list(l,n):
  for idx in range(0,len(l),n):
    yield l[idx:idx +n]

"""def rand_temp(a, b, k):
  ns = list(range(a,b+1)) 
  ns_temp = ["./result/res_temp{}.png".format(n)for n in ns]
  ns_auth = ["./result/res_auth{}.png".format(n)for n in ns]
  print(ns)
  ns_temp = [cv2.imread(n) for n in ns_temp ]
  ns_auth = [cv2.imread(n) for n in ns_auth ]
  random.shuffle(ns_temp)
  result_temp =split_list(ns_temp,16)
  random.shuffle(ns_auth)
  result_auth =split_list(ns_auth,16)

  return result_temp, result_auth"""


def rand_auth2(ns,q):
  new_list2 = []
  for l in enumerate(ns):
    #print(l)
    #print(p[l[1]])
    #print("AAA")
    #print(l[1])
    #print(type(l[1]))

    new_list2.append(q[l[1]-1])
    #new_list.append(p[l])
  result =list(split_list(new_list2,5))

  return result

def num2alpha(num):
    if num<=26:
        return chr(64+num)
    elif num%26==0:
        return num2alpha(num//26-1)+chr(90)
    else:
        return num2alpha(num//26)+chr(64+num%26)
        
def alpha2num(alpha):
    num=0
    for index, item in enumerate(list(alpha)):
        num += pow(26,len(alpha)-index-1)*(ord(item)-ord('A')+1)
    return num

def edit_contrast(image, gamma):
    """コントラスト調整"""
    look_up_table = [np.uint8(255.0 / (1 + np.exp(-gamma * (i - 128.) / 255.)))
        for i in range(256)]
    result_image = np.array([look_up_table[value]
                             for value in image.flat], dtype=np.uint8)
    result_image = result_image.reshape(image.shape)
    return result_image


def trim(temp_file):

    # トリミングのサイズ(ピクセル)
    new_size = 256

    # 画像読み込み
    img = Image.open(temp_file)

    # 中心座標を計算
    center_x = int(img.width / 2) 
    center_y = int(img.height / 2)

    # トリミング
    img_crop = img.crop((center_x - new_size / 2, center_y - new_size / 2, center_x + new_size / 2, center_y + new_size / 2))

    # トリミングした画像を保存
    img_crop.save('input/temp' + str(temp_counter-1) + '_center.png', 'JPEG', quality=10)
    img_crop.save('trimmed/temp' + str(temp_counter-1) + '_center.png', 'JPEG', quality=10)

def convert_file(in_filename):
  radius = 3
  point = 22 * radius
  method = "default"

  # LBP変換
  image = io.imread(in_filename)
  image = rgb2gray(image)
  lbp = local_binary_pattern(image, point, radius, method = method)
  cv2.imwrite("./input/sample.png",lbp)
  
  return lbp


def jen_rand(a,b):
  new_list = []
  ns = list(range(a,b+1))
  random.shuffle(ns)
  return ns


def print_list(ns):
    return  "["+",".join([str(n) for n in ns])+"]"

def loader(s):
    l = list(map(int,s[1:-1].split(",")))
    return l

def num2ascii(num_list):
    newlist =""
    for i in num_list:
        bin_num = bin(i)
        #print(bin_num)
        bin_num = bin_num[2:]
        zero_num = bin_num.zfill(5)
        
        newlist = newlist + str(zero_num)
    

    v = [newlist[i: i+7] for i in range(0, len(newlist), 7)]

    

    acode_list = ""

    for i in range(len(v)):
        num5 = int(str(v[i]),2)
        asc = chr(num5)
        
        #if(i == len):
        #   print()
        #   asc = asc*2 + int(v[i+1])
        acode_list = acode_list + asc

    
    return acode_list

def ascii2num(acode_list):

    
    t = [acode_list[i: i+1] for i in range(0, len(acode_list), 1)]
    

    num_code =""
    for j in range(len(t)):
        num = ord(t[j])
        #print(num6)
        #print(bin(num6))
        num2 = bin(num)[2:]
        num3 = num2.zfill(7)
        
        if(j == len(t)-1):
            #print("AAA")
            #print(str(num3)[0])
            if(int(str(num3)[0])==0):
                num3 = num3[1:]
                

        num_code = num_code + str(num3)

    

    k =  [num_code[i: i+5] for i in range(0, len(num_code), 5)]
    

    res_list=[]
    
    for i in range(len(k)):
        num_int = int(k[i],2)
        res_list.append(num_int)
        
    print(res_list)
    return res_list

def ld_overall():
    #生体検知

    dx_list =[]
    ld_list =[]
    link_validation_flag = False

    org_position = cv2.imread("./input/liveness_detection/ld_before.png")
    org_position = cv2.cvtColor(org_position, cv2.COLOR_RGB2GRAY)

    print("生体検知を行います")
    print("指をもう少し前に押しこんでください")
    time.sleep(0.2)
    detect_counter =0
    after_score = 1

    # with open("./input/liveness_detection/ld_result.txt", mode='a',encoding = "shift_jis") as f:
    #         f.write("forward process"+"\n")

    ta = time.time()
    for i in tqdm(range(25)):
        ret, frame = cap0.read()
        cv2.imshow('frame',frame)
        cv2.imwrite("./input/liveness_detection/liveness_detection"+str(detect_counter)+".png",frame)
        detect_counter += 1
        #time.sleep(0.15)


        #位置ずれ計算用
        #print("")
        current_position = frame
        #current_position = cv2.imread("./input/liveness_detection/liveness_detection_forward"+str(detect_counter-1)+".png")
        current_position = cv2.cvtColor(current_position, cv2.COLOR_RGB2GRAY)
        current_center = crop_center(current_position,300,300)
        match = cv2.matchTemplate(current_center, org_position, cv2.TM_CCOEFF_NORMED)
        min_value, max_value, min_pt, max_pt = cv2.minMaxLoc(match)
        pt = max_pt
        with open("./input/liveness_detection/ld_result.txt", mode='a',encoding = "utf-8") as f:
            f.write('dx = ' +str(pt[1]- 140)+" : ")
        dx_list.append(pt[1]- 140)
        #print("Δx = " +str(pt[1]- 140))

        #R値割合計算用
        crop_image = crop_center2(frame,300,300)
        current_redrate = liveness_detection(crop_image)
        with open("./input/liveness_detection/ld_result.txt", mode='a',encoding = "utf-8") as f:
            f.write("red_rate = " + str(current_redrate) +"\n")
        ld_list.append(current_redrate)
        if(after_score> current_redrate):
            after_score = current_redrate
        #print("red_rate = "+str(current_redrate))
        #print("")
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    tb = time.time()
    #print(tb-ta)



    cv2.imwrite("./input/liveness_detection/detection_after.png",frame)
    ld_after = frame


    # red_rate2 = liveness_detection(ld_after)
    # if(after_score> red_rate2):
    #         after_score = red_rate2

    # detect_counter = 0
    # with open("./input/liveness_detection/ld_result.txt", mode='a',encoding = "shift_jis") as f:
    #         f.write("backward process"+"\n")

    # for i in range(10):
    #     ret, frame = cap0.read()
    #     cv2.imshow('frame',frame)
    #     cv2.imwrite("./input/liveness_detection/liveness_detection_backword"+str(detect_counter)+".png",frame)
    #     detect_counter += 1
    #     #time.sleep(0.15)


    #     #位置ずれ計算用
    #     #print("")
    #     current_position = frame
    #     #current_position = cv2.imread("./input/liveness_detection/liveness_detection_backword"+str(detect_counter-1)+".png")
    #     current_position = cv2.cvtColor(current_position, cv2.COLOR_RGB2GRAY)
    #     current_center = crop_center(current_position,300,300)
    #     match = cv2.matchTemplate(current_center, org_position, cv2.TM_CCOEFF_NORMED)
    #     min_value, max_value, min_pt, max_pt = cv2.minMaxLoc(match)
    #     pt = max_pt
    #     with open("./input/liveness_detection/ld_result.txt", mode='a',encoding = "shift_jis") as f:
    #         f.write('dx = ' +str(pt[1]- 140)+" : ")
    #     dx_list.append(pt[1]- 140)
    #     #print("Δx = " +str(pt[1]- 140))

    #     #R値割合計算用
    #     crop_image = crop_center2(frame,300,300)
    #     current_redrate = liveness_detection(crop_image)
    #     with open("./input/liveness_detection/ld_result.txt", mode='a',encoding = "shift_jis") as f:
    #         f.write("red_rate = " + str(current_redrate) +"\n")
    #     ld_list.append(current_redrate)
    #     if(after_score> current_redrate):
    #         after_score = current_redrate
    #     #print("red_rate = "+str(current_redrate))
    #     #print("")


    with open("./input/liveness_detection/ld_result.txt", mode='a',encoding = "shift_jis") as f:
        f.write("after = " + str(after_score)+"\n")

    #print("before = "+str(red_rate1)+", after = "+str(after_score)+"\n")

    # print("---------------------確認用------------------------")
    # print(ld_list)
    # print(dx_list)
    # print("ld_min index = "+str(np.argmin(ld_list)))
    # print("ld_max index = "+str(np.argmax(ld_list)))
    min_ld_index = int(np.argmin(ld_list))
    max_ld_index = int(np.argmax(ld_list))
    max_dx = max(dx_list)

    ld_result_list = []
    dx_result_list = []
    ld_result = True
    dx_result = True
    link_counter = 0

    for i in range(len(ld_list)-3):#R値割合が減少すればTrueを返す
        if(ld_list[i+3]-ld_list[i+2]<0):
            ld_result = True
        else:
            ld_result = False
        ld_result_list.append(ld_result)

        if(dx_list[i+3]-dx_list[i+2]>0):#ズレ値が増加すればTrueを返す
            dx_result = True
        else:
            dx_result = False
        dx_result_list.append(dx_result)

    with open("./input/liveness_detection/ld_result.txt", mode='a',encoding = "shift_jis") as f:
        f.write("ld_list = "+str(ld_result_list)+"\n")
        f.write("dx_list = "+str(dx_result_list)+"\n")
    #print(ld_result_list)
    #print(dx_result_list)

    for i in range(len(ld_result_list)):
        if(ld_result_list[i] == dx_result_list[i]):
            link_counter += 1
    print(link_counter)
    print(len(ld_result_list))

    if(link_counter/len(ld_result_list) >0.7):
        link_validation_flag = True

    with open("./input/liveness_detection/ld_result.txt", mode='a',encoding = "shift_jis") as f:
        f.write("link_validation = "+str(link_counter/len(ld_result_list))+"\n")



    # 旧方式での生体検知アルゴリズム
    # if(min_ld_index ==0 or min_ld_index == len(ld_list)):
    #     print("リンク検証失敗しました")
    # elif(dx_list[min_ld_index-1]==max_dx or dx_list[min_ld_index] ==max_dx or dx_list[min_ld_index+1]==max_dx):
    #     #print("成功です")
    #     if(max_ld_index == 0 or max_ld_index == 1 or max_ld_index == 2 or max_ld_index == len(ld_list) or max_ld_index == len(ld_list)-1 or max_ld_index == len(ld_list) -2 ):
    #         link_validation_flag = True



    with open("./input/liveness_detection/ld_result.txt", mode='a',encoding = "shift_jis") as f:
            f.write("\n")

    # if(red_rate1-after_score >=0.02 and link_validation_flag == True):
    #     print("生体検知成功です\n\n")
    # elif(red_rate1-after_score >=0.02 and link_validation_flag == False):
    #     print("生体検知失敗です(リンク検証失敗)\n\n") 
    # elif(red_rate1-after_score <0.02 and link_validation_flag == True):
    #     print("生体検知失敗です(閾値未満)\n\n") 
    # else:
    #     print("生体検知失敗です(リンク検証失敗＆閾値未満)\n\n")



def liveness_detection(img):
    imgArray = np.array(img)

    tmp = np.where(imgArray >=215,0,imgArray)  
    l_R = np.where(tmp[:,:,0]>150,True,False)
    l_G = np.where(tmp[:,:,1]>150,True,False)
    l_B = np.where(tmp[:,:,2]>150,True,False)
    n_R = np.count_nonzero(l_B == True)
    n_B = np.count_nonzero(l_G == True)
    n_G = np.count_nonzero(l_R == True)
            
    red_rate = n_R/(n_B+n_R+n_G)

    return red_rate


def template_matching_zncc2(auth, temp):

    score = 0

    
    # 認証画像の平均画素値
    mu_r = np.mean(auth)

    # 認証画像 - 認証画像の平均
    auth = auth - mu_r

   

    # ZNCCの計算式
    num = np.sum(auth * temp)
    den = np.sqrt(np.sum(auth ** 2)) * np.sqrt(np.sum(temp ** 2))

    if den == 0:
        score = 0
        
    score = num / den
    return score



def template_matching_zncc(temp_file,auth_counter,ns):
    # 入力画像とテンプレート画像をで取得

    t1 = time.time()
    highscore = 0
    count = 0    
    crop_time = 0
    split_time = 0
    concat_time = 0
    convert_time =0
    matching_time = 0

    
    #cv2.imshow("test",temp_file)
    #cv2.waitKey(0)
    print("認証を行います\n\n")
    auth_before = False
    
    #----------LBP処理-----------------
    auth_file =convert_file("./input/auth"+str(auth_counter-1)+".png")
    #----------------------------------

    auth_file[auth_file<0] = 0
    auth_file[auth_file>255] = 255
    auth_file = np.asarray(auth_file, dtype=np.uint8)
    cv2.imwrite("./input/convert_auth.png",auth_file)

    temp = cv2.cvtColor(temp_file, cv2.COLOR_RGB2GRAY)

     # テンプレート画像の平均画素値
    mu_t = np.mean(temp)
    # テンプレート画像 - 認証画像の平均
    temp = temp - mu_t

    t2 = time.time()
    process_time = t2 - t1
    #print("LBP process_time is " + str(process_time))


    for i in range(45): #探索するyのピクセル数
        for k in range(120): #探索するxのピクセル数
            left = 120 + k#画像左辺x座標
            right = 420 + k#画像右辺x座標
            top = 120 + i#画像上辺y座標
            bottom = 420 + i#画像下辺y座標

            q = []

            #crop_before = time.time()
            #---------マッチングする認証画像のクロッピング-------------
            img2 = auth_file[top : bottom, left : right]
            #cv2.imwrite("./result/auth_before"+".png",img2)
            #-------------------------------------------------
            #crop_after = time.time()
            #crop_time += crop_after-crop_before


            #split_before = time.time()
            #-----------クロッピングした画像の分割処理-------------
            for number, ig in enumerate(ImgSplit(img2), 1):
                q.append(ig)
                # 保存先フォルダの指定
                #cv2.imwrite("./result/res_auth"+str(number)+".png",ig)
            #------------------------------------------------
            #split_after = time.time()
            #split_time += split_after - split_before


            #concat_before = time.time()
            #----------分割した画像を並び替えて結合処理------------
            im_auth_list = rand_auth2(ns,q)
            res_auth_file = concat_tile(im_auth_list)    
            #cv2.imwrite("./result/res_result"+str(number)+".png",res_auth_file)       
            #-------------------------------------------------　
            #concat_after = time.time()
            #concat_time += concat_after - concat_before


          

            max_value =template_matching_zncc2(res_auth_file, temp)

            #matching_after = time.time()
            #matching_time += matching_after - matching_before


            #print(max_value)
            if(max_value > highscore):
              highscore = max_value

            count = count +1
            #print(max_value)
            if(auth_before == False):
                t3 = time.time()
                process_time2 = t3 -t2
                #print(process_time2)
                auth_before = True

    t4 = time.time()
    process_time3 = t4 -t1
    #print(process_time3)
    #time.sleep(0.5)
    with open("./input/matching_result.txt", mode='a',encoding = "shift_jis") as f:
            f.write(str(highscore)+"\n")
    print("matching score is "+str(highscore))
    if(highscore >= 0.04):
        print("認証成功です")
    else:
        print("認証失敗です")
    
    #return highscore



cap0 = cv2.VideoCapture(0)
cap0.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap0.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) 
cap0.set(cv2.CAP_PROP_FPS,60)
cv2.namedWindow('frame',cv2.WINDOW_NORMAL)

dir_flag = True

hogecount = 0

hoge_time1 = time.time()


while(True):

    # Capture frame-by-frame
    ret, frame = cap0.read()  #カメラアクセス

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray,(7,7),0)
    
    image = edit_contrast(blur, 5)
    cv2.imshow('frame',frame)

    


    # cv2.imwrite("./hoge/frame"+str(hogecount)+".png",gray)
    # cv2.imwrite("./hoge/frame_blur"+str(hogecount)+".png",image)
    # hogecount += 1
    # hoge_time2 = time.time()
    # print(hoge_time2 - hoge_time1)

    # 加工した画像からフレームQRコードを取得してデコードする

    #QRコード読み取り処理
    
    codes = decode(image)
    # print(codes)
    if len(codes) > 0:
        print(codes[0][0].decode('utf-8','ignore'))
        inputX=codes[0][0].decode('utf-8', 'ignore')
        #num0=input[1:len(input)-1]
        # コード内容を出力

        dirc = "./"+str(inputX)
        print("読み取り成功です")
        # cv2.imwrite("./hoge/result.png",gray)
        # cv2.imwrite("./hoge/result_blue.png",image)

        
        read_result = inputX.split(":")
        if(dir_flag == True):
            os.chdir(str(read_result[0])) #ディレクトリの移動
            print(os.getcwd())
            dir_flag = False

        

        # sample = list(read_result[1])
        numcode = ascii2num(read_result[1])


        # ns = list(map(alpha2num,sample))
        # ns_org = list(map(alpha2num,sample))
        ns = numcode
        ns_org = numcode



        print(ns)



        time.sleep(1)

    cv2.imshow('frame',frame)


    if msvcrt.kbhit(): # キーが押されているか
        kb = msvcrt.getch() # 押されていれば、キーを取得する
        if kb.decode() == 'q' :# やめるとき
            sys.exit()
        elif kb.decode() == 'z':
            ns_org = jen_rand(1,25)
            asc = num2ascii(ns_org)
            print(asc)

        elif kb.decode() == 'e':
            print("ユーザ登録を行います")
            print("ユーザIDを入力してください")
            ans = input()
            if not os.path.exists("./"+str(ans)):#ディレクトリがなかったら
                os.makedirs("./"+str(ans))
                #os.makedirs("./"+str(ans)+"./input")
                os.makedirs("./"+str(ans)+"./input/liveness_detection")
            dirc = "./"+str(ans)
            os.chdir(dirc)
            print(os.getcwd())

            qr = qrcode.QRCode(
                version=3,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=2,
                border=4
            )

            ns_org = jen_rand(1,25)
            ns = ns_org
            with open("./input/ID_backup.txt", mode='a',encoding = "shift_jis") as f:
                f.write(str(ns_org))
            
            print(ns_org)
            asc = num2ascii(ns_org)
            

            

            # ns_alpha = list(map(num2alpha,ns_org))#数値→アルファベット変換
            # print(ns_alpha)
            # ns_res ="".join(ns_alpha)
            # print(ns_res)

            qr.add_data(str(ans)+":")

            qr.add_data(str(asc))
            # qr.add_data(str(ns_res))
            qr.make()
            print(qr)
            img = qr.make_image()
            img.save('./qrcode.png')

        elif kb.decode() == 'w' :
            # ns = [22, 4, 3, 12, 20, 2, 19, 7, 23, 16, 24, 8, 17, 5, 6, 13, 11, 18, 1, 15, 25, 21, 10, 14, 9]
            # ns_org = [22, 4, 3, 12, 20, 2, 19, 7, 23, 16, 24, 8, 17, 5, 6, 13, 11, 18, 1, 15, 25, 21, 10, 14, 9]
            ns = [11, 23, 14, 20, 15, 4, 1, 9, 24, 16, 7, 13, 8, 10, 6, 17, 18, 22, 2, 12, 3, 25, 21, 5, 19]
            ns_org = [11, 23, 14, 20, 15, 4, 1, 9, 24, 16, 7, 13, 8, 10, 6, 17, 18, 22, 2, 12, 3, 25, 21, 5, 19]
            print("IDが入力されました")
        elif kb.decode() == 's':

            ans = input()
            dirc = "./"+str(ans)
            os.chdir(dirc)

            print(os.getcwd())


        elif kb.decode() == 't' :#テンプレート撮影コマンド
            try :#指定ウィンドウを画像保存するコード
                print("hoge")
                # handle = m.getid('frame')
                # rect = winxpgui.GetWindowRect(handle)
            except IndexError as e:
                print("Oops!  That was no valid number.  Try again...")
            print("テンプレート用画像を撮影します---------------")   
            print("この画像でよろしいですか?（YES→any key,NO→n）")
            ans = input()
            if(ans == "n"):
              continue
            print("撮影が完了しました---------------------------")

            #path = "./input/temp.png"
            cv2.imwrite("./input/temp"+ str(temp_counter) +".png",frame)
            

            temp_file =convert_file("./input/temp"+str(temp_counter)+".png")
            temp_file_center=crop_center(temp_file,300,300)
            cv2.imwrite("./input/temp0_center.png", temp_file_center)

            #----------tempファイル分割--------------
            #im_temp =cv2.imread('./input/temp0_center.png')
            p = []
            for number, ig in enumerate(ImgSplit(temp_file_center), 1):
                p.append(ig)
                # 保存先フォルダの指定            
                #cv2.imwrite("./result/res_temp"+str(number)+".png",ig)
            #---------------------------------------

            #------並び替え順序作成------------------
            im_temp_list = rand_auth2(ns_org,p)#←分割ブロックの数を入力
            print(ns_org)
            #print(im_temp_list)
            #--------------------------------------

            #------結合ファイル作成--------------------
            res_temp_file = concat_tile(im_temp_list)
            cv2.imwrite("./input/result_temp"+str(temp_counter)+".png", res_temp_file)
            #--------------------------------------

            temp_counter += 1


            continue

        elif kb.decode() == 'a' :
            try :#指定ウィンドウを画像保存するコード
                # handle = m.getid('frame')
                # rect = winxpgui.GetWindowRect(handle)
                print("hoge")
            except IndexError as e:
                print("Oops!  That was no valid number.  Try again...")
            print("認証用画像を撮影します-----------------------")
            print("この画像でよろしいですか?（YES→any key,NO→n）")
            ans = input()
            if(ans == "n"):
              continue
            print("撮影が完了しました----------------------------\n\n")
            if(temp_counter == 0):
              temp_counter = 1

            #path = "./input/auth.png"
            cv2.imwrite("./input/auth"+ str(auth_counter) +".png",frame)
            auth_counter += 1

            temp = cv2.imread("./input/result_temp"+str(temp_counter-1)+".png")

            cv2.imwrite("./input/liveness_detection/ld_before.png",frame)

            ld_cropped = crop_center2(frame,300,300)
            cv2.imwrite("input/liveness_detection/ld_before_cropped.png",ld_cropped)
            red_rate1 = liveness_detection(ld_cropped)
            with open("./input/liveness_detection/ld_result.txt", mode='a',encoding = "shift_jis") as f:
                f.write("before = " + str(red_rate1)+"\n")
            


            # thread1 =threading.Thread(target=template_matching_zncc(temp,auth_counter,ns))
            # thread2 = threading.Thread(target=ld_overall())

            thread1 =threading.Thread(target=template_matching_zncc,args =(temp,auth_counter,ns))
            thread2 = threading.Thread(target=ld_overall)


            thread1.start()
            thread2.start()
            thread1.join()
            thread2.join()


            continue



    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap0.release()
cv2.destroyAllWindows()