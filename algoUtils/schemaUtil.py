"""
@Create: 2024/9/30 14:06
@File: defUtil.py
@Author: Jijingyuan
"""
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel


class Signal(BaseModel):
    batch_id: str  # str(uuid)
    symbol: str  # 'btc_usdt|binance_future'
    action: str  # 'open' or 'close'
    position: str  # 'long' or 'short'
    timestamp: Optional[float] = None  # timestamp default is None
    price_dict: Optional[Dict[str, float]] = None  # {'btc_usdt|binance_future': price, ...} default is None

class Sample(BaseModel):
    signal: Signal
    features: Optional[Dict[str, float]] = {}
    targets: Optional[Dict[str, float]] = {}
    forecast: bool = False
    actual: bool = False

class SignalMgrParam(BaseModel):
    signal_method_name: str
    signal_method_param: Dict[str, Any] = {}

class FeatureMgrParam(BaseModel):
    feature_method_name: str
    feature_method_param: Dict[str, Any] = {}

class TargetMgrParam(BaseModel):
    target_method_name: str
    target_method_param: Dict[str, Any] = {}

class InterceptMgrParam(BaseModel):
    intercept_method_name: str
    intercept_method_param: Dict[str, Any] = {}

class SignalTaskParam(BaseModel):
    signal_task_name: str
    signal_mgr_param: SignalMgrParam
    feature_mgr_params: Optional[Union[List[FeatureMgrParam], FeatureMgrParam]] = None
    target_mgr_param: Optional[TargetMgrParam] = None
    intercept_mgr_param: Optional[InterceptMgrParam] = None
    lag: float
    symbols: Union[List[str], str]
    data_type: str
    start_timestamp: float
    end_timestamp: float
