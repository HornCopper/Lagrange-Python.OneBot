import inspect

from typing import Union, get_origin, get_args
from config import logger

def get_params(func, data_dict):
    sig = inspect.signature(func)
    converted_data = {}
    for param_name, param in sig.parameters.items():
        if param_name in data_dict:
            value = data_dict[param_name]
            param_type = param.annotation
            if param_type != inspect.Parameter.empty:
                try:
                    origin_type = get_origin(param_type)
                    if origin_type is Union:
                        possible_types = get_args(param_type)
                        possible_types = sorted(possible_types, key=lambda t: t is list)
                        for possible_type in possible_types:
                            try:
                                converted_data[param_name] = possible_type(value)
                                break
                            except (ValueError, TypeError):
                                continue
                        else:
                            logger.onebot.error(
                                f"Cannot convert '{param_name}' value '{value}' to any type in {possible_types}."
                            )
                    else:
                        converted_data[param_name] = param_type(value)
                except (ValueError, TypeError) as e:
                    logger.onebot.error(f"Cannot convert '{param_name}' value '{value}' to type {param_type}: {e}")
            else:
                converted_data[param_name] = value
    return converted_data
