import os
import time
import logging
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox

from trader import Trader, numeric_to_string_month
from dotenv import load_dotenv
from pathlib import Path
from tkinter import *
from multiprocessing import Queue

# window size 
window_width = 640
window_height = 480

# frame padding global constant
x = 0
y = 1
FRAME_PAD  = (5,5)
FRAME_IPAD = (7,7)
PLACEHODLER = "Value"


class main_menu(Menu):
    def __init__(self, master, **kwargs):
        super().__init__(master, kwargs)
        self.master = master    

        # init
        self._init_vars()
        self._init_widgets()

    def _init_vars(self):
        self.language_var = StringVar()
        self.language_var.set("KR")

    def _init_widgets(self):
        self.file_menu = Menu(self, tearoff=0)
        self.file_menu.add_command(label="Exit", command=self.master.quit)
        self.add_cascade(label="File", menu=self.file_menu)

        self.language_menu = Menu(self, tearoff=0)
        self.language_menu.add_radiobutton(label="한국어", value="KR", variable=self.language_var)
        self.language_menu.add_radiobutton(label="English", value="EN", variable=self.language_var)
        self.add_cascade(label="Language", menu=self.language_menu)


class coin_frame(LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # initialize 
        self._init_vars()
        self._init_widgets()

    def _init_vars(self):
        self.coin_list = ["BTC", "ETH", "GNO", "AUD"]

    def _init_widgets(self):
        self.coin_list_box = ttk.Combobox(self, values=self.coin_list, state="readonly")
        self.coin_list_box.set("코인을 선택하세요")
        self.coin_list_box.bind("<<ComboboxSelected>>", func=lambda event: self.coin_price_label.config(text=f"You choose {self.coin_list_box.get()}"))
        
        self.coin_price_label = Label(self, text="You choose", font=("Arial", 14))
        self.current_balance = Label(self, text="Available Balance: 100$")
        self.current_margin_balance = Label(self, text="Margin Balance: 100$")

    def _pack_widgets(self, pad: tuple[int], ipad: tuple[int], fill="y", side="left"):
        super().pack(padx=pad[x], pady=pad[y], ipadx=ipad[x], ipady=ipad[y], fill=fill, side=side)
        self.coin_price_label.pack()
        self.coin_list_box.pack()
        self.current_balance.pack(side="bottom")
        self.current_margin_balance.pack(side="bottom")

    def get_selected_coin(self):
        return self.coin_list_box.get()


class order_frame(LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, kwargs)

        self.master = master

        # initialize
        self._init_vars()
        self._init_widgets()

    def _init_vars(self):
        global PLACEHODLER
        self.row = 5
        self.col = 3
        
        self.margin_mode_list = ["Isolated", "Cross", "Portfolio"]
        self.leverage_list = [1, 2, 5, 10, 100]
        self.qty_option_list = ["USDT", "COIN"]
        
        self.coin_qty_entry_placeholder = PLACEHODLER
        self.vcmd_leverage = (self.master.register(order_frame.validate_leverage), '%P')
        self.vcmd_coin_qty = (self.master.register(order_frame.validate_coin_qty), '%P')

        self.long_short = IntVar()

        self.upper_bound_unit = ["%", "$"]
        self.lower_bound_unit = ["%", "$"]

    def _init_widgets(self):
        # init grid
        for r in range(self.row):
            self.rowconfigure(r, weight=1)
        for c in range(self.col):
            self.columnconfigure(c, weight=1)

        # init widgets
        self.margin_mode = ttk.Combobox(self, width=15, state="readonly", values=self.margin_mode_list)
        self.margin_mode.set(self.margin_mode_list[0])

        self.leverage = ttk.Combobox(self, width=15, values=self.leverage_list, validate="key", validatecommand=self.vcmd_leverage)
        
        self.order_detail = Frame(self) 

        self.coin_qty_option = ttk.Combobox(self.order_detail, values=self.qty_option_list, state="readonly", width=5)
        self.coin_qty_option.set(self.qty_option_list[0])

        self.coin_qty_entry = Entry(self.order_detail, validate="key", validatecommand=self.vcmd_coin_qty, fg="grey", font=("Arial", 15), border=1)
        self.coin_qty_entry.insert(END, self.coin_qty_entry_placeholder)
        self.coin_qty_entry.bind("<FocusIn>", order_frame.entry_click)   
        self.coin_qty_entry.bind("<FocusOut>", order_frame.on_focusout) 

        self.long = Radiobutton(self, text="Long", value=0, variable=self.long_short, font=("Arial", 13), bg="#1ae41a", activebackground="#93ff93", activeforeground="#1ae41a", disabledforeground="#1ae41a")
        self.short = Radiobutton(self, text="Short", value=1, variable=self.long_short, font=("Arial", 13), bg="#e41a1a", activebackground="#ff9393", activeforeground="#e41a1a", disabledforeground="#e41a1a")

        self.upper_bound_frame = Frame(self)

        self.upper_bound_unit_option = ttk.Combobox(self.upper_bound_frame, values=self.upper_bound_unit, state="readonly", width=2)
        self.upper_bound_unit_option.set(self.upper_bound_unit[0])

        self.upper_bound = Entry(self.upper_bound_frame)
        self.upper_bound.insert(0, "Upper bound")

        self.lower_bound_frame = Frame(self)

        self.lower_bound_unit_option = ttk.Combobox(self.lower_bound_frame, values=self.lower_bound_unit, state="readonly", width=2)
        self.lower_bound_unit_option.set(self.upper_bound_unit[0])

        self.lower_bound = Entry(self.lower_bound_frame)
        self.lower_bound.insert(0,"Lower bound")

        self.order_button = Button(self, text="구매 및 전략 실행", command=self.send_order_msg)

    def _pack_widgets(self, pad: tuple[int], ipad: tuple[int], side="right", fill="both", expand=True):
        super().pack(padx=pad[x], pady=pad[y], ipadx=ipad[x], ipady=ipad[y], side=side, fill=fill, expand=expand)
        
        self.margin_mode.grid(row=0, column=0, sticky=E+W+S, padx=1, pady=2)
        self.leverage.grid(row=0, column=1, sticky=W+E+S, pady=2, padx=1)

        self.order_detail.grid(row=1, column=0, sticky=N+E+W+S, columnspan=2, pady=3, padx=5)
        self.coin_qty_option.pack(side="right", fill="y")
        self.coin_qty_entry.pack(side="right", fill="both", expand=True)
        
        self.long.grid(row=2, column=0, sticky="new", padx=1, pady=1)
        self.short.grid(row=2, column=1, sticky="new", padx=1, pady=1)

        self.upper_bound_frame.grid(row=3, column=0, sticky=N+E+W+S)
        self.upper_bound_unit_option.pack(side="right", fill="y")
        self.upper_bound.pack(side="right", fill="both", expand=True)

        self.lower_bound_frame.grid(row=3, column=1, sticky=N+E+W+S)
        self.lower_bound_unit_option.pack(side="right", fill="y")
        self.lower_bound.pack(fill="both", expand=True)

        self.order_button.grid(column=2, row=4)  #.place(relx=1, rely=1, x= -FRAME_IPAD[x], y= -FRAME_IPAD[y], anchor="se")


    # methods of passing functions
    @staticmethod
    def validate_leverage(leverage: str):
        return leverage.isdigit() or leverage == "" or leverage.count(".") == 1
    
    @staticmethod
    def validate_coin_qty(entry: str):
        global PLACEHODLER
        return entry.isdigit() or entry == "" or entry.count(".") == 1 or entry == PLACEHODLER
    
    @staticmethod
    def entry_click(event: Event):
        global PLACEHODLER
        if event.widget.get() == PLACEHODLER:
            event.widget.delete(0, END)
            event.widget.config(fg="black")
        elif event.widget.get() == "":
            event.widget.config(fg="grey")
            event.widget.insert(0, PLACEHODLER)
    
    @staticmethod
    def on_focusout(event: Event):
        global PLACEHODLER
        if event.widget.get() == '':
            event.widget.config(fg="grey")
            event.widget.insert(0, PLACEHODLER)

    def send_order_msg():
        pass


class position_frame(LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, kwargs)    # frame init

        # create related varible
        self._init_vars()
        self._init_widgets()

    def _init_vars(self):
        #  판매 상태 (판매 되면 체크, 아님 빈칸)| 코인 이름 | 량 | 가치 | calculated pnl | (entry price | market price 없앨수도 있음)| 구매 시작 시간 | 판매 된 경우 판매 시간 
        self.position_tree_heading = ("코인 이름", "보유량", "구매 가격", "상한", "하한", "tmp")
        self.positions = [
            ("Alice", 25, "USA", 1),
            ("Bob", 30, "UK", 2),
            ("Charlie", 22, "Canada", 3)
        ]

    def _init_widgets(self):
        self.position_treeview = ttk.Treeview(self, columns=self.position_tree_heading, show="headings")

        self.y_scroll_bar = ttk.Scrollbar(self, orient="vertical", command=self.position_treeview.yview)
        self.x_scroll_bar = ttk.Scrollbar(self, orient="horizontal", command=self.position_treeview.xview)

        self.position_treeview.configure(yscrollcommand=self.y_scroll_bar.set)
        self.position_treeview.configure(xscrollcommand=self.x_scroll_bar.set)

        # 열 헤더 설정
        for col in self.position_tree_heading:
            self.position_treeview.heading(col, text=col)
            self.position_treeview.column(col, width=100, anchor="center")
        
        # 데이터 추가
        for position in self.positions:
            self.position_treeview.insert("", END, values=position)

    def _pack_widgets(self, pad: tuple[int], ipad: tuple[int], side="bottom", fill="x"):
        super().pack(padx=pad[x], pady=pad[y], ipadx=ipad[x], ipady=ipad[y], side=side, fill=fill)

        self.x_scroll_bar.pack(side="bottom", fill="x")
        self.position_treeview.pack(side="left", expand=True, fill="both")
        self.y_scroll_bar.pack(side="right", fill="y")


class gui(Tk):
    def __init__(self):
        super().__init__()
        
        global window_height
        global window_width

        # 특성 설정
        self.title("Bitcoin Trader")
        self.resizable(False, False)
        self.geometry(f"{window_width}x{window_height}+{(self.winfo_screenwidth() - window_width)//2}+{(self.winfo_screenheight() - window_height)//2}")

        # 메뉴 설정
        self.menu = main_menu(self)
        self.config(menu=self.menu)
        
        # 프레임 설정
        self.position_frame = position_frame(self, text="현재 관리중인 코인")
        self.coin_frame = coin_frame(self, text="코인 설정")
        self.order_frame = order_frame(self, text="코인 구매 설정")

        # 가시화
        self.position_frame._pack_widgets(FRAME_PAD, FRAME_IPAD)
        self.coin_frame._pack_widgets(FRAME_PAD, FRAME_IPAD)
        self.order_frame._pack_widgets(FRAME_PAD, FRAME_IPAD)


def set_log_file_path(current_time: time.struct_time):
    # get month name
    month = numeric_to_string_month(current_time.tm_mon)

    # create log file name of current time
    log_file_name = f"{current_time.tm_year}-{current_time.tm_mon}-{current_time.tm_mday}.log"
    
    # set the folder of the file to be year and month
    log_path = f"./log/{current_time.tm_year}/{month}/" + log_file_name

    return log_path


if __name__ == "__main__":
    # create file and path for logfile setting based on current time 
    # path = set_log_file_path(time.localtime())
    # log_path = Path(path)
    # log_path.parent.mkdir(parents=True, exist_ok=True)   

    # # configure the logging
    # logging.basicConfig(
    #     filename = str(log_path),
    #     filemode = "a",
    #     encoding = "utf-8",
    #     level = logging.INFO,
    #     format = '[%(asctime)s] %(message)s',
    #     datefmt = '%H:%M:%S'
    # )


    # initializing tkinter
    main = gui()
    main.mainloop()
