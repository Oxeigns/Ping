from handlers import panels


def test_command_list_contains_commands():
    text = panels.command_list()
    for cmd in panels.COMMANDS:
        assert cmd in text
