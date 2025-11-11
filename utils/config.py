from dataclasses import dataclass

@dataclass
class Config:

   model_dir: str = 'models'
   model_name: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    
    
