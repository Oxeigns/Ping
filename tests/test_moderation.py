from handlers import moderation


class Dummy:
    def __init__(self):
        self.count = 0

    def on_message(self, *a, **k):
        def dec(fn):
            self.count += 1
            return fn

        return dec

    def add_handler(self, *a, **k):
        self.count += 1


def test_register_registers_handlers():
    app = Dummy()
    moderation.register(app)
    assert app.count > 0
