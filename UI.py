import tkinter
from PIL import Image, ImageTk
import ctypes, sys, os
from PyQt5.QtWidgets import QApplication
import ScreenCapture
import OptimizeRelics
import time
import win32gui


class OriginWindow():
    def __init__(self):
        self.origin_window = tkinter.Tk()
        self.origin_window.title('Relic Helper')
        self.origin_window.geometry('640x480')
        # self.origin_window.configure(bg='#FFEFD5')
        self.origin_window.resizable(width=False, height=False)
        self.origin_window.iconbitmap('assets/genshin.ico')
        self.save_relic = True

        self.character_name = "甘雨"
        self.weapon_name = "阿莫斯之弓"
        self.suite = ["流浪大地的乐团", "追忆之注连"]
        self.suite_num = [2, 2]
        self.strict = {'暴击率': [0, 0.8]}

        self.capture = None

        self.image_label('assets/ganyu.webp', 0, 0)
        self.image_button('assets/artifacts/乐团的晨光.webp', x=200, y=200, text='Traverse', command=self.traverse_relics)
        self.image_button('assets/artifacts/乐团的晨光.webp', x=300, y=200, text='Optimize', command=self.optimize_relics)

        self.origin_window.mainloop()

    def optimize_relics(self):
        try:
            character = OptimizeRelics.Character(self.character_name, self.weapon_name,
                                                 self.suite, self.suite_num, self.strict)
            character.optimaze_relics()
            character.show_relics_combination()
            character.show_character_info()
        except:
            print("搭配失败，请检查圣遗物是否存入数据库。")

    def traverse_relics(self):
        try:
            hwnd = win32gui.FindWindow(None, '原神')
            if hwnd == 0:
                raise Exception("Please open Genshin first.")
            self.capture = ScreenCapture.Capture()
            win32gui.SetForegroundWindow(hwnd)
            self.capture.traverse_relics(rec_relic=self.save_relic)
            hwnd = win32gui.FindWindow(None, 'Relic Helper')
            win32gui.SetForegroundWindow(hwnd)
        except BaseException as e:
            print(e)
            print("识别失败。调整分辨率或游戏窗口大小，建议使游戏横向铺满桌面。")

    def image_label(self, img_path, x=0, y=0, width=256, height=256):
        img = Image.open(img_path)
        print(img.size)
        img = img.resize((width, height))
        render = ImageTk.PhotoImage(img)
        img_label = tkinter.Label(self.origin_window, image=render, width=width, height=height)
        img_label.image = render

        img_label.place(x=x, y=y)

    def image_button(self, img_path, text=None, image_size_match=False, size: tuple = (80, 20), x=0, y=0, command=None):
        img = Image.open(img_path)
        render = ImageTk.PhotoImage(img)
        if image_size_match:
            w, h = img.size
            img = img.resize((size[1], size[1])) if w / h < size[0] / size[1] else img.resize((size[0], size[0]))
        img_button = tkinter.Button(self.origin_window, compound=tkinter.CENTER, text=text, image=render, width=size[0],
                                    height=size[1],
                                    command=command, fg="white", font=("microsoft yahei", 12, 'bold'))
        img_button.image = render
        img_button.place(x=x, y=y)


def open_window():
    window = OriginWindow()


if __name__ == "__main__":
    print(sys.argv)
    open_window()
