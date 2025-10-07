import logging
import json
import time
import socket
import threading
import struct
import copy

from dataclasses import dataclass
from pybit.unified_trading import HTTP
from decimal import Decimal
from peekqueue import PeekableQueue

MONTH = [
    "January"     ,
    "February"    ,
    "March"       ,
    "April"       ,
    "May"         ,
    "June"        ,
    "July"        ,
    "August"      ,
    "September"   ,
    "October"     ,
    "November"    ,
    "December"    ,
]


def numeric_to_string_month(month):
    """num: 1-12, this function returns the name of the month in string based on number"""
    return MONTH[month - 1]


def set_log_file_path(current_time: time.struct_time):
    # get month name
    month = numeric_to_string_month(current_time.tm_mon)

    # create log file name of current time
    log_file_name = f"{current_time.tm_year}-{current_time.tm_mon}-{current_time.tm_mday}.log"
    
    # set the folder of the file to be year and month
    log_path = f"./log/{current_time.tm_year}/{month}/" + log_file_name

    return log_path


@dataclass
class TradeBalance:
    initial_balance: float # or str
    margin_balance: float # or str
    profit: float # or str / marigin_balance - initial_balance


@dataclass
class TradingSetting:
    symbol: str
    #category: str   # not used as always linear
    leverage: str   # or float
    position_size: float  
    stop_loss_pct: float 
    take_profit_pct: float


# helpful function to check whether the http request was successful
def successful(returns) -> tuple[bool, dict]:
    """
    Check return code and message and return True and result if the request is successful.\n
    CAUTION\n
    This is fully based on bybit api. Do NOT use it for other than the bybit api's result.
    """

    # static constant variable
    RETCODE = "retCode"
    SUC_RETCODE = 0
    RETMSG  = "retMsg"
    SUC_RETMSG = ["OK", "SUCCESS", ""]
    success = False

    if isinstance(returns, dict):
        if returns[RETCODE] == SUC_RETCODE and returns[RETMSG].upper() in SUC_RETMSG:
            success = True
        else:
            returns = returns[RETMSG]

    return success, returns


class QueueItem:
    def __init__(self, priority_time: int, handler: str):
        self.priority_time = priority_time      # time is the id for priority queue 
        self.handler = handler                  # key of handler lookup dictionary 

    def __lt__(self, other):
        return self.priority_time < other.priority_time

    def __str__(self):
        return f"Time interval {self.priority_time} with handler key of {self.handler}"
    
    def __isub__(self, other):
        "decrease the priority time"
        if isinstance(other, int):
            self.priority_time -= other
        elif isinstance(other, QueueItem):
            self.priority_time -= other
        else:
            raise TypeError(f"Not supporint type for QueueItem: {type(other)}")
        return self

    # getters
    def get_priority_time(self): return self.priority_time
    def get_handler(self): return self.handler

    # setters
    def set_priority_time(self, time):         
        self.priority_time = max(time, 0)
    def set_handler(self, handler):
        self.handler = handler


class WorkItem(QueueItem):
    def __init__(self, priority_time: int = 1, handler: str = "check"): # or use *args
        super().__init__(priority_time, handler)


class CoinItem(QueueItem):
    def __init__(self, coin_entry_price: Decimal, coin_qty: Decimal, coin_name: str, long: bool, priority_time: int = 2, handler: str = "stat1"):
        super().__init__(priority_time, handler)
        self.coin_name = coin_name
        self.coin_qty = coin_qty
        self.coin_entry_price = coin_entry_price
        self.long = long
    
    def __str__(self):
        return super().__str__() + f", coin entry price {self.coin_entry_price}, coin qty {self.coin_qty}, and coin name {self.coin_name}"


class Trader:
    def __init__(self, api_key, api_secret, rsa_auth=True, testnet=False):
        self.session = HTTP(
            testnet=testnet,
            api_key=api_key,
            api_secret = api_secret,
            rsa_authentication=rsa_auth
        )
        self.positions = []

    # using get_wallet_balance
    # 
    # > totalWalletBalance	string	Account wallet balance (USD): ∑Asset Wallet Balance By USD value of each asset
    # > totalMarginBalance	string	Account margin balance (USD): totalWalletBalance + totalPerpUPL
    # > totalAvailableBalance	string	Account available balance (USD), Cross Margin: totalMarginBalance - totalInitialMargin
    # > totalPerpUPL	string	Account Perps and Futures unrealised p&l (USD): ∑Each Perp and USDC Futures upl by base coin
    # > totalInitialMargin	string	Account initial margin (USD): ∑Asset Total Initial Margin Base Coin
    def get_wallet_balance(self) -> Decimal:
        self.success, self.result = successful(
            self.session.get_wallet_balance(accountType="UNIFIED")
        )

        if self.success:
            return Decimal(self.result['result']['list'][0]['coin'][0]['walletBalance'])

    def get_margin_balance(self):       
        self.session.get_wallet_balance()

    def get_available_balance(self) -> Decimal:
        self.success, self.result = successful(
            self.session.get_coins_balance(accountType="UNIFIED", coin="USDT")
        )

        if self.success:
            return Decimal(self.result['result']['balance'][0]['transferBalance'])

    def get_live_positions(self):
        self.success, new_positions = successful(
            self.session.get_positions(category="linear", symbol=None, settleCoin="USDT")
        )
        if self.success:
            return new_positions['result']['list']
    
    def get_live_position(self, coin_name):
        self.success, new_positions = successful(
            self.session.get_positions(category="linear", symbol=coin_name, settleCoin="USDT")
        )
        if self.success:
            return new_positions['result']['list']
    
    def update_position(self, work_queue: PeekableQueue, current_task: WorkItem, setting: dict[str, dict]):
        self.success, new_positions = successful(
            self.session.get_positions(category="linear", symbol=None, settleCoin="USDT")
        )
        # create list of only symbols of positions
        if self.success:
            # update positions
            new_positions = new_positions['result']['list']

            # record new position for adding queue
            for new_pos in new_positions:
                # add to queue if new position is added
                if new_pos['symbol'] not in [pos['symbol'] for pos in self.positions]:
                    with threading.Lock():
                        newtask = CoinItem(Decimal(new_pos['avgPrice']), Decimal(new_pos['size']), new_pos['symbol'], new_pos['side'] == "Buy", priority_time=setting['frequency'])
                        work_queue.put(newtask)
            
            self.positions = new_positions

        print(f"This is checking position of doing{current_task}")
        print(f"Current positions: {[pos['symbol'] for pos in self.positions]}")
            
        # add checking position work back to queue
        current_task.set_priority_time(setting['frequency'])
        work_queue.put(current_task)
                
    # 선물 매매
    #   - 구매 
    #   - 판매
    #   using place_order

    def buy_coin_future(self, coin_name, amount, leverage, order_type="Market"):
        leverage = str(leverage)
        self.session.set_leverage(category="linear", symbol=coin_name, buyLeverage=leverage, sellLeverage=leverage)
        
        success, result = successful(self.session.place_order(
            category="linear",
            symbol=coin_name,
            side="Buy",
            orderType=order_type,
            qty=amount
        ))

        return success
    
    def sell_coin_future(self, coin_name, order_type="Market"):
        success, result = successful(self.session.place_order(
            category="linear",
            symbol=coin_name,
            side="Sell",
            orderType=order_type,
        ))
        return success
    

    # 전략 구현
    def strategy1(self, work_queue: PeekableQueue, current_task: CoinItem, setting: dict):
        print(f"This is strategy 1 with doing {current_task}")
        
        # 내가 구입한 가격 얻기 
        # 내가 구입한 코인의 qty얻기
        # 현재 시장가 얻기
        
        # 시장가가 원하는 이득에 상승하면 익절
        # 시장가가 (설정한) 반대로 하락하면 
        #   - 추가 롱채결 ()
        #   - 익절 가격 조절 (새 평단 + 원래 익절 간격)

        # 시장가가 손절 가격 까지 가면 자동 손절. (또는 사용자가 수동으로 bybit웹/앱에서 손절 가능)

        # 그사이면 아무것도 안함
        pos = self.get_live_position(current_task.coin_name)

        if Decimal(pos['size']) > 0:

            # calculate price
            upperbound_price = current_task.coin_entry_price + Decimal(setting['upperbound']['value'])\
                                if setting['upperbound']['unit'] == "$"\
                                else current_task.coin_entry_price + current_task.coin_entry_price * Decimal(setting['upperbound']['value']) /100
            
            lowerbound_price = current_task.coin_entry_price + Decimal(setting['lowerbound']['value'])\
                                if setting['lowerbound']['unit'] == "$"\
                                else current_task.coin_entry_price + current_task.coin_entry_price * Decimal(setting['lowerbound']['value']) /100
            
            stoploss_price = current_task.coin_entry_price - Decimal(setting['stoploss']['value']) \
                                if setting['stoploss']['unit'] == "$"\
                                else current_task.coin_entry_price - current_task.coin_entry_price * Decimal(setting['stoploss']['value']) / 100

            cur_price = Decimal(pos['markPrice'])


            # execute strategy
            if cur_price < stoploss_price:  
                self.sell_coin_future(current_task.coin_name)
            elif cur_price > upperbound_price:
                if current_task.long:   
                    # made a profit
                    self.sell_coin_future(current_task.coin_name)
                else:
                    # continue
                    self.buy_coin_future(current_task.coin_name, str(current_task.coin_qty * 2))
            elif cur_price < lowerbound_price:
                if current_task.long:
                    #continue
                    self.buy_coin_future(current_task.coin_name, str(current_task.coin_qty * 2))
                else: 
                    # made a profit
                    self.sell_coin_future(current_task.coin_name)
            # else:
            #     do nothing

        # put the task back to queue
        current_task.set_priority_time(setting['frequency'])
        work_queue.put(current_task)


class MainWorker:
    trader: Trader
    handlers: dict                          # dict[str, func] dictionary of functions for callback, these fuctions may return
    work_queue: PeekableQueue[QueueItem]
    logger: logging.Logger                  # logger for log
    server_sock: socket.socket

    def __init__(self, trader: Trader, setting: dict, logger: logging.Logger):        
        
        # ============================ socket part ===================================
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


        # ============================ worker part ===================================
        self.trader = trader
        self.handlers = {
            "debug": lambda x: print(f"This is debuging with item: {x}"),
            "check": self.trader.update_position,
            "stat1": self.trader.strategy1,
        }
        self.work_queue = PeekableQueue()
        self.logger = logger

        self.default_setting = setting
        self.coin_settings = {}

        # ======================== initialization =====================================
        # initialize the queue with checking position item
        self.work_queue.put(WorkItem(self.default_setting['frequency'], "check"))
        self.stop_event = threading.Event()

        # create server thread
        self.server_thread = threading.Thread(target=self.server_loop, args=[self.stop_event], daemon=True)
        self.server_thread.start()


    def update_setting(self):
        # udpate: add coin in the setting list
        with threading.Lock():
            for pos in self.trader.positions:
                if pos['symbol'] not in self.coin_settings.keys():
                    self.coin_settings[pos['symbol']] = copy.deepcopy(self.default_setting)

            # update: remove coin in the setting list
            for coin in self.coin_settings.keys():
                if coin not in [pos['symbol'] for pos in self.trader.positions]:
                    del self.coin_settings[coin]


    def mainloop(self):
        task: QueueItem
        try:
            # main loop
            while True:
                # wait 
                time.sleep(self.work_queue.peek_first().get_priority_time())
                # time to do work
                self.work_queue.decrease(self.work_queue.peek_first().get_priority_time())

                # do all works that has same priority
                while self.work_queue.peek_first().get_priority_time() == 0:
                    task = self.work_queue.get()

                    # call handler (and do stuff)
                    with threading.Lock():
                        if isinstance(task, CoinItem):
                            self.handlers[task.get_handler()](self.work_queue, task, self.coin_settings[task.coin_name])
                        elif isinstance(task, WorkItem):
                            self.handlers[task.get_handler()](self.work_queue, task, self.default_setting)

                    self.work_queue.task_done()
                
                self.update_setting()

        except KeyboardInterrupt:
                self.stop_event.set()
                print("exit")
                

    # destructor, kind of.
    def exit(self):
        # 소켓 및 스레드 정리
        self.server_sock.close()


    # ===================================================== network method =======================================================
    
    
    # ========= 공통: 길이프리픽스 송수신 =========
    def send_msg(self, payload: dict):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.server_sock.sendall(struct.pack("!I", len(data)) + data)

    def recv_msg(self) -> dict:
        data = self.server_sock.recv(1024)
        return json.loads(data.decode("utf-8"))

    def do_get_request_task(self, result, data):
        print(self.trader.positions)
        if data['what'] == 'symbols':
            result['symbols'] = [coin['symbol'] for coin in self.trader.positions]
        
        else: # get coin setting
            with threading.Lock():
                result['setting'] = self.coin_settings[data['what']]
            

    def do_set_request_task(self, result, data):
        if data['what'] == "default":            
            # update json file
            with open('default.json', 'w') as setting_file:
                # nothing else to change except frquency.
                with threading.Lock():
                    self.default_setting['frequency'] = int(data['change'])

                # update
                json.dump(self.default_setting, setting_file, ensure_ascii=False, indent=4)

        elif data['what'] in [pos['symbol'] for pos in self.trader.positions]:
            # do setting
            with threading.Lock():
                print("setting changed!")
                # update only not None setting
                for key, val in self.coin_settings[data['what']].items():
                    if data['change'][key]:
                        # if dict = upper bound, lower bound stop loss
                        if isinstance(data['change'][key], dict):
                            # update unit and value
                            for in_key in val.keys():
                                if data['change'][key][in_key]:
                                    self.coin_settings[data['what']][key][in_key] = data['change'][key][in_key]
                        # frequency, strategy
                        else:
                            self.coin_settings[data['what']][key] = data['change'][key]


    def server_loop(self, stop_event: threading.Event): # this server gonna be reply server
        self.server_sock.bind(("localhost", 55555))
        self.server_sock.listen(0)
        
        self.server_sock.settimeout(5)  # 주기적으로 stop_event 확인
        
        print("Thread opened successful")

        while not stop_event.is_set():
            try:
                client_sock, addr = self.server_sock.accept()
            except socket.timeout:
                continue

            with client_sock:
                client_sock.settimeout(3.0)
                
                try:
                    while True:
                        
                        # ========= main communication with client here
                        try:
                            data = json.loads(client_sock.recv(65535).decode("utf-8"))
                        except socket.timeout:
                            continue

                        result = {
                            "ret": "success",
                        }
                        # parse the request
                        match data['req']:
                            case 'get':
                                print("doing getting")
                                self.do_get_request_task(result, data)
                            case 'set':
                                self.do_set_request_task(result, data)
                            case _:
                                result = {'ret' : 'fail'}
                
                        client_sock.send(json.dumps(result, ensure_ascii=False).encode("utf-8"))

                except (ConnectionError, json.JSONDecodeError) as e:
                    print(f"[server] client disconnected: {e}")
                finally:
                    print("[server] session closed; waiting next client...")
        else:
            self.exit()
                    

# debugging purpose
def main():
    import os
    from dotenv import load_dotenv

    load_dotenv()   # load environment file
    with open(os.getenv("API_KEY_PATH"), "r") as f:
        api_key = f.read()
    with open(os.getenv("PRIVATE_KEY_PATH"), "r") as f: 
        rsa_private_key = f.read()

    with open("default.json", "r", encoding="utf-8") as default_json_file:
        default_setting = json.load(default_json_file)

        print(json.dumps(default_setting, indent=3))

    # initialize the trader
    trader = Trader(api_key, rsa_private_key, testnet=False)
    worker = MainWorker(trader, default_setting, logger=logging.getLogger(__name__))

    #worker.mainloop()
    worker.mainloop()



if __name__ == "__main__":
    main()
