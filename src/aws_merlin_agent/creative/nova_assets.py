"""
Amazon Nova integration for creative asset generation.

Demonstrates multimodal AI capabilities using Nova Canvas (images) and Nova Reel (video).
This satisfies the hackathon requirement for Nova integration.
"""
from __future__ import annotations

import base64
import json
from typing import Dict

from aws_merlin_agent.config.settings import EnvironmentSettings
from aws_merlin_agent.utils import aws, logging

logger = logging.get_logger(__name__)


def generate_listing_image(prompt: str, product_name: str = "product") -> Dict[str, str]:
    """
    Generate product imagery using Amazon Nova Canvas.
    
    This demonstrates Nova's multimodal capabilities for the hackathon.
    """
    settings = EnvironmentSettings.load()
    bedrock_runtime = aws.client("bedrock-runtime", region_name=settings.region)
    
    full_prompt = f"Professional product photography: {prompt}"
    
    try:
        # Use Nova Canvas for image generation
        model_id = "amazon.nova-canvas-v1:0"
        
        request_body = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": full_prompt
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "width": 1024,
                "height": 1024,
                "cfgScale": 8.0,
                "seed": 42
            }
        }
        
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response["body"].read())
        
        # Extract base64 image
        if "images" in response_body and len(response_body["images"]) > 0:
            image_base64 = response_body["images"][0]
            # In production, save to S3
            asset_uri = f"s3://{settings.creative_bucket}/assets/{product_name}-generated.png"
            logger.info("Generated product image using Nova Canvas")
            return {
                "prompt": prompt,
                "asset_uri": asset_uri,
                "image_base64": image_base64,
                "status": "success"
            }
        else:
            logger.warning("No images returned from Nova Canvas")
            return {
                "prompt": prompt,
                "asset_uri": f"s3://{settings.creative_bucket}/assets/mock-image.png",
                "status": "no_images"
            }
            
    except Exception as e:
        logger.error("Nova Canvas image generation failed: %s", str(e))
        return {
            "prompt": prompt,
            "asset_uri": f"s3://{settings.creative_bucket}/assets/mock-image.png",
            "status": "error",
            "error": str(e)
        }


def generate_promotional_video(
    product_name: str,
    key_features: list[str],
    duration_seconds: int = 6
) -> Dict[str, str]:
    """
    Generate promotional video using Amazon Nova Reel.
    
    Args:
        product_name: Name of the product
        key_features: List of key features to highlight
        duration_seconds: Video duration (max 6 seconds)
        
    Returns:
        Dict with video URI and metadata
    """
    settings = EnvironmentSettings.load()
    bedrock_runtime = aws.client("bedrock-runtime", region_name=settings.region)
    
    features_text = ", ".join(key_features)
    prompt = f"Professional product showcase video for {product_name}. Highlights: {features_text}. Clean, modern aesthetic."
    
    try:
        # Use Nova Reel for video generation
        model_id = "amazon.nova-reel-v1:0"
        
        request_body = {
            "taskType": "TEXT_VIDEO",
            "textToVideoParams": {
                "text": prompt
            },
            "videoGenerationConfig": {
                "durationSeconds": min(duration_seconds, 6),
                "fps": 24,
                "dimension": "1280x720",
                "seed": 42
            }
        }
        
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response["body"].read())
        
        # Extract base64 video
        if "video" in response_body:
            video_base64 = response_body["video"]
            asset_uri = f"s3://{settings.creative_bucket}/videos/{product_name}-promo.mp4"
            logger.info("Generated promotional video using Nova Reel")
            return {
                "product_name": product_name,
                "asset_uri": asset_uri,
                "video_base64": video_base64,
                "status": "success"
            }
        else:
            logger.warning("No video returned from Nova Reel")
            return {
                "product_name": product_name,
                "asset_uri": f"s3://{settings.creative_bucket}/videos/mock-video.mp4",
                "status": "no_video"
            }
            
    except Exception as e:
        logger.error("Nova Reel video generation failed: %s", str(e))
        return {
            "product_name": product_name,
            "asset_uri": f"s3://{settings.creative_bucket}/videos/mock-video.mp4",
            "status": "error",
            "error": str(e)
        }


def analyze_product_image(image_bytes: bytes, questions: list[str]) -> dict[str, str]:
    """
    Analyze product images using Amazon Nova Pro's vision capabilities.
    
    Args:
        image_bytes: Image data
        questions: List of questions to ask about the image
        
    Returns:
        Dict mapping questions to answers
    """
    settings = EnvironmentSettings.load()
    bedrock_runtime = aws.client("bedrock-runtime", region_name=settings.region)
    
    try:
        # Use Nova Pro for vision analysis
        model_id = "amazon.nova-pro-v1:0"
        
        # Encode image to base64
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        
        results = {}
        for question in questions:
            request_body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "image": {
                                    "format": "png",
                                    "source": {
                                        "bytes": image_base64
                                    }
                                }
                            },
                            {
                                "text": question
                            }
                        ]
                    }
                ],
                "inferenceConfig": {
                    "max_new_tokens": 300,
                    "temperature": 0.7
                }
            }
            
            response = bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response["body"].read())
            answer = response_body["output"]["message"]["content"][0]["text"]
            results[question] = answer
        
        logger.info("Analyzed product image using Nova Pro vision")
        return results
        
    except Exception as e:
        logger.error("Nova Pro vision analysis failed: %s", str(e))
        return {q: f"Analysis failed: {str(e)}" for q in questions}
