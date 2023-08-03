from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import *
from PIL import Image, ImageQt
import win32gui
import sys
import numpy as np
import time

sys.path.append(r'D:\Code\ORC\PaddleOCR')
from PaddleOCR import paddleocr
import json
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

hwnd = win32gui.FindWindow(None, '原神')
app = QApplication(sys.argv)
wid = QWindow.fromWinId(hwnd)
wid_pos = wid.position()
screen = QApplication.primaryScreen()
# t = time.clock()
# captured_screen = screen.grabWindow(hwnd,1735, 160, 645, 725).toImage().save('temp.jpg')
# print(time.clock() - t)
# t = time.clock()
lenx = 645
leny = 740
captured_screen = screen.grabWindow(hwnd, 1735, 160, lenx, leny).toImage()
# ocr = paddleocr.PaddleOCR(lang='ch', use_gpu=False)
# img = Image.fromqimage(captured_screen)
# text = ocr.ocr(np.array(img))
# print(text)
beginx = 20
beginy = 5
# print(
#     ocr.ocr(np.array(ImageQt.fromqimage(captured_screen.copy(beginx, beginy, lenx - beginx - 50, 70 - beginy).save('name.jpg')))))

beginx = 20
beginy = 90
# captured_screen.copy(beginx, beginy, 100, 40).save('place.jpg')
beginx = 10
beginy = 190
captured_screen.copy(beginx, beginy, 240, 60).save('main_attribute.jpg')
beginx = 55
beginy = 475
# captured_screen.copy(beginx, beginy, 360, 200).save('attributes.jpg')
# captured_screen.copy(20, 400, 100, 50).save('rank.jpg')
captured_screen.copy(10, 680, 360, 50).save('suite.jpg')

captured_screen.save('temp.jpg')

# name = self.grabWindowAndOCR(1740, 160, 480, 70, paddle_orc=True)[0]
# place = self.grabWindowAndOCR(1740, 240, 120, 50, paddle_orc=True)[0]
# main_attribute = self.grabWindowAndOCR(1750, 350, 240, 50, paddle_orc=True)[0]
# attributes = self.grabWindowAndOCR(1790, 620, 352, 220, paddle_orc=True)
# # attribute1 = self.grabWindowAndOCR(1785, 630, 360, 50, size.width(), size.height())
# # attribute2 = self.grabWindowAndOCR(1785, 680, 360, 51, size.width(), size.height())
# # attribute3 = self.grabWindowAndOCR(1785, 730, 360, 52, size.width(), size.height())
# # attribute4 = self.grabWindowAndOCR(1785, 780, 360, 53, size.width(), size.height())
# attributes = unpackAttributes(attributes)
#
# rank = self.grabWindowAndOCR(1765, 573, 70, 33, paddle_orc=False)


# sys.path.append(r'D:\Code\ORC\PaddleOCR')
# from PaddleOCR import paddleocr
# import json

# nameElementMap = {'安柏': '火', '可莉': '火', '迪卢克': '火', '班尼特': '火', '香菱': '火', '辛焱': '火', '胡桃': '火', '烟绯': '火',
#                   '芭芭拉': '水', '行秋': '水', '莫娜': '水', '达达利亚': '水',
#                   '凯亚': '冰', '重云': '冰', '七七': '冰', '迪奥娜': '冰', '甘雨': '冰', '罗莎莉亚': '冰', '优菈': '冰', '神里绫华': '冰',
#                   '丽莎': '雷', '雷泽': '雷', '菲谢尔': '雷', '北斗': '雷', '刻晴': '雷',
#                   '琴': '风', '温迪': '风', '砂糖': '风', '枫原万叶': '风',
#                   '诺艾尔': '岩', '凝光': '岩', '钟离': '岩', '阿贝多': '岩',
#                   '主角': '岩', }
# mapName = {"火伤": "火元素伤害", "水伤": "水元素伤害", "冰伤": "冰元素伤害", "岩伤": "岩元素伤害", "风伤": "风元素伤害", "雷伤": "雷元素伤害", "物伤": "物理攻击伤害",
#            "攻击": "攻击力", "防御": "防御力", "暴率": "暴击率", "爆伤": "暴击伤害", "充能": "元素充能效率", "精通": "元素精通", "生命": "生命值", "治疗": "治疗加成"}

# orc = paddleocr.PaddleOCR(use_angle_cls=False, lang='ch', use_gpu=False)
# img_path = 'assets/characterInfo.bmp'
# res = orc.ocr(img=img_path, cls=False)
# totalInfo = []
# i = 0
# while i < len(res):
#     name = res[i][1][0]
#     try:
#         tempList = [int(res[i + 1][1][0]), int(res[i + 2][1][0]), int(res[i + 3][1][0])]
#     except:
#         tempList = [res[i + 1][1][0], res[i + 2][1][0], res[i + 3][1][0]]
#     tempList.sort(reverse=False)
#     [attack, defence, hp] = tempList
#     breakInfo = res[i + 4][1][0][0:2]
#     if res[i + 4][1][0][-1] == '%':
#         value = eval(res[i + 4][1][0][2:-1]) / 100
#     else:
#         value = eval(res[i + 4][1][0][2:])
#     element = "***"
#     try:
#         element = nameElementMap[name]
#     except:
#         element = "***"
#         print("name:", name, " wrong map.")
#     totalInfo.append(
#         {"name": name, "element": element,
#          "baseInfo": {"attack": attack, "defence": defence, "hp": hp, "breakInfo": [mapName[breakInfo], value]}})
#     i += 5
#     if name == '砂糖':
#         i += 4
#
# with open("assets/CharacterInfo.json", "w", encoding='utf-8') as f:
#     json.dump(totalInfo, f, ensure_ascii=False)
# print("Character Base Info Saved.")
# {'name': '安柏', 'element': '火', 'baseInfo': {'attack': 223, 'defence': 601, 'hp': 9461, 'breakInfo': {'攻击力': 0.24}}}
# def addCharacterInfo(name, element, attack, defence, hp, breakInfo):
#     f = open("assets/CharacterInfo.json", "r", encoding='utf-8')
#     characterInfoData = json.load(f)
#     characterInfoData.append({'name': name, 'element': element,
#                               'baseInfo': {'attack': attack, 'defence': defence, 'hp': hp, 'breakInfo': breakInfo}})
#     f.close()
#     f = open("assets/CharacterInfo.json", "w", encoding='utf-8')
#     json.dump(characterInfoData, f, ensure_ascii=False)
#     f.close()
#     print("Successfully add character information.")
#
#
# def delCharacterInfo(name):
#     f = open("assets/CharacterInfo.json", "r", encoding='utf-8')
#     characterInfoData = json.load(f)
#     for info in characterInfoData:
#         if info['name'] == name:
#             characterInfoData.remove(info)
#             break
#     f.close()
#     f = open("assets/CharacterInfo.json", "w", encoding='utf-8')
#     json.dump(characterInfoData, f, ensure_ascii=False)
#     f.close()
#     print("Successfully delete character information.")


# delCharacterInfo('安柏')
# addCharacterInfo('安柏', '火', 223, 601, 9461, ['攻击力', 0.24])
