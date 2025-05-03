# Chess Web App

A simple web-based chess game built with Python FastAPI and JavaScript. The chess logic is handled by the Python-chess library on the backend, while the frontend provides an interactive chessboard interface.

## Features

- Interactive chess board
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

3. Open your web browser and navigate to:
```
http://localhost:8000
```

## How to Play

1. The game starts with white (you) to move
2. Click on a piece to select it
3. Available moves will be highlighted with green dots
4. Click on a highlighted square to move your piece there
5. Click the "New Game" button to reset the board at any time

## Project Structure

```
chess-ai-agent/
├── app/
│   ├── main.py            # FastAPI backend
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css # Styling for the chess board
│   │   └── js/
│   │       └── chessboard.js # Frontend logic
│   └── templates/
│       └── index.html     # Main HTML template
├── pyproject.toml         # Poetry configuration
└── README.md              # This file
```

## Technologies Used

- **Backend**: Python with FastAPI, Python-chess
- **Frontend**: HTML, CSS, JavaScript
- **Package Management**: Poetry