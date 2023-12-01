from pyzbar.pyzbar import decode
from PIL import Image


def ascii2num(acode_list):

    t = [acode_list[i: i+1] for i in range(0, len(acode_list), 1)]

    num_code = ""
    for j in range(len(t)):
        num = ord(t[j])
        # print(num6)
        # print(bin(num6))
        num2 = bin(num)[2:]
        num3 = num2.zfill(7)

        if (j == len(t)-1):
            # print("AAA")
            # print(str(num3)[0])
            if (int(str(num3)[0]) == 0):
                num3 = num3[1:]

        num_code = num_code + str(num3)

    k = [num_code[i: i+5] for i in range(0, len(num_code), 5)]

    res_list = []

    for i in range(len(k)):
        num_int = int(k[i], 2)
        res_list.append(num_int)

    print(res_list)
    return res_list


def hoge(acode_list):
    t = [acode_list[i: i + 1] for i in range(0, len(acode_list), 1)]
    num_code = ""
    for j in range(len(t)):
        num = ord(t[j])
        num2 = bin(num)[2:]
        num3 = num2.zfill(7)

        if j == len(t) - 1:
            if int(str(num3)[0]) == 0:
                num3 = num3[1:]
        num_code = num_code + str(num3)
    print(num_code)
    k = [num_code[i: i + 5] for i in range(0, len(num_code), 5)]

    res_list = []

    for i in range(len(k)):
        num_int = int(k[i], 2)
        res_list.append(num_int)

    return res_list


d = decode(Image.open("tume_data/ggy/qrcode.png"))
print(d[0][0].decode("utf-8", "ignore"))
print(hoge(d[0][0].decode("utf-8", "ignore").split(":")[1]))
print(ascii2num(d[0][0].decode("utf-8", "ignore").split(":")[1]))
