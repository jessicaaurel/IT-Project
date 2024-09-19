"""
Perform Gemini related operations

The actual Gemini calls are made using the function get_api_gemini_response, defined in clara_gemini
If you want to use another LLM, you need to provide a similar function

Functions are async to allow multiple simultaneous calls

We pass the list of available moves so that we can catch responses which suggest an illegal move.
If this happens, we retry.
"""

from .tictactoe_engine import get_opponent, algebraic_to_index, index_to_algebraic, get_available_moves
from .clara_gemini import get_api_gemini_response
from .clara_utils import post_task_update, post_task_update_async
from .clara_classes import GeminiError

import asyncio
from collections import defaultdict
import traceback

max_number_of_gemini_tries = 5

def prepare_payload(data):
    # Convert all dictionary keys and values to strings
    if isinstance(data, dict):
        return {str(key): str(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [str(item) for item in data]
    return str(data)

# Get a move using a plain Gemini prompt
async def request_minimal_gemini_move_async(board, player, callback=None):
    formatted_request = format_minimal_gemini_request(board, player)
    available_moves = [index_to_algebraic(move) for move in get_available_moves(board)]
    return await call_gemini_with_retry_async(formatted_request, available_moves, callback=callback)

# Get a move using a Chain of Thought Gemini prompt with few-shot examples.
# The list of few-shot examples can be empty
async def request_cot_analysis_and_move_async(board, player, cot_template_name, few_shot_examples, callback=None):
    formatted_request = format_cot_request(board, player, cot_template_name, few_shot_examples)
    available_moves = [index_to_algebraic(move) for move in get_available_moves(board)]
    return await call_gemini_with_retry_async(formatted_request, available_moves, callback=callback)

# Get a move using a Chain of Thought Gemini prompt with few-shot examples.
# The list of few-shot examples can be empty
# Make the request multiple times until the same move has been returned twice.
async def request_cot_analysis_and_move_with_voting_async(board, player, cot_template_name, few_shot_examples, callback=None):
    formatted_request = format_cot_request(board, player, cot_template_name, few_shot_examples)
    available_moves = [index_to_algebraic(move) for move in get_available_moves(board)]

    move_counts = defaultdict(int)
    cot_records = {}
    api_calls = []

    # Run the first two invocations in parallel
    tasks = [asyncio.create_task(call_gemini_with_retry_async(formatted_request, available_moves, callback=callback)) for _ in range(2)]
    results = await asyncio.gather(*tasks)

    for response in results:
        move = response['selected_move']
        move_counts[move] += 1
        cot_records[move] = response['cot_record']
        api_calls.extend(response['api_calls'])

        if move_counts[move] == 2:
            return {'selected_move': move, 'cot_record': cot_records[move], 'prompt': formatted_request, 'api_calls': api_calls}

    # Continue submitting requests until we get two responses selecting the same move
    while True:
        response = await call_gemini_with_retry_async(formatted_request, available_moves, callback=callback)
        move = response['selected_move']
        move_counts[move] += 1
        cot_records[move] = response['cot_record']
        api_calls.extend(response['api_calls'])

        if move_counts[move] == 2:
            return {'selected_move': move, 'cot_record': cot_records[move], 'prompt': formatted_request, 'api_calls': api_calls}

# Submit a request to Gemini, interpret it as JSON, extract the move, and check that it is a legal one.
# If it isn't, retry.
# Return a dict of the form
#
# {'cot_record': response_string, 'prompt': formatted_request, 'selected_move': selected_move, 'api_calls': api_calls}
#
# We use the api_call objects to get costs.
async def call_gemini_with_retry_async(formatted_request, gemini_model, callback=None):
    """
    Call Gemini API with retries in case of failure.
    """
    max_attempts = 3
    attempt = 0
    while attempt < max_attempts:
        attempt += 1
        try:
            # Prepare the request payload
            payload = prepare_payload(formatted_request)
            
            # Await the coroutine to get the result
            response = await get_api_gemini_response(payload, config_info={'gemini_model': gemini_model}, callback=callback)
            
            # Access the response and status code from the response dictionary
            response_string = response.get('response', {})
            status_code = response.get('status_code', None)
            
            if status_code == 200:
                # Await the coroutine to get the move_info
                move_info = await get_api_gemini_response(response_string)
                selected_move = move_info.get('selected_move')
                return selected_move
            else:
                print(f"Error: Received status code {status_code}")
        except Exception as e:
            print(f"Warning: error when sending request to Gemini [callback = {callback}]")
            print(f"{str(e)}")
    raise Exception("Failed to call Gemini API after multiple attempts.")

# Call Gemini to try to determine if a CoT response gave the right answer using consistent reasons.
async def call_gemini_with_retry_for_cot_evaluation_async(formatted_request, gemini_model='gemini-1', callback=None):
    api_calls = []
    n_attempts = 0
    limit = max_number_of_gemini_tries
    while True:
        if n_attempts >= limit:
            await post_task_update_async(callback, f'*** Giving up, have tried sending this to Gemini {limit} times')
            return {'evaluation': None, 'api_calls': api_calls}
        n_attempts += 1
        await post_task_update_async(callback, f'--- Calling {gemini_model} (attempt #{n_attempts})')
        try:
            api_call = await get_api_gemini_response(formatted_request, config_info={'gemini_model': gemini_model}, callback=callback)
            api_calls.append(api_call)
            response_string = api_call.get('response', {})
            move_info = get_api_gemini_response(response_string)
            if not 'logically_consistent' in evaluation or not 'correct_threats_and_opportunities' in evaluation:
                raise ValueError(f'Evaluation not in requested format: {evaluation}')
            return {'evaluation': evaluation, 'api_calls': api_calls}
        except GeminiError as e:
            await post_task_update_async(callback, f"Error parsing Gemini response: {e}")
        except Exception as e:
            await post_task_update_async(callback, f'*** Warning: error when sending request to Gemini')
            await post_task_update_async(callback, f'"{str(e)}"\n{traceback.format_exc()}')

minimal_template = """
Given the current Tic-Tac-Toe board state, find the best move for the player {player}.

Here is the board state, where the squares occupied by X and O, and the unoccupied squares, are given using chess algebraic notation:

{board}

A player wins if they can occupy all three squares on one of the following eight lines:

{possible_lines}

Return the selected move in JSON format as follows, where <move> is given in chess algebraic notation:
```json
{{
    "selected_move": "<move>"
}}
"""

cot_template = """ Given the current Tic-Tac-Toe board state, provide a detailed Chain of Thought analysis to determine the best move for the player {player}. Consider in particular possible winning moves for {player}, possible winning moves that {opponent} may be threatening to make, and possible moves that {player} can make which will threaten to win.

Here is the board state, where the squares occupied by X and O, and the unoccupied squares, are given using chess algebraic notation:

{board}

A player wins if they can occupy all three squares on one of the following eight lines:

{possible_lines}

Provide your analysis and the best move. At the end, return the selected move in JSON format as follows:
```json
{{
    "selected_move": "<move>"
}}
```

{cot_examples}
"""

cot_template_explicit = """
Given the current Tic-Tac-Toe board state, provide a detailed Chain of Thought analysis to determine the best move for the player {player}.

Here is the board state, where the squares occupied by X and O, and the unoccupied squares, are given using chess algebraic notation:

{board}

A player wins if they can occupy all three squares on one of the following eight lines:

{possible_lines}

Reason as follows:
1. If {player} can play on an empty square and make a line of three {player}s, play on that square and win now.

2. Otherwise, if {opponent} could play on an empty square and make a line of three {opponent}s, play on that square to stop them winning next move.

3. Otherwise, if {player} can play on an empty square and create a position where they have more than one immediate threat,
   i.e. more than one line containing two {player}s and an empty square, play the move which creates the multiple threats and win.

4. Otherwise, if {player} can play on an empty square and make an immediate threat,
   consider whether there is a strong followup after {opponent}'s forced reply.

Provide your analysis and the best move. At the end, return the selected move in JSON format as follows:
```json
{{
    "selected_move": "<move>"
}}
```

{cot_examples}
"""

possible_lines = """Vertical:
a1, a2, a3
b1, b2, b3
c1, c2, c3

Horizontal:
a1, b1, c1
a2, b2, c2
a3, b3, c3

Diagonal:
a1, b2, c3
a3, b2, c1"""


def format_minimal_gemini_request(board, player):
    board_str = format_board_for_gemini(board)
    return minimal_template.format(player=player, board=board_str, possible_lines=possible_lines)


def format_cot_request(board, player, cot_template_name, few_shot_examples):
    opponent = get_opponent(player)
    board_str = format_board_for_gemini(board)
    cot_str = format_examples_for_cot(few_shot_examples)
    
    # Choose the appropriate template based on the cot_template_name
    template = cot_template_explicit if cot_template_name == 'explicit' else cot_template
    
    return template.format(
        player=player, 
        opponent=opponent, 
        board=board_str, 
        possible_lines=possible_lines, 
        cot_examples=cot_str
    )

def format_board_for_gemini(board):
    x_line_content = ', '.join([index_to_algebraic(i) for i, s in enumerate(board) if s == "X"])
    o_line_content = ', '.join([index_to_algebraic(i) for i, s in enumerate(board) if s == "O"])
    unoccupied_line_content = ', '.join([index_to_algebraic(i) for i, s in enumerate(board) if s == " "])

    return f"""Squares occupied by X: {x_line_content}
Squares occupied by O: {o_line_content}
Unoccupied squares: {unoccupied_line_content}"""


def format_examples_for_cot(few_shot_examples):
    separator = "\n-------------"
    
    if len(few_shot_examples) == 0:
        return ''
    elif len(few_shot_examples) == 1:
        return f"""Here is an example of a CoT analysis:\n{format_cot_example(few_shot_examples[0])}{separator}"""
    else:
        return f"""Here are examples of CoT analyses:\n{separator.join([format_cot_example(example) for example in few_shot_examples])}{separator}"""


def format_cot_example(example):
    board = example['board']
    player = example['player']
    cot_record = example['cot_record']
    
    return f"""Example with {player} to play:\n{format_board_for_gemini(board)}\n\nOutput:\n{cot_record}"""
