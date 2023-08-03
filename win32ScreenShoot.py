import win32gui, win32ui, win32con
from PIL import Image
from ctypes import windll
import cv2
import numpy
import time
from ctypes import wintypes
import ctypes
from Config import *


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


def split_screen_shoot_img(type_, img: Image.Image):
    assert type_ in relic_info_position_dict.keys()
    x, y, width, height = relic_info_position_dict[type_]
    return img.crop((x, y, x + width, y + height))


def get_split_screen_shoot_img(img: Image.Image):
    assert type(img) is Image.Image
    for key in relic_info_dict.keys():
        split_img = split_screen_shoot_img(key, img)
        split_img.save(key + ".jpg")
    #     orc_info = self.orc(split_img)
    #     relic_info_dict[key] = unpack_attributes(orc_info) if len(orc_info) > 1 else orc_info[0]
    # relic_info_dict['rank'] = relic_info_dict['rank'].strip('+')
    # relic_info_dict['suite'] = dim_match(relic_info_dict['suite'].strip(':'))
    # relic_info_dict['sub_attributes'].append(
    #     [relic_info_dict['main_attribute'], main_attribute_to_value_dict[relic_info_dict['main_attribute']]])


def grab_window(window_name):
    # 获取后台窗口的句柄，注意后台窗口不能最小化
    hWnd = win32gui.FindWindow(None, window_name)
    # 获取句柄窗口的大小信息
    rect = get_window_rect(hWnd)
    rect = [int(i) for i in rect]
    print(rect)
    # rect = win32gui.GetWindowRect(hWnd)
    left, top, right, bot = rect

    width = right - left
    height = bot - top

    # 返回句柄窗口的设备环境，覆盖整个窗口，包括非客户区，标题栏，菜单，边框
    hWndDC = win32gui.GetWindowDC(hWnd)
    # 创建设备描述表
    mfcDC = win32ui.CreateDCFromHandle(hWndDC)
    # 创建内存设备描述表
    saveDC = mfcDC.CreateCompatibleDC()
    # 创建位图对象准备保存图片
    saveBitMap = win32ui.CreateBitmap()
    # 为bitmap开辟存储空间
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    # 将截图保存到saveBitMap中
    saveDC.SelectObject(saveBitMap)
    # 保存bitmap到内存设备描述表
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

    # 获取位图信息
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    # 生成图像
    im_PIL = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
    l, t, w, h = relic_info_position_dict['captured_screen']
    img = im_PIL.crop((l, t, l + w, t + h))
    # get_split_screen_shoot_img(im_PIL)

    # 内存释放
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hWnd, hWndDC)

    # 方法二（第二部分）：PIL保存
    # PrintWindow成功,保存到文件,显示到屏幕
    im_PIL.save('im_PIL.png')
    im = im_PIL.crop((160 + 196, 197, 160 + 166 + 196, 197 + 206))
    im.save("im.png")  # 保存
    # im_PIL.show()  # 显示
    return im_PIL


# 方法三（第二部分）：opencv+numpy保存
# PrintWindow成功，保存到文件，显示到屏幕
# im_opencv = numpy.frombuffer(signedIntsArray, dtype='uint8')
# im_opencv.shape = (height, width, 4)
# cv2.cvtColor(im_opencv, cv2.COLOR_BGRA2RGB)
# cv2.imwrite("im_opencv.jpg", im_opencv, [int(cv2.IMWRITE_JPEG_QUALITY), 100])  # 保存
# cv2.namedWindow('im_opencv')  # 命名窗口
# cv2.imshow("im_opencv", im_opencv)  # 显示
# cv2.waitKey(0)
# cv2.destroyAllWindows()
# im = grab_window("原神")
# print(type(im))
import win32api

hwnd = win32gui.FindWindow(None, "原神")
win32gui.SetForegroundWindow(hwnd)
print(win32api.GetSystemMetrics(win32con.SM_CXSCREEN))
print(win32api.GetSystemMetrics(win32con.SM_CYSCREEN))
from pymouse import PyMouse

m = PyMouse()
print(m.screen_size())
m.click(160+196, 197)
