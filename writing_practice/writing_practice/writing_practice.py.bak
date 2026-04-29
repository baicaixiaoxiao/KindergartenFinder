import tkinter as tk
from tkinter import ttk, messagebox
import random

class WritingPracticeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("小朋友学写字")
        self.root.geometry("800x600")
        
        # 默认字库
        self.characters = ["一", "二", "三", "十", "人", "大", "天", "口", "日", "月",
                          "水", "火", "山", "石", "土", "木", "禾", "米", "草", "花",
                          "上", "下", "左", "右", "前", "后", "东", "西", "南", "北"]
        
        self.current_char = ""
        self.drawing = False
        self.last_x = 0
        self.last_y = 0
        
        # 创建主界面
        self.create_widgets()
        
    def create_widgets(self):
        # 顶部控制面板
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        # 字选择标签
        ttk.Label(control_frame, text="选择要写的字：").pack(side=tk.LEFT, padx=5)
        
        # 字选择下拉框
        self.char_var = tk.StringVar()
        self.char_combobox = ttk.Combobox(control_frame, textvariable=self.char_var, 
                                          values=self.characters, width=10)
        self.char_combobox.current(0)
        self.char_combobox.pack(side=tk.LEFT, padx=5)
        # 选择变化时自动显示汉字
        self.char_combobox.bind("<<ComboboxSelected>>", lambda e: self.show_character())
        
        # 显示按钮
        ttk.Button(control_frame, text="显示汉字", command=self.show_character).pack(side=tk.LEFT, padx=5)
        
        # 随机按钮
        ttk.Button(control_frame, text="随机选字", command=self.random_character).pack(side=tk.LEFT, padx=5)
        
        # 清空按钮
        ttk.Button(control_frame, text="清空画布", command=self.clear_canvas).pack(side=tk.RIGHT, padx=5)
        
        # 笔画粗细调节
        ttk.Label(control_frame, text="笔画粗细：").pack(side=tk.RIGHT, padx=5)
        self.pen_size = tk.IntVar(value=5)
        ttk.Scale(control_frame, from_=2, to=15, variable=self.pen_size, 
                  orient=tk.HORIZONTAL, length=100).pack(side=tk.RIGHT, padx=5)
        
        # 颜色选择
        ttk.Label(control_frame, text="颜色：").pack(side=tk.RIGHT, padx=5)
        self.color_var = tk.StringVar(value="#000000")
        colors = ["#000000", "#FF0000", "#00FF00", "#0000FF", "#FF6600"]
        ttk.Combobox(control_frame, textvariable=self.color_var, values=colors, width=8).pack(side=tk.RIGHT, padx=5)
        
        # 主画布区域
        canvas_frame = ttk.Frame(self.root, padding="10")
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建田字格画布
        self.canvas = tk.Canvas(canvas_frame, bg="white", bd=2, relief=tk.SUNKEN)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绑定鼠标事件
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)
        
        # 绑定窗口大小变化事件
        self.root.bind("<Configure>", self.on_resize)
        
        # 初始化显示第一个字
        self.show_character()
        
    def on_resize(self, event):
        # 窗口大小变化时重新绘制田字格
        if self.current_char:
            self.show_character()
        
    def show_character(self):
        self.current_char = self.char_var.get()
        # 更换文字时清除所有内容（包括用户画的和旧的参考字）
        self.canvas.delete("all")
        self.draw_tian_zi_ge()
        self.draw_character()
        
    def random_character(self):
        self.char_var.set(random.choice(self.characters))
        self.show_character()
        
    def clear_canvas(self):
        # 只删除用户绘制的内容，保留田字格和汉字参考
        self.canvas.delete("user_drawing")
        
    def draw_tian_zi_ge(self):
        # 获取画布尺寸
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width == 1 or height == 1:
            return
        
        # 计算田字格边界（留边距）
        margin = min(width, height) * 0.1
        box_size = min(width, height) * 0.8
        
        # 田字格外框
        self.canvas.create_rectangle(margin, margin, margin + box_size, margin + box_size, 
                                     outline="#CCCCCC", width=3)
        
        # 中心十字线
        center_x = margin + box_size / 2
        center_y = margin + box_size / 2
        
        # 水平线
        self.canvas.create_line(margin, center_y, margin + box_size, center_y, 
                                fill="#CCCCCC", width=2, dash=(5, 5))
        
        # 垂直线
        self.canvas.create_line(center_x, margin, center_x, margin + box_size, 
                                fill="#CCCCCC", width=2, dash=(5, 5))
        
        # 对角线
        self.canvas.create_line(margin, margin, margin + box_size, margin + box_size, 
                                fill="#EEEEEE", width=1, dash=(3, 3))
        self.canvas.create_line(margin + box_size, margin, margin, margin + box_size, 
                                fill="#EEEEEE", width=1, dash=(3, 3))
        
        # 保存田字格区域信息
        self.box_x = margin
        self.box_y = margin
        self.box_width = box_size
        
    def draw_character(self):
        if not self.current_char:
            return
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width == 1 or height == 1:
            return
        
        # 计算字体大小（根据田字格大小）
        font_size = int(self.box_width * 0.6)
        
        # 在田字格中心显示汉字（浅色作为参考）
        center_x = self.box_x + self.box_width / 2
        center_y = self.box_y + self.box_width / 2
        
        self.canvas.create_text(center_x, center_y, text=self.current_char, 
                                font=("KaiTi", font_size, "bold"), fill="#DDDDDD")
        
    def start_draw(self, event):
        self.drawing = True
        self.last_x = event.x
        self.last_y = event.y
        
    def draw(self, event):
        if not self.drawing:
            return
        
        # 创建线条（添加标签便于区分）
        self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                               fill=self.color_var.get(),
                               width=self.pen_size.get(),
                               capstyle=tk.ROUND,
                               smooth=True,
                               tags="user_drawing")
        
        self.last_x = event.x
        self.last_y = event.y
        
    def stop_draw(self, event):
        self.drawing = False

if __name__ == "__main__":
    root = tk.Tk()
    app = WritingPracticeApp(root)
    root.mainloop()
