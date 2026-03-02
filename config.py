import os
import logging
from typing import List, Dict
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATA_SOURCE_ID = os.getenv("NOTION_DATA_SOURCE_ID")

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("AI-Meeting-Assistant")

class ActionItem(BaseModel):
    task: str
    assignee: str

class MeetingMinutes(BaseModel):
    title: str = Field(..., description="The generated title of the meeting")
    summary: str = Field(..., description="A concise summary of the meeting")
    key_decisions: List[str] = Field(default_factory=list, description="List of key decisions made")
    action_items: List[ActionItem] = Field(default_factory=list, description="List of tasks and assignees")
