import chess
import chess.pgn
from typing import cast
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def convert_board_to_pgn(board: chess.Board) -> str:
    logger.debug("Converting this board to PGN:\n%s", board)
    # Create a new game
    game = chess.pgn.Game()
    
    # Add the moves from the board's move stack to create the game
    node = game
    for move in board.move_stack:
        node = cast(chess.pgn.Game, node.add_variation(move))
    
    full_pgn = str(game)
    lines = full_pgn.split('\n')
    
    # remove metadata headers
    moves_start = 0
    for i, line in enumerate(lines):
        if not line.startswith('[') and line.strip():
            moves_start = i
            break
    
    moves_only = '\n'.join(lines[moves_start:]).strip()
    
    logger.debug("PGN string constructed for the LLM: \n" + moves_only)
    return moves_only