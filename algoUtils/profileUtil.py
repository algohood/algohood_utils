import time
from functools import wraps
from .loggerUtil import generate_logger
import asyncio
import inspect


logger = generate_logger()


class ProfileStats:
    def __init__(self, name="default"):
        self.name = name
        # Remove class-level statistics, only keep function statistics dictionary
        self.func_stats = {}
        
    def update_cost_time(self, func):
        """
        Decorator: Calculate the execution time of the decorated function and update statistics
        Each function will have its own statistics data
        """
        func_name = func.__name__
        # Ensure the function exists in the statistics dictionary
        if func_name not in self.func_stats:
            self.func_stats[func_name] = {
                "total_cost": 0,
                "call_count": 0
            }
        
        # 检查函数是否为异步函数
        is_async = inspect.iscoroutinefunction(func)
            
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            
            elapsed = end_time - start_time
            
            # Only update function-specific statistics
            func_stat = self.func_stats[func_name]
            func_stat["total_cost"] += elapsed
            func_stat["call_count"] += 1
            
            return result
            
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            elapsed = end_time - start_time
            
            # Only update function-specific statistics
            func_stat = self.func_stats[func_name]
            func_stat["total_cost"] += elapsed
            func_stat["call_count"] += 1
            
            return result
        
        return async_wrapper if is_async else sync_wrapper
    
    def show_stats(self, func_name=None):
        """
        Display statistics information
        Parameters:
            func_name: Function name, if specified displays statistics for that function, otherwise displays statistics for all functions
        """
        if func_name is not None:
            if func_name in self.func_stats:
                stats = self.func_stats[func_name]
                if stats["call_count"] == 0:
                    logger.info(f"Function {func_name} has no statistics data yet")
                else:
                    avg_time = stats["total_cost"] / stats["call_count"]
                    logger.info(f"Function {func_name} statistics: "
                                f"Call: {stats['call_count']}, "
                                f"Time: {stats['total_cost']:.2f} s")
            else:
                logger.info(f"Function {func_name} has no statistics data")
        else:
            # Display overall statistics and statistics for each function
            for func_name in self.func_stats:
                stats = self.func_stats[func_name]
                if stats["call_count"] > 0:
                    logger.info(f"Function {func_name}: "
                                f"Call: {stats['call_count']}, "
                                f"Time: {stats['total_cost']:.2f} s")
