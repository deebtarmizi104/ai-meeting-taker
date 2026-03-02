import os
from datetime import datetime
from config import logger, MeetingMinutes

class FileExporter:
    def __init__(self, output_dir="meeting-content"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Created directory: {self.output_dir}")

    def export_to_file(self, minutes: MeetingMinutes):
        current_date = datetime.now().strftime("%Y-%m-%d")
        # Sanitize filename
        safe_title = "".join([c for c in minutes.title if c.isalnum() or c in (" ", "-", "_")]).strip()
        file_name = f"{safe_title} - {current_date}.txt"
        file_path = os.path.join(self.output_dir, file_name)

        logger.info(f"Exporting meeting minutes to: {file_path}")

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"MEETING TITLE: {minutes.title}\n")
                f.write(f"DATE: {current_date}\n")
                f.write("="*40 + "\n\n")

                f.write("SUMMARY:\n")
                f.write(f"{minutes.summary}\n\n")

                f.write("KEY DECISIONS:\n")
                for decision in minutes.key_decisions:
                    f.write(f"- {decision}\n")
                f.write("\n")

                f.write("ACTION ITEMS:\n")
                for item in minutes.action_items:
                    f.write(f"[ ] {item.task} (Assignee: {item.assignee})\n")

            logger.info("Successfully exported to local file.")
            print(f"\nSaved to: {file_path}")
        except Exception as e:
            logger.error(f"Failed to export to file: {e}")
