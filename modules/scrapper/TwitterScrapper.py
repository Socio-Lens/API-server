import logging
from .BaseScrapper import BaseScrapper
from twikit import Client

logger = logging.getLogger(__name__)

class TwitterScrapper(BaseScrapper):
    
    def __init__(self):
        super().__init__()
        self.client = Client('en-US')
        
    
    
    async def login(self, username=str, email=None, password=str):
        try:
            await self.client.login(
                auth_info_1=username,
                auth_info_2=email,
                password=password,
                cookies_file='cookies.json'
            )
        except Exception as e:
            logger.error("Twitter client login failed: ", e)
            return False
        
        return True
    
    def get_caption_from_post_url(self, post_url):
        pass
    
    def get_post_from_url(self, post_url):
        pass
    
    def get_comments_from_post_url(self, post_url):
        pass
 
 
async def main():
    scrapper = TwitterScrapper()
    await scrapper.login("ultimatescrape", None, "zananth2003@")       
            
if __name__ == "__main__":
    import asyncio
    
    asyncio.run(main())