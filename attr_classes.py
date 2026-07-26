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

class PlayerStatus(Enum):
    ALIVE = 0
    DEAD = 1
    TRUE_DEAD = 2
    NULL = 3

perks_to_sections: dict[str: [str, str]] = {
    "Golden Gavel": ["GG", "number"]
}

class Saveable:
    def save_data(self) -> dict:
        pass

    @staticmethod
    def load_data(data: dict) -> "Saveable":
        pass

class Perk(Saveable):
    name: str = ""
    upgrade: int = 0
    owner: "Player" = None
    @staticmethod
    def load_perk(perk_name: str, upgrade: int = 0) -> "Perk":
        perk_class_name = perk_name.replace(" ", "")
        try:
            module = importlib.import_module(f'perks')
            perk_class = getattr(module, perk_class_name)
            #print(perk_class)
            args = (perk_name, upgrade)
            #print(perk_class)
            instance = perk_class(*args)
            #print(f'Instance: {instance}')
            return instance
        except (ModuleNotFoundError, ImportError, AttributeError) as e:
            #print(f'{perk_name} has no corresponding class')
            return Perk(perk_name, upgrade)
            #raise ImportError(f"Could not load perk '{perk_name}': {e}")
    
    def __init__(self, name, upgrade = 0):
        self.name = name
        self.upgrade = upgrade

    def set_luck_functions(self, luck_calc_dict: dict["Player", dict]) -> None:
        pass # To be implemented in subclasses

    def save_data(self):
        return {"name": self.name, "upgrade": self.upgrade}

class Ability(Saveable):
    name: str = ""
    charges: int = 0
    upgrade: int = 0

    def __init__(self, name, charges = 1, upgrade = 0, from_dict = None):
        self.name = name
        self.charges = charges
        self.upgrade = upgrade

    def save_data(self):
        return {"charges": self.charges, "upgrade": self.upgrade}

class InventorySection(Saveable):
    name: str = ""
    category: str = "list"
    display_priority: int = 99
    alias: list[str] = []
    contents = None

    def __init__(self, name, category = "list", priority = 99, alias = [], from_dict = None):
        self.name = name
        self.contents = None
        self.alias = []
        if from_dict is None:
            self.category = category.lower()
            self.priority = priority
            self.alias = [name.lower()] + alias
            match self.category:
                case "list":
                    self.contents = []
                case "number":
                    self.contents = 0
                case "decimal":
                    self.contents = 0.0
                case "dict":
                    self.contents = {}
                case _:
                    self.category = "list"
                    self.contents = []
        else:
            self.category = from_dict.get("category", "list")
            self.priority = from_dict.get("priority", 99)
            self.alias = from_dict.get("alias", [name.lower()])
            self.contents = from_dict.get("contents", [])

    def __str__(self):
        display_string = f"{self.name}: "
        match self.category:
            case "list":
                display_string += ", ".join(self.contents)
            case "dict":
                display_string += ", ".join([f"{item} [{amount}]" for item, amount in self.contents.items()])
            case _:
                display_string += f"{self.contents}"
        return display_string

    def process_command(self, command: str, arguments: list) -> bool:
        match command:
            case "add":
                match self.category:
                    case "list":
                        for argument in arguments:
                            self.contents.append(argument)
                    case "dict":
                        for i in range(len(arguments)):
                            argument = arguments[i]
                            if argument.isdigit():
                                continue
                            amount = 1
                            if i < len(arguments) - 1 and arguments[i+1].isdigit():
                                amount = int(arguments[i+1])
                            self.contents[argument] = self.contents.get(argument, 0) + amount
                    case "number":
                        try: 
                            self.contents += int(arguments[0])
                        except ValueError:
                            return False
                    case "decimal":
                        try: 
                            self.contents += float(arguments[0])
                        except ValueError:
                            return False

            case "remove":
                match self.category:
                    case "list":
                        for argument in arguments:
                            for item in self.contents:
                                if item.lower() == argument.lower():
                                    self.contents.remove(item)
                                    break
                    case "dict":
                        for argument in arguments:
                            for item in self.contents.keys():
                                if item.lower() == argument.lower():
                                    self.contents.pop(item)
                                    break
                    case "number":
                        try: 
                            self.contents -= int(arguments[0])
                        except ValueError:
                            return False
                    case "decimal":
                        try: 
                            self.contents -= float(arguments[0])
                        except ValueError:
                            return False

            case "clear":
                match self.category:
                    case "list" | "dict":
                        self.contents.clear()
                    case "number":
                        self.contents = 0
                    case "decimal":
                        self.contents = 0.0

            case "set":
                match self.category:
                    case "list":
                        self.contents.clear()
                        for argument in arguments:
                            self.contents.append(argument)
                    case "dict":
                        self.contents.clear()
                        for i in range(len(arguments)):
                            argument = arguments[i]
                            if argument.isdigit():
                                continue
                            amount = 1
                            if i < len(arguments) - 1 and arguments[i+1].isdigit():
                                amount = int(arguments[i+1])
                            self.contents[argument] = amount
                    case "number":
                        try: 
                            self.contents = int(arguments[0])
                        except ValueError:
                            return False
                    case "decimal":
                        try: 
                            self.contents = float(arguments[0])
                        except ValueError:
                            return False

        return True

    def save_data(self) -> dict:
        return {"category": self.category, "contents": self.contents, "priority": self.priority, "alias": self.alias}

    @staticmethod
    def load_data(name, data):
        return InventorySection(name, from_dict = data)
    

class Inventory(Saveable):
    sections: list[InventorySection] = []
    message_id: int = 0

    def __init__(self, from_dict = None):
        self.sections = []
        if from_dict is None:
            default_sections = {
                "Coins": ["number", 0, ["coin"]],
                "Bonus": ["decimal", 1, []],
                "Inventory": ["list", 2, ["item", "items"]],
                "AA": ["dict", 3, ["aas"]],
                "Statuses": ["list", 4, ["status"]],
                "Effects": ["list", 5, ["effect"]],
                "Immunities": ["list", 6, ["immunity"]],
                "Vote(s)": ["list", 100, ["vote"]]
            }

            for section_name, section_data in default_sections.items():
                self.sections.append(InventorySection(section_name, section_data[0], section_data[1], section_data[2]))

        else:
            for section_name, section_data in from_dict.items():
                if section_name == "message_id":
                    continue
                self.sections.append(InventorySection.load_data(section_name, section_data))
            self.message_id = from_dict["message_id"]

    def __str__(self):
        self.sections.sort(key=lambda sec: sec.priority)
        display_string = "```\n"
        coin_section = self.get_section("Coins")
        bonus_section = self.get_section("Bonus")
        if coin_section is not None and bonus_section is not None:
            display_string += f"{coin_section} [{bonus_section.contents}%]\n"
        for section in self.sections:
            if section.name in ("Coins", "Bonus"):
                continue
            display_string += f"{str(section)}\n"
        display_string += "```"
        return display_string

    def get_section(self, name) -> InventorySection:
        return next((s for s in self.sections if name.lower() in s.alias), None)

    def has_section(self, name):
        return self.get_section(name) is not None

    def process_command(self, target: str, arguments: list) -> bool:
        reserved_targets = ("create", "send", "forget", "delete", "section", "message_id") #Handled by bot code
        target = target.lower()
        if len(arguments) < 2:
            return False
        command = arguments[0].lower()

        if target in ("section", "sections"):
            match command:
                case "add":
                    name = arguments[1]
                    category = "list"
                    if len(arguments) >= 3:
                        category = arguments[2]
                    if self.get_section(name) is not None or name.lower() in reserved_targets:
                        return False
                    self.sections.append(InventorySection(name, category))

                case "remove":
                    name = arguments[1]
                    section = self.get_section(name)
                    if self.get_section(name) is None:
                        return False
                    self.sections.remove(section)

        else:
            section = self.get_section(target)
            if section is None:
                return False

            return section.process_command(command, arguments[1:])
        
        return True

    def save_data(self):
        data = {"message_id": self.message_id}
        for section in self.sections:
            data[section.name] = section.save_data()
        return data

    @staticmethod
    def load_data(data):
        return Inventory(data)


class PlayerRole(Saveable):
    role_name: str = ""
    alignment: str = ""
    abilities: list[Ability] = []
    perks: list[Perk] = []
    message_ids: list[int] = []
    owner: "Player" = None

    def __init__(self, role_name: str = "", role_info: dict = None, owner: "Player" = None, from_dict = None):
        self.abilities = []
        self.perks = []
        self.message_ids = []
        self.owner = owner
        if from_dict is None:
            self.role_name = role_name
            self.alignment = role_info["alignment"]

            for ability, charges in role_info["abilities"].items():
                self.abilities.append(Ability(ability, charges))

            for perk in role_info["perks"]:
                self.add_perk(perk)

        else:
            self.role_name = from_dict["name"]
            self.alignment = from_dict["alignment"]
            for ability, ability_data in from_dict["abilities"].items():
                self.abilities.append(Ability(ability, ability_data["charges"], ability_data["upgrade"]))
            for perk_data in from_dict["perks"]:
                perk = Perk.load_perk(perk_data["name"], perk_data["upgrade"])
                perk.owner = self.owner
                self.perks.append(perk)
            for message_id in from_dict["messageIds"]:
                self.message_ids.append(message_id)

    def get_ability(self, ability_name: str):
        return next((a for a in self.abilities if ability_name == a.name), None)

    def remove_ability(self, ability_name: str):
        ability = self.get_ability(ability_name)
        if ability is not None:
            self.abilities.remove(ability)
            del ability

    def has_ability(self, ability_name: str):
        return self.get_ability(ability_name) is not None

    def add_ability(self, ability_name: str, charges: int = 1):
        ability = self.get_ability(ability_name)
        if ability is None:
            self.abilities.append(Ability(ability_name, charges))
        else:
            if ability.charges == -1: #-1 stands for infinite charges
                return
            if ability.charges + charges >= 0:
                ability.charges += charges
            else:
                ability.charges = 0

    def get_perk(self, perk_name: str):
        return next((p for p in self.perks if perk_name == p.name), None)

    def has_perk(self, perk_name: str):
        return self.get_perk(perk_name) is not None

    def add_perk(self, perk_name: str):
        perk = Perk.load_perk(perk_name)
        perk.owner = self.owner
        self.perks.append(perk)
        if self.owner.inventory is not None and perk_name in perks_to_sections:
            section_data = perks_to_sections[perk_name]
            self.owner.inventory.process_command("section", ["add", section_data[0], section_data[1]])

    def remove_perk(self, perk_name: str):
        perk = self.get_perk(perk_name)
        if perk is not None:
            self.perks.remove(perk)
            del perk

    def save_data(self):
        data = {"name": self.role_name, "alignment": self.alignment, "abilities": {}, "perks": [], "messageIds": []}

        for ability in self.abilities:
            data["abilities"][ability.name] = ability.save_data()

        for perk in self.perks:
            data["perks"].append(perk.save_data())

        for messageId in self.message_ids:
            data["messageIds"].append(messageId)

        return data

    @staticmethod
    def load_data(owner, data):
        return PlayerRole(owner=owner, from_dict=data)

class Player(Saveable):
    inventory: Inventory = None
    role: PlayerRole = None
    conf_name: str = ""
    channel_id: int = 0
    luck: int = 0
    calced_coins: int = 0
    calced_items: list[str] = []
    calced_aas: list[str] = []
    status: PlayerStatus = PlayerStatus.ALIVE

    def __init__(self, conf_name, channel_id = 0, from_dict = None):
        self.conf_name = conf_name
        self.calced_coins = 0
        self.calced_items = []
        self.calced_aas = []
        if from_dict is None:
            self.channel_id = channel_id
            self.status = PlayerStatus.ALIVE

        else:
            self.channel_id = from_dict["channelId"]
            self.luck = from_dict["luck"]
            self.calced_coins = from_dict["calcedCoins"]
            self.calced_items = from_dict["calcedItems"]
            self.calced_aas = from_dict["calcedAas"]
            self.status = PlayerStatus[from_dict["status"]]
            if "role" in from_dict.keys():
                self.role = PlayerRole.load_data(self, from_dict["role"])
            if "inventory" in from_dict.keys():
                self.inventory = Inventory.load_data(from_dict["inventory"])

    def add_role(self, role_name: str, role_info: dict) -> PlayerRole:
        if self.role is None:
            self.role = PlayerRole(role_name, role_info, self)
        return self.role

    def remove_role(self):
        if self.role is not None:
            del self.role

    def has_role(self):
        return self.role is not None

    def add_inventory(self) -> Inventory:
        if self.inventory is None:
            self.inventory = Inventory()
            if self.role is not None:
                for perk in self.role.perks:
                    if perk.name in perks_to_sections:
                        section_data = perks_to_sections[perk.name]
                        self.inventory.process_command("section", ["add", section_data[0], section_data[1]])

        return self.inventory

    def remove_inventory(self):
        if self.inventory is not None:
            del self.inventory

    def can_gain(self) -> bool: #Returns true if the player can get coin drop/item rain/etc
        if self.status == PlayerStatus.ALIVE:
            return True
        if self.has_perk("Secret Spirit"):
            return True
        return False

    def in_play(self) -> bool:
        return self.status != PlayerStatus.NULL

    def has_perk(self, perk_name: str) -> bool:
        if self.role is None:
            return False
        return self.role.has_perk(perk_name)

    def save_data(self):
        data = {"channelId": self.channel_id, "luck": self.luck, "calcedCoins": self.calced_coins, "calcedItems": self.calced_items, "calcedAas": self.calced_aas, "status": self.status.name}
        if self.role is not None:
            data["role"] = self.role.save_data()

        if self.inventory is not None:
            data["inventory"] = self.inventory.save_data()

        return data

    @staticmethod
    def load_data(conf_name, data):
        return Player(conf_name, from_dict=data)

        

class Game(Saveable):
    guild_name: str = ""
    guild_id: int = 0
    conf_category_name: str = ""
    dead_conf_category_name: str = ""
    alliance_category_name: str = ""
    conf_links: dict[int: str] = {}
    players: list[Player] = []

    def __init__(self, guild_id: int, guild_name = "", from_dict = None):
        self.guild_id = guild_id
        self.conf_links = {}
        self.players = []
        if from_dict is None:
            self.guild_name = guild_name
            self.conf_category_name = "Confessionals"
            self.dead_conf_category_name = "Dead Confessionals"
            self.alliance_category_name = "Alliances"

        else:
            self.guild_name = from_dict["guildName"]
            self.conf_category_name = from_dict["confessionalCategory"]
            self.dead_conf_category_name = from_dict["deadConfessionalCategory"]
            self.alliance_category_name = from_dict["allianceCategory"]

            for user_id, channel_name in from_dict["confLinks"].items():
                self.conf_links[int(user_id)] = channel_name

            for conf_name, player_data in from_dict["players"].items():
                self.players.append(Player.load_data(conf_name, player_data))

    def add_player(self, conf_name: str, channel_id: int):
        self.players.append(Player(conf_name, channel_id))

    def get_player(self, conf_name: str):
        return next((p for p in self.players if conf_name == p.conf_name), None)

    def has_player(self, conf_name: str):
        return self.get_player(conf_name) is not None

    def get_player_from_link(self, user_id: int) -> Player | None:
        return self.get_player(self.conf_links.get(user_id, None))

    def add_link(self, user_id, channel_name):
        self.conf_links[user_id] = channel_name

    def remove_link(self, user_id) -> bool:
        if user_id in self.conf_links.keys():
            self.conf_links.pop(user_id)
            return True
        return False

    def remove_links(self):
        self.conf_links = {}

    def links_empty(self) -> bool:
        return self.conf_links == {}

    def save_data(self):
        data = {"guildName": self.guild_name, "confessionalCategory": self.conf_category_name, 
                "deadConfessionalCategory": self.dead_conf_category_name,
                "allianceCategory": self.alliance_category_name, "confLinks": {}, "players": {}}

        for user_id, channel_name in self.conf_links.items():
            data["confLinks"][str(user_id)] = channel_name

        for player in self.players:
            data["players"][player.conf_name] = player.save_data()

        return data

    @staticmethod
    def load_data(guild_id: int, data):
        return Game(guild_id, from_dict=data)