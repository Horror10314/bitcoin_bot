import os
import time
import pandas as pd
import logging
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox

from trader import Trader, numeric_to_string_month
from dotenv import load_dotenv
from pathlib import Path
from tkinter import *


# class BybitFuturesTrader:
#     def __init__(self, apikey, rsa_private_key, testnet=True):
#         """
#         Bybit 선물 자동매매 시스템 초기화
        
#         Args:
#             api_key (str): Bybit API 키
#             api_secret (str): Bybit API 시크릿
#             testnet (bool): 테스트넷 사용 여부
#         """
#         self.session = HTTP(
#             testnet=testnet,
#             api_key=apikey,
#             rsa_authentication = True,
#             api_secret = rsa_private_key
#         )
        
#         # 트레이딩 설정
#         self.symbol = "BTCUSDT"
#         self.category = "linear"  # 선물
#         self.position_size = 0.01  # 포지션 크기 (BTC 단위)
#         self.stop_loss_pct = 0.02  # 손절매 2%
#         self.take_profit_pct = 0.04  # 익절 4%
        
#         # 상태 관리
#         self.position = None
#         self.last_signal = None
#         self.is_trading = False
        
#         # 로깅 설정
#         logging.basicConfig(level=logging.INFO, 
#                           format='%(asctime)s - %(levelname)s - %(message)s')
#         self.logger = logging.getLogger(__name__)
    
#     def get_account_info(self):
#         try:
#             response = self.session.get_account_info()
#             return response
#         except Exception as e:
#             self.logger.error(f"계정 정보 조회 실패: {e}")
#             return None
#     def get_current_price(self, symbol=None):
#         """현재가 조회"""
#         if symbol is None:
#             symbol = self.symbol
            
#         try:
#             response = self.session.get_tickers(
#                 category=self.category,
#                 symbol=symbol
#             )
#             if response['retCode'] == 0:
#                 return float(response['result']['list'][0]['lastPrice'])
#             return None
#         except Exception as e:
#             self.logger.error(f"현재가 조회 실패: {e}")
#             return None
#     def get_kline_data(self, interval="5", limit=100):
#         """캔들스틱 데이터 조회"""
#         try:
#             response = self.session.get_kline(
#                 category=self.category,
#                 symbol=self.symbol,
#                 interval=interval,
#                 limit=limit
#             )
            
#             if response['retCode'] == 0:
#                 klines = response['result']['list']
#                 df = pd.DataFrame(klines, columns=[
#                     'timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'
#                 ])
                
#                 # 데이터 타입 변환
#                 for col in ['open', 'high', 'low', 'close', 'volume']:
#                     df[col] = pd.to_numeric(df[col])
                
#                 df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms')
#                 df = df.sort_values('timestamp').reset_index(drop=True)
                
#                 return df
#             return None
#         except Exception as e:
#             self.logger.error(f"캔들스틱 데이터 조회 실패: {e}")
#             return None
    
#     def calculate_sma(self, data, window):
#         """단순 이동평균 계산"""
#         return data['close'].rolling(window=window).mean()
#     def calculate_rsi(self, data, period=14):
#         """RSI 계산"""
#         delta = data['close'].diff()
#         gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
#         loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
#         rs = gain / loss
#         rsi = 100 - (100 / (1 + rs))
#         return rsi
    
#     def generate_signal(self, data):
#         """매매 신호 생성 (단순한 이동평균 교차 전략)"""
#         if len(data) < 50:
#             return "HOLD"
        
#         # 기술적 지표 계산
#         data['sma_20'] = self.calculate_sma(data, 20)
#         data['sma_50'] = self.calculate_sma(data, 50)
#         data['rsi'] = self.calculate_rsi(data)
        
#         latest = data.iloc[-1]
#         prev = data.iloc[-2]
        
#         # 매수 신호: 단기 이평이 장기 이평을 상향돌파 + RSI < 70
#         if (prev['sma_20'] <= prev['sma_50'] and 
#             latest['sma_20'] > latest['sma_50'] and 
#             latest['rsi'] < 70):
#             return "BUY"
        
#         # 매도 신호: 단기 이평이 장기 이평을 하향돌파 + RSI > 30
#         elif (prev['sma_20'] >= prev['sma_50'] and 
#               latest['sma_20'] < latest['sma_50'] and 
#               latest['rsi'] > 30):
#             return "SELL"
        
#         return "HOLD"
    
#     def get_position_info(self):
#         """현재 포지션 정보 조회"""
#         try:
#             response = self.session.get_positions(
#                 category=self.category,
#                 symbol=self.symbol
#             )
            
#             if response['retCode'] == 0 and response['result']['list']:
#                 position_data = response['result']['list'][0]
#                 if float(position_data['size']) > 0:
#                     return {
#                         'side': position_data['side'],
#                         'size': float(position_data['size']),
#                         'entry_price': float(position_data['avgPrice']),
#                         'unrealized_pnl': float(position_data['unrealisedPnl']),
#                         'pnl_percentage': float(position_data['unrealisedPnl']) / float(position_data['positionValue']) * 100 if float(position_data['positionValue']) > 0 else 0
#                     }
#             return None
#         except Exception as e:
#             self.logger.error(f"포지션 정보 조회 실패: {e}")
#             return None
    
#     def place_order(self, side, order_type="Market", qty=None, price=None, stop_loss=None, take_profit=None):
#         """주문 실행"""
#         if qty is None:
#             qty = self.position_size
            
#         try:
#             order_params = {
#                 "category": self.category,
#                 "symbol": self.symbol,
#                 "side": side,
#                 "orderType": order_type,
#                 "qty": str(qty),
#                 "timeInForce": "GTC" if order_type == "Limit" else "IOC"
#             }
            
#             if price and order_type == "Limit":
#                 order_params["price"] = str(price)
            
#             if stop_loss:
#                 order_params["stopLoss"] = str(stop_loss)
                
#             if take_profit:
#                 order_params["takeProfit"] = str(take_profit)
            
#             response = self.session.place_order(**order_params)
            
#             if response['retCode'] == 0:
#                 self.logger.info(f"주문 성공: {side} {qty} {self.symbol}")
#                 return response
#             else:
#                 self.logger.error(f"주문 실패: {response}")
#                 return None
                
#         except Exception as e:
#             self.logger.error(f"주문 실행 실패: {e}")
#             return None
    
#     def close_position(self):
#         """포지션 청산"""
#         position = self.get_position_info()
#         if position:
#             opposite_side = "Sell" if position['side'] == "Buy" else "Buy"
#             return self.place_order(opposite_side, qty=position['size'])
#         return None
    
#     def check_stop_loss_take_profit(self):
#         """손절매/익절 체크"""
#         position = self.get_position_info()
#         if not position:
#             return
        
#         pnl_pct = position['pnl_percentage']
        
#         # 손절매 체크
#         if pnl_pct <= -self.stop_loss_pct * 100:
#             self.logger.info(f"손절매 실행: {pnl_pct:.2f}%")
#             self.close_position()
            
#         # 익절 체크
#         elif pnl_pct >= self.take_profit_pct * 100:
#             self.logger.info(f"익절 실행: {pnl_pct:.2f}%")
#             self.close_position()
    
#     def execute_strategy(self):
#         """전략 실행"""
#         try:
#             # 캔들스틱 데이터 조회
#             data = self.get_kline_data()
#             if data is None:
#                 return
            
#             # 매매 신호 생성
#             signal = self.generate_signal(data)
#             current_price = self.get_current_price()
            
#             self.logger.info(f"현재가: {current_price}, 신호: {signal}")
            
#             # 현재 포지션 확인
#             position = self.get_position_info()
            
#             if position:
#                 self.logger.info(f"현재 포지션: {position['side']} {position['size']}, "
#                                f"PnL: {position['pnl_percentage']:.2f}%")
                
#                 # 손절매/익절 체크
#                 self.check_stop_loss_take_profit()
                
#                 # 포지션과 반대 신호일 경우 청산
#                 if ((position['side'] == "Buy" and signal == "SELL") or 
#                     (position['side'] == "Sell" and signal == "BUY")):
#                     self.close_position()
#                     time.sleep(1)  # 청산 후 잠시 대기
                    
#             # 새로운 포지션 진입
#             if signal == "BUY" and (not position or position['side'] != "Buy"):
#                 stop_loss_price = current_price * (1 - self.stop_loss_pct)
#                 take_profit_price = current_price * (1 + self.take_profit_pct)
                
#                 self.place_order("Buy", 
#                                 stop_loss=stop_loss_price,
#                                 take_profit=take_profit_price)
                
#             elif signal == "SELL" and (not position or position['side'] != "Sell"):
#                 stop_loss_price = current_price * (1 + self.stop_loss_pct)
#                 take_profit_price = current_price * (1 - self.take_profit_pct)
                
#                 self.place_order("Sell",
#                                 stop_loss=stop_loss_price,
#                                 take_profit=take_profit_price)
                
#         except Exception as e:
#             self.logger.error(f"전략 실행 중 오류: {e}")
    
#     def start_trading(self, interval=60):
#         """자동매매 시작"""
#         self.is_trading = True
#         self.logger.info("자동매매 시작")
        
#         while self.is_trading:
#             try:
#                 self.execute_strategy()
#                 time.sleep(interval)  # 대기 시간 (초)
                
#             except KeyboardInterrupt:
#                 self.logger.info("사용자에 의해 중단됨")
#                 self.is_trading = False
#             except Exception as e:
#                 self.logger.error(f"예상치 못한 오류: {e}")
#                 time.sleep(10)  # 오류 발생 시 10초 대기 후 재시작
    
#     def stop_trading(self):
#         """자동매매 중단"""
#         self.is_trading = False
#         self.logger.info("자동매매 중단")

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

        self.order_button = Button(self, text="구매 및 전략 실행")

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


class position_frame(LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, kwargs)    # frame init

        # create related varible
        self._init_vars()
        self._init_widgets()

    def _init_vars(self):
        #  판매 상태 (판매 되면 체크, 아님 빈칸)| 코인 이름 | 량 | 가치 | calculated pnl | (entry price | market price 없앨수도 있음)| 구매 시작 시간 | 판매 된 경우 판매 시간 
        self.position_tree_heading = ("Name", "Age", "Country")
        self.positions = [
            ("Alice", 25, "USA"),
            ("Bob", 30, "UK"),
            ("Charlie", 22, "Canada")
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
        self.coin_list_box.bind("<<ComboboxSelected>>", func=lambda event: self.cur_price_label.config(text=f"You choose {self.coin_list_box.get()}"))
        
        self.coin_price_label = Label(self, text="You choose", font=("Arial", 14))
        self.current_balance = Label(self, text="Available Balance: 100$")
        self.current_margin_balance = Label(self, text="Margin Balance: 100$")

    def _pack_widgets(self, pad: tuple[int], ipad: tuple[int], fill="y", side="left"):
        super().pack(padx=pad[x], pady=pad[y], ipadx=ipad[x], ipady=ipad[y], fill=fill, side=side)
        self.coin_price_label.pack()
        self.coin_list_box.pack()
        self.current_balance.pack(side="bottom")
        self.current_margin_balance.pack(side="bottom")  


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
    """
    # # API 키 설정 (실제 키로 변경 필요)
    # load_dotenv()
    # key_path = os.getenv("PRIVATE_KEY_PATH")
    # with open(key_path, "r") as key_file:
    #     private_key = key_file.read()
    # API_KEY = "DFnhgHXGXV0X3CFTx5"
    
    # # 트레이더 인스턴스 생성
    # trader = BybitFuturesTrader(API_KEY, private_key, testnet=False)
    
    # # 계정 정보 확인
    # account_info = trader.get_account_info()
    # if account_info:
    #     print("계정 정보:", json.dumps(account_info, indent=2))

    # # 자동매매 시작 (60초 간격)
    # # try:
    # #     trader.start_trading(interval=60)
    # # except Exception as e:
    # #     print(f"오류 발생: {e}")
    # # finally:
    # #     trader.stop_trading()"""
    
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

    # get keys for initializing
    load_dotenv()   # load environment file
    with open(os.getenv("API_KEY_PATH"), "r") as f:
        api_key = f.read()
    with open(os.getenv("PRIVATE_KEY_PATH"), "r") as f:
        rsa_private_key = f.read()

    # initialize the trader
    #trader = Trader(api_key, rsa_private_key, logger=logging.getLogger(__name__))
    
    # main loop
    #trader.trading_loop()

    # initializing tkinter
    main = gui()
    main.mainloop()
