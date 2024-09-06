import os

os.chdir('/Users/macbookpro/Documents/GitHub/IT-Project/c-lara')  # cd to the directory above the one where you've put the Tic-Tac-Toe dir

import tictactoe.tictactoe_game # Import the file with the game function

import asyncio # Import asyncio to be able to call the async function

asyncio.run(tictactoe.tictactoe_game.play_game_async('human_player', 'cot_player_without_few_shot', 'dummy_experiment', 0)) # Start a game between yourself and the minimal GPT-4 player