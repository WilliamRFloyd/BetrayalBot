from attr_classes import Game
import os

code_path = os.path.dirname(os.path.realpath(__file__))

#Filename constants
INFO_FILE = code_path + "/data/info.json"
GAME_FILE = code_path + "/data/inventoryInfo.json"

class Data:
    game_data: Game = None