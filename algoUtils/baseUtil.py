"""
@Create: 2024/9/30 14:06
@File: defUtil.py
@Author: Jijingyuan
"""
import abc
import asyncio
import uuid
import numpy as np
from typing import Optional, List, Dict
from .schemaUtil import *

from .loggerUtil import generate_logger
from .onlineLoggerUtil import OnlineLogger

logger = generate_logger()


class QuicEventBase:
    def __init__(self):
        self.connections = {}
        self.cache = asyncio.Queue()

    def on_connected(self, _host_id: bytes):
        pass

    def on_disconnected(self, _host_id: bytes):
        pass

    async def get_data(self):
        return await self.cache.get()

    async def send_msg(self, _host_id: bytes, _msg: bytes):
        conn = self.connections.get(_host_id)
        if not conn:
            logger.error('{} is not available'.format(_host_id))
            return

        await conn.send_msg(_msg)

    async def send_all(self, _msg: bytes):
        tasks = [v.send_msg(_msg) for v in self.connections.values()]
        await asyncio.gather(*tasks)

    async def loop_service(self):
        pass


class SignalBase(abc.ABC):
    @abc.abstractmethod
    def update_state(self, _current_ts: float, _data: Dict[str, np.ndarray]):
        """
        update state base on the data
        :param _current_ts: current timestamp
        :param _data: {symbol: np.ndarray[[recv_ts, exchange_ts, price, amount, direction], ...], ...}
        """
        pass
    
    @abc.abstractmethod
    def generate_signals(self, _current_ts: float, _data: Dict[str, np.ndarray]) -> Optional[Signal]:
        """
        generate signal to execution module
        :param _current_ts: current timestamp
        :param _data: {symbol: np.ndarray[[recv_ts, exchange_ts, price, amount, direction], ...], ...}
        :return: Signal
        class Signal:
            batch_id: str  # str(uuid)
            symbol: Union[str, List[str]]  # 'btc_usdt|binance_future'
            price: Union[float, List[float]]  # positive if long, negative if short
        """
        return


class TargetBase(abc.ABC):
    @abc.abstractmethod
    def init_instance(self, _signal: Signal):
        pass

    @abc.abstractmethod
    def generate_targets(self, _current_ts: float, _data: Dict[str, np.ndarray]) -> Optional[Dict[str, float]]:
        """
        generate target dict that could be used in intercept modeling
        :param _current_ts: current timestamp
        :param _data: {symbol: np.ndarray[[recv_ts, exchange_ts, price, amount, direction], ...], ...}
        :return: None or dict
        """
        pass  # 使用 pass 而不是 return

    @abc.abstractmethod
    def intercept_signal_given_targets(self, _targets: Dict[str, float]) -> bool:
        """
        intercept signal base on the target
        :param _targets: targets
        :return: True or False
        """
        pass


class FeatureBase(abc.ABC):
    @abc.abstractmethod
    def update_state(self, _current_ts: float, _data: Dict[str, np.ndarray]):
        """
        update state base on the data
        :param _current_ts: current timestamp
        :param _data: {symbol: np.ndarray[[recv_ts, exchange_ts, price, amount, direction], ...], ...}
        """
        pass

    @abc.abstractmethod
    def generate_features(self, _current_ts: float, _data: Dict[str, np.ndarray]) -> Optional[Dict[str, float]]:
        """
        generate features dict based on the state
        :param _current_ts: current timestamp
        :param _data: {symbol: np.ndarray[[recv_ts, exchange_ts, price, amount, direction], ...], ...}
        :return: None or dict
        """
        pass


class SelectorBase(abc.ABC):
    @abc.abstractmethod
    def select_features(self, _features: List[Dict[str, float]], _targets: List[Dict[str, float]]) -> Optional[List[str]]:
        # 筛选特征
        # 返回特征列表
        # 特征列表为空，则不进行特征筛选
        pass


class ModelBase(abc.ABC):  # 继承 abc.ABC
    @abc.abstractmethod
    def check_feature_drift(self, _features: List[Dict[str, float]], _targets: List[Dict[str, float]]) -> bool:
        # 若模型不支持增量学习，则**忽略此函数**
        # 实现特征飘变检测逻辑
        pass

    @abc.abstractmethod
    def incremental_train(self, _features: List[Dict[str, float]], _targets: List[Dict[str, float]]):
        # 若模型不支持增量学习，则**忽略此函数**
        # 实现增量训练逻辑
        pass

    @abc.abstractmethod
    def full_train(self, _features: List[Dict[str, float]], _targets: List[Dict[str, float]]):
        # 实现全量训练逻辑
        pass
    
    @abc.abstractmethod
    def train_model(self, _features: List[Dict[str, float]], _targets: List[Dict[str, float]]):
        # 若模型不支持增量学习，则**直接调用full_train**
        # 整合训练逻辑（全量/增量）
        pass

    @abc.abstractmethod
    def predict(self, _features: Dict[str, float]) -> Optional[Dict[str, float]]:
        # 实现预测逻辑
        pass


class PerformanceBase(abc.ABC):
    @abc.abstractmethod
    def init_signal(self, _signal: Signal):
        pass

    @abc.abstractmethod
    def generate_trading_result(self, _data: Dict[str, np.ndarray]) -> Optional[TradingResult]:
        """
        generate trading result for signals
        :param _data: {symbol: np.ndarray[[recv_ts, exchange_ts, price, amount, direction], ...], ...}
        :return: TradingResult
        """
        pass


class OptimizerBase(abc.ABC):
    @abc.abstractmethod
    def on_timer(self, _current_ts: float) -> Optional[List[str]]:
        pass

    @abc.abstractmethod
    def on_order(self, _current_ts: float, _strategy_id: str, _order_info: OrderInfo) -> Optional[List[str]]:
        pass

    @abc.abstractmethod
    def on_sniffer(self, _current_ts: float, _strategy_id: str, _sniffer_info: TargetSnifferInfo | TrailingSnifferInfo) -> Optional[List[str]]:
        pass

    @abc.abstractmethod
    def on_earning(self, _current_ts: float, _strategy_id: str, _earning_info: EarningInfo) -> Optional[List[str]]:
        pass

    @abc.abstractmethod
    def get_local_values(self) -> Optional[Dict[str, Union[float, str, List, Dict]]]:
        pass

    @abc.abstractmethod
    def set_local_values(self, _local_dict: Optional[Dict[str, Union[float, str, List, Dict]]]):
        pass


class RiskBase(abc.ABC):
    @abc.abstractmethod
    def on_timer(self, _current_ts: float) -> Optional[List[str]]:
        pass
    
    @abc.abstractmethod
    def on_order(self, _current_ts: float, _strategy_id: str, _order_info: OrderInfo) -> Optional[List[str]]:
        pass

    @abc.abstractmethod
    def on_sniffer(self, _current_ts: float, _strategy_id: str, _sniffer_info: TargetSnifferInfo | TrailingSnifferInfo) -> Optional[List[str]]:
        pass

    @abc.abstractmethod
    def on_earning(self, _current_ts: float, _strategy_id: str, _earning_info: EarningInfo) -> Optional[List[str]]:
        pass

    @abc.abstractmethod
    def get_local_values(self) -> Optional[Dict[str, Union[float, str, List, Dict]]]:
        pass

    @abc.abstractmethod
    def set_local_values(self, _local_dict: Optional[Dict[str, Union[float, str, List, Dict]]]):
        pass


class LiquidityBase(abc.ABC):
    @abc.abstractmethod
    def on_timer(self, _current_ts: float) -> Optional[Dict[str, float]]:
        pass
    
    @abc.abstractmethod
    def on_order(self, _current_ts: float, _strategy_id: str, _order_info: OrderInfo) -> Optional[Dict[str, float]]:
        pass

    @abc.abstractmethod
    def on_sniffer(self, _current_ts: float, _strategy_id: str, _sniffer_info: TargetSnifferInfo | TrailingSnifferInfo) -> Optional[Dict[str, float]]:
        pass

    @abc.abstractmethod
    def on_earning(self, _current_ts: float, _strategy_id: str, _earning_info: EarningInfo) -> Optional[Dict[str, float]]:
        pass

    @abc.abstractmethod
    def get_local_values(self) -> Optional[Dict[str, Union[float, str, List, Dict]]]:
        pass

    @abc.abstractmethod
    def set_local_values(self, _local_dict: Optional[Dict[str, Union[float, str, List, Dict]]]):
        pass


class OrderBase(abc.ABC):
    ORDER_STATUS = {
        'pending': 0,
        'waiting': 1,
        'triggered': 2,
        'partial_filled': 3,
        'canceling': 4,
        'canceled': 5,
        'error': 5,
        'filled': 5
    }

    SNIFFER_STATUS = {
        'pending': 0,
        'waiting': 1,
        'triggered': 2,
        'canceled': 2,
        'error': 2
    }

    def __init__(self):
        self._precision_dict: Dict[str, PrecisionDict] = {}

    def format_amount(self, _symbol, _amount, _upper=True) -> float:
        amount_p = self._precision_dict[_symbol].amount
        factor = 10 ** amount_p
        int_amount = int(_amount * factor)
        bias = 1 if _upper else 0
        return round((int_amount + bias) / factor, amount_p)

    def format_price(self, _symbol, _price, _upper=True) -> float:
        price_p = self._precision_dict[_symbol].price
        factor = 10 ** price_p
        int_price = int(_price * factor)
        bias = 1 if _upper else 0
        return round((int_price + bias) / factor, price_p)
    
    @abc.abstractmethod
    async def get_batch_price(self, _symbol, _start_ts, _end_ts) -> np.ndarray:
        pass

    @abc.abstractmethod
    def get_current_price(self, _symbol) -> float:
        pass

    @abc.abstractmethod
    def get_trading_cash(self, _symbol) -> float:
        pass

    @abc.abstractmethod
    def get_current_timestamp(self) -> float:
        pass

    @abc.abstractmethod
    async def place_timer(self, _to_timestamp, _event):
        pass

    @abc.abstractmethod
    async def place_order(
            self,
            _batch_id,
            _symbol,
            _order_type,
            _action,
            _position,
            _amount,
            _feature=None,
            _expire=None,
            _delay=None,
            _condition=None,
            _price=None,
    ) -> str:
        pass

    @abc.abstractmethod
    async def place_target_sniffer(
            self,
            _batch_id,
            _symbol,
            _operator,
            _target_price,
            _expire=None,
            _delay=None
    ) -> str:
        pass

    @abc.abstractmethod
    async def place_trailing_sniffer(
            self,
            _batch_id,
            _symbol,
            _operator,
            _target_price,
            _back_pct,
            _smooth=None,
            _expire=None,
            _delay=None
    ) -> str:
        pass

    @abc.abstractmethod
    async def cancel_order(self, _order_id, _delay=None):
        pass

    @abc.abstractmethod
    async def cancel_sniffer(self, _order_id, _delay=None):
        pass

    @abc.abstractmethod
    def _update_precision_dict(self, _symbol: str, _trades: np.ndarray): 
        pass


class ExecuteBase(abc.ABC):
    def __init__(self):
        self.order_mgr: OrderBase = None  # type: ignore
        self.logger: OnlineLogger = None # type: ignore

    def init_mgr(self, _order_mgr: OrderBase, _logger_type: str):
        self.order_mgr = _order_mgr
        self.logger = OnlineLogger(_logger_type)

    @abc.abstractmethod
    async def on_signal(self, _signal: Signal):
        pass

    @abc.abstractmethod
    async def on_order(self, _order_info: OrderInfo):
        pass

    @abc.abstractmethod
    async def on_sniffer(self, _sniffer_info: TargetSnifferInfo | TrailingSnifferInfo):
        pass

    @abc.abstractmethod
    async def on_timer(self, _event):
        pass

    @abc.abstractmethod
    async def on_start(self, _event):
        pass

    @abc.abstractmethod
    async def on_stop(self, _event):
        pass

    @abc.abstractmethod
    def get_local_values(self) -> Optional[Dict[str, Union[float, str, List]]]:
        pass

    @abc.abstractmethod
    def set_local_values(self, _local_dict: Optional[Dict[str, Union[float, str, List]]]):
        pass
