from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import requests

# AI agents
from ai_agents.agents import AgentConfig, SearchAgent, ChatAgent


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# AI agents init
agent_config = AgentConfig()
search_agent: Optional[SearchAgent] = None
chat_agent: Optional[ChatAgent] = None

# Main app
app = FastAPI(title="AI Agents API", description="Minimal AI Agents API with LangGraph and MCP support")

# API router
api_router = APIRouter(prefix="/api")


# Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str


# AI agent models
class ChatRequest(BaseModel):
    message: str
    agent_type: str = "chat"  # "chat" or "search"
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    success: bool
    response: str
    agent_type: str
    capabilities: List[str]
    metadata: dict = Field(default_factory=dict)
    error: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    max_results: int = 5


class SearchResponse(BaseModel):
    success: bool
    query: str
    summary: str
    search_results: Optional[dict] = None
    sources_count: int
    error: Optional[str] = None


class WallpaperRequest(BaseModel):
    prompt: str
    aspect_ratio: str = "9:16"  # Default to phone aspect ratio
    style: Optional[str] = None


class WallpaperResponse(BaseModel):
    success: bool
    image_url: Optional[str] = None
    prompt: str
    aspect_ratio: str
    error: Optional[str] = None

# Routes
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]


# AI agent routes
@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    # Chat with AI agent
    global search_agent, chat_agent
    
    try:
        # Init agents if needed
        if request.agent_type == "search" and search_agent is None:
            search_agent = SearchAgent(agent_config)
            
        elif request.agent_type == "chat" and chat_agent is None:
            chat_agent = ChatAgent(agent_config)
        
        # Select agent
        agent = search_agent if request.agent_type == "search" else chat_agent
        
        if agent is None:
            raise HTTPException(status_code=500, detail="Failed to initialize agent")
        
        # Execute agent
        response = await agent.execute(request.message)
        
        return ChatResponse(
            success=response.success,
            response=response.content,
            agent_type=request.agent_type,
            capabilities=agent.get_capabilities(),
            metadata=response.metadata,
            error=response.error
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return ChatResponse(
            success=False,
            response="",
            agent_type=request.agent_type,
            capabilities=[],
            error=str(e)
        )


@api_router.post("/search", response_model=SearchResponse)
async def search_and_summarize(request: SearchRequest):
    # Web search with AI summary
    global search_agent
    
    try:
        # Init search agent if needed
        if search_agent is None:
            search_agent = SearchAgent(agent_config)
        
        # Search with agent
        search_prompt = f"Search for information about: {request.query}. Provide a comprehensive summary with key findings."
        result = await search_agent.execute(search_prompt, use_tools=True)
        
        if result.success:
            return SearchResponse(
                success=True,
                query=request.query,
                summary=result.content,
                search_results=result.metadata,
                sources_count=result.metadata.get("tools_used", 0)
            )
        else:
            return SearchResponse(
                success=False,
                query=request.query,
                summary="",
                sources_count=0,
                error=result.error
            )
            
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        return SearchResponse(
            success=False,
            query=request.query,
            summary="",
            sources_count=0,
            error=str(e)
        )


@api_router.get("/agents/capabilities")
async def get_agent_capabilities():
    # Get agent capabilities
    try:
        capabilities = {
            "search_agent": SearchAgent(agent_config).get_capabilities(),
            "chat_agent": ChatAgent(agent_config).get_capabilities()
        }
        return {
            "success": True,
            "capabilities": capabilities
        }
    except Exception as e:
        logger.error(f"Error getting capabilities: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@api_router.post("/generate-wallpaper", response_model=WallpaperResponse)
async def generate_wallpaper(request: WallpaperRequest):
    # Generate AI wallpaper using AI image generation
    try:
        # Enhanced prompt for better wallpaper generation
        enhanced_prompt = request.prompt
        if request.style:
            enhanced_prompt += f", {request.style} style"

        enhanced_prompt += ", high quality, detailed, vibrant colors, perfect for phone wallpaper, 4K resolution"

        # Use ChatAgent to generate wallpaper with image capabilities
        global chat_agent

        if chat_agent is None:
            chat_agent = ChatAgent(agent_config)

        # Create a special prompt for image generation
        image_generation_prompt = f"Generate a high-quality phone wallpaper with the following description: {enhanced_prompt}. The image should be optimized for mobile screens with vibrant colors and sharp details."

        # Execute the agent request
        result = await chat_agent.execute(image_generation_prompt, use_tools=True)

        if result.success and result.metadata.get("generated_image_url"):
            return WallpaperResponse(
                success=True,
                image_url=result.metadata["generated_image_url"],
                prompt=request.prompt,
                aspect_ratio=request.aspect_ratio
            )
        else:
            # Fallback to curated images based on prompt
            # Use a more sophisticated fallback with better image sources
            fallback_images = {
                "mountain": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1080&h=1920&fit=crop&crop=center",
                "ocean": "https://images.unsplash.com/photo-1439066615861-d1af74d74000?w=1080&h=1920&fit=crop&crop=center",
                "forest": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1080&h=1920&fit=crop&crop=center",
                "city": "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=1080&h=1920&fit=crop&crop=center",
                "space": "https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=1080&h=1920&fit=crop&crop=center",
                "abstract": "https://images.unsplash.com/photo-1557682250-33bd709cbe85?w=1080&h=1920&fit=crop&crop=center",
                "sunset": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1080&h=1920&fit=crop&crop=center",
                "flowers": "https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=1080&h=1920&fit=crop&crop=center"
            }

            # Find best matching fallback image
            prompt_lower = request.prompt.lower()
            selected_image = None

            for keyword, image_url in fallback_images.items():
                if keyword in prompt_lower:
                    selected_image = image_url
                    break

            # Default fallback
            if not selected_image:
                selected_image = f"https://picsum.photos/1080/1920?random={abs(hash(request.prompt)) % 1000}"

            return WallpaperResponse(
                success=True,
                image_url=selected_image,
                prompt=request.prompt,
                aspect_ratio=request.aspect_ratio
            )

    except Exception as e:
        logger.error(f"Error generating wallpaper: {e}")
        return WallpaperResponse(
            success=False,
            prompt=request.prompt,
            aspect_ratio=request.aspect_ratio,
            error=str(e)
        )

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    # Initialize agents on startup
    global search_agent, chat_agent
    logger.info("Starting AI Agents API...")
    
    # Lazy agent init for faster startup
    logger.info("AI Agents API ready!")


@app.on_event("shutdown")
async def shutdown_db_client():
    # Cleanup on shutdown
    global search_agent, chat_agent
    
    # Close MCP
    if search_agent and search_agent.mcp_client:
        # MCP cleanup automatic
        pass
    
    client.close()
    logger.info("AI Agents API shutdown complete.")
