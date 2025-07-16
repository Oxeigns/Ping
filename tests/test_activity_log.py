import importlib

logmod = importlib.import_module("handlers.activity_log")


class Dummy:
    def __init__(self):
        self.count = 0

    def on_message(self, *a, **k):
        def dec(fn):
            self.count += 1
            return fn

        return dec


def test_register_adds_handler():
    app = Dummy()
    logmod.register(app)
    assert app.count > 0
