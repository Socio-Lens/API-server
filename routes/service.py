import os
import torch
import logging
from urllib.parse import urlparse
from pydantic import BaseModel
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from modules.scrapper.InstaScrapper import InstaScrapper
from modules.LLM.Groq import GroqClient
from utils.validations import validate_caption_for_sentiment, validate_post_url


logger = logging.getLogger(__name__)
llmclient = GroqClient()
router = APIRouter(prefix="/service", tags=["service"])

class PostInput(BaseModel):
    text: str
    
class CaptionInput(BaseModel):
    url: str
    
class OptimizeInput(BaseModel):
    sentiment: str
    caption: str


def validate_request(request):
    pass

@router.post(
    "/caption/instagram",
    name="caption_instagram", 
    summary="Get the caption from an Instagram URL"
)
async def get_instagram_caption(request: Request, postInput: CaptionInput):
    logger.debug(f"Received Instagram URL: {postInput.url}")
    
    # Validate Instagram post URL
    is_valid, error_msg = validate_post_url(postInput.url, platform="instagram")
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Invalid URL: {error_msg}")
    
    try:
        scrapper = InstaScrapper()
        caption = scrapper.get_caption_from_post_url(postInput.url)
    except Exception as e:   # replace with real exception(s)
        logger.exception("Error fetching caption", e)
        raise HTTPException(status_code=502, detail="Failed to fetch caption")
    return {"caption": caption}

@router.post(
    "/caption/optimize", 
    name="caption_optimize",
    summary="Augment caption with a LLM"
)
async def optimize_caption(request: Request, postInput: OptimizeInput):
    # Validate caption
    is_valid, error_msg = validate_caption_for_sentiment(postInput.caption)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Invalid caption: {error_msg}")
    
    # Validate sentiment value
    valid_sentiments = ["positive", "negative", "neutral"]
    if postInput.sentiment.lower() not in valid_sentiments:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid sentiment. Must be one of: {', '.join(valid_sentiments)}"
        )
    
    return {
        "caption": llmclient.optimizeCaption(postInput.sentiment, postInput.caption)
    }
    

@router.post(
    "/sentiment/base", 
    name="sentiment_base",
    summary="Classify sentiment of a social media post"
)
async def classify_sentiment(request: Request, post: PostInput):

    logger.debug(post)

    # Validate text/caption
    is_valid, error_msg = validate_caption_for_sentiment(post.text)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Invalid text: {error_msg}")
    
    text = post.text.strip()
    worker_pool = request.app.state.worker_pool
    
    worker = await worker_pool.acquire_worker()

    try:
        tokenizer = worker.tokenizer
        model = worker.model

        # Tokenize and encode
        inputs = tokenizer(text, return_tensors="pt", truncation=True)

        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1).squeeze().tolist()

        max_idx = int(torch.argmax(torch.tensor(probs)))
        sentiment = model.config.id2label[max_idx]
        confidence = round(probs[max_idx], 4)

        result = {
            "input_text": text,
            "predicted_label": sentiment,
            "confidence": confidence,
            "all_scores": {model.config.id2label[i]: round(p, 4) for i, p in enumerate(probs)},
        }

        logger.info(f"Sentiment classified: {result}")

    finally:
        await worker_pool.release_worker(worker)

    return result