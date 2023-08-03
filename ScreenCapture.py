import pymouse
import skimage.util
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import *
from PIL import Image
import numpy as np
import win32gui, win32api, win32con, win32ui
import time, copy, sys, json, os
from Config import *
from ctypes import wintypes
import ctypes


def get_window_rect(hwnd):
    try:
        f = ctypes.windll.dwmapi.DwmGetWindowAttribute
        rect = ctypes.wintypes.RECT()
        DWMWA_EXTENDED_FRAME_BOUNDS = 9
        f(ctypes.wintypes.HWND(hwnd), ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
          ctypes.byref(rect), ctypes.sizeof(rect))
        return rect.left, rect.top, rect.right, rect.bottom
    except WindowsError as e:
        raise e


sys.path.append(r'PaddleOCR')
from PaddleOCR import paddleocr

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


# 根据识别出的文字模糊匹配，匹配相似度最高的套装
def dim_match(name, flag):
    best_match_count = 0
    best_name = name
    if flag == 'suite':
        match_dict = suite_buff_dict.keys()
    elif flag == 'attribute':
        match_dict = attribute_standard_dict.keys()
    else:
        return name

    for suite in match_dict:
        match_count = 0
        for word in name:
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
        name = dim_match(name, flag='attribute')
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
    with open("assets/RelicsNew.json", "w", encoding='utf-8') as f:
        json.dump(relics, f, ensure_ascii=False)
    print("Relics saved.")


def grab_window(window_name, relic_info=True):
    # 获取后台窗口的句柄，注意后台窗口不能最小化
    hwnd = win32gui.FindWindow(None, window_name)
    # 获取句柄窗口的大小信息
    left, top, right, bot = get_window_rect(hwnd)
    width = right - left
    height = bot - top
    # 返回句柄窗口的设备环境，覆盖整个窗口，包括非客户区，标题栏，菜单，边框
    hwnd_dc = win32gui.GetWindowDC(hwnd)
    # 创建设备描述表
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    # 创建内存设备描述表
    save_dc = mfc_dc.CreateCompatibleDC()
    # 创建位图对象准备保存图片
    save_bit_map = win32ui.CreateBitmap()
    # 为bitmap开辟存储空间
    save_bit_map.CreateCompatibleBitmap(mfc_dc, width, height)
    # 将截图保存到saveBitMap中
    save_dc.SelectObject(save_bit_map)
    # 保存bitmap到内存设备描述表
    save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)

    # 获取位图信息
    bmp_info = save_bit_map.GetInfo()
    bmp_str = save_bit_map.GetBitmapBits(True)
    # 生成图像
    img = Image.frombuffer('RGB', (bmp_info['bmWidth'], bmp_info['bmHeight']), bmp_str, 'raw', 'BGRX', 0, 1)
    l, t, w, h = relic_info_position_dict['captured_screen'] if relic_info else [left, top, width, height]
    img = img.crop((l, t, l + w, t + h))
    # 内存释放
    # win32gui.DeleteObject(save_bit_map.GetHandle())
    # save_dc.DeleteDC()
    # mfc_dc.DeleteDC()
    # win32gui.ReleaseDC(hwnd, hwnd_dc)

    return img


class Capture:
    def __init__(self):
        self.paddle = paddleocr.PaddleOCR(lang='ch', use_gpu=False)
        self.hwnd = win32gui.FindWindow(None, '原神')
        self.mouse = pymouse.PyMouse()
        # 获取真实分辨率下的像素位置
        rect = get_window_rect(self.hwnd)
        self.left, self.top, self.right, self.bottom = rect
        self.window_width = self.right - self.left
        self.window_height = self.bottom - self.top

        # self.top += 56  # 窗体项目栏宽度

        self.x_proportional = win32api.GetSystemMetrics(win32con.SM_CXSCREEN) / 2560
        self.y_proportional = win32api.GetSystemMetrics(win32con.SM_CYSCREEN) / 1600
        self.init = False
        # 2.4版本前：275 160是第一个圣遗物的左上角，圣遗物尺寸为167*205，所以第一个圣遗物的中心约为（358，263），一行7个圣遗物
        # 2.5版本后：158 160是第一个圣遗物的左上角，圣遗物尺寸为166*206，所以第一个圣遗物的中心约为（241，263），一行8个圣遗物
        # 更新不再使用QApplication，全部使用win32之后，对于整个窗口(2564 * 1479)，点(160, 197)是第一个圣遗物的左上角
        first_relic_left = self.__match_resolution_ratio(160, 'x')
        first_relic_top = self.__match_resolution_ratio(197, 'y')
        relic_width = self.__match_resolution_ratio(166, 'x')
        relic_height = self.__match_resolution_ratio(206, 'y')
        # 每次跨度约为195.5，四舍五入取196，上下跨度约为240
        self.ltx = first_relic_left + relic_width / 2
        self.lty = first_relic_top + relic_height / 2
        self.count = 8
        self.Package = {}

    def __match_resolution_ratio(self, x: [int, float, list], flag):
        assert type(x) in [int, float, list]
        if isinstance(x, list):
            return [
                x_ * self.window_width / 2560 if flag == 'x' else x_ * self.window_height / 1440 for x_ in x]
        else:
            return x * self.window_width / 2560 if flag == 'x' else x * self.window_height / 1440

    @staticmethod
    def __split_screen_shoot_img(type_, img: Image.Image):
        assert type_ in relic_info_position_dict.keys()
        x, y, width, height = relic_info_position_dict[type_]
        return img.crop((x, y, x + width, y + height))

    def __get_split_screen_shoot_img(self, img: Image.Image):
        assert type(img) is Image.Image
        for key in relic_info_dict.keys():
            split_img = self.__split_screen_shoot_img(key, img)
            orc_info = self.orc(split_img)
            relic_info_dict[key] = unpack_attributes(orc_info) if len(orc_info) > 1 else orc_info[0]
        relic_info_dict['rank'] = relic_info_dict['rank'].strip('+')
        relic_info_dict['suite'] = dim_match(relic_info_dict['suite'].strip(':'), flag='suite')
        relic_info_dict['sub_attributes'].append(
            [relic_info_dict['main_attribute'], main_attribute_to_value_dict[relic_info_dict['main_attribute']]])
        if relic_info_dict['place'] == '生之花':
            relic_info_dict['sub_attributes'][-1][1] = 4780
        elif relic_info_dict['place'] == '死之羽':
            relic_info_dict['sub_attributes'][-1][1] = 311

    @staticmethod
    def show_relic_info_dict():
        for key in relic_info_dict.keys():
            print("{}: {}".format(key, relic_info_dict[key]))

    def __screen_shoot(self):
        captured_screen = grab_window("原神", relic_info=True)
        self.__get_split_screen_shoot_img(captured_screen)
        if '20' in relic_info_dict['rank']:
            self.Package[str(len(self.Package) + 1)] = copy.deepcopy(relic_info_dict)
            return True
        return False

    def orc(self, img: Image.Image, paddle_orc=True):
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
            return [
                x_ * self.x_proportional * self.window_width / 2560 if flag == 'x'
                else x_ * self.y_proportional * self.window_height / 1440 for x_ in x]
        else:
            return x * self.x_proportional * self.window_width / 2560 if flag == 'x' \
                else x * self.y_proportional * self.window_height / 1440

    def __mouse_middle_button_roll(self, x, y, span):
        x, y = int(self.__normalize_pos(x, 'x')), int(self.__normalize_pos(y, 'y'))
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
        x, y = int(self.__normalize_pos(x, 'x')), int(self.__normalize_pos(y, 'y'))
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y)

    def traverse_relics(self, rec_relic=True):
        span_width = relic_margin_pixel / 2560 * self.window_width
        # 窗口置顶
        win32gui.SetForegroundWindow(self.hwnd)
        time.sleep(0.5)
        count = 0
        diff = 3
        while True:
            self.__mouse_click(int(self.ltx + self.left + count * span_width),
                               int(self.lty + self.top))

            if not self.__screen_shoot():
                break

            if (count + 1) % self.count == 0:
                if diff == 0:
                    self.__mouse_middle_button_roll(self.ltx, self.lty, 9)
                    diff = 3
                else:
                    self.__mouse_middle_button_roll(self.ltx, self.lty, 10)
                    diff -= 1
                count = 0
                continue
            # if count == 5:
            #     break
            count += 1
        self.__mouse_middle_button_roll(self.ltx, self.lty, -220)
        self.__mouse_middle_button_roll(self.ltx, self.lty, -220)
        self.__mouse_click(int(self.ltx + self.left), int(self.lty + self.top))
        if rec_relic:
            save_relics_in_json(self.Package)
        print("All relics have been recorded.")


if __name__ == '__main__':
    # 需要退出全屏模式，否则可能出现截图为黑屏的情况
    # 在sleep期间切换到原神
    capture = Capture()
    capture.traverse_relics(rec_relic=True)
