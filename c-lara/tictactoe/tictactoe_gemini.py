from .clara_gemini import request_minimal_gemini_move_async
from .tictactoe_engine import index_to_algebraic, algebraic_to_index, get_available_moves

async def gemini_minimal_player_async(board, player):
    """Get a move from Gemini and apply it to the board."""
    move_algebraic = await request_minimal_gemini_move_async(board, player)
    move_index = algebraic_to_index(move_algebraic)
    
    if move_index in get_available_moves(board):
        return move_index
    else:
        raise ValueError("Gemini suggested an invalid move.")

# Example function to play a game move using Gemini
async def play_with_gemini(board, player):
    try:
        move = await gemini_minimal_player_async(board, player)
        board[move] = player  # Assume player is either 'X' or 'O'
    except Exception as e:
        print(f"Error during play with Gemini: {e}")
