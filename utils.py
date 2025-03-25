class Spec:
    """
    A class representing a WoW spec, including icon, role, heroism, and battle res flags.
    """
    def __init__(self, icon: str):
        # Handle special PUG cases
        if icon in ["Tank PUG", "Healer PUG", "DPS PUG"]:
            self.name = icon
            self.hero = False  # PUGs do not provide Hero
            self.br = False  # PUGs do not provide Battle Res
            self.role = icon.split()[0].lower()  # Extracts role from "Tank PUG" → "tank"
            self.icon = "<:pug:1302700000000000000>"  # Placeholder PUG icon
        else:
            self.name = getspec_name(icon)
            self.hero = getspec_hero(icon)
            self.br = getspec_br(icon)
            self.role = getspec_role(icon)
            self.icon = icon

    def get_icon(self):
        """
        Returns the icon string used for display.
        """
        return self.icon

def getspec_name(icon: str) -> str:
    """Parses the icon string to return the spec's readable name."""
    temp = icon.split(':')[1]
    temp1 = temp.split('_')
    return temp1[1] + " " + temp1[0]
def getspec_hero(icon: str) -> bool:
    """Returns True if the spec provides Heroism, False otherwise."""
    if hero_list.count(icon) == 1:
        return True
    else:
        return False
def getspec_br(icon: str) -> bool:
    """Returns True if the spec provides Battle Res, False otherwise."""
    if br_list.count(icon) == 1:
        return True
    else:
        return False
def getspec_role(icon: str) -> str:
    """Determines and returns the role ('tank', 'heal', or 'dps') of the spec."""
    if tank_list.count(icon) == 1:
        return 'tank'
    elif heal_list.count(icon) == 1:
        return 'heal'
    else:
        return 'dps'

def get_spec(id: int):
    """Returns a Spec object based on a numeric ID (1-39)."""
    spec_dict = {
        1: "<:Hunter_Marksmanship:1302704567485726730>",
        2: "<:Hunter_Beastmastery:1302704152488448020>",
        3: "<:Hunter_Survival:1302704155965788190>",
        4: "<:Deathknight_Blood:1302704136575258818>",
        5: "<:Deathknight_Frost:1302704137888338053>",
        6: "<:Deathknight_Unholy:1302704139352145961>",
        7: "<:Druid_Balance:1302704140916625521>",
        8: "<:Druid_Feral:1302704142111866880>",
        9: "<:Druid_Guardian:1302704143613296750>",
        10: "<:Druid_Restoration:1302704144817197157>",
        11: "<:Evoker_Augmentation:1302704563442417715>",
        12: "<:Evoker_Devestation:1302704148118241351>",
        13: "<:Evoker_Preservation:1302704565749153802>",
        14: "<:Deamonhunter_Havoc:1302704133371072614>",
        15: "<:Deamonhunter_Vengeance:1302704135186944140>",
        16: "<:Mage_Arcane:1302704568752406578>",
        17: "<:Mage_Fire:1302704159337742336>",
        18: "<:Mage_Frost:1302704570069155870>",
        19: "<:Monk_Brewmaster:1302704162466955377>",
        20: "<:Monk_Mistweaver:1302704571403075614>",
        21: "<:Monk_Windwalker:1302704165645975633>",
        22: "<:Paladin_Holy:1302704572652851290>",
        23: "<:Paladin_Protection:1302704169026715700>",
        24: "<:Paladin_Retribution:1302704574544613397>",
        25: "<:Priest_Discepline:1302704173493518478>",
        26: "<:Priest_Holy:1302704175867625592>",
        27: "<:Priest_Shadow:1302704179080335532>",
        28: "<:Rogue_Assasination:1302704575832391742>",
        29: "<:Rogue_Outlaw:1302704183786602597>",
        30: "<:Rogue_Subtlety:1302704186122702848>",
        31: "<:Shaman_Elemental:1302706706383638648>",
        32: "<:Shaman_Enhancement:1302704189918679190>",
        33: "<:Shaman_Restoration:1302704579221127268>",
        34: "<:Warlock_Affliction:1302704193970241627>",
        35: "<:Warlock_Demonologie:1302704581259690015>",
        36: "<:Warlock_Destruction:1302704197225021532>",
        37: "<:Warrior_Arms:1302704659961741436>",
        38: "<:Warrior_Fury:1302704201943617599>",
        39: "<:Warrior_Protection:1302704585437085788>"
    }
    return Spec(spec_dict.get(id, "Unknown Spec"))

#Lookup lists for getting spec specific data

hero_list = ['<:Shaman_Elemental:1302706706383638648>',
            '<:Shaman_Enhancement:1302704189918679190>',
            '<:Shaman_Restoration:1302704579221127268>',
            '<:Evoker_Augmentation:1302704563442417715>',
            '<:Evoker_Devestation:1302704148118241351>',
            '<:Evoker_Preservation:1302704565749153802>',
            '<:Hunter_Beastmastery:1302704152488448020>',
            '<:Hunter_Marksmanship:1302704567485726730>',
            '<:Hunter_Survival:1302704155965788190>',
            '<:Mage_Arcane:1302704568752406578>',
            '<:Mage_Fire:1302704159337742336>',
             '<:Mage_Frost:1302704570069155870>']

br_list = ['<:Deathknight_Blood:1302704136575258818>',
          '<:Deathknight_Frost:1302704137888338053>',
          '<:Deathknight_Unholy:1302704139352145961>',
          '<:Druid_Balance:1302704140916625521>',
          '<:Druid_Feral:1302704142111866880>',
          '<:Druid_Guardian:1302704143613296750>',
          '<:Druid_Restoration:1302704144817197157>',
          '<:Paladin_Holy:1302704572652851290>',
          '<:Paladin_Protection:1302704169026715700>',
          '<:Paladin_Retribution:1302704574544613397>',
          '<:Warlock_Affliction:1302704193970241627>',
           '<:Warlock_Demonologie:1302704581259690015>',
           '<:Warlock_Destruction:1302704197225021532>']

tank_list = ['<:Deamonhunter_Vengeance:1302704135186944140>',
            '<:Deathknight_Blood:1302704136575258818>',
            '<:Druid_Guardian:1302704143613296750>',
            '<:Paladin_Protection:1302704169026715700>',
            '<:Warrior_Protection:1302704585437085788>',
            '<:Monk_Brewmaster:1302704162466955377>']

heal_list = ['<:Druid_Restoration:1302704144817197157>',
            '<:Evoker_Preservation:1302704565749153802>',
            '<:Paladin_Holy:1302704572652851290>',
            '<:Priest_Discepline:1302704173493518478>',
            '<:Shaman_Restoration:1302704579221127268>',
            '<:Priest_Holy:1302704175867625592>',
            '<:Monk_Mistweaver:1302704571403075614>']