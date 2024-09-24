import os
import requests

# Function to get the Claude API key from environment variables
def get_claude_api_key():
    api_key = os.environ.get('CLAUDE_API_KEY')
    if not api_key:
        raise ValueError("API key for Claude not found. Please set the 'CLAUDE_API_KEY' environment variable.")
    return api_key

# Function to send a request to Claude's API
async def get_api_claude_response(prompt, config_info=None, callback=None):
    try:
        api_key = get_claude_api_key()  # Get the API key
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            "prompt": prompt,
            "model": "claude-v1"  # Assuming this is the model you're using
        }

        await post_task_update_async(callback, "--- Calling Claude API ---")

        # Replace the mocked response with an actual API request
        response = requests.post("https://claude-api-endpoint.com/v1/complete", json=data, headers=headers)
        response.raise_for_status()  # Ensure the request was successful

        response_data = response.json()
        selected_move = response_data.get("selected_move", "unknown")
        cost = response_data.get("cost", 0.0)

        # Return the actual response data
        return {
            "selected_move": selected_move,
            "cost": cost
        }

    except Exception as e:
        await post_task_update_async(callback, f"Claude request failed: {str(e)}")
        raise e
