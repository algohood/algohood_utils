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
            
        if isinstance(data.price, list):
            data.price = [float(p) for p in data.price]
        else:
            data.price = float(data.price)
        
        return data


class Features(BaseModel):
    feature_fields: List[str]
    features: List[Optional[float]]

    @model_validator(mode='after')
    def validate_features(cls, data):
        if len(data.feature_fields) != len(data.features):
            raise ValueError("feature_fields和features的长度必须相等")
        
        return data

    def as_dict(self):
        return {field: value for field, value in zip(self.feature_fields, self.features)}
    
    @classmethod
    def from_dict(cls, _features_dict: Dict[str, Optional[float]]):
        return cls(
            feature_fields=list(_features_dict.keys()),
            features=list(_features_dict.values())
        )
    
    def filter(self, _fields: List[str]):
        return Features(
            feature_fields=[field for field in self.feature_fields if field in _fields],
            features=[value for field, value in zip(self.feature_fields, self.features) if field in _fields]
        )
    
    def update(self, other_features: 'Features'):
        """
        合并两个Features对象
        
        Args:
            other_features: 要合并的另一个Features对象
            
        Returns:
            None，直接修改当前对象
        """
        if not isinstance(other_features, Features):
            raise ValueError("参数必须是Features类型")
        
        # 创建字段到索引的映射，用于快速查找
        current_field_map = {field: idx for idx, field in enumerate(self.feature_fields)}
        
        # 遍历要合并的features
        for field, value in zip(other_features.feature_fields, other_features.features):
            if field in current_field_map:
                # 如果字段已存在，更新值
                self.features[current_field_map[field]] = value
            else:
                # 如果字段不存在，添加新字段和值
                self.feature_fields.append(field)
                self.features.append(value)


class Target(BaseModel):
    target_name: str
    target: float
    timestamp: float = 0


class TradingResult(BaseModel):
    success: bool
    direction: Optional[int] = None
    entry_timestamp: Optional[float] = None
    exit_timestamp: Optional[float] = None
    is_win: Optional[int] = None  # 1: win, 0: lose
    trade_ret: Optional[float] = None
    open_duration: Optional[float] = None
    close_duration: Optional[float] = None


class Sample(BaseModel):
    signal: Signal
    features: Optional[Features] = None
    target: Optional[Target] = None
    forcast: Optional[Target] = None
    actual_pass: Optional[bool] = None
    forcast_pass: Optional[bool] = None


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


class SelectorMgrParam(BaseModel):
    selector_method_name: str
    selector_method_param: Dict[str, Any] = {}


class ModelMgrParam(BaseModel):
    model_method_name: str
    model_method_param: Dict[str, Any] = {}


class PerformanceMgrParam(BaseModel):
    performance_method_name: str
    performance_method_param: Dict[str, Any] = {}


class ExecuteMgrParam(BaseModel):
    execute_method_name: str
    execute_method_param: Dict[str, Any] = {}


class OptimizeMgrParam(BaseModel):
    optimize_method_name: str
    optimize_method_param: Dict[str, Any] = {}


class RiskMgrParam(BaseModel):
    risk_method_name: str
    risk_method_param: Dict[str, Any] = {}


class LiquidityMgrParam(BaseModel):
    liquidity_method_name: str
    liquidity_method_param: Dict[str, Any] = {}


class SignalTaskParam(BaseModel):
    signal_name: str
    signal_mgr_param: SignalMgrParam
    feature_mgr_params: Optional[Union[List[FeatureMgrParam], FeatureMgrParam]] = None
    target_mgr_param: Optional[TargetMgrParam] = None
    lag: Optional[float] = None
    symbols: Union[List[str], str]
    data_type: str


class PerformanceTaskParam(BaseModel):
    performance_name: str
    performance_mgr_param: PerformanceMgrParam
    signal_task_id: Optional[str] = None
    signal_name: Optional[str] = None


class ExecuteTaskParam(BaseModel):
    execute_name: str
    execute_mgr_param: ExecuteMgrParam
    signal_task_id: Optional[str] = None
    signal_name: Optional[str] = None


class ModelTaskParam(BaseModel):
    model_name: str
    selector_mgr_param: SelectorMgrParam
    model_mgr_param: ModelMgrParam
    target_mgr_param: TargetMgrParam
    signal_task_id: Optional[str] = None
    signal_names: Optional[Union[List[str], str]] = None


class PortfolioTaskParam(BaseModel):
    portfolio_name: str
    optimize_mgr_param: OptimizeMgrParam
    risk_mgr_param: RiskMgrParam
    liquidity_mgr_param: LiquidityMgrParam
    open_rebalance: bool = False
    close_rebalance: bool = False
    interval: Optional[int] = None
    data_type: str = 'trade'
    execute_task_id: Optional[str] = None
    execute_names: Optional[Union[List[str], str]] = None


class OnlineTaskParam(BaseModel):
    signal_tasks: List[SignalTaskParam]
    model_tasks: Optional[ModelTaskParam] = None
    execute_tasks: List[ExecuteTaskParam]
    portfolio_task: PortfolioTaskParam
    backward_duration: float
    max_cash: float
    max_loss: float
    is_online: bool = False
    mode: Literal['replace', 'update'] = 'update'


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
        self.execute_price = float(_update_info.execute_price)
        self.execute_amount = float(_update_info.execute_amount)
        self.fee_rate = _update_info.fee_rate
        self.msg = _update_info.msg

        if _update_info.status == 'triggered':
            self.trigger_timestamp = round(_update_info.exchange_timestamp, 6)
            self.trigger_local_timestamp = round(_update_info.local_timestamp, 6)
    
    # 添加属性设置器，确保单独赋值时也保持三位小数精度
    def __setattr__(self, name, value):
        if name in ['current_timestamp', 'send_timestamp', 'receive_timestamp', 'exchange_timestamp', 'local_timestamp'] and value is not None:
            value = round(float(value), 6)
        elif name == 'price' and value is not None:
            value = float(value)
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
    drop: bool = True

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
    drop: bool = True

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


class EarningInfo(BaseModel):
    """
    盈利信息
    """
    batch_id: str
    start_timestamp: float
    open_timestamp: float
    close_timestamp: float
    batch_ret: float
    batch_ret_after_fee: float
    opt_pass: bool
    rsk_pass: bool
    