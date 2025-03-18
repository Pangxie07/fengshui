import tkinter as tk
from tkinter import ttk, messagebox
from lunardate import LunarDate
from datetime import datetime
import json

class FengshuiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("风水测算系统")
        self.root.geometry("1000x800")

        # 加载地区数据
        self.load_regions()

        # 创建界面
        self.create_widgets()

    def load_regions(self):
        """加载地区数据"""
        try:
            with open("data/regions.json", "r", encoding="utf-8") as f:
                self.regions = json.load(f)
        except Exception as e:
            messagebox.showerror("错误", f"加载地区数据失败：{str(e)}")
            self.regions = {}

    def create_widgets(self):
        """创建主界面"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # 姓名输入
        ttk.Label(main_frame, text="姓名:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=25).grid(row=0, column=1, padx=5, pady=5)

        # 地区选择
        self.create_region_selector(main_frame)

        # 日期选择
        self.create_date_selector(main_frame)

        # 排盘按钮
        ttk.Button(main_frame, text="排盘", command=self.calculate_bazi, width=15).grid(row=10, columnspan=2, pady=20)

    def create_region_selector(self, frame):
        """创建地区选择菜单"""
        # 国家选择
        ttk.Label(frame, text="国家:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.country_var = tk.StringVar()
        self.country_cb = ttk.Combobox(frame, textvariable=self.country_var, width=22)
        self.country_cb["values"] = list(self.regions.keys())
        self.country_cb.grid(row=1, column=1, padx=5, pady=5)
        self.country_cb.bind("<<ComboboxSelected>>", self.update_provinces)

        # 省份选择
        ttk.Label(frame, text="省份:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.province_var = tk.StringVar()
        self.province_cb = ttk.Combobox(frame, textvariable=self.province_var, width=22)
        self.province_cb.grid(row=2, column=1, padx=5, pady=5)
        self.province_cb.bind("<<ComboboxSelected>>", self.update_cities)

        # 城市选择
        ttk.Label(frame, text="城市:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.city_var = tk.StringVar()
        self.city_cb = ttk.Combobox(frame, textvariable=self.city_var, width=22)
        self.city_cb.grid(row=3, column=1, padx=5, pady=5)
        self.city_cb.bind("<<ComboboxSelected>>", self.update_districts)

        # 区县选择
        ttk.Label(frame, text="区县:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.district_var = tk.StringVar()
        self.district_cb = ttk.Combobox(frame, textvariable=self.district_var, width=22)
        self.district_cb.grid(row=4, column=1, padx=5, pady=5)

    def update_provinces(self, event):
        """更新省份选项"""
        country = self.country_var.get()
        if country in self.regions:
            self.province_cb["values"] = list(self.regions[country].keys())
            self.province_cb.current(0)
            self.update_cities(None)

    def update_cities(self, event):
        """更新城市选项"""
        country = self.country_var.get()
        province = self.province_var.get()
        if country in self.regions and province in self.regions[country]:
            self.city_cb["values"] = list(self.regions[country][province].keys())
            self.city_cb.current(0)
            self.update_districts(None)

    def update_districts(self, event):
        """更新区县选项"""
        country = self.country_var.get()
        province = self.province_var.get()
        city = self.city_var.get()
        if country in self.regions and province in self.regions[country] and city in self.regions[country][province]:
            self.district_cb["values"] = self.regions[country][province][city]
            self.district_cb.current(0)

    def create_date_selector(self, frame):
        """创建日期选择菜单"""
        # 年份选择
        ttk.Label(frame, text="年份:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.year_var = tk.StringVar()
        self.year_cb = ttk.Combobox(frame, textvariable=self.year_var, width=22)
        self.year_cb["values"] = [str(y) for y in range(1900, 2101)]
        self.year_cb.grid(row=5, column=1, padx=5, pady=5)

        # 月份选择
        ttk.Label(frame, text="月份:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.month_var = tk.StringVar()
        self.month_cb = ttk.Combobox(frame, textvariable=self.month_var, width=22)
        self.month_cb["values"] = [f"{m:02d}" for m in range(1, 13)]
        self.month_cb.grid(row=6, column=1, padx=5, pady=5)

        # 日期选择
        ttk.Label(frame, text="日期:").grid(row=7, column=0, padx=5, pady=5, sticky="w")
        self.day_var = tk.StringVar()
        self.day_cb = ttk.Combobox(frame, textvariable=self.day_var, width=22)
        self.day_cb["values"] = [f"{d:02d}" for d in range(1, 32)]
        self.day_cb.grid(row=7, column=1, padx=5, pady=5)

        # 日期类型选择
        self.date_type = tk.StringVar(value="solar")
        ttk.Radiobutton(frame, text="阳历", variable=self.date_type, value="solar").grid(row=8, column=0, padx=5, pady=5)
        ttk.Radiobutton(frame, text="农历", variable=self.date_type, value="lunar").grid(row=8, column=1, padx=5, pady=5)

    def calculate_bazi(self):
        """排盘测算"""
        try:
            # 获取输入数据
            name = self.name_var.get()
            country = self.country_var.get()
            province = self.province_var.get()
            city = self.city_var.get()
            district = self.district_var.get()
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            day = int(self.day_var.get())
            date_type = self.date_type.get()

            # 显示结果（待实现）
            result = f"""
            姓名：{name}
            地区：{country} {province} {city} {district}
            日期：{year}年{month}月{day}日（{date_type}）
            """
            messagebox.showinfo("排盘结果", result)
        except Exception as e:
            messagebox.showerror("错误", f"排盘失败：{str(e)}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = FengshuiApp(root)
        root.mainloop()
    except Exception as e:
        print(f"程序出错：{str(e)}")
        input("按回车键退出...")