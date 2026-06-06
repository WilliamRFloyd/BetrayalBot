import importlib
from enum import Enum
'''
Plans for how this works
Each perk will be a class in perks.py
Each perk will add appropriate functions to the luck_calc_dict that it's passed
These functions will be called in order based on the LuckCalcOrder enum
'''


class LuckCalcOrder(Enum):
    PRE_LUCK = -1 #Calculate before base luck, like setting how much luck a certain alignment gives
    LUCK_CALC = 0 #The base luck calculation
    PRE_STATUSES = 1 #Calculates after base luck but before statuses are applied
    STATUSES = 2 #Status effects that modify luck
    POST_STATUSES = 3 #Calculates after statuses are applied
    FINAL = 4 #Final things, like Freakish Nature setting luck to 0

class Perk:
    upgrade: int = 0
    @staticmethod
    def load_perk(perk_name: str, upgrade:int = 0) -> "Perk":
        perk_name = perk_name.replace(" ", "")
        try:
            module = importlib.import_module(f'perks')
            perk_class = getattr(module, perk_name)
            #print(perk_class)
            args = (upgrade,)
            #print(perk_class)
            instance = perk_class(*args)
            #print(f'Instance: {instance}')
            return instance
        except (ModuleNotFoundError, ImportError, AttributeError) as e:
            #print(f'{perk_name} has no corresponding class')
            return None
            #raise ImportError(f"Could not load perk '{perk_name}': {e}")
    
    def __init__(self, upgrade: int = 0):
        self.upgrade = upgrade

    def set_luck_functions(self, player_conf: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
        pass # To be implemented in subclasses