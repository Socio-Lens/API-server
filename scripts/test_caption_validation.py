"""
Test script to demonstrate caption validation for sentiment analysis.
"""
from utils.validations import validate_caption_for_sentiment


def test_validation(caption, description):
    is_valid, error = validate_caption_for_sentiment(caption)
    status = "✓ PASS" if is_valid else "✗ FAIL"
    print(f"{status} - {description}")
    if not is_valid:
        print(f"  Error: {error}")
    print()


def main():
    print("=" * 60)
    print("CAPTION VALIDATION TESTS FOR SENTIMENT ANALYSIS")
    print("=" * 60)
    print()
    
    # Valid captions
    print("VALID CAPTIONS:")
    print("-" * 60)
    test_validation("This is a great product!", "Normal caption")
    test_validation("I love this! 😊", "Caption with emoji")
    test_validation("a" * 500, "Maximum length (500 chars)")
    test_validation("Amazing product with great features and excellent customer service!", "Realistic review")
    
    # Invalid captions
    print("\nINVALID CAPTIONS:")
    print("-" * 60)
    test_validation(None, "None value")
    test_validation("", "Empty string")
    test_validation("   ", "Whitespace only")
    test_validation("a" * 501, "Exceeds max length (501 chars)")
    test_validation("hellooooooooooooooooooooo", "Excessive repetition")
    test_validation("!!!!!!@@@@@######$$$$$%%%%", "Too many special characters")
    test_validation("😊" * 60, "Too many emojis")
    test_validation("word " * 201, "Too many words (>200)")
    test_validation("test\x00caption", "Contains null byte")
    test_validation("test\x01\x02caption", "Contains control characters")
    
    # Edge cases
    print("\nEDGE CASES:")
    print("-" * 60)
    test_validation("!", "Single character")
    test_validation("Buy now! Limited offer!!! #sale @shop", "Marketing caption")
    test_validation("Check this: https://example.com", "Caption with URL")
    test_validation("@user1 @user2 @user3 #tag1 #tag2", "Social media tags")
    test_validation("Regular text with some 😊😂🔥 emojis", "Moderate emoji use")


if __name__ == "__main__":
    main()
