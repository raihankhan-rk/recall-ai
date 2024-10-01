# Recall AI

Recall AI is an intelligent bot that serves as the brain you've always wanted. It remembers everything for you and recalls information effortlessly when needed.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Overview

Recall AI is a Telegram bot that uses advanced AI techniques to process and store various types of information, including text, documents, images, and audio. It can then recall this information on demand, acting as an extended memory for users.

## Features

- Process and remember text messages
- Extract information from documents (PDF, DOCX)
- Analyze images and extract text
- Transcribe and remember audio content
- Extract and summarize content from URLs
- Answer questions based on stored information
- User activation system with license keys

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8+
- pip (Python package manager)
- MongoDB
- Qdrant vector database

You'll also need to obtain the following:
- OpenAI API key
- Telegram Bot Token

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/recall-ai.git
   cd recall-ai
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root and add the following:
   ```
   BOT_TOKEN=your_telegram_bot_token
   MONGODB_URI=your_mongodb_uri
   DB_NAME=your_database_name
   OPENAI_API_KEY=your_openai_api_key
   QDRANT_URL=your_qdrant_url
   QDRANT_API_KEY=your_qdrant_api_key
   ```

5. Create MongoDB collections:
   ```
   python create_collections.py
   ```

6. Generate license keys (optional):
   ```
   python admin_tools.py
   ```
   Choose option 1 to generate license keys.

## Usage

1. Start the bot:
   ```
   python main.py
   ```

2. In Telegram, start a chat with your bot and use the following commands:
   - `/start`: Initialize the bot
   - `/help`: Get information about available commands
   - `/activate <LICENSE_KEY>`: Activate your account
   - `/ask <QUESTION>`: Ask a question based on stored information

Send text messages, documents, images, or audio files to the bot, and it will process and store the information for later recall.

## Project Structure

- `main.py`: Entry point of the application
- `handlers.py`: Telegram bot command and message handlers
- `processors.py`: Functions to process different types of input (text, documents, images, audio)
- `utils.py`: Utility functions for AI processing and database operations
- `database.py`: Database-related functions
- `admin_tools.py`: Admin tools for managing license keys
- `create_collections.py`: Script to set up MongoDB collections

## Contributing

We welcome contributions to Recall AI! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more information on how to get started.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
