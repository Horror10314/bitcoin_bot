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