import logging
import json

from dataclasses import dataclass
from pybit.unified_trading import HTTP
from pybit._helpers import is_usdt_perpetual, is_usdc_perpetual
from decimal import Decimal

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


class Trader:
    session: HTTP                           # connection with bitcon trading server
    __balance: TradeBalance                 # balance info
    positions: list[str]                    # or dict(coin name : info) trading info: position
    trading_setting: dict[str, TradingSetting]   # or dict(coin name: TradingSetting) trading setting
    logger: logging.Logger                  # logger for log

    def __init__(self, api_key, api_secret, rsa_auth=True, testnet=False, logger=None):        
        self.session = HTTP(
            api_key=api_key,
            api_secret = api_secret,
            rsa_authentication=rsa_auth,    
            testnet=testnet
        )

        # self.success, self.test = successful(
        #     self.session.get_positions(category="linear", symbol=None, settleCoin="USDT")
        # )
        
        
        # if self.success:
        #     for symbols in self.test["result"]["list"]:
        #         if is_usdt_perpetual(symbols['symbol']):
        #             print(symbols['symbol'], ":", symbols['displayName'])

        self.__balance = TradeBalance(0,0,0)
        self.positions = []
        self.trading_setting = []
        self.logger = logger


    # 현재 정보
    #   - 현재 돈 (availaibe balance)
    #   - 현재 투자 가치 (margin balance)
    #   - 현재 이득 (P&L)
    #   - 현재 산 코인 들
    #   - 각 코인의 포지션

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

    def get_pnl(self):  
        # get_positions(coin_name)             
        pass
    
    def get_position(self):
        self.success, positions = successful(
            self.session.get_positions(category="linear", symbol=None, settleCoin="USDT")
        )

        if self.success:
            for pos in positions['result']['list']:
                self.positions.append(pos['symbol'])
        
        return self.positions
                

    def get_all_coins(self):
        return self.positions

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

    # 종료 및 시작 기능
    #   - 종료
    #   - 메인 루프
    def trading_loop(self):
        self.logger.info("===== Tradier Starts =====")

        # main loop your main stratgy going here
        

        self.logger.info("=====  Trader Ends  =====")

    def kill(self):
        pass


# debugging purpose
def debug_main():
    #import json
    import os
    from dotenv import load_dotenv

    load_dotenv()   # load environment file
    with open(os.getenv("API_KEY_PATH"), "r") as f:
        api_key = f.read()
    with open(os.getenv("PRIVATE_KEY_PATH"), "r") as f:
        rsa_private_key = f.read()

    # initialize the trader
    trader = Trader(api_key, rsa_private_key, testnet=False, logger=logging.getLogger(__name__))


if __name__ == "__main__":
    debug_main()
