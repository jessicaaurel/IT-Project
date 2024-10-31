import os
import requests

# Function to get the API key from environment variables
def get_llama_api_key():
    api_key = os.environ.get('LLAMA_API_KEY')
    if not api_key:
        raise ValueError("API key for LLaMA not found. Please set the 'LLAMA_API_KEY' environment variable.")
    return api_key

# Function to send the request to LLaMA
async def get_api_llama_response(formatted_request, callback=None):
    try:
        api_key = get_llama_api_key()  # Get the API key
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            "prompt": formatted_request,
            "model": "llama-v2"  # Assuming this is the model you're using
        }
        
        response = requests.post("https://llama-api-endpoint.com/v1/complete", json=data, headers=headers)
        response.raise_for_status()  # Ensure the request was successful

        llama_response = response.json()
        return llama_response

    except Exception as e:
        if callback:
            await post_task_update_async(callback, f"LLaMA request failed: {str(e)}")
        raise e
