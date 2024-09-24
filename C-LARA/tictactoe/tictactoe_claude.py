# tictactoe_claude.py
"""
Perform Claude-related operations for Tic-Tac-Toe
"""

from .clara_claude import get_api_claude_response
from .tictactoe_engine import index_to_algebraic, algebraic_to_index, get_available_moves

async def request_minimal_claude_move_async(board, player, callback=None):
    formatted_request = format_minimal_claude_request(board, player)
    available_moves = [index_to_algebraic(move) for move in get_available_moves(board)]
    
    return await call_claude_with_retry_async(formatted_request, available_moves, callback=callback)

async def call_claude_with_retry_async(formatted_request, available_moves, callback=None):
    api_calls = []
    n_attempts = 0
    limit = 5

    while n_attempts < limit:
        n_attempts += 1
        try:
            api_call = await get_api_claude_response(formatted_request, callback=callback)
            api_calls.append(api_call)
            selected_move = api_call['selected_move']

            if selected_move in available_moves:
                return {'selected_move': selected_move, 'prompt': formatted_request, 'api_calls': api_calls}
            else:
                raise ValueError(f"Illegal move: {selected_move}")
        except Exception as e:
            await post_task_update_async(callback, f"Error in Claude request: {str(e)}")
    return {'selected_move': None, 'prompt': formatted_request, 'api_calls': api_calls}

def format_minimal_claude_request(board, player):
    x_line_content = ', '.join([index_to_algebraic(i) for i, s in enumerate(board) if s == "X"])
    o_line_content = ', '.join([index_to_algebraic(i) for i, s in enumerate(board) if s == "O"])
    unoccupied_line_content = ', '.join([index_to_algebraic(i) for i, s in enumerate(board) if s == " "])

    return f"""Claude Tic-Tac-Toe move request:
    Player {player} to move.
    X occupied: {x_line_content}
    O occupied: {o_line_content}
    Unoccupied: {unoccupied_line_content}
    """
