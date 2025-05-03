# Chess Master

A modern, sleek web-based chess game built with Python FastAPI, chess.js, and chessboard.js. The chess logic is handled by the Python-chess library on the backend and chess.js on the frontend, while chessboard.js provides an interactive chessboard interface.

## Features

- Modern UI with sleek design and animations
- Interactive chess board with drag-and-drop moves
- Legal move validation and move highlighting
- Game state tracking (check, checkmate, draw)
- Move history with standard algebraic notation
- Last move highlighting
- Player always starts as white
- Undo move functionality
- New game / reset functionality
- Fully responsive design for all devices
- Visual effects and status indicators

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

3. Open a web browser and navigate to:
```
http://localhost:8000
```

## How to Play

1. The game starts with white (you) to move
2. Drag and drop pieces to make moves
3. Invalid moves will automatically snap back
4. The last move made is highlighted on the board
5. Move history is displayed on the right side
6. Status indicators show whose turn it is and game state
7. "Undo" button allows you to take back the last move
8. "New Game" button resets the board at any time

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
│   ├── main.py            # FastAPI backend with Python-chess
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
- **Frontend**: HTML, CSS, JavaScript
- **Chess Libraries**: 
  - [chessboard.js](https://chessboardjs.com/) - JavaScript chessboard UI
  - [chess.js](https://github.com/jhlywa/chess.js) - JavaScript chess logic
- **UI/UX**: 
  - Google Fonts (Montserrat, Roboto)
  - Font Awesome icons
  - CSS animations and transitions
- **Package Management**: Poetry