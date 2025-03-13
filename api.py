from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import logging
import asyncio
from httpx import Timeout

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

RUNPOD_URL = "https://api.runpod.ai/v2/4qvyr433og9mmo/runsync"
API_KEY = "rpa_W2GU0PU0LVX6HYBO0MG4UIW3ZD5XJS6X2JRJFVRIt6dmai"  # Your RunPod API key

# Configure default timeout
default_timeout = Timeout(30.0, connect=10.0)

class ImageGeneration(BaseModel):
    prompt: str
    number_of_images: int

class BackgroundChange(BaseModel):
    prompt: str
    input_image: str

class PoseGeneration(BaseModel):
    prompt: str
    input_image: str

@app.post("/generate-image")
async def generate_image(data: ImageGeneration):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    body = {
        "input": {
            "generation_type": "GenerateImage",
            "number_of_images": data.number_of_images,
            "prompt": data.prompt
        }
    }
    
    logger.info(f"Sending request to ComfyUI: {body}")
    
    try:
        # Create a new client for each request with defined timeouts
        async with httpx.AsyncClient(timeout=default_timeout) as client:
            # Add retry mechanism
            max_retries = 2
            retry_delay = 1
            
            for attempt in range(max_retries + 1):
                try:
                    response = await client.post(RUNPOD_URL, json=body, headers=headers)
                    
                    # Log response info
                    logger.info(f"Response status: {response.status_code}")
                    logger.info(f"Response headers: {dict(response.headers)}")
                    
                    # Check for successful response
                    if response.status_code == 200:
                        content = response.text
                        logger.info(f"Response content: {content}")
                        return response.json()
                    elif response.status_code == 429:  # Rate limit
                        if attempt < max_retries:
                            wait_time = retry_delay * (2 ** attempt)
                            logger.warning(f"Rate limited, retrying in {wait_time}s...")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            raise HTTPException(
                                status_code=429, 
                                detail="Rate limit exceeded on RunPod API"
                            )
                    else:
                        raise HTTPException(
                            status_code=response.status_code,
                            detail=f"RunPod API error: {response.text}"
                        )
                except httpx.TimeoutException:
                    if attempt < max_retries:
                        logger.warning(f"Request timed out, retrying ({attempt+1}/{max_retries})...")
                        continue
                    else:
                        raise HTTPException(
                            status_code=504,
                            detail="Request to RunPod API timed out"
                        )
                except httpx.RequestError as e:
                    logger.error(f"Request error on attempt {attempt+1}: {str(e)}")
                    if attempt < max_retries:
                        continue
                    raise
    except httpx.RequestError as e:
        error_msg = f"Request error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=502, detail=error_msg)
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/change-background")
async def change_background(data: BackgroundChange):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    body = {
        "input": {
            "generation_type": "BackgroundChanger",
            "input_image": data.input_image,
            "prompt": data.prompt
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=default_timeout) as client:
            response = await client.post(RUNPOD_URL, json=body, headers=headers)
            
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text
                logger.info(f"Response content: {content}")
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"RunPod API error: {response.text}"
                )
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/generate-pose")
async def generate_pose(data: PoseGeneration):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    body = {
        "input": {
            "generation_type": "PoseGenerator",
            "input_image": data.input_image,
            "prompt": data.prompt
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=default_timeout) as client:
            response = await client.post(RUNPOD_URL, json=body, headers=headers)
            
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text
                logger.info(f"Response content: {content}")
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"RunPod API error: {response.text}"
                )
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/test")
async def test():
    return {"status": "API is running"}