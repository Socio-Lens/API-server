import os
import torch
import logging
from urllib.parse import urlparse
from pydantic import BaseModel
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from modules.scrapper.InstaScrapper import InstaScrapper


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/service", tags=["service"])

class PostInput(BaseModel):
    text: str
    
class CaptionInput(BaseModel):
    url: str


def validate_request(request):
    pass

@router.post("/caption/instagram", summary="Get the caption from an Instagram URL")
async def get_instagram_caption(request: Request, postInput: CaptionInput):
    logger.debug(postInput)
    
    parsed = urlparse(postInput.url)
    domain = parsed.netloc.lower()
    logger.debug(domain)

    if domain != 'www.instagram.com':
        raise HTTPException(status_code=400, detail="Invalid or unsupported URL domain")
    
    try:
        scrapper = InstaScrapper()
        caption = scrapper.get_caption_from_post_url(postInput.url)
    except Exception as e:   # replace with real exception(s)
        logger.exception("Error fetching caption", e)
        raise HTTPException(status_code=502, detail="Failed to fetch caption")
    return {"caption": caption}

@router.post("/", summary="Classify sentiment of a social media post")
async def classify_sentiment(request: Request, post: PostInput):

    logger.debug(post)

    text = post.text.strip()
    worker_pool = request.app.state.worker_pool
    if not text:
        raise HTTPException(status_code=400, detail="Empty text provided")
    
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