from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import *
from PIL import ImageQt
import numpy as np
import win32gui, win32api, win32con
import time, copy, sys, json, os
from Config import main_attribute_to_value_dict, attribute_standard_dict, suite_buff_dict, relic_info_position_dict, \
    relic_info_dict, relic_margin_pixel

sys.path.append(r'PaddleOCR')
from PaddleOCR import paddleocr

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


# 根据识别出的文字模糊匹配，匹配相似度最高的套装
def dim_match(suite_name):
    best_match_count = 0
    best_name = suite_name
    for suite in suite_buff_dict.keys():
        match_count = 0
        for word in suite_name:
            if word in suite:
                match_count += 1
        if match_count > best_match_count:
            best_name = suite
            best_match_count = match_count
    return best_name


def check_attribute_value(name, value):
    for standard in attribute_standard_dict[name]:
        if standard[0] < value < standard[1]:
            return True
    print("Wrong data {}: {}".format(name, value))
    return False


def unpack_attributes(attributes):
    res = []
    for attribute in attributes:
        [name, value] = attribute.split('+')
        try:
            if value[-1] == '%':
                res.append([name, round(float(value.strip("%")) / 100, 4)] if check_attribute_value(name, round(
                    float(value.strip("%")) / 100, 4)) else [name, 0])
            else:
                res.append([name, eval(value)] if check_attribute_value(name, eval(value)) else [name, 0])
        except:
            res.append([name, 0])
    return res


def save_relics_in_json(relics):
    with open("assets/Relics.json", "w", encoding='utf-8') as f:
        json.dump(relics, f, ensure_ascii=False)
    print("Relics saved.")


class Capture:
    def __init__(self):
        self.paddle = paddleocr.PaddleOCR(lang='ch', use_gpu=False)
        self.hwnd = win32gui.FindWindow(None, '原神')
        win32gui.SetForegroundWindow(self.hwnd)
        self.app = QApplication(sys.argv)
        self.screen = QApplication.primaryScreen()
        self.size = self.screen.grabWindow(self.hwnd).size()
        self.window_pos = QWindow.fromWinId(self.hwnd).position()
        # self.__mouse_click(self.window_pos.x(), self.window_pos.y())

        print(self.size,self.window_pos)
        # input()
        # 2.4版本前：275 160是第一个圣遗物的左上角，圣遗物尺寸为167*205，所以第一个圣遗物的中心约为（358，263），一行7个圣遗物
        # 2.5版本后：158 160是第一个圣遗物的左上角，圣遗物尺寸为166*206，所以第一个圣遗物的中心约为（241，263），一行8个圣遗物
        # 每次左右跨度约为195.5，四舍五入取196，上下跨度约为240
        # img = screen.grabWindow(hwnd, 275, 128, 1340, 240).toImage()
        # img = screen.grabWindow(hwnd, 158, 160, 166,206).toImage()
        self.ltx = self.__normalize_pos(241, 'x')
        self.lty = self.__normalize_pos(263, 'y')
        self.Package = {}


    @staticmethod
    def __split_screen_shoot_img(type_, img: QImage):
        assert type_ in relic_info_position_dict.keys()
        x, y, width, height = relic_info_position_dict[type_]
        return ImageQt.fromqimage(img.copy(x, y, width, height))

    def __get_split_screen_shoot_img(self, img: QImage):
        assert type(img) is QImage
        for key in relic_info_dict.keys():
            split_img = self.__split_screen_shoot_img(key, img)
            orc_info = self.orc(split_img)
            relic_info_dict[key] = unpack_attributes(orc_info) if len(orc_info) > 1 else orc_info[0]
        relic_info_dict['rank'] = relic_info_dict['rank'].strip('+')
        relic_info_dict['suite'] = dim_match(relic_info_dict['suite'].strip(':'))
        relic_info_dict['sub_attributes'].append(
            [relic_info_dict['main_attribute'], main_attribute_to_value_dict[relic_info_dict['main_attribute']]])

    @staticmethod
    def show_relic_info_dict():
        for key in relic_info_dict.keys():
            print("{}: {}".format(key, relic_info_dict[key]))

    def __screen_shoot(self):
        x, y, width, height = relic_info_position_dict['captured_screen']
        captured_screen = self.screen.grabWindow(self.hwnd, x, y, width, height).toImage()
        self.__get_split_screen_shoot_img(captured_screen)
        if '20' in relic_info_dict['rank']:
            self.Package[str(len(self.Package) + 1)] = copy.deepcopy(relic_info_dict)
            return True
        return False

    def orc(self, img, paddle_orc=True):
        if paddle_orc:
            img = np.array(img)
            res = self.paddle.ocr(img=img, cls=False)
            text = []
            for line in res:
                text.append(line[1][0])
            return text

    # 2560 * 1440 或 1920 * 1080 或 1280 * 720 或等比例的分辨率下可行，否则无法准确提取文字信息
    def __normalize_pos(self, x: [int, float, list], flag):
        assert type(x) in [int, float, list]
        if isinstance(x, list):
            return [x_ / 2560 * self.size.width() if flag == 'x' else x_ / 1440 * self.size.height() for x_ in x]
        else:
            return x / 2560 * self.size.width() if flag == 'x' else x / 1440 * self.size.height()

    def __mouse_middle_button_roll(self, x, y, span):
        x, y = int(self.__normalize_pos(x, 'x')), int(self.__normalize_pos(y, 'y'), )
        i = 0
        if span > 0:
            while i < span:
                win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, x, y, -1)
                i += 1
        else:
            while i < -span:
                win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, x, y, 1)
                i += 1
        time.sleep(0.5)

    def __mouse_click(self, x, y):
        x, y = int(self.__normalize_pos(x, 'x')), int(self.__normalize_pos(y, 'y'), )
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y)

    def traverse_relics(self, rec_relic=True):
        span_width = self.__normalize_pos(relic_margin_pixel, 'x')
        # 窗口置顶
        win32gui.SetForegroundWindow(self.hwnd)
        time.sleep(0.5)
        count = 0
        diff = 3
        while True:
            self.__mouse_click(int(self.ltx + span_width * count + self.window_pos.x()),
                               int(self.lty + self.window_pos.y()))
            break
            if not self.__screen_shoot():
                break

            if (count + 1) % relic_per_row == 0:
                if diff == 0:
                    self.__mouse_middle_button_roll(self.ltx, self.lty, 9)
                    diff = 3
                else:
                    self.__mouse_middle_button_roll(self.ltx, self.lty, 10)
                    diff -= 1
                count = 0
                continue
            count += 1
        self.__mouse_middle_button_roll(self.ltx, self.lty, -220)
        self.__mouse_click(int(self.ltx + self.window_pos.x()), int(self.lty + self.window_pos.y()))
        if rec_relic:
            save_relics_in_json(self.Package)
        print("All relics have been recorded.")


if __name__ == '__main__':
    # 需要退出全屏模式，否则可能出现截图为黑屏的情况
    # 在sleep期间切换到原神
    capture = Capture()
    capture.traverse_relics()
