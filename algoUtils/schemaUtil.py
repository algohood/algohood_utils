"""
@Create: 2024/9/30 14:06
@File: defUtil.py
@Author: Jijingyuan
"""
from typing import Optional, List, Dict, Any, Union, Literal
from pydantic import BaseModel, field_validator, model_validator


class Signal(BaseModel):
    batch_id: str  # str(uuid)
    symbol: str  # 'btc_usdt|binance_future'
    direction: str  # 'long' or 'short'
    timestamp: Optional[float] = None  # timestamp default is None
    price_dict: Optional[Dict[str, float]] = None  # {'btc_usdt|binance_future': price, ...} default is None


class EntryInfo(BaseModel):
    entry_success: bool
    entry_direction: Optional[str] = None # 'long' or 'short'
    entry_price: Optional[float] = None
    entry_timestamp: Optional[float] = None
    entry_duration: Optional[float] = None


class ExitInfo(BaseModel):
    exit_price: float
    exit_timestamp: float
    exit_duration: float


class TradingResult(BaseModel):
    success: bool
    is_win: Optional[int] = None  # 1: win, 0: lose
    trade_ret: Optional[float] = None
    trade_duration: Optional[float] = None


class Sample(BaseModel):
    signal: Signal
    features: Optional[Dict[str, float]] = {}
    targets: Optional[Dict[str, float]] = {}
    target_fields: Optional[List[str]] = None
    intercept: Optional[bool] = None
    sim_targets: Optional[Dict[str, float]] = {}
    sim_intercept: Optional[bool] = None


class SignalMgrParam(BaseModel):
    signal_method_name: str
    signal_method_param: Dict[str, Any] = {}
    cool_down_grid: Optional[float] = 0.001
    cool_down_ts: Optional[float] = 1


class FeatureMgrParam(BaseModel):
    feature_method_name: str
    feature_method_param: Dict[str, Any] = {}


class TargetMgrParam(BaseModel):
    target_type: Literal['trading', 'status'] = 'status'
    target_method_name: str
    target_method_param: Dict[str, Any] = {}
    entry_fee: float = 0.0001
    exit_fee: float = 0.0001
    target_fields: Optional[List[str]] = None

class ModelMgrParam(BaseModel):
    model_method_name: str
    model_method_param: Dict[str, Any] = {}
    model_cache_size: int = 100
    model_retain_size: int = 0


class SignalTaskParam(BaseModel):
    signal_task_name: str
    signal_mgr_param: SignalMgrParam
    feature_mgr_params: Optional[Union[List[FeatureMgrParam], FeatureMgrParam]] = None
    target_mgr_param: Optional[TargetMgrParam] = None
    model_mgr_param: Optional[ModelMgrParam] = None
    lag: float
    symbols: Union[List[str], str]
    data_type: str
    start_timestamp: float
    end_timestamp: float
