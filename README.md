# AI Meeting Assistant

A cross-platform tool to record meetings (microphone + system audio) and generate structured meeting minutes using Gemini AI.

## Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (Recommended Python package manager)

## Setup Instructions

### 1. Environment Variables

Copy the `.env.template` file to a new file named `.env` and fill in your API keys:

```bash
cp .env.template .env
```

Required variables:
- `GEMINI_API_KEY`: Get this from [Google AI Studio](https://aistudio.google.com/).
- `NOTION_API_KEY`: Your Notion internal integration token.
- `NOTION_DATA_SOURCE_ID`: The ID of your Notion data source (required for the 2025-09-03 API version).

### 2. Installation

Use `uv` to synchronize dependencies and create a virtual environment:

```bash
uv sync
```

### 3. Running the Application

To start the meeting assistant:

```bash
uv run main.py
```

Follow the on-screen prompts to start and stop the recording. Meeting minutes will be generated and saved to the `meeting-content` directory by default.

## Features

- **Dual-Stream Recording**: Captures both your microphone and the system audio (other participants).
- **AI-Powered Analysis**: Uses Gemini 2.5 Flash to transcribe and summarize meetings.
- **Structured Output**: Generates titles, summaries, key decisions, and action items with assignees.
- **Local Export**: Saves minutes as formatted text files.
- **Notion Integration**: (Optional) Export minutes directly to a Notion database.
