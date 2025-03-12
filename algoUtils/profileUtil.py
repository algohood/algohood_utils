import time
from functools import wraps
from .loggerUtil import generate_logger


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
                "call_count": 0,
                "min_time": float('inf'),
                "max_time": 0
            }
            
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            elapsed = end_time - start_time
            
            # Only update function-specific statistics
            func_stat = self.func_stats[func_name]
            func_stat["total_cost"] += elapsed
            func_stat["call_count"] += 1
            func_stat["min_time"] = min(func_stat["min_time"], elapsed)
            func_stat["max_time"] = max(func_stat["max_time"], elapsed)
            
            return result
        return wrapper
    
    def reset(self):
        """Reset all statistics data"""
        # Reset function statistics dictionary
        for func_name in self.func_stats:
            self.func_stats[func_name] = {
                "total_cost": 0,
                "call_count": 0,
                "min_time": float('inf'),
                "max_time": 0
            }
    
    def _get_total_stats(self):
        """Calculate the overall statistics for all functions"""
        total_cost = 0
        call_count = 0
        min_time = float('inf')
        max_time = 0
        
        for func_name, stats in self.func_stats.items():
            total_cost += stats["total_cost"]
            call_count += stats["call_count"]
            if stats["call_count"] > 0:
                min_time = min(min_time, stats["min_time"])
                max_time = max(max_time, stats["max_time"])
        
        # If no functions have been called, set the minimum time to 0
        if call_count == 0:
            min_time = 0
            
        return {
            "total_cost": total_cost,
            "call_count": call_count,
            "min_time": min_time,
            "max_time": max_time
        }
    
    def get_average_time(self, func_name=None):
        """
        Get the average execution time
        Parameters:
            func_name: Function name, if specified returns the average time for that function, otherwise returns the overall average time
        """
        if func_name is not None:
            if func_name in self.func_stats and self.func_stats[func_name]["call_count"] > 0:
                stats = self.func_stats[func_name]
                return stats["total_cost"] / stats["call_count"]
            return 0
        
        # Calculate the overall average time for all functions
        total_stats = self._get_total_stats()
        if total_stats["call_count"] == 0:
            return 0
        return total_stats["total_cost"] / total_stats["call_count"]
    
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
                                f"Call count: {stats['call_count']}, "
                                f"Total time: {stats['total_cost']:.6f} seconds, "
                                f"Average: {avg_time:.6f} seconds, "
                                f"Min: {stats['min_time']:.6f} seconds, "
                                f"Max: {stats['max_time']:.6f} seconds")
            else:
                logger.info(f"Function {func_name} has no statistics data")
        else:
            # Display overall statistics and statistics for each function
            logger.info(self.__str__())
            for func_name in self.func_stats:
                stats = self.func_stats[func_name]
                if stats["call_count"] > 0:
                    avg_time = stats["total_cost"] / stats["call_count"]
                    logger.info(f"  Function {func_name}: "
                                f"Call count: {stats['call_count']}, "
                                f"Total time: {stats['total_cost']:.6f} seconds, "
                                f"Average: {avg_time:.6f} seconds, "
                                f"Min: {stats['min_time']:.6f} seconds, "
                                f"Max: {stats['max_time']:.6f} seconds")

    def get_stats(self, func_name=None):
        """
        Get complete statistics information
        Parameters:
            func_name: Function name, if specified returns statistics for that function, otherwise returns statistics for all functions
        """
        if func_name is not None:
            if func_name in self.func_stats:
                stats = self.func_stats[func_name]
                return {
                    "name": f"{self.name}.{func_name}",
                    "total_time": stats["total_cost"],
                    "call_count": stats["call_count"],
                    "avg_time": stats["total_cost"] / stats["call_count"] if stats["call_count"] > 0 else 0,
                    "min_time": stats["min_time"] if stats["call_count"] > 0 else 0,
                    "max_time": stats["max_time"]
                }
            return {"name": f"{self.name}.{func_name}", "error": "Function has no statistics data"}
        
        # Calculate overall statistics
        total_stats = self._get_total_stats()
        return {
            "name": self.name,
            "total_time": total_stats["total_cost"],
            "call_count": total_stats["call_count"],
            "avg_time": total_stats["total_cost"] / total_stats["call_count"] if total_stats["call_count"] > 0 else 0,
            "min_time": total_stats["min_time"] if total_stats["call_count"] > 0 else 0,
            "max_time": total_stats["max_time"],
            "functions": self.func_stats
        }
    
    def __str__(self):
        total_stats = self._get_total_stats()
        if total_stats["call_count"] == 0:
            return f"ProfileStats({self.name}): No statistics data yet"
        
        avg_time = total_stats["total_cost"] / total_stats["call_count"]
        return (f"ProfileStats({self.name}): "
                f"Total call count: {total_stats['call_count']}, "
                f"Total time: {total_stats['total_cost']:.6f} seconds, "
                f"Average: {avg_time:.6f} seconds, "
                f"Min: {total_stats['min_time']:.6f} seconds, "
                f"Max: {total_stats['max_time']:.6f} seconds")
