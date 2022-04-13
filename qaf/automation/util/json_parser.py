class JsonParser(dict):
    __getattr__ = dict.__getitem__

    def __init__(self, *args, **kwargs):
        super(JsonParser, self).__init__(*args, **kwargs)
        self.update(**dict((k, self.parse(v))
                           for k, v in dict.items(self)))

    @classmethod
    def parse(cls, v):
        if isinstance(v, dict):
            return cls(v)
        elif isinstance(v, list):
            return [cls.parse(i) for i in v]
        else:
            return v
