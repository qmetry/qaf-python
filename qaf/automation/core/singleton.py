class Singleton(type):
    """
        allow only a single instance to be made of a class that inherits from this metaclass

        attributes:
            _instances (dict): a dictionary of class types and the instances associated with them

        return:
            instance: returns a new instance (or old instance) of the class being called
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
