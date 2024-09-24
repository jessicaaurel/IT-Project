# tictactoe_llama.py

from .tictactoe_engine import index_to_algebraic, algebraic_to_index
from .clara_llama import get_llama_move

# Ask LLaMA for the best move
async def llama_minimal_player_async(board, player):
    formatted_request = format_llama_request(board, player)
    llama_response = await get_llama_move(formatted_request)
    
    # Parse the response to get the selected move
    selected_move = llama_response.get('selected_move')
    return algebraic_to_index(selected_move), llama_response['cot_record'], llama_response['prompt'], llama_response['total_cost']

# Format the request to send to LLaMA, similar to GPT-4 and Gemini
def format_llama_request(board, player):
    x_line_content = ', '.join([index_to_algebraic(i) for i, s in enumerate(board) if s == "X"])
    o_line_content = ', '.join([index_to_algebraic(i) for i, s in enumerate(board) if s == "O"])
    unoccupied_line_content = ', '.join([index_to_algebraic(i) for i, s in enumerate(board) if s == " "])
    
    # Construct the request for LLaMA
    return f"""Player {player} is to move. The board state is as follows:
Squares occupied by X: {x_line_content}
Squares occupied by O: {o_line_content}
Unoccupied squares: {unoccupied_line_content}
Please provide the best move for player {player}."""
