import attr_classes

alignment_index_dict = {
    "Good": 0,
    "Neutral": 1,
    "Evil": 2
}

class HeroicPower(attr_classes.Perk):
    def set_luck_functions(self, player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
        #+3 Luck if no one in your alliances has an opposite alignment
        def heroic_power_luck(player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
            luck_modify = 3
            alignment = player_info.get(player_conf_name, {}).get("role", {}).get("alignment", "Neutral")
            for alliance_name, members in alliances.items():
                if player_conf_name in members:
                    for member_name in members:
                        member = player_info.get(member_name, {})
                        member_alignment = member.get("role", {}).get("alignment", "Neutral")
                        if alignment == "Good" and member_alignment == "Evil":
                            luck_modify = 0
                            break
                        elif alignment == "Evil" and member_alignment == "Good":
                            luck_modify = 0
                            break
                        elif alignment == "Neutral" and member_alignment == "Neutral":
                            luck_modify = 0
                            break
                    if luck_modify == 0:
                        break
            luck_dict[player_conf_name] += luck_modify
            
        
        luck_calc_dict.setdefault(player_conf_name, {}).setdefault(attr_classes.LuckCalcOrder.PRE_STATUSES, []).append(heroic_power_luck)

class LeadActor(attr_classes.Perk):
    def set_luck_functions(self, player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
        #2 Luck from Goods/Evils
        def lead_actor_boosted_luck(player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
            alignment_amount[player_conf_name][alignment_index_dict["Good"]] = 2
            alignment_amount[player_conf_name][alignment_index_dict["Evil"]] = 2
        
        #+2 Luck from each pair of Good & Evil in an alliance
        def lead_actor_pair_luck(player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
            luck_modify = 0
            for alliance_name, members in alliances.items():
                if player_conf_name in members:
                    good_count = 0
                    evil_count = 0
                    for member_name in members:
                        member = player_info.get(member_name, {})
                        member_alignment = member.get("role", {}).get("alignment", "Neutral")
                        if member_alignment == "Evil":
                            evil_count += 1
                        elif member_alignment == "Good":
                            good_count += 1
                    luck_modify += min(good_count, evil_count) * 2
            luck_dict[player_conf_name] += luck_modify
        print(self)
        print(luck_calc_dict)
        luck_calc_dict.setdefault(player_conf_name, {}).setdefault(attr_classes.LuckCalcOrder.PRE_LUCK, []).append(lead_actor_boosted_luck)
        luck_calc_dict.setdefault(player_conf_name, {}).setdefault(attr_classes.LuckCalcOrder.PRE_STATUSES, []).append(lead_actor_pair_luck)
        print(luck_calc_dict)

class GasolineFumes(attr_classes.Perk):
    def set_luck_functions(self, player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
        #+1 Luck for every two players in the Doused section of the inventory
        def gasoline_fumes_luck(player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
            doused_list = player_info[player_conf_name]["inventory"].get("Doused", [])
            luck_modify = len(doused_list) // 2
            luck_dict[player_conf_name] += luck_modify
            
        
        luck_calc_dict.setdefault(player_conf_name, {}).setdefault(attr_classes.LuckCalcOrder.PRE_STATUSES, []).append(gasoline_fumes_luck)

class MotorGang(attr_classes.Perk):
    def set_luck_functions(self, player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
        #+1 Luck for every good player in an alliance with the holder
        def motor_gang_luck(player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
            boosted_players = [player_conf_name]
            for alliance, members in alliances.items():
                if player_conf_name in members:
                    for member in members:
                        if player_info[member]["role"]["alignment"] == "Good" and member not in boosted_players:
                            boosted_players.append(member)
            for player in boosted_players:
                luck_dict[player] += 1
            
        
        luck_calc_dict.setdefault(player_conf_name, {}).setdefault(attr_classes.LuckCalcOrder.PRE_STATUSES, []).append(motor_gang_luck)

class BardsCharisma(attr_classes.Perk):
    def set_luck_functions(self, player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
        #*2 Luck
        def bards_charisma_luck(player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
            luck_dict[player_conf_name] *= 2
            
        
        luck_calc_dict.setdefault(player_conf_name, {}).setdefault(attr_classes.LuckCalcOrder.POST_STATUSES, []).append(bards_charisma_luck)
    
class Loveable(attr_classes.Perk):
    def set_luck_functions(self, player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
        #2 Luck from neutrals
        def loveable_luck(player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
            alignment_amount[player_conf_name][alignment_index_dict["Neutral"]] = 2
            
        
        luck_calc_dict.setdefault(player_conf_name, {}).setdefault(attr_classes.LuckCalcOrder.PRE_LUCK, []).append(loveable_luck)

class Lonesome(attr_classes.Perk):
    def set_luck_functions(self, player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
        #+3 if not in any alliances
        def lonesome_luck(player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
            luck_modify = 3
            for alliance, members in alliances:
                if player_conf_name in members:
                    luck_modify = 0
                    break
            luck_dict[player_conf_name] += luck_modify
            
        
        luck_calc_dict.setdefault(player_conf_name, {}).setdefault(attr_classes.LuckCalcOrder.PRE_STATUSES, []).append(lonesome_luck)

class GoldenGavel(attr_classes.Perk):
    def set_luck_functions(self, player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
        #+3 if not in any alliances
        def golden_gavel_luck(player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
            luck_dict[player_conf_name] += player_info[player_conf_name]["inventory"].get("Golden Gavel", [0])[0]
            
        
        luck_calc_dict.setdefault(player_conf_name, {}).setdefault(attr_classes.LuckCalcOrder.PRE_STATUSES, []).append(golden_gavel_luck)

class EvilAura(attr_classes.Perk):
    def set_luck_functions(self, player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
        #+3 Luck if no one in your alliances has an opposite alignment
        def evil_aura_luck(player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
            luck_modify = 2
            alignment = player_info.get(player_conf_name, {}).get("role", {}).get("alignment", "Neutral")
            for alliance_name, members in alliances.items():
                if player_conf_name in members:
                    for member_name in members:
                        member = player_info.get(member_name, {})
                        member_alignment = member.get("role", {}).get("alignment", "Neutral")
                        if alignment == "Good" and member_alignment == "Evil":
                            luck_modify = 0
                            break
                        elif alignment == "Evil" and member_alignment == "Good":
                            luck_modify = 0
                            break
                        elif alignment == "Neutral" and member_alignment == "Neutral":
                            luck_modify = 0
                            break
                    if luck_modify == 0:
                        break
            luck_dict[player_conf_name] += luck_modify
            
        
        luck_calc_dict.setdefault(player_conf_name, {}).setdefault(attr_classes.LuckCalcOrder.PRE_STATUSES, []).append(evil_aura_luck)