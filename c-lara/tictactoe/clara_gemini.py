import json
import aiohttp
import os
import asyncio
import ssl
import certifi
import logging
from .clara_classes import APICall
from .clara_utils import get_config, post_task_update_async, absolute_local_file_name

def get_gemini_api_key(config_info):
    if 'gemini_api_key' in config_info and config_info['gemini_api_key']:
        return config_info['gemini_api_key']
    return os.environ.get("GEMINI_API_KEY")

def generate_gemini_prompt(board, player):
    board_str = ''.join(board)  # Convert board list to string
    return f"Player {player} is playing Tic-Tac-Toe. Here is the current board state:\n{board_str}\nWhat is the best move?"

async def get_api_gemini_response(formatted_request, config_info=None, callback=None):
    endpoint_url = "https://api.gemini.com/v1/endpoint"  # Replace with actual endpoint
    api_key = get_gemini_api_key(config_info)
    
    if not api_key:
        raise ValueError("API key is not set in the environment variables.")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "request": formatted_request
    }

    ssl_context = ssl.create_default_context(cafile=certifi.where())

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(endpoint_url, json=payload, headers=headers, ssl=ssl_context) as response:
                response_json = await response.json()
                response_data = {
                    'response': response_json,
                    'status_code': response.status
                }
                if callback:
                    await callback(response_data)
                return response_data
        except aiohttp.ClientError as e:
            raise Exception(f"Network error while calling Gemini API: {e}")
        except aiohttp.ContentTypeError as e:
            raise Exception(f"Unexpected content type in Gemini API response: {e}")
        except Exception as e:
            raise Exception(f"Error while calling Gemini API: {e}")

async def request_gemini_move_async(board, player):
    url = "https://api.gemini.com/v1/ask"  # Replace with actual endpoint
    config_info = get_config()  # Load configuration
    headers = {
        "Authorization": f"Bearer {get_gemini_api_key(config_info)}",
        "Content-Type": "application/json"
    }
    prompt = generate_gemini_prompt(board, player)

    data = {
        "prompt": prompt,
        "max_tokens": 10,
        "temperature": 0.5
    }

    try:
        response_data = await get_api_gemini_response(data, config_info)
        move = parse_gemini_response(response_data['response'])
    except Exception as e:
        logging.error(f"Error requesting Gemini move: {e}")
        move = "a1"  # Fallback move

    return {
        "selected_move": move,
        "api_calls": [APICall("gemini", url, prompt)],
        "prompt": prompt
    }

def parse_gemini_response(response_json):
    # Implement this function based on the Gemini API response format
    return response_json.get('selected_move', 'a1')
