class SlackleContext:
    """
    Context for the Slackle app.
    This context will be used to store the state of the app.
    """

    def __init__(self, **kwargs):
        self._context = kwargs
        self._skip = False
        self._skip_reason = ""

    def __getattr__(self, item):
        if item in self._context:
            return self._context[item]
        raise AttributeError(f"{item} not found in context")

    def __setattr__(self, key, value):
        if key in ["_context", "_skip"]:
            super().__setattr__(key, value)
        else:
            self._context[key] = value

    def __delattr__(self, item):
        if item in ["_context", "_skip"]:
            super().__delattr__(item)
        else:
            del self._context[item]

    def __contains__(self, item):
        return item in self._context

    def __iter__(self):
        return iter(self._context)

    def __len__(self):
        return len(self._context)

    def __repr__(self):
        return f"<SlackleContext {self._context}>"

    def __str__(self):
        return self.__repr__()

    def skip(self, reason: str = ""):
        self._skip = True
        self._skip_reason = reason

    @property
    def is_skipped(self) -> bool:
        return self._skip

    @property
    def skip_reason(self) -> str:
        return self._skip_reason

    def get(self, key, default=None):
        return self._context.get(key, default)

    def setdefault(self, key, default=None):
        return self._context.setdefault(key, default)

    def update(self, **kwargs):
        self._context.update(kwargs)
