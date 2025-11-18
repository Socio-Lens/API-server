import instaloader
import argparse
from base64 import b64encode, b64decode
from urllib.parse import urlparse
from .BaseScrapper import BaseScrapper

class InstaScrapper(BaseScrapper):
    
    def __init__(self, username=None, password=None):
        super().__init__()
        
        self.instaloader = instaloader.Instaloader(
            download_geotags=True,
            download_comments=True,
            save_metadata=True
        )
        
        if username and password:
            print("found username, logging in using-", username, password)
            self.login(username, password)
        
    def login(self, username, password):
        self.instaloader.login(username, password)
            
    def get_post_from_url(self, post_url: str) -> instaloader.Post:
        shortcode = self.get_shortcode_from_url(post_url)
        if not shortcode:
            raise ValueError("Could not parse shortcode from URL")
        post = instaloader.Post.from_shortcode(self.instaloader.context, shortcode)
        return post
            
    def get_shortcode_from_url(self, url: str) -> str:
        path = urlparse(url).path
        parts = [p for p in path.split("/") if p]
        # typical: /p/<shortcode>/
        if len(parts) >= 2 and parts[0] in ("p", "reel", "tv"):
            return parts[1]
        return parts[-1] if parts else ""
    
    def get_caption_from_post_url(self, post_url: str, username=None, password=None):

        shortcode = self.get_shortcode_from_url(post_url)
        if not shortcode:
            raise ValueError("Could not parse shortcode from URL")
        post = instaloader.Post.from_shortcode(self.instaloader.context, shortcode)
        return post.caption

    def comments_from_post_url(self, post_url: str):
        
        shortcode = self.get_shortcode_from_url(post_url)
        if not shortcode:
            raise ValueError("Could not parse shortcode from URL")
        post = instaloader.Post.from_shortcode(self.instaloader.context, shortcode)
        comments = post.get_comments()
        return comments
    
    def shortcode_to_mediaid(self, code: str) -> int:
        if len(code) > 11:
            raise Exception("Wrong shortcode \"{0}\", unable to convert to mediaid.".format(code))
        code = 'A' * (12 - len(code)) + code
        return int.from_bytes(b64decode(code.encode(), b'-_'), 'big')


    def mediaid_to_shortcode(self, mediaid: int) -> str:
        if mediaid.bit_length() > 64:
            raise Exception("Wrong mediaid {0}, unable to convert to shortcode".format(str(mediaid)))
        return b64encode(mediaid.to_bytes(9, 'big'), b'-_').decode().replace('A', ' ').lstrip().replace(' ', 'A')

    def get_comments_from_post_url(self, post_url):
        pass

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

def comments_From_post_url(post_url: str):
    pass



if __name__ == '__main__':
    import os
    import pickle as pkl
    parser = argparse.ArgumentParser(description='Scrape Instagram posts')
    parser.add_argument('url', help='Instagram post URL')
    parser.add_argument('--u', '--username', type=str, default=None)
    parser.add_argument('--p', '--password', type=str, default=None)
    

    
    args = parser.parse_args()
    
    os.makedirs('secret', exist_ok=True)
    
    # cookie_keys = ['csrftoken', 'sessionid', 'ds_user_id', 'mid', 'ig_did']
    cookies = {
        "csrftoken": "T4mWnDkTI20BoX6X1DLHcwXsx3ChEmPb",
        "sessionid": "78538186745%3AUbCPVopYpRogm5%3A14%3AAYg8BmztM7qfGICNgql3FMRY2au2ieRPKntABEEwog",
        "ds_user_id": "78538186745",
        "mid": "aJcSBQALAAGM-DOswoYk8aUf8e4G",
        "ig_did": "AFCB52EC-EAD1-4A27-9593-05675F6B0987"
    }
    
    scrapper = InstaScrapper()
    
    # with open(os.path.join('secret', args.u), 'wb') as f:
    #     pkl.dump(scrapper.instaloader.save_session(), f)
        
    # with open(os.path.join('secret', args.u), 'rb') as f:
    #     cookies = pkl.load(f)
    #     print(cookies)
        
    scrapper.instaloader.load_session(args.u, cookies)
    print(scrapper.shortcode_to_mediaid('DQ8f5txEls1'))
    # scrapper.instaloader.load_session_from_file(os.path.join(os.getcwd(), args.u))
    # scrapper.instaloader.save_session_to_file(args.u)
    # print(scrapper.get_post_from_url(args.url).comments)

    comments = scrapper.comments_from_post_url(args.url)
    
    with open("test.txt", 'w', encoding='utf-8') as f:
        for comment in comments:
            f.write(comment.text + "\n")
    