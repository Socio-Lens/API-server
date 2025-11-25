import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqClient:
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        
    def optimizeCaption(self, sentiment, caption):
        
        completion = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
            {
                "role": "user",
                "content": f"The caption from a social media post is given below. Modify and improve the caption to attract more users and interactions and it reflects a {sentiment} sentiment. include relevant tags and emojis if necessary\n The caption: '{caption}' \n\nNOTE: RETURN THE CAPTION ONLY"
            }
            ],
            temperature=1,
            max_completion_tokens=8192,
            top_p=1,
            reasoning_effort="medium",
            stream=False,
            stop=None
        )

        return completion.choices[0].message.content
        
        
if __name__ == "__main__":
    client = GroqClient()
    print(client.optimizeCaption("negative", "messi retires from football"))