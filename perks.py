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
            in_alliance = False
            alignment = player_info.get(player_conf_name, {}).get("role", {}).get("alignment", "Neutral")
            for alliance_name, members in alliances.items():
                if player_conf_name in members:
                    in_alliance = True
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
            if not in_alliance:
                luck_modify = 0
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
            for alliance, members in alliances.items():
                if player_conf_name in members:
                    for member in members:
                        if player_info[member]["role"]["alignment"] == "Good":
                            luck_dict[member] += 1
            
        
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
            for alliance, members in alliances.items():
                if player_conf_name in members:
                    luck_modify = 0
                    break
            luck_dict[player_conf_name] += luck_modify
            
        
        luck_calc_dict.setdefault(player_conf_name, {}).setdefault(attr_classes.LuckCalcOrder.PRE_STATUSES, []).append(lonesome_luck)

class GoldenGavel(attr_classes.Perk):
    def set_luck_functions(self, player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
        def golden_gavel_luck(player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
            try:
                luck_dict[player_conf_name] += int(player_info[player_conf_name]["inventory"].get("GG", [0])[0])
            except:
                pass
            
        
        luck_calc_dict.setdefault(player_conf_name, {}).setdefault(attr_classes.LuckCalcOrder.PRE_STATUSES, []).append(golden_gavel_luck)

class Tradesman(attr_classes.Perk):
    def set_luck_functions(self, player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
        def tradesman_luck(player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
            try:
                luck_dict[player_conf_name] += int(player_info[player_conf_name]["inventory"].get("Tradesman", [0])[0])
            except:
                pass
            
        
        luck_calc_dict.setdefault(player_conf_name, {}).setdefault(attr_classes.LuckCalcOrder.PRE_STATUSES, []).append(tradesman_luck)

class EvilAura(attr_classes.Perk):
    def set_luck_functions(self, player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
        #+2 Luck if no one in your alliances has an opposite alignment
        def evil_aura_luck(player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
            luck_modify = 2
            in_alliance = False
            alignment = player_info.get(player_conf_name, {}).get("role", {}).get("alignment", "Neutral")
            for alliance_name, members in alliances.items():
                if player_conf_name in members:
                    in_alliance = True
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
            if not in_alliance:
                luck_modify = 0
            luck_dict[player_conf_name] += luck_modify
            
        
        luck_calc_dict.setdefault(player_conf_name, {}).setdefault(attr_classes.LuckCalcOrder.PRE_STATUSES, []).append(evil_aura_luck)

class FreakishNature(attr_classes.Perk):
    def set_luck_functions(self, player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
        #Sets luck of all allies of different alignments to 0 and adds their luck to the holder. Also temporarily undoes lucky/unlucky on the holder for the calculation, then reapplies it after.
        def freakish_nature_luck(player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
            alignment = player_info.get(player_conf_name, {}).get("role", {}).get("alignment", "Neutral")
            statuses = [x.lower() for x in player_info.get(player_conf_name, {}).get("inventory", {}).get("statuses", [])]

            #Temporarily remove lucky/unlucky for the holder
            if "lucky" in statuses:
                luck_dict[player_conf_name] = luck_dict[player_conf_name] // 2
            elif "unlucky" in statuses:
                luck_dict[player_conf_name] = luck_dict[player_conf_name] * 2

            for alliance_name, members in alliances.items():
                if player_conf_name in members:
                    for member_name in members:
                        if member_name == player_conf_name:
                            continue
                        member_alignment = player_info.get(member_name, {}).get("role", {}).get("alignment", "Neutral")
                        if member_alignment != alignment:
                            luck_dict[player_conf_name] += luck_dict[member_name]
                            luck_dict[member_name] = 0

            #Reapply lucky/unlucky for the holder
            if "lucky" in statuses:
                luck_dict[player_conf_name] = luck_dict[player_conf_name] * 2
            elif "unlucky" in statuses:
                luck_dict[player_conf_name] = luck_dict[player_conf_name] // 2

        luck_calc_dict.setdefault(player_conf_name, {}).setdefault(attr_classes.LuckCalcOrder.FINAL, []).append(freakish_nature_luck)