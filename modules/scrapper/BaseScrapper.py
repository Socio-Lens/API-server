from abc import ABC, abstractmethod

class BaseScrapper(ABC):
    
    @abstractmethod
    def login(self) -> None:
        pass   
    
    @abstractmethod
    def get_post_from_url(self, post_url: str):
        pass
    
    @abstractmethod
    def get_comments_from_post_url(self, post_url: str):
        pass
    
    @abstractmethod
    def get_caption_from_post_url(self, post_url: str):
        pass
    
    
__all__ = ['BaseScrapper']