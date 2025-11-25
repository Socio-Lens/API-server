import re


def validate_caption(caption: str, max_length: int = 500, min_length: int = 1) -> tuple[bool, str]:
    """
    Validate caption text for sentiment analysis.
    
    Args:
        caption: The caption text to validate
        max_length: Maximum allowed length (default: 500)
        min_length: Minimum required length (default: 1)
    
    Returns:
        tuple: (is_valid, error_message)
    """
    
    # 1. Check if caption is None or not a string
    if caption is None:
        return False, "Caption cannot be None"
    
    if not isinstance(caption, str):
        return False, "Caption must be a string"
    
    # 2. Check empty/whitespace-only caption
    if not caption.strip():
        return False, "Caption cannot be empty or contain only whitespace"
    
    # 3. Length validation
    caption_length = len(caption)
    if caption_length < min_length:
        return False, f"Caption must be at least {min_length} character(s)"
    
    if caption_length > max_length:
        return False, f"Caption exceeds maximum length of {max_length} characters"
    
    # 4. Check for excessive special characters (spam detection)
    special_char_count = len(re.findall(r'[^a-zA-Z0-9\s]', caption))
    if special_char_count / caption_length > 0.5:  # More than 50% special chars
        return False, "Caption contains too many special characters"
    
    # 5. Check for excessive repetition (spam detection)
    # Detect repeated characters (e.g., "hellooooooo")
    if re.search(r'(.)\1{10,}', caption):
        return False, "Caption contains excessive character repetition"
    
    # 6. Check for excessive emoji/unicode (optional, can affect sentiment models)
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251]+",
        flags=re.UNICODE
    )
    emoji_count = len(emoji_pattern.findall(caption))
    if emoji_count > 50:  # Adjust threshold as needed
        return False, "Caption contains too many emojis"
    
    # 7. Check for null bytes or control characters
    if '\x00' in caption:
        return False, "Caption contains null bytes"
    
    control_chars = [c for c in caption if ord(c) < 32 and c not in '\n\r\t']
    if len(control_chars) > 0:
        return False, "Caption contains invalid control characters"
    
    # 8. Check word count (ensure meaningful content)
    words = caption.split()
    if len(words) > 200:  # Adjust based on model's token limit
        return False, "Caption contains too many words (max 200)"
    
    # 9. Check for scripts that might cause encoding issues
    # This is optional - depends on your model's training data
    
    # All validations passed
    return True, ""


def validate_caption_for_sentiment(caption: str) -> tuple[bool, str]:
    """
    Convenience wrapper for caption validation with sentiment analysis defaults.
    """
    return validate_caption(caption, max_length=500, min_length=1)


def validate_post_url(url: str, platform: str = "instagram") -> tuple[bool, str]:
    """
    Validate a social media post URL.
    
    Args:
        url: The URL to validate
        platform: The platform to validate against ("instagram", "twitter", etc.)
    
    Returns:
        tuple: (is_valid, error_message)
    """
    from urllib.parse import urlparse
    
    # 1. Check if URL is None or empty
    if not url:
        return False, "URL cannot be empty"
    
    if not isinstance(url, str):
        return False, "URL must be a string"
    
    url = url.strip()
    
    # 2. Basic URL format validation
    if not url.startswith(("http://", "https://")):
        return False, "URL must start with http:// or https://"
    
    # 3. Parse the URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"Invalid URL format: {str(e)}"
    
    # 4. Validate domain based on platform
    if platform.lower() == "instagram":
        valid_domains = ["www.instagram.com", "instagram.com"]
        if parsed.netloc.lower() not in valid_domains:
            return False, f"URL must be from Instagram (got: {parsed.netloc})"
        
        # 5. Validate Instagram post path and extract shortcode
        path = parsed.path.strip("/")
        
        # Check if path is empty (just domain)
        if not path:
            return False, "Instagram URL must contain a post path (e.g., /p/shortcode/ or /reel/shortcode/)"
        
        # Instagram post patterns: /p/shortcode/, /reel/shortcode/, /tv/shortcode/
        path_parts = path.split("/")
        
        if len(path_parts) < 2:
            return False, "Invalid Instagram post URL format"
        
        post_type = path_parts[0]
        valid_post_types = ["p", "reel", "tv"]
        
        if post_type not in valid_post_types:
            return False, f"Instagram URL must be a post (/p/), reel (/reel/), or IGTV (/tv/). Got: /{post_type}/"
        
        shortcode = path_parts[1] if len(path_parts) > 1 else ""
        
        # Validate shortcode is not empty and has reasonable length
        if not shortcode:
            return False, "Instagram post URL must contain a valid shortcode"
        
        # Instagram shortcodes are typically 11 characters (alphanumeric, underscore, dash)
        if len(shortcode) < 5 or len(shortcode) > 20:
            return False, f"Invalid Instagram shortcode length: {len(shortcode)} characters"
        
        if not re.match(r'^[A-Za-z0-9_-]+$', shortcode):
            return False, "Instagram shortcode contains invalid characters"
    
    elif platform.lower() == "twitter":
        valid_domains = ["www.twitter.com", "twitter.com", "x.com", "www.x.com"]
        if parsed.netloc.lower() not in valid_domains:
            return False, f"URL must be from Twitter/X (got: {parsed.netloc})"
        
        # Twitter post validation can be added here
        path = parsed.path.strip("/")
        if not path:
            return False, "Twitter URL must contain a post path"
    
    else:
        return False, f"Unsupported platform: {platform}"
    
    # All validations passed
    return True, ""
    