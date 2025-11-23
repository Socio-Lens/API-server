from utils.text_cleaning import clean_text, clean_texts


EXAMPLES = [
    "<p>Hello World!                 Visit https://example.com 👋 #Welcome @user</p>",
    "Check this out: www.example.org/test?x=1 #Fun",
    "Multiple   spaces\nand newlines\tand\t tabs!",
    "Emojis 😊😂🔥 \n\n\n\n\n\n\n\nand punctuation!!!",
]


def main():
    print("Default cleaning:")
    for e in EXAMPLES:
        print("-", clean_text(e, normalize_whitespace=True, normalize_newlines=True))

    print("\nNormalize multiple newlines to single newline (preserve other whitespace):")
    for e in EXAMPLES:
        print("- Original:\n" + e)
        print("  Normalized:\n" + clean_text(e, normalize_newlines=True, normalize_whitespace=False))



if __name__ == "__main__":
    main()
