"""
Test script to demonstrate Instagram post URL validation.
"""
from utils.validations import validate_post_url


def test_url(url, description):
    is_valid, error = validate_post_url(url, platform="instagram")
    status = "✓ PASS" if is_valid else "✗ FAIL"
    print(f"{status} - {description}")
    print(f"  URL: {url}")
    if not is_valid:
        print(f"  Error: {error}")
    print()


def main():
    print("=" * 80)
    print("INSTAGRAM POST URL VALIDATION TESTS")
    print("=" * 80)
    print()
    
    # Valid URLs
    print("VALID URLS:")
    print("-" * 80)
    test_url(
        "https://www.instagram.com/p/ABC123XYZ/",
        "Standard post URL"
    )
    test_url(
        "https://instagram.com/p/ABC123XYZ/",
        "Post URL without www"
    )
    test_url(
        "https://www.instagram.com/reel/XYZ789ABC/",
        "Reel URL"
    )
    test_url(
        "https://www.instagram.com/tv/DEF456GHI/",
        "IGTV URL"
    )
    test_url(
        "https://www.instagram.com/p/ABC_123-XYZ/",
        "Post with underscore and dash in shortcode"
    )
    test_url(
        "https://www.instagram.com/p/ABC123XYZ/?utm_source=ig_web",
        "Post with query parameters"
    )
    
    # Invalid URLs
    print("\nINVALID URLS:")
    print("-" * 80)
    test_url(
        "",
        "Empty URL"
    )
    test_url(
        None,
        "None value"
    )
    test_url(
        "www.instagram.com/p/ABC123/",
        "Missing protocol"
    )
    test_url(
        "https://www.facebook.com/p/ABC123/",
        "Wrong domain (Facebook)"
    )
    test_url(
        "https://www.instagram.com/",
        "Just domain, no path"
    )
    test_url(
        "https://www.instagram.com/username/",
        "Profile URL (not a post)"
    )
    test_url(
        "https://www.instagram.com/p/",
        "Post path without shortcode"
    )
    test_url(
        "https://www.instagram.com/p//",
        "Empty shortcode"
    )
    test_url(
        "https://www.instagram.com/p/AB/",
        "Shortcode too short (< 5 chars)"
    )
    test_url(
        "https://www.instagram.com/p/ABCDEFGHIJKLMNOPQRSTUVWXYZ/",
        "Shortcode too long (> 20 chars)"
    )
    test_url(
        "https://www.instagram.com/p/ABC@123#XYZ/",
        "Invalid characters in shortcode"
    )
    test_url(
        "https://www.instagram.com/stories/username/123456/",
        "Story URL (not a post/reel/tv)"
    )
    
    # Edge cases
    print("\nEDGE CASES:")
    print("-" * 80)
    test_url(
        "http://www.instagram.com/p/ABC123XYZ/",
        "HTTP instead of HTTPS"
    )
    test_url(
        "https://www.instagram.com/p/ABC123XYZ/?img_index=1",
        "Carousel post with image index"
    )
    test_url(
        "https://www.instagram.com/reel/ABC123XYZ/?igsh=example",
        "Reel with share parameter"
    )


if __name__ == "__main__":
    main()
