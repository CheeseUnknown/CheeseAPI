import inspect
from typing import Callable, Dict, Any

def doFunc(func: Callable, args = (), kwargs: Dict[str, Any] = {}):
    if hasattr(func, '__wrapped__'):
        _kwargs = kwargs
    else:
        _kwargs = {}
        sig = inspect.signature(func)
        for key, value in kwargs.items():
            if key in sig.parameters or 'kwargs' in sig.parameters:
                _kwargs[key] = value
    return func(*args, **_kwargs)

async def async_doFunc(func: Callable, args = (), kwargs: Dict[str, Any] = {}):
    if hasattr(func, '__wrapped__'):
        _kwargs = kwargs
    else:
        _kwargs = {}
        sig = inspect.signature(func)
        for key, value in kwargs.items():
            if key in sig.parameters or 'kwargs' in sig.parameters:
                _kwargs[key] = value
    return await func(*args, **_kwargs)
