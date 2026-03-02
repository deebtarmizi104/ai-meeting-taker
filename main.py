import sys
from config import logger, GEMINI_API_KEY
from audio_manager import CrossPlatformAudioRecorder
from gemini_processor import MeetingIntelligence
from file_exporter import FileExporter

def check_env():
    if not GEMINI_API_KEY:
        logger.error("Missing GEMINI_API_KEY environment variable.")
        sys.exit(1)

def main():
    check_env()
    
    recorder = CrossPlatformAudioRecorder()
    processor = MeetingIntelligence()
    exporter = FileExporter() # Switching to local file exporter

    print("\n--- AI Meeting Assistant (FOSS) ---")
    input("Press Enter to START recording...")
    
    try:
        recorder.start_recording()
        input("Recording in progress... Press Enter to STOP.")
    except Exception as e:
        logger.error(f"Error during capture: {e}")
        return
    finally:
        audio_path = recorder.stop_recording()

    if not audio_path:
        logger.error("No audio was recorded.")
        return

    try:
        minutes = processor.process_audio(audio_path)
        if minutes:
            # Export to a local .txt file
            exporter.export_to_file(minutes)
            
            print("\n--- Meeting Minutes Captured ---")
            print(f"Title: {minutes.title}")
            print(f"Summary: {minutes.summary}")
            print("--------------------------------")
        else:
            logger.error("Failed to generate meeting minutes.")
    except Exception as e:
        logger.error(f"Orchestration error: {e}")
    finally:
        recorder.cleanup()

if __name__ == "__main__":
    main()
