# Chess Master with Stockfish AI

A modern, sleek web-based chess game built with Python FastAPI, chess.js, chessboard.js, and Stockfish. The chess logic is handled by python-chess on the backend and chess.js on the frontend, while Stockfish provides AI opponent capabilities.

## Features

- Play against Stockfish chess engine (user plays as white)
- Adjustable AI difficulty levels and search depth
- Modern UI with sleek design and animations
- Interactive chess board with drag-and-drop moves
- Legal move validation and move highlighting
- Game state tracking (check, checkmate, draw)
- Move history with standard algebraic notation
- Last move highlighting
- Undo move functionality
- New game / reset functionality
- Fully responsive design for all devices
- Visual effects and status indicators

## Prerequisites

- Python 3.11+
- Poetry (Python package manager)
- Stockfish chess engine

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

3. Make sure you have Stockfish installed and update the path in `app/main.py`:
```python
stockfish_path = r"path/to/your/stockfish"
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

3. Open a web browser and navigate to:
```
http://localhost:8000
```

## How to Play

1. The game starts with you playing as white
2. Drag and drop pieces to make moves
3. Stockfish will automatically respond with black's moves
4. Invalid moves will automatically snap back
5. The last move made is highlighted on the board
6. Move history is displayed on the right side
7. Status indicators show whose turn it is and game state
8. "Undo" button allows you to take back moves
9. "New Game" button resets the board at any time
10. Adjust Stockfish difficulty in the "Stockfish Settings" panel

## AI Difficulty Settings

You can customize Stockfish's playing strength:

- **Skill Level**: Controls how strong the AI plays (1-20)
  - Beginner (1): Very weak play suitable for beginners
  - Casual (5): Moderate play with occasional mistakes
  - Intermediate (10): Solid play with fewer mistakes
  - Advanced (15): Strong play, challenging for most players
  - Master (20): Very strong play, challenging even for advanced players

- **Search Depth**: Controls how deeply Stockfish analyzes positions
  - Quick (5): Fast response times but less accurate analysis
  - Normal (10): Balanced between speed and accuracy
  - Deep (15): More accurate but slower response
  - Very Deep (20): Most accurate but slowest response

## UI Features

- **Modern Interface**: Clean, card-based layout with shadow effects
- **Responsive Design**: Adapts to different screen sizes from desktop to mobile
- **Visual Feedback**: Hover effects, animations, and transitions
- **Game Status Indicators**: Special styling for check, checkmate and draw
- **Move History**: Scrollable list of all moves in algebraic notation
- **Highlighting**: Last move highlighting helps track game progress
- **Victory Effects**: Special animations when a player wins

## Project Structure

```
chess-ai-agent/
├── app/
│   ├── main.py            # FastAPI backend with Python-chess and Stockfish integration
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css # Modern styling for the chess board and UI
│   │   └── js/
│   │       └── chessboard.js # Frontend logic using chess.js and chessboard.js
│   └── templates/
│       └── index.html     # Main HTML template with modern structure
├── pyproject.toml         # Poetry configuration
├── run.py                 # Simple runner script
└── README.md              # This file
```

## Technologies Used

- **Backend**: Python with FastAPI, Python-chess
- **AI Engine**: Stockfish chess engine
- **Frontend**: HTML, CSS, JavaScript
- **Chess Libraries**: 
  - [chessboard.js](https://chessboardjs.com/) - JavaScript chessboard UI
  - [chess.js](https://github.com/jhlywa/chess.js) - JavaScript chess logic
- **UI/UX**: 
  - Google Fonts (Montserrat, Roboto)
  - Font Awesome icons
  - CSS animations and transitions
- **Package Management**: Poetry