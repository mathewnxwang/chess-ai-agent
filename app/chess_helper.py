import chess
import chess.pgn
import io
from typing import cast

def convert_board_to_pgn(board: chess.Board) -> str:
    # Create a new game
    game = chess.pgn.Game()
    
    # Add the moves from the board's move stack to create the game
    node = game
    for move in board.move_stack:
        node = cast(chess.pgn.Game, node.add_variation(move))
    
    # Write the game to a string
    pgn_string = io.StringIO()
    exporter = chess.pgn.FileExporter(pgn_string)
    game.accept(exporter)
    
    print("PGN string for the LLM: \n" + pgn_string.getvalue())
    return pgn_string.getvalue()