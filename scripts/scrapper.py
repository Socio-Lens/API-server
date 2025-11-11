import instaloader
import argparse
from urllib.parse import urlparse

def get_shortcode_from_url(url: str) -> str:
    path = urlparse(url).path
    parts = [p for p in path.split("/") if p]
    # typical: /p/<shortcode>/
    if len(parts) >= 2 and parts[0] in ("p", "reel", "tv"):
        return parts[1]
    return parts[-1] if parts else ""

def caption_from_post_url(post_url: str, username=None, password=None):
    L = instaloader.Instaloader()
    if username and password:
        L.login(username, password)  # optional, increases rate limits and access
    shortcode = get_shortcode_from_url(post_url)
    if not shortcode:
        raise ValueError("Could not parse shortcode from URL")
    post = instaloader.Post.from_shortcode(L.context, shortcode)
    return post.caption


def main():
    parser = argparse.ArgumentParser(description='Scrape Instagram posts')
    parser.add_argument('url', help='Instagram post URL')

    
    args = parser.parse_args()
    

    print(caption_from_post_url(args.url))


if __name__ == '__main__':
    main()