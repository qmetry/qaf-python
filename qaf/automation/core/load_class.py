import importlib


def load_class(full_class_string: str):
    class_data = full_class_string.split(".")
    module_path = ".".join(class_data[:-1])
    class_str = class_data[-1]

    module_name = importlib.import_module(module_path)
    return getattr(module_name, class_str)


def module_exists(module_name: str) -> bool:
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True