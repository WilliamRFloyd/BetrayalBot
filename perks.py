import attr_classes

alignment_index_dict = {
    "Good": 0,
    "Neutral": 1,
    "Evil": 2
}

class HeroicPower(attr_classes.Perk):
    def set_luck_functions(self, luck_calc_dict: dict) -> None:
        #+3 Luck if no one in your alliances has an opposite alignment
        def heroic_power_luck(player: attr_classes.Player, alliances: dict[str, list[attr_classes.Player]], luck_calc_dict: dict, alignment_amount: dict) -> None:
            luck_modify = 3
            in_alliance = False
            alignment = player.get_alignment()
            for alliance_name, members in alliances.items():
                if player in members:
                    in_alliance = True
                    for member in members:
                        member_alignment = member.get_alignment()
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
            player.luck += luck_modify
            
        
        luck_calc_dict.setdefault(self.owner, {}).setdefault(attr_classes.LuckCalcOrder.PRE_STATUSES, []).append(heroic_power_luck)

class LeadActor(attr_classes.Perk):
    def set_luck_functions(self, luck_calc_dict: dict) -> None:
        #2 Luck from Goods/Evils
        def lead_actor_boosted_luck(player: attr_classes.Player, alliances: dict[str, list[attr_classes.Player]], luck_calc_dict: dict, alignment_amount: dict) -> None:
            alignment_amount[player][alignment_index_dict["Good"]] = 2
            alignment_amount[player][alignment_index_dict["Evil"]] = 2
        
        #+2 Luck from each pair of Good & Evil in an alliance
        def lead_actor_pair_luck(player: attr_classes.Player, alliances: dict[str, list[attr_classes.Player]], luck_calc_dict: dict, alignment_amount: dict) -> None:
            luck_modify = 0
            for alliance_name, members in alliances.items():
                if player in members:
                    good_count = 0
                    evil_count = 0
                    for member in members:
                        member_alignment = member.get_alignment()
                        if member_alignment == "Evil":
                            evil_count += 1
                        elif member_alignment == "Good":
                            good_count += 1
                    luck_modify += min(good_count, evil_count) * 2
            player.luck += luck_modify

        luck_calc_dict.setdefault(self.owner, {}).setdefault(attr_classes.LuckCalcOrder.PRE_LUCK, []).append(lead_actor_boosted_luck)
        luck_calc_dict.setdefault(self.owner, {}).setdefault(attr_classes.LuckCalcOrder.PRE_STATUSES, []).append(lead_actor_pair_luck)

class GasolineFumes(attr_classes.Perk):
    def set_luck_functions(self, luck_calc_dict: dict) -> None:
        #+1 Luck for every two players in the Doused section of the inventory
        def gasoline_fumes_luck(player: attr_classes.Player, alliances: dict[str, list[attr_classes.Player]], luck_calc_dict: dict, alignment_amount: dict) -> None:
            if player.inventory is None:
                return
            doused_section = player.inventory.get_section("Doused")
            if doused_section is None:
                return
            doused_list = doused_section.contents
            luck_modify = len(doused_list) // 2
            player.luck += luck_modify
        
        luck_calc_dict.setdefault(self.owner).setdefault(attr_classes.LuckCalcOrder.PRE_STATUSES, []).append(gasoline_fumes_luck)

class MotorGang(attr_classes.Perk):
    def set_luck_functions(self, luck_calc_dict: dict) -> None:
        #+1 Luck for every good player in an alliance with the holder
        def motor_gang_luck(player: attr_classes.Player, alliances: dict[str, list[attr_classes.Player]], luck_calc_dict: dict, alignment_amount: dict) -> None:
            for alliance, members in alliances.items():
                if player in members:
                    for member in members:
                        if member.get_alignment() == "Good":
                            member.luck += 1
            
        
        luck_calc_dict.setdefault(self.owner).setdefault(attr_classes.LuckCalcOrder.PRE_STATUSES, []).append(motor_gang_luck)

class BardsCharisma(attr_classes.Perk):
    def set_luck_functions(self, luck_calc_dict: dict) -> None:
        #*2 Luck
        def bards_charisma_luck(player: attr_classes.Player, alliances: dict[str, list[attr_classes.Player]], luck_calc_dict: dict, alignment_amount: dict) -> None:
            player.luck *= 2
            
        
        luck_calc_dict.setdefault(self.owner).setdefault(attr_classes.LuckCalcOrder.POST_STATUSES, []).append(bards_charisma_luck)
    
class Loveable(attr_classes.Perk):
    def set_luck_functions(self, luck_calc_dict: dict) -> None:
        #2 Luck from neutrals
        def loveable_luck(player: attr_classes.Player, alliances: dict[str, list[attr_classes.Player]], luck_calc_dict: dict, alignment_amount: dict) -> None:
            alignment_amount[player][alignment_index_dict["Neutral"]] = 2
            
        
        luck_calc_dict.setdefault(self.owner).setdefault(attr_classes.LuckCalcOrder.PRE_LUCK, []).append(loveable_luck)

class Lonesome(attr_classes.Perk):
    def set_luck_functions(self, luck_calc_dict: dict) -> None:
        #+3 if not in any alliances
        def lonesome_luck(player: attr_classes.Player, alliances: dict[str, list[attr_classes.Player]], luck_calc_dict: dict, alignment_amount: dict) -> None:
            luck_modify = 3
            for alliance, members in alliances.items():
                if player in members:
                    luck_modify = 0
                    break
            player.luck += luck_modify
            
        
        luck_calc_dict.setdefault(self.owner).setdefault(attr_classes.LuckCalcOrder.PRE_STATUSES, []).append(lonesome_luck)

class GoldenGavel(attr_classes.Perk):
    def set_luck_functions(self, luck_calc_dict: dict) -> None:
        def golden_gavel_luck(player: attr_classes.Player, alliances: dict[str, list[attr_classes.Player]], luck_calc_dict: dict, alignment_amount: dict) -> None:
            if player.inventory is None:
                return
            gavel_section = player.inventory.get_section("GG")
            if gavel_section is None:
                return
            player.luck += gavel_section.contents
        
        luck_calc_dict.setdefault(self.owner).setdefault(attr_classes.LuckCalcOrder.PRE_STATUSES, []).append(golden_gavel_luck)

class Tradesman(attr_classes.Perk):
    def set_luck_functions(self, luck_calc_dict: dict) -> None:
        def tradesman_luck(player: attr_classes.Player, alliances: dict[str, list[attr_classes.Player]], luck_calc_dict: dict, alignment_amount: dict) -> None:
            if player.inventory is None:
                return
            tradesman_section = player.inventory.get_section("Tradesman")
            if tradesman_section is None:
                return
            player.luck += tradesman_section.contents
        
        luck_calc_dict.setdefault(self.owner).setdefault(attr_classes.LuckCalcOrder.PRE_STATUSES, []).append(tradesman_luck)

class Corruption(attr_classes.Perk):
    def set_luck_functions(self, luck_calc_dict: dict) -> None:
        def corruption_luck(player: attr_classes.Player, alliances: dict[str, list[attr_classes.Player]], luck_calc_dict: dict, alignment_amount: dict) -> None:
            if player.inventory is None:
                return
            corruption_section = player.inventory.get_section("Corruption")
            if corruption_section is None:
                return
            player.luck += corruption_section.contents

        luck_calc_dict.setdefault(self.owner).setdefault(attr_classes.LuckCalcOrder.PRE_STATUSES, []).append(corruption_luck)

class EvilAura(attr_classes.Perk):
    def set_luck_functions(self, luck_calc_dict: dict) -> None:
        #+2 Luck if no one in your alliances has an opposite alignment
        def evil_aura_luck(player: attr_classes.Player, alliances: dict[str, list[attr_classes.Player]], luck_calc_dict: dict, alignment_amount: dict) -> None:
            luck_modify = 2
            in_alliance = False
            alignment = player.get_alignment()
            for alliance_name, members in alliances.items():
                if player in members:
                    in_alliance = True
                    for member in members:
                        member_alignment = member.get_alignment()
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
            player.luck += luck_modify
            
        luck_calc_dict.setdefault(self.owner).setdefault(attr_classes.LuckCalcOrder.PRE_STATUSES, []).append(evil_aura_luck)

class FreakishNature(attr_classes.Perk):
    def set_luck_functions(self, luck_calc_dict: dict) -> None:
        #Sets luck of all allies of different alignments to 0 and adds their luck to the holder. Also temporarily undoes lucky/unlucky on the holder for the calculation, then reapplies it after.
        def freakish_nature_luck(player: attr_classes.Player, alliances: dict[str, list[attr_classes.Player]], luck_calc_dict: dict, alignment_amount: dict) -> None:
            alignment = player.get_alignment()
            if player.inventory is None:
                statuses = []
            else:
                statuses = [x.lower() for x in player.inventory.get_section("status").contents]

            #Temporarily remove lucky/unlucky for the holder
            if "lucky" in statuses:
                player.luck = player.luck // 2
            elif "unlucky" in statuses:
                player.luck *= 2

            for alliance_name, members in alliances.items():
                if player in members:
                    for member in members:
                        if member is player:
                            continue
                        member_alignment = member.get_alignment()
                        if member_alignment != alignment:
                            player.luck += member.luck
                            member.luck = 0

            #Reapply lucky/unlucky for the holder
            if "lucky" in statuses:
                player.luck *= 2
            elif "unlucky" in statuses:
                player.luck = player.luck // 2

        luck_calc_dict.setdefault(self.owner).setdefault(attr_classes.LuckCalcOrder.FINAL, []).append(freakish_nature_luck)

class BankLoans(attr_classes.Perk):
    def set_coin_functions(self, coin_calc_dict) -> None:

        def bank_loans_coin(player: attr_classes.Player, alliances: dict[str, list[attr_classes.Player]]) -> None:
            loans = player.inventory.get_section("Loans")
            if loans is None:
                return
            if "on" not in [x.lower() for x in loans.contents]:
                return
            effected_players = []
            for alliance_name, members in alliances.items():
                if player in members:
                    for member in members:
                        if member not in effected_players:
                            effected_players.append(member)
            for effected_player in effected_players:
                effected_player.calced_coins = int(effected_player.calced_coins * 1.2)
        
        coin_calc_dict.setdefault(self.owner).setdefault(attr_classes.CoinCalcOrder.POST_STATUSES, []).append(bank_loans_coin)

class Greedy(attr_classes.Perk):
    def set_coin_functions(self, coin_calc_dict) -> None:

        def greedy_coin(player: attr_classes.Player, alliances: dict[str, list[attr_classes.Player]]) -> None:
            loans = player.inventory.get_section("Greedy")
            if loans is None:
                return
            if "on" not in [x.lower() for x in loans.contents]:
                return
            effected_players = []
            player_alignment = player.get_alignment()
            for alliance_name, members in alliances.items():
                if player in members:
                    for member in members:
                        if member not in effected_players:
                            effected_players.append(member)
            for effected_player in effected_players:
                if effected_player.get_alignment() != player_alignment:
                    player.calced_coins += effected_player.calced_coins
                    effected_player.calced_coins = 0
        
        coin_calc_dict.setdefault(self.owner).setdefault(attr_classes.CoinCalcOrder.FINAL, []).append(greedy_coin)

