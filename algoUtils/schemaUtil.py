"""
@Create: 2024/9/30 14:06
@File: defUtil.py
@Author: Jijingyuan
"""
from typing import Optional, List, Dict, Any, Union, Literal, Hashable
from pydantic import BaseModel, field_validator, model_validator


class Signal(BaseModel):
    batch_id: str  # str(uuid)
    symbol: Union[str, List[str]]  # 'btc_usdt|binance_future'
    price: Union[float, List[float]]  # positive if long, negative if short
    timestamp: float = 0  # timestamp default is 0   
    other_info: Optional[Dict[Hashable, Any]] = None

    @model_validator(mode='after')
    def validate_price_and_symbol(cls, data):
        # 检查price和symbol的类型是否一致（都是单个值或都是列表）
        if isinstance(data.price, list) != isinstance(data.symbol, list):
            raise ValueError("price和symbol必须类型一致，要么都是单个值，要么都是列表")
        
        # 如果都是列表，检查长度是否相等
        if isinstance(data.price, list) and isinstance(data.symbol, list):
            if len(data.price) != len(data.symbol):
                raise ValueError("当price和symbol都是列表时，长度必须相等")
        
        return data


class TradingResult(BaseModel):
    success: bool
    direction: Optional[int] = None
    entry_timestamp: Optional[float] = None
    exit_timestamp: Optional[float] = None
    is_win: Optional[int] = None  # 1: win, 0: lose
    trade_ret: Optional[float] = None
    trade_duration: Optional[float] = None


class Sample(BaseModel):
    signal: Signal
    features: Optional[Dict[str, float]] = {}
    targets: Optional[Dict[str, float]] = {}
    fields: Optional[List[str]] = None
    intercept: Optional[bool] = None
    sim_targets: Optional[Dict[str, float]] = {}
    sim_intercept: Optional[bool] = None


class SignalMgrParam(BaseModel):
    signal_method_name: str
    signal_method_param: Dict[str, Any] = {}
    cool_down_ts: Optional[float] = 1


class FeatureMgrParam(BaseModel):
    feature_method_name: str
    feature_method_param: Dict[str, Any] = {}


class TargetMgrParam(BaseModel):
    target_method_name: str
    target_method_param: Dict[str, Any] = {}
    target_fields: Optional[Union[List[str], str]] = None


class ModelMgrParam(BaseModel):
    model_method_name: str
    model_method_param: Dict[str, Any] = {}
    model_cache_size: int = 100
    model_retain_size: int = 0


class PerformanceMgrParam(BaseModel):
    performance_name: str
    performance_method_name: str
    performance_method_param: Dict[str, Any] = {}


class ExecuteMgrParam(BaseModel):
    execute_name: str
    execute_method_name: str
    execute_method_param: Dict[str, Any] = {}


class SignalTaskParam(BaseModel):
    signal_task_name: str
    signal_mgr_param: SignalMgrParam
    feature_mgr_params: Optional[Union[List[FeatureMgrParam], FeatureMgrParam]] = None
    target_mgr_param: Optional[TargetMgrParam] = None
    model_mgr_param: Optional[ModelMgrParam] = None
    lag: Optional[float] = None
    symbols: Union[List[str], str]
    data_type: str
    start_timestamp: float
    end_timestamp: float


class PerformanceTaskParam(BaseModel):
    performance_task_name: str
    performance_mgr_params: Union[List[PerformanceMgrParam], PerformanceMgrParam]
    signal_paths: List[str]


class UpdateOrderInfo(BaseModel):
    """
    更新订单信息
    """
    order_id: str
    status: Literal['waiting', 'triggered', 'partial_filled', 'canceling', 'canceled', 'error', 'filled']
    exchange_timestamp: float
    local_timestamp: float
    execute_price: float = 0
    execute_amount: float = 0
    fee_rate: Optional[float] = None
    msg: Optional[Dict[str, Any]] = None

    @field_validator('exchange_timestamp', 'local_timestamp')
    @classmethod
    def validate_timestamp_precision(cls, v):
        if v is not None:
            # 确保时间戳保留三位小数
            return round(float(v), 6)
        return v


class UpdateSnifferInfo(BaseModel):
    """
    更新嗅探器信息
    """
    order_id: str
    status: Literal['waiting', 'triggered', 'canceled', 'error']
    exchange_timestamp: float
    local_timestamp: float

    @field_validator('exchange_timestamp', 'local_timestamp')
    @classmethod
    def validate_timestamp_precision(cls, v):
        if v is not None:
            # 确保时间戳保留三位小数
            return round(float(v), 6)
        return v


class PrecisionDict(BaseModel):
    """
    精度字典
    """
    price: int
    amount: int


class OrderInfo(BaseModel):
    """
    订单信息
    """
    order_id: str
    batch_id: str
    symbol: str
    exchange: str
    order_type: Literal['market', 'limit', 'condition_limit', 'condition_market']
    action: Literal['open', 'close']
    position: Literal['long', 'short']
    direction: Literal[-1, 0, 1] = 0
    amount: float
    feature: Optional[Literal['fok', 'fak', 'gtx', 'queue']] = None
    expire: Optional[float] = None
    delay: Optional[float] = None
    condition: Optional[Dict[str, Any]] = None
    price: Optional[float] = None
    status: Literal['pending', 'waiting', 'triggered', 'partial_filled', 'canceling', 'canceled', 'error', 'filled'] = 'pending'
    current_timestamp: float
    send_timestamp: Optional[float] = None
    receive_timestamp: Optional[float] = None
    exchange_timestamp: Optional[float] = None
    local_timestamp: Optional[float] = None
    trigger_timestamp: Optional[float] = None
    trigger_local_timestamp: Optional[float] = None
    execute_price: float = 0
    execute_amount: float = 0
    fee_rate: Optional[float] = None
    msg: Optional[Dict[str, Any]] = None

    @field_validator('current_timestamp', 'send_timestamp', 'receive_timestamp', 'exchange_timestamp', 'local_timestamp', 'trigger_timestamp', 'trigger_local_timestamp')
    @classmethod
    def validate_timestamp_precision(cls, v):
        if v is not None:
            # 确保时间戳保留三位小数
            return round(float(v), 6)
        return v

    @model_validator(mode='after')
    def validate_direction(cls, data):
        # 根据position和action自动设置direction
        if data.position == 'long' and data.action == 'open':
            data.direction = 1
        elif data.position == 'long' and data.action == 'close':
            data.direction = -1
        elif data.position == 'short' and data.action == 'open':
            data.direction = -1
        elif data.position == 'short' and data.action == 'close':
            data.direction = 1
        return data
    
    @model_validator(mode='after')
    def validate_price_required(cls, data):
        # 当order_type为limit或condition_limit时，price不可为空
        if data.order_type in ['limit', 'condition_limit'] and data.price is None and data.feature != 'queue':
            raise ValueError(f"当order_type为'{data.order_type}'时，price字段不能为空")
        return data
    
    def update(self, _update_info: UpdateOrderInfo):
        self.status = _update_info.status
        self.exchange_timestamp = round(_update_info.exchange_timestamp, 6)
        self.local_timestamp = round(_update_info.local_timestamp, 6)
        self.execute_price = _update_info.execute_price
        self.execute_amount = _update_info.execute_amount
        self.fee_rate = _update_info.fee_rate
        self.msg = _update_info.msg

        if _update_info.status == 'triggered':
            self.trigger_timestamp = round(_update_info.exchange_timestamp, 6)
            self.trigger_local_timestamp = round(_update_info.local_timestamp, 6)
    
    # 添加属性设置器，确保单独赋值时也保持三位小数精度
    def __setattr__(self, name, value):
        if name in ['current_timestamp', 'send_timestamp', 'receive_timestamp', 'exchange_timestamp', 'local_timestamp'] and value is not None:
            value = round(float(value), 6)
        super().__setattr__(name, value)


class TargetSnifferInfo(BaseModel):
    """
    目标嗅探器信息
    """
    order_id: str
    batch_id: str
    symbol: str
    exchange: str
    operator: str
    target_price: float
    expire: Optional[float] = None
    delay: Optional[float] = None
    status: Literal['pending', 'waiting', 'triggered', 'canceled', 'error'] = 'pending' 
    current_timestamp: float
    exchange_timestamp: Optional[float] = None
    local_timestamp: Optional[float] = None

    @field_validator('current_timestamp', 'exchange_timestamp', 'local_timestamp')
    @classmethod
    def validate_timestamp_precision(cls, v):
        if v is not None:
            # 确保时间戳保留三位小数
            return round(float(v), 6)
        return v

    def update(self, _update_info: UpdateSnifferInfo):
        self.status = _update_info.status
        self.exchange_timestamp = round(_update_info.exchange_timestamp, 6)
        self.local_timestamp = round(_update_info.local_timestamp, 6)
    
    # 添加属性设置器，确保单独赋值时也保持三位小数精度
    def __setattr__(self, name, value):
        if name in ['current_timestamp', 'exchange_timestamp', 'local_timestamp'] and value is not None:
            value = round(float(value), 6)
        super().__setattr__(name, value)


class TrailingSnifferInfo(BaseModel):
    """
    追踪嗅探器信息
    """
    order_id: str
    batch_id: str
    symbol: str
    exchange: str
    operator: str
    target_price: float
    back_pct: float
    expire: Optional[float] = None
    delay: Optional[float] = None
    status: Literal['pending', 'waiting', 'triggered', 'canceled', 'error'] = 'pending'
    current_timestamp: float
    exchange_timestamp: Optional[float] = None
    local_timestamp: Optional[float] = None
    other_info: Dict[str, Any] = {}

    @field_validator('current_timestamp', 'exchange_timestamp', 'local_timestamp')
    @classmethod
    def validate_timestamp_precision(cls, v):
        if v is not None:
            # 确保时间戳保留三位小数
            return round(float(v), 6)
        return v

    def update(self, _update_info: UpdateSnifferInfo):
        self.status = _update_info.status
        self.exchange_timestamp = round(_update_info.exchange_timestamp, 6)
        self.local_timestamp = round(_update_info.local_timestamp, 6)
    
    # 添加属性设置器，确保单独赋值时也保持三位小数精度
    def __setattr__(self, name, value):
        if name in ['current_timestamp', 'exchange_timestamp', 'local_timestamp'] and value is not None:
            value = round(float(value), 6)
        super().__setattr__(name, value)
