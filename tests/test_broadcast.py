from handlers import broadcast
from unittest.mock import patch


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
    with patch("handlers.broadcast.get_db") as g:
        g.return_value = type("DB", (), {})()
        broadcast.register(app)
    assert app.count > 0
