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
