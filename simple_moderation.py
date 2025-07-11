from pathlib import Path

BANNED_WORDS_FILE = Path(__file__).with_name("banned_words.txt")

def load_banned_words():
    try:
        with open(BANNED_WORDS_FILE, "r", encoding="utf-8") as f:
            return {line.strip().lower() for line in f if line.strip()}
    except FileNotFoundError:
        print(f"Banned words file not found: {BANNED_WORDS_FILE}")
        return set()

def contains_banned_word(text: str, banned_words: set[str]) -> bool:
    lower = text.lower()
    return any(word in lower for word in banned_words)

def main():
    banned_words = load_banned_words()
    if not banned_words:
        print("No banned words loaded.")
    while True:
        try:
            message = input("Enter a message (Ctrl-D to quit): ")
        except EOFError:
            print()
            break
        banned_words = load_banned_words()  # Reload in case file changed
        if contains_banned_word(message, banned_words):
            print("⚠️  Warning: message contains a banned word!")
        else:
            print("Message is clean.")

if __name__ == "__main__":
    main()
