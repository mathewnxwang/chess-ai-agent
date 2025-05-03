# Chess Web App

A web-based chess game built with Python FastAPI, chess.js, and chessboard.js. The chess logic is handled by the Python-chess library on the backend and chess.js on the frontend, while chessboard.js provides an interactive chessboard interface.

## Features

- Interactive chess board with drag-and-drop moves
- Legal move validation 
- Game state tracking (check, checkmate, etc.)
- Player always starts as white
- Reset game functionality

## Prerequisites

- Python 3.11+
- Poetry (Python package manager)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd chess-ai-agent
```

2. Install dependencies using Poetry:
```bash
poetry install
```

## Running the Application

1. Activate the Poetry virtual environment:
```bash
poetry shell
```

2. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```
or
```bash
python run.py
```

3. Open your web browser and navigate to:
```
http://localhost:8000
```

## How to Play

1. The game starts with white (you) to move
2. Drag and drop pieces to make moves
3. Invalid moves will automatically snap back
4. Click the "New Game" button to reset the board at any time

## Project Structure

```
chess-ai-agent/
├── app/
│   ├── main.py            # FastAPI backend with Python-chess
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css # Styling for the chess board
│   │   └── js/
│   │       └── chessboard.js # Frontend logic using chess.js and chessboard.js
│   └── templates/
│       └── index.html     # Main HTML template with CDN imports
├── pyproject.toml         # Poetry configuration
├── run.py                 # Simple runner script
└── README.md              # This file
```

## Technologies Used

- **Backend**: Python with FastAPI, Python-chess
- **Frontend**: HTML, CSS, JavaScript
- **Chess Libraries**: 
  - [chessboard.js](https://chessboardjs.com/) - JavaScript chessboard UI
  - [chess.js](https://github.com/jhlywa/chess.js) - JavaScript chess logic
- **Package Management**: Poetry