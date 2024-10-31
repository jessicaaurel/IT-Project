import requests

def get_gemini_api_key():
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("API key for Gemini not found. Please set the 'GEMINI_API_KEY' environment variable.")
    return api_key

async def request_gemini_move(board, player):
    """Sends the Tic-Tac-Toe board to Gemini and gets the move recommendation."""
    api_url = 'https://api.gemini.com/move'
    api_key = get_gemini_api_key()
    headers = {'Authorization': f'Bearer {api_key}'}  # Replace YOUR_API_KEY with your actual key
    payload = {
        'board': board,
        'player': player
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()  # This will raise an exception for HTTP error responses
        return response.json()['move']
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return None

def request_minimal_gemini_move_async(board, player):
    """Asynchronous wrapper for the Gemini move request."""
    return asyncio.run(request_gemini_move(board, player))
