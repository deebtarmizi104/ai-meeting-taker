from notion_client import Client
from datetime import datetime
from config import NOTION_API_KEY, NOTION_DATA_SOURCE_ID, logger, MeetingMinutes

class NotionIntegration:
    def __init__(self):
        # We must use the specific API version for data_source_id support
        self.notion = Client(auth=NOTION_API_KEY, notion_version="2025-09-03")
        self.data_source_id = NOTION_DATA_SOURCE_ID

    def export_to_notion(self, minutes: MeetingMinutes):
        current_date = datetime.now().strftime("%Y-%m-%d")
        page_title = f"{minutes.title} - {current_date}"
        
        logger.info(f"Creating Notion page: {page_title}")
        
        children = [
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Summary"}}]}},
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": minutes.summary}}]}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Key Decisions"}}]}},
        ]
        
        for decision in minutes.key_decisions:
            children.append({
                "object": "block", 
                "type": "bulleted_list_item", 
                "bulleted_list_item": {"rich_text": [{"text": {"content": decision}}]}
            })
            
        children.append({"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Action Items"}}]}})
        
        for item in minutes.action_items:
            children.append({
                "object": "block", 
                "type": "to_do", 
                "to_do": {
                    "rich_text": [{"text": {"content": f"{item.task} (Assignee: {item.assignee})"}}],
                    "checked": False
                }
            })

        try:
            # Using the required 2025-09-03 data_source_id payload
            self.notion.pages.create(
                parent={
                    "type": "data_source_id",
                    "data_source_id": self.data_source_id
                },
                properties={
                    "Name": { # Default property name for title in most Notion databases/data sources
                        "title": [{"text": {"content": page_title}}]
                    }
                },
                children=children
            )
            logger.info("Successfully exported to Notion.")
        except Exception as e:
            logger.error(f"Failed to export to Notion: {e}")
