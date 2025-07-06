# -*- coding: utf-8 -*-
from enums import CardType, ClassType, EffectType, ProcessType, TargetType, TribeType
from card_data import CardData

BASIC_CARD_DATABASE = {
    "Indomitable Fighter": CardData("Indomitable Fighter", "Indomitable Fighter", 2, CardType.FOLLOWER, ClassType.NEUTRAL, 2, 2, tribes=[], effects=[{'type': EffectType.ENHANCE, 'process': ProcessType.STAT_BUFF, 'target': TargetType.SELF, 'value': (3, 3), 'enhance_cost': 4}]),
    "Leah, Bellringer Angel": CardData("Leah, Bellringer Angel", "Leah, Bellringer Angel", 2, CardType.FOLLOWER, ClassType.NEUTRAL, 0, 2, tribes=[], effects=[
		{'type': EffectType.WARD},
        {'type': EffectType.LAST_WORDS, 'process': ProcessType.DRAW, 'target': TargetType.OWN_LEADER, 'value': 1},
        {'type': EffectType.ON_EVOLVE, 'process': ProcessType.DRAW, 'target': TargetType.OWN_LEADER, 'value': 1}]),
    "Quake Goliath": CardData("Quake Goliath", "Quake Goliath", 4, CardType.FOLLOWER, ClassType.NEUTRAL, 4, 5, tribes=[], effects=[{'type': EffectType.WARD}]),
    "Detective's Lens": CardData("Detective's Lens", "Detective's Lens", 2, CardType.FOLLOWER, ClassType.NEUTRAL, 0, 0, tribes=[], effects=[{'type': EffectType.ACTIVATE, 'raw_action_text': 'Destroy this card. Select an enemy follower on the field and remove Ward from it.'}]),
    "Arriet, Luxminstrel": CardData("Arriet, Luxminstrel", "Arriet, Luxminstrel", 3, CardType.FOLLOWER, ClassType.NEUTRAL, 3, 3, tribes=[], effects=[
		{'type': EffectType.ON_EVOLVE, 'process': ProcessType.HEAL, 'target': TargetType.OWN_LEADER, 'value': 2},
        {'type': EffectType.ON_SUPER_EVOLVE, 'raw_action_text': 'Restore 4 defense instead.'}]),
    "Caravan Mammoth": CardData("Caravan Mammoth", "Caravan Mammoth", 7, CardType.FOLLOWER, ClassType.NEUTRAL, 10, 10, tribes=[], effects=[]),
    "Adventurers' Guild": CardData("Adventurers' Guild", "Adventurers' Guild", 3, CardType.FOLLOWER, ClassType.NEUTRAL, 0, 0, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Draw a follower.'},
        {'type': EffectType.ACTIVATE, 'raw_action_text': 'Destroy this card. Select an allied follower on the field and give it Rush.'}]),
    "Fairy Tamer": CardData("Fairy Tamer", "Fairy Tamer", 2, CardType.FOLLOWER, ClassType.FORESTCRAFT, 1, 1, tribes=[], effects=[{'type': EffectType.FANFARE, 'raw_action_text': 'Add 2 copies of Fairy to your hand.'}]),
    "Stray Beastman": CardData("Stray Beastman", "Stray Beastman", 2, CardType.FOLLOWER, ClassType.FORESTCRAFT, 2, 2, tribes=[], effects=[{'type': EffectType.FANFARE, 'raw_action_text': 'Increase your Combo by 1.'}]),
    "Gentle Treant": CardData("Gentle Treant", "Gentle Treant", 4, CardType.FOLLOWER, ClassType.FORESTCRAFT, 4, 4, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Combo (3) - Evolve this follower.'},
        {'type': EffectType.STRIKE, 'process': ProcessType.HEAL, 'target': TargetType.OWN_LEADER, 'value': 2}]),
    "Wild Profusion": CardData("Wild Profusion", "Wild Profusion", 2, CardType.FOLLOWER, ClassType.FORESTCRAFT, 0, 0, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Add a Fairy to your hand.'},
        {'raw_effect_text': 'Countdown (2)'},
        {       'raw_effect_text': 'Whenever an allied Pixie follower enters the field, deal 1 damage to a random '
                                   'enemy follower.'}]),
    "May, Journey Elf": CardData("May, Journey Elf", "May, Journey Elf", 1, CardType.FOLLOWER, ClassType.FORESTCRAFT, 1, 1, tribes=[], effects=[{'type': EffectType.FANFARE, 'raw_action_text': 'Combo (3) - Select an enemy follower on the field and deal it 3 damage.'}]),
    "Selwyn, Sonic Archer": CardData("Selwyn, Sonic Archer", "Selwyn, Sonic Archer", 7, CardType.FOLLOWER, ClassType.FORESTCRAFT, 4, 6, tribes=[], effects=[
		{'type': EffectType.STORM},
        {'type': EffectType.ON_SUPER_EVOLVE, 'raw_action_text': 'Select an enemy follower on the field and return it to hand.'}]),
    "Bug Alert": CardData("Bug Alert", "Bug Alert", 1, CardType.SPELL, ClassType.FORESTCRAFT, 0, 0, tribes=[], effects=[{       'raw_effect_text': 'Select an allied card on the field and return it to hand. Deal 2 damage to a '
                                   'random enemy follower.'}]),
    "Flashstep Quickblader": CardData("Flashstep Quickblader", "Flashstep Quickblader", 1, CardType.FOLLOWER, ClassType.SWORDCRAFT, 1, 1, tribes=[], effects=[{'type': EffectType.STORM}]),
    "Arms Peddler": CardData("Arms Peddler", "Arms Peddler", 4, CardType.FOLLOWER, ClassType.SWORDCRAFT, 3, 2, tribes=[], effects=[
		{'type': EffectType.RUSH},
        {'type': EffectType.LAST_WORDS, 'process': ProcessType.DRAW, 'target': TargetType.OWN_LEADER, 'value': 1}]),
    "Centaur Centurion": CardData("Centaur Centurion", "Centaur Centurion", 8, CardType.FOLLOWER, ClassType.SWORDCRAFT, 7, 5, tribes=[], effects=[{'type': EffectType.STORM}]),
    "Way of the Maid": CardData("Way of the Maid", "Way of the Maid", 2, CardType.SPELL, ClassType.SWORDCRAFT, 0, 0, tribes=[], effects=[{'raw_effect_text': 'Select a card in your hand and return it to deck. Draw 2 Swordcraft followers.'}]),
    "Royal Coachwoman": CardData("Royal Coachwoman", "Royal Coachwoman", 2, CardType.FOLLOWER, ClassType.SWORDCRAFT, 1, 2, tribes=[], effects=[{'type': EffectType.LAST_WORDS, 'raw_action_text': 'Summon a Knight.'}]),
    "Rusty, Luxcard Trickster": CardData("Rusty, Luxcard Trickster", "Rusty, Luxcard Trickster", 3, CardType.FOLLOWER, ClassType.SWORDCRAFT, 3, 3, tribes=[], effects=[{'type': EffectType.ON_SUPER_EVOLVE, 'raw_action_text': 'Draw all copies of Rusty, Luxcard Trickster and give them Storm.'}]),
    "Ancestral Crown": CardData("Ancestral Crown", "Ancestral Crown", 4, CardType.FOLLOWER, ClassType.SWORDCRAFT, 0, 0, tribes=[], effects=[
		{'raw_effect_text': 'Countdown (4)'},
        {'raw_effect_text': 'Whenever an allied follower enters the field, give it +1/+1.'}]),
    "Dazzling Runeknight": CardData("Dazzling Runeknight", "Dazzling Runeknight", 3, CardType.FOLLOWER, ClassType.NEUTRAL, 2, 2, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Select a Mode to activate.'},
        {'raw_effect_text': '1. Spellboost your hand 2 times.'},
        {'raw_effect_text': '2. Earth Rite (1) - Give this follower +2/+2 and Ward.'}]),
    "Witch's New Brew": CardData("Witch's New Brew", "Witch's New Brew", 1, CardType.FOLLOWER, ClassType.NEUTRAL, 0, 0, tribes=[TribeType.EARTH_SIGIL], effects=[
		{'type': EffectType.FANFARE, 'process': ProcessType.DRAW, 'target': TargetType.OWN_LEADER, 'value': 1},
        {'raw_effect_text': 'Earth Sigil'},
        {'type': EffectType.ACTIVATE, 'raw_action_text': 'Gain an earth sigil.', 'cost': 1}]),
    "Foresight": CardData("Foresight", "Foresight", 1, CardType.SPELL, ClassType.NEUTRAL, 0, 0, tribes=[], effects=[{'raw_effect_text': 'Draw a card.'}]),
    "Truth Summons": CardData("Truth Summons", "Truth Summons", 2, CardType.SPELL, ClassType.NEUTRAL, 0, 0, tribes=[], effects=[{'raw_effect_text': 'Summon a Clay Golem.'}]),
    "Remi & Rami, Two-Faced Witch": CardData("Remi & Rami, Two-Faced Witch", "Remi & Rami, Two-Faced Witch", 4, CardType.FOLLOWER, ClassType.NEUTRAL, 4, 4, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Earth Rite (1) - Summon a Guardian Golem.'},
        {'type': EffectType.ON_SUPER_EVOLVE, 'raw_action_text': 'Select an allied Golem follower on the field, evolve it, and give it +3/+3.'}]),
    "Blaze Destroyer": CardData("Blaze Destroyer", "Blaze Destroyer", 10, CardType.FOLLOWER, ClassType.NEUTRAL, 8, 6, tribes=[], effects=[{'raw_effect_text': 'On Spellboost: Reduce the cost of this card by 1.'}]),
    "Arcane Eruption": CardData("Arcane Eruption", "Arcane Eruption", 4, CardType.SPELL, ClassType.NEUTRAL, 0, 0, tribes=[], effects=[{'raw_effect_text': 'Deal 2 damage to all followers. Earth Rite (1) - Draw a card.'}]),
    "Searing Firenewt": CardData("Searing Firenewt", "Searing Firenewt", 2, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 2, 2, tribes=[], effects=[{'type': EffectType.FANFARE, 'raw_action_text': 'Select an enemy follower on the field and deal it 1 damage.'}]),
    "Axe-Wielding Dragonslayer": CardData("Axe-Wielding Dragonslayer", "Axe-Wielding Dragonslayer", 6, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 5, 10, tribes=[], effects=[{'type': EffectType.WARD}]),
    "Warrior of the Deep": CardData("Warrior of the Deep", "Warrior of the Deep", 8, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 6, 6, tribes=[], effects=[{'type': EffectType.FANFARE, 'raw_action_text': 'Deal 6 damage to the enemy leader.'}]),
    "Strike of the Dragonewt": CardData("Strike of the Dragonewt", "Strike of the Dragonewt", 1, CardType.SPELL, ClassType.DRAGONCRAFT, 0, 0, tribes=[], effects=[{       'raw_effect_text': "Select an enemy follower on the field and deal it 2 damage. If you're in Overflow, "
                                   'deal 4 damage instead.'}]),
    "Draconic Berserker": CardData("Draconic Berserker", "Draconic Berserker", 4, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 4, 5, tribes=[], effects=[
		{'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Select an enemy follower on the field and deal it 4 damage.'},
        {'type': EffectType.ON_SUPER_EVOLVE, 'raw_action_text': 'Deal damage to all enemy followers instead.'}]),
    "Battleforged Dragon Keeper": CardData("Battleforged Dragon Keeper", "Battleforged Dragon Keeper", 5, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 5, 5, tribes=[], effects=[{'type': EffectType.ENHANCE, 'raw_action_text': 'Summon a Vastwing Dragon.', 'enhance_cost': 7}]),
    "Dragonsign": CardData("Dragonsign", "Dragonsign", 3, CardType.SPELL, ClassType.DRAGONCRAFT, 0, 0, tribes=[], effects=[{'raw_effect_text': 'Gain 1 max play point. Then, if you have 10 max play points, draw a card.'}]),
    "Mistress of the Fanged": CardData("Mistress of the Fanged", "Mistress of the Fanged", 6, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 3, 6, tribes=[], effects=[
		{'type': EffectType.STORM}, {'type': EffectType.BANE}]),
    "Night Fiend": CardData("Night Fiend", "Night Fiend", 3, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 4, 3, tribes=[], effects=[{'type': EffectType.FANFARE, 'raw_action_text': 'Deal 1 damage to your leader.'}]),
    "Devious Lesser Mummy": CardData("Devious Lesser Mummy", "Devious Lesser Mummy", 2, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 2, 2, tribes=[], effects=[{'type': EffectType.FANFARE, 'raw_action_text': 'Necromancy (4) - Give this follower Storm.'}]),
    "Chaos Cyclone": CardData("Chaos Cyclone", "Chaos Cyclone", 2, CardType.SPELL, ClassType.ABYSSCRAFT, 0, 0, tribes=[], effects=[
		{'raw_effect_text': 'Select a Mode to activate.'},
        {'raw_effect_text': '1. Draw a follower.'},
        {'raw_effect_text': '2. Reanimate (2).'}]),
    "Lilith, Enchanting Succubus": CardData("Lilith, Enchanting Succubus", "Lilith, Enchanting Succubus", 1, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 1, 1, tribes=[], effects=[{'type': EffectType.LAST_WORDS, 'raw_action_text': 'Add a Bat to your hand.'}]),
    "Amorous Necromancer": CardData("Amorous Necromancer", "Amorous Necromancer", 4, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 5, 4, tribes=[], effects=[
		{'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Summon 2 copies of Ghost.'},
        {'type': EffectType.ON_SUPER_EVOLVE, 'raw_action_text': 'Give them Drain.'}]),
    "Soul Predation": CardData("Soul Predation", "Soul Predation", 2, CardType.SPELL, ClassType.ABYSSCRAFT, 0, 0, tribes=[], effects=[{'raw_effect_text': 'Select an allied follower on the field and destroy it. Draw 2 cards.'}]),
    "Soulcure Sister": CardData("Soulcure Sister", "Soulcure Sister", 6, CardType.FOLLOWER, ClassType.HAVENCRAFT, 3, 5, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'process': ProcessType.HEAL, 'target': TargetType.OWN_LEADER, 'value': 5},
        {'type': EffectType.WARD}]),
    "Fox of Purity": CardData("Fox of Purity", "Fox of Purity", 2, CardType.FOLLOWER, ClassType.HAVENCRAFT, 1, 3, tribes=[], effects=[{'type': EffectType.WARD}]),
    "Winged Warrior": CardData("Winged Warrior", "Winged Warrior", 4, CardType.FOLLOWER, ClassType.HAVENCRAFT, 4, 4, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Select another allied follower on the field and give it +1/+1.'},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': "Replicate the effects of this card's Fanfare ability."}]),
    "Avian Statue": CardData("Avian Statue", "Avian Statue", 4, CardType.FOLLOWER, ClassType.HAVENCRAFT, 0, 0, tribes=[], effects=[
		{'raw_effect_text': 'Countdown (2)'},
        {'type': EffectType.LAST_WORDS, 'raw_action_text': 'Summon a Regal Falcon.'},
        {'type': EffectType.ACTIVATE, 'raw_action_text': "Advance this amulet's count by 2.", 'cost': 2}]),
    "Ironfist Priest": CardData("Ironfist Priest", "Ironfist Priest", 4, CardType.FOLLOWER, ClassType.HAVENCRAFT, 5, 4, tribes=[], effects=[
		{'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Select an enemy follower on the field with 3 defense or less and banish it.'},
        {'type': EffectType.ON_SUPER_EVOLVE, 'raw_action_text': 'Banish all enemy followers with 3 defense or less instead.'}]),
    "Sacred Griffon": CardData("Sacred Griffon", "Sacred Griffon", 8, CardType.FOLLOWER, ClassType.HAVENCRAFT, 6, 8, tribes=[], effects=[
		{'type': EffectType.WARD}, {'raw_effect_text': 'Whenever you Engage an amulet, give this follower Storm.'}]),
    "Winged Statue": CardData("Winged Statue", "Winged Statue", 1, CardType.FOLLOWER, ClassType.HAVENCRAFT, 0, 0, tribes=[], effects=[
		{'raw_effect_text': 'Countdown (4)'},
        {'type': EffectType.LAST_WORDS, 'raw_action_text': 'Summon a Holy Falcon.'},
        {'type': EffectType.ACTIVATE, 'raw_action_text': "Advance this amulet's count by 1.", 'cost': 1}]),
    "Kitty Cannoneer": CardData("Kitty Cannoneer", "Kitty Cannoneer", 3, CardType.FOLLOWER, ClassType.PORTALCRAFT, 3, 2, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Add a Gear of Ambition to your hand.'}, {'type': EffectType.RUSH}]),
    "Puppet Lancer": CardData("Puppet Lancer", "Puppet Lancer", 2, CardType.FOLLOWER, ClassType.PORTALCRAFT, 2, 1, tribes=[], effects=[{'type': EffectType.FANFARE, 'raw_action_text': 'Add an Enhanced Puppet to your hand.'}]),
    "Mechanized Beast": CardData("Mechanized Beast", "Mechanized Beast", 6, CardType.FOLLOWER, ClassType.PORTALCRAFT, 4, 9, tribes=[], effects=[
		{'type': EffectType.BANE}, {'type': EffectType.WARD}]),
    "Bullet from Beyond": CardData("Bullet from Beyond", "Bullet from Beyond", 4, CardType.SPELL, ClassType.PORTALCRAFT, 0, 0, tribes=[], effects=[{       'raw_effect_text': 'Select an enemy follower on the field and destroy it. Add a Gear of Ambition and '
                                   'Gear of Remembrance to your hand.'}]),
    "Electric Whip Lass": CardData("Electric Whip Lass", "Electric Whip Lass", 2, CardType.FOLLOWER, ClassType.PORTALCRAFT, 1, 3, tribes=[], effects=[{'type': EffectType.FANFARE, 'raw_action_text': 'Add a Gear of Remembrance to your hand.'}]),
    "Mecha Cavalier": CardData("Mecha Cavalier", "Mecha Cavalier", 5, CardType.FOLLOWER, ClassType.PORTALCRAFT, 4, 4, tribes=[], effects=[
		{'type': EffectType.WARD},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Summon a Mecha Cavalier.'},
        {'type': EffectType.ON_SUPER_EVOLVE, 'raw_action_text': 'Summon 2 instead.'}]),
    "Puppet Theater": CardData("Puppet Theater", "Puppet Theater", 2, CardType.FOLLOWER, ClassType.PORTALCRAFT, 0, 0, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Add a Puppet to your hand.'},
        {'raw_effect_text': 'Countdown (2)'},
        {'raw_effect_text': 'At the end of your turn, add a Puppet to your hand.'}]),
}

LEGENDS_RISE_CARD_DATABASE = {
    "Ruby, Greedy Cherub": CardData("Ruby, Greedy Cherub", "Ruby, Greedy Cherub", 2, CardType.FOLLOWER, ClassType.NEUTRAL, 2, 2, tribes=[], effects=[{'type': EffectType.FANFARE, 'process': ProcessType.DRAW, 'target': TargetType.OWN_LEADER, 'value': 1}]),
    "Vigilant Detective": CardData("Vigilant Detective", "Vigilant Detective", 3, CardType.FOLLOWER, ClassType.NEUTRAL, 3, 3, tribes=[], effects=[{'type': EffectType.LAST_WORDS, 'raw_action_text': "Add a Detective's Lens to your hand."}]),
    "Goblin Foray": CardData("Goblin Foray", "Goblin Foray", 5, CardType.SPELL, ClassType.NEUTRAL, 0, 0, tribes=[], effects=[{'raw_effect_text': 'Summon 5 copies of Goblin.'}]),
    "Apollo, Heaven's Envoy": CardData("Apollo, Heaven's Envoy", "Apollo, Heaven's Envoy", 3, CardType.FOLLOWER, ClassType.NEUTRAL, 1, 2, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Deal 1 damage to all enemy followers.'},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': "Replicate the effects of this card's Fanfare ability."}]),
    "Seraphic Tidings": CardData("Seraphic Tidings", "Seraphic Tidings", 3, CardType.SPELL, ClassType.NEUTRAL, 0, 0, tribes=[], effects=[{'raw_effect_text': 'Draw 2 cards.'}]),
    "Phildau, Lionheart Ward": CardData("Phildau, Lionheart Ward", "Phildau, Lionheart Ward", 2, CardType.FOLLOWER, ClassType.NEUTRAL, 2, 2, tribes=[], effects=[{'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Select an enemy follower on the field and destroy it.'}]),
    "Divine Thunder": CardData("Divine Thunder", "Divine Thunder", 4, CardType.SPELL, ClassType.NEUTRAL, 0, 0, tribes=[], effects=[{'raw_effect_text': 'Destroy a random enemy follower with the highest attack. Deal 1 damage to all enemy followers.'}]),
    "Olivia, Heroic Dark Angel": CardData("Olivia, Heroic Dark Angel", "Olivia, Heroic Dark Angel", 7, CardType.FOLLOWER, ClassType.NEUTRAL, 4, 4, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'process': ProcessType.DRAW, 'target': TargetType.OWN_LEADER, 'value': 2},
        {'type': EffectType.ON_SUPER_EVOLVE, 'raw_action_text': 'Select another unevolved allied follower on the field and super-evolve it.'}]),
    "Ruler of Cocytus": CardData("Ruler of Cocytus", "Ruler of Cocytus", 10, CardType.FOLLOWER, ClassType.NEUTRAL, 10, 10, tribes=[], effects=[{'type': EffectType.FANFARE, 'raw_action_text': 'Replace your deck with the Apocalypse Deck.'}]),
    "Fay Twinkletoes": CardData("Fay Twinkletoes", "Fay Twinkletoes", 2, CardType.FOLLOWER, ClassType.FORESTCRAFT, 2, 1, tribes=[], effects=[{'type': EffectType.FANFARE, 'raw_action_text': 'Combo (3) - Give all other allied followers on the field +1/+1.'}]),
    "Capricious Sprite": CardData("Capricious Sprite", "Capricious Sprite", 3, CardType.FOLLOWER, ClassType.FORESTCRAFT, 1, 1, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Summon a Fairy. Add a Fairy to your hand.'},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': "Replicate the effects of this card's Fanfare ability."}]),
    "Deepwood Fairy Beast": CardData("Deepwood Fairy Beast", "Deepwood Fairy Beast", 8, CardType.FOLLOWER, ClassType.FORESTCRAFT, 4, 4, tribes=[], effects=[{'type': EffectType.FANFARE, 'process': ProcessType.DRAW, 'target': TargetType.OWN_LEADER, 'value': 1}]),
    "Workin' Grasshopper": CardData("Workin' Grasshopper", "Workin' Grasshopper", 3, CardType.FOLLOWER, ClassType.FORESTCRAFT, 2, 1, tribes=[], effects=[{'type': EffectType.FANFARE, 'raw_action_text': 'Draw an X-cost follower. X is your Combo.'}]),
    "Elder Sagebrush": CardData("Elder Sagebrush", "Elder Sagebrush", 4, CardType.FOLLOWER, ClassType.FORESTCRAFT, 3, 3, tribes=[], effects=[{'type': EffectType.FANFARE, 'raw_action_text': 'Deal 3 damage to a random enemy follower. Combo (3) - Deal damage to 3 random enemy followers instead.'}]),
    "Fairy Convocation": CardData("Fairy Convocation", "Fairy Convocation", 1, CardType.SPELL, ClassType.FORESTCRAFT, 0, 0, tribes=[], effects=[{'raw_effect_text': 'Add 2 copies of Fairy to your hand.'}]),
    "Aerin, Crystalian Frostward": CardData("Aerin, Crystalian Frostward", "Aerin, Crystalian Frostward", 7, CardType.FOLLOWER, ClassType.FORESTCRAFT, 6, 8, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'process': ProcessType.HEAL, 'target': TargetType.OWN_LEADER, 'value': 2},
        {'type': EffectType.WARD}]),
    "Good Fairy of the Pond": CardData("Good Fairy of the Pond", "Good Fairy of the Pond", 1, CardType.FOLLOWER, ClassType.FORESTCRAFT, 1, 1, tribes=[], effects=[{'type': EffectType.LAST_WORDS, 'raw_action_text': 'Add a Fairy to your hand.'}]),
    "Baby Carbuncle": CardData("Baby Carbuncle", "Baby Carbuncle", 2, CardType.FOLLOWER, ClassType.FORESTCRAFT, 2, 2, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Select another allied card on the field and return it to hand.'},
        {'type': EffectType.ON_SUPER_EVOLVE, 'raw_action_text': 'Recover 3 play points.'}]),
    "Lambent Cairn": CardData("Lambent Cairn", "Lambent Cairn", 2, CardType.FOLLOWER, ClassType.FORESTCRAFT, 0, 0, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Add a Fairy to your hand. Combo (3) - Add a Deepwood Bounty to your hand.'},
        {'type': EffectType.ACTIVATE, 'raw_action_text': 'Destroy this card. Select an allied follower on the field and give it +1/+1.'}]),
    "Fragrantwood Whispers": CardData("Fragrantwood Whispers", "Fragrantwood Whispers", 3, CardType.SPELL, ClassType.FORESTCRAFT, 0, 0, tribes=[], effects=[{'raw_effect_text': 'Add a Deepwood Bounty to your hand. Draw a card.'}]),
    "Lily, Crystalian Innocence": CardData("Lily, Crystalian Innocence", "Lily, Crystalian Innocence", 2, CardType.FOLLOWER, ClassType.FORESTCRAFT, 1, 3, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Combo (3) - Select an enemy follower on the field and set its defense to 1.'},
        {'type': EffectType.ON_EVOLVE, 'process': ProcessType.DRAW, 'target': TargetType.OWN_LEADER, 'value': 1}]),
    "Glade, Fragrantwood Ward": CardData("Glade, Fragrantwood Ward", "Glade, Fragrantwood Ward", 5, CardType.FOLLOWER, ClassType.FORESTCRAFT, 3, 3, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'process': ProcessType.DRAW, 'target': TargetType.OWN_LEADER, 'value': 2},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Deal X damage split between all enemy followers. X is the number of cards in your hand.'}]),
    "Bayle, Luxglaive Warrior": CardData("Bayle, Luxglaive Warrior", "Bayle, Luxglaive Warrior", 8, CardType.FOLLOWER, ClassType.FORESTCRAFT, 4, 4, tribes=[], effects=[
		{       'raw_effect_text': 'Activates in hand. Whenever an allied follower leaves the field, reduce the cost '
                                   'of this card by 1.'},
        {'type': EffectType.FANFARE, 'raw_action_text': 'Select an enemy follower on the field and deal it 4 damage.'}]),
    "Killer Rhinoceroach": CardData("Killer Rhinoceroach", "Killer Rhinoceroach", 3, CardType.FOLLOWER, ClassType.FORESTCRAFT, 0, 2, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Give this follower +X/+0. X is your Combo.'},
        {'type': EffectType.STORM}]),
    "Godwood Staff": CardData("Godwood Staff", "Godwood Staff", 3, CardType.FOLLOWER, ClassType.FORESTCRAFT, 0, 0, tribes=[], effects=[
		{'raw_effect_text': 'At the end of your turn, Combo (3) - Draw a card.'},
        {'type': EffectType.ACTIVATE, 'raw_action_text': 'Destroy this card. Select another allied card on the field and return it to hand.'}]),
    "Aria, Lady of the Woods": CardData("Aria, Lady of the Woods", "Aria, Lady of the Woods", 6, CardType.FOLLOWER, ClassType.FORESTCRAFT, 4, 4, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Gain Crest: Aria, Lady of the Woods.'},
        {'type': EffectType.ON_SUPER_EVOLVE, 'raw_action_text': 'Summon 3 copies of Fairy.'}]),
    "Opulent Rose Queen": CardData("Opulent Rose Queen", "Opulent Rose Queen", 9, CardType.FOLLOWER, ClassType.FORESTCRAFT, 6, 6, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Transform all Forestcraft cards in your hand that cost 1 or less into copies of Bramble Burst.'},
        {'type': EffectType.WARD}]),
    "Amataz, Origin Blader": CardData("Amataz, Origin Blader", "Amataz, Origin Blader", 3, CardType.FOLLOWER, ClassType.FORESTCRAFT, 2, 2, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Give this follower +X/+X. X is the number of Pixie followers in your hand.'},
        {'type': EffectType.WARD},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Do this X times: "Deal 1 damage to a random enemy follower." X is the number of Pixie followers in your hand.'}]),
    "Ian, Lovebound Knight": CardData("Ian, Lovebound Knight", "Ian, Lovebound Knight", 3, CardType.FOLLOWER, ClassType.SWORDCRAFT, 2, 2, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Select another allied follower on the field and give it +1/+1.'},
        {'type': EffectType.WARD}]),
    "Ernesta, Peace Hawker": CardData("Ernesta, Peace Hawker", "Ernesta, Peace Hawker", 6, CardType.FOLLOWER, ClassType.SWORDCRAFT, 4, 6, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Give all other allied followers on the field +1/+1.'},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': "Replicate the effects of this card's Fanfare ability."}]),
    "Lyrala, Luminous Potionwright": CardData("Lyrala, Luminous Potionwright", "Lyrala, Luminous Potionwright", 3, CardType.FOLLOWER, ClassType.SWORDCRAFT, 1, 2, tribes=[TribeType.LUMINOUS], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Summon a Steelclad Knight.'},
        {'raw_effect_text': 'Whenever an allied Officer follower enters the field, restore 1 defense to your leader.'}]),
    "Hound of War": CardData("Hound of War", "Hound of War", 3, CardType.FOLLOWER, ClassType.SWORDCRAFT, 4, 2, tribes=[], effects=[
		{'type': EffectType.ENHANCE, 'raw_action_text': 'Summon 2 copies of Hound of War.', 'enhance_cost': 6},
        {'type': EffectType.RUSH}]),
    "Ignominious Samurai": CardData("Ignominious Samurai", "Ignominious Samurai", 2, CardType.FOLLOWER, ClassType.SWORDCRAFT, 2, 1, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': "If you've unlocked super-evolution, give this follower Bane."},
        {'type': EffectType.RUSH}]),
    "Knightly Rending": CardData("Knightly Rending", "Knightly Rending", 4, CardType.SPELL, ClassType.SWORDCRAFT, 0, 0, tribes=[], effects=[{'raw_effect_text': 'Select an enemy follower on the field and destroy it. Summon a Steelclad Knight.'}]),
    "Luminous Commander": CardData("Luminous Commander", "Luminous Commander", 1, CardType.FOLLOWER, ClassType.SWORDCRAFT, 1, 1, tribes=[TribeType.LUMINOUS], effects=[
		{       'raw_effect_text': 'Whenever an allied Officer follower enters the field, give this follower +1/+0 '
                                   'until the end of the turn.'},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Summon a Knight.'}]),
    "Luminous Magus": CardData("Luminous Magus", "Luminous Magus", 5, CardType.FOLLOWER, ClassType.SWORDCRAFT, 1, 3, tribes=[TribeType.LUMINOUS], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Summon 3 copies of Steelclad Knight.'},
        {'raw_effect_text': 'Whenever an allied Officer follower enters the field, give it Ward.'}]),
    "Luminous Lancetrooper": CardData("Luminous Lancetrooper", "Luminous Lancetrooper", 2, CardType.FOLLOWER, ClassType.SWORDCRAFT, 1, 2, tribes=[TribeType.LUMINOUS], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Summon a Knight.'},
        {'raw_effect_text': 'Whenever an allied Officer follower enters the field, give it Rush.'}]),
    "Shinobi Squirrel": CardData("Shinobi Squirrel", "Shinobi Squirrel", 2, CardType.FOLLOWER, ClassType.SWORDCRAFT, 2, 1, tribes=[], effects=[
		{'type': EffectType.AMBUSH}, {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Summon a Shinobi Squirrel.'}]),
    "Ironcrown Majesty": CardData("Ironcrown Majesty", "Ironcrown Majesty", 3, CardType.SPELL, ClassType.SWORDCRAFT, 0, 0, tribes=[], effects=[
		{'raw_effect_text': 'Select a Mode to activate.'},
        {'raw_effect_text': '1. Summon a Steelclad Knight and Knight.'},
        {'raw_effect_text': '2. Give all allied followers on the field +1/+1.'}]),
    "Jeno, Levin Axeraider": CardData("Jeno, Levin Axeraider", "Jeno, Levin Axeraider", 7, CardType.FOLLOWER, ClassType.SWORDCRAFT, 7, 6, tribes=[TribeType.LEVIN], effects=[
		{'type': EffectType.RUSH},
        {'raw_effect_text': 'Can attack 2 times per turn.'},
        {'type': EffectType.STRIKE, 'raw_action_text': 'Give this follower Barrier. Summon a Knight.'}]),
    "Valse, Silent Sniper": CardData("Valse, Silent Sniper", "Valse, Silent Sniper", 3, CardType.FOLLOWER, ClassType.SWORDCRAFT, 2, 1, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Select an enemy follower on the field and deal it 5 damage.'},
        {'type': EffectType.ENHANCE, 'process': ProcessType.STAT_BUFF, 'target': TargetType.SELF, 'value': (2, 2), 'enhance_cost': 6}]),
    "Zirconia, Ironcrown Ward": CardData("Zirconia, Ironcrown Ward", "Zirconia, Ironcrown Ward", 4, CardType.FOLLOWER, ClassType.SWORDCRAFT, 4, 4, tribes=[], effects=[{'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Summon 2 copies of Knight. Give all other allied followers on the field +1/+1.'}]),
    "Amalia, Luxsteel Paladin": CardData("Amalia, Luxsteel Paladin", "Amalia, Luxsteel Paladin", 8, CardType.FOLLOWER, ClassType.SWORDCRAFT, 6, 6, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Summon 4 copies of Steelclad Knight.'},
        {'raw_effect_text': 'Whenever another allied follower enters the field, give it +1/+0, Rush, and Ward.'}]),
    "Ravening Tentacles": CardData("Ravening Tentacles", "Ravening Tentacles", 7, CardType.SPELL, ClassType.SWORDCRAFT, 0, 0, tribes=[TribeType.LEVIN], effects=[{       'raw_effect_text': 'Select an enemy follower on the field or the enemy leader and deal it 5 damage. '
                                   'Restore 5 defense to your leader.'}]),
    "Albert, Levin Stormsaber": CardData("Albert, Levin Stormsaber", "Albert, Levin Stormsaber", 5, CardType.FOLLOWER, ClassType.SWORDCRAFT, 3, 5, tribes=[TribeType.LEVIN], effects=[
		{'type': EffectType.ENHANCE, 'raw_action_text': 'Deal 3 damage to all enemy followers. Give this follower "Can attack 2 times per turn."', 'enhance_cost': 9},
        {'type': EffectType.STORM}]),
    "Amelia, Silver Captain": CardData("Amelia, Silver Captain", "Amelia, Silver Captain", 6, CardType.FOLLOWER, ClassType.SWORDCRAFT, 4, 4, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Draw 2 Swordcraft followers. Recover 3 play points.'},
        {'type': EffectType.ON_SUPER_EVOLVE, 'raw_action_text': 'Give all other allied Swordcraft followers on the field Barrier.'}]),
    "Kagemitsu, Enduring Warrior": CardData("Kagemitsu, Enduring Warrior", "Kagemitsu, Enduring Warrior", 3, CardType.FOLLOWER, ClassType.SWORDCRAFT, 2, 2, tribes=[], effects=[
		{'type': EffectType.LAST_WORDS, 'raw_action_text': 'Gain Crest: Kagemitsu, Enduring Warrior.'},
        {'type': EffectType.ON_SUPER_EVOLVE, 'raw_action_text': 'Give this follower Storm.'}]),
    "Runeblade Conductor": CardData("Runeblade Conductor", "Runeblade Conductor", 5, CardType.FOLLOWER, ClassType.NEUTRAL, 1, 1, tribes=[], effects=[
		{'raw_effect_text': 'On Spellboost: Give this follower +1/+1.'},
        {'type': EffectType.FANFARE, 'raw_action_text': "Select an enemy follower on the field and deal it X damage. X is this follower's attack."}]),
    "Apprentice Astrologer": CardData("Apprentice Astrologer", "Apprentice Astrologer", 2, CardType.FOLLOWER, ClassType.NEUTRAL, 2, 2, tribes=[], effects=[{'type': EffectType.FANFARE, 'process': ProcessType.DRAW, 'target': TargetType.OWN_LEADER, 'value': 1}]),
    "Owl Summoner": CardData("Owl Summoner", "Owl Summoner", 3, CardType.FOLLOWER, ClassType.NEUTRAL, 3, 3, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Gain an earth sigil.'},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Select an enemy follower on the field and deal it 5 damage.'}]),
    "Starry-Eyed Penguin Wizard": CardData("Starry-Eyed Penguin Wizard", "Starry-Eyed Penguin Wizard", 4, CardType.FOLLOWER, ClassType.NEUTRAL, 2, 2, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'process': ProcessType.DRAW, 'target': TargetType.OWN_LEADER, 'value': 2},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Spellboost your hand 2 times.'}]),
    "Radiant Rainbow": CardData("Radiant Rainbow", "Radiant Rainbow", 2, CardType.SPELL, ClassType.NEUTRAL, 0, 0, tribes=[], effects=[{'raw_effect_text': 'Select a card in your hand with On Spellboost and spellboost it. Draw a card.'}]),
    "Stormy Blast": CardData("Stormy Blast", "Stormy Blast", 1, CardType.SPELL, ClassType.NEUTRAL, 0, 0, tribes=[], effects=[
		{'raw_effect_text': 'X starts at 2.'},
        {'raw_effect_text': 'On Spellboost: Increase X by 1.'},
        {'raw_effect_text': 'Select an enemy follower on the field and deal it X damage.'}]),
    "Ms. Miranda, Adored Academic": CardData("Ms. Miranda, Adored Academic", "Ms. Miranda, Adored Academic", 2, CardType.FOLLOWER, ClassType.NEUTRAL, 2, 2, tribes=[TribeType.MYSTERIA], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Spellboost your hand.'},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Select an enemy follower on the field and deal it 3 damage. Spellboost your hand.'}]),
    "Emmylou, Witch of Wonder": CardData("Emmylou, Witch of Wonder", "Emmylou, Witch of Wonder", 5, CardType.FOLLOWER, ClassType.NEUTRAL, 2, 2, tribes=[], effects=[
		{'raw_effect_text': 'On Spellboost: Reduce the cost of this card by 1.'},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Summon a Clay Golem. Deal X damage to all enemy followers. X is the number of allied Golem followers on the field.'}]),
    "William, Mysterian Student": CardData("William, Mysterian Student", "William, Mysterian Student", 6, CardType.FOLLOWER, ClassType.NEUTRAL, 5, 5, tribes=[TribeType.MYSTERIA], effects=[
		{'raw_effect_text': 'X starts at 0.'},
        {'raw_effect_text': 'On Spellboost: Increase X by 1.'},
        {'type': EffectType.FANFARE, 'raw_action_text': 'Deal X damage to all enemy followers.'},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Spellboost your hand 2 times.'}]),
    "Sagelight Teachings": CardData("Sagelight Teachings", "Sagelight Teachings", 3, CardType.SPELL, ClassType.NEUTRAL, 0, 0, tribes=[], effects=[
		{'raw_effect_text': 'Select a Mode to activate.'},
        {'raw_effect_text': '1. Gain 4 earth sigils.'},
        {'raw_effect_text': '2. Restore 4 defense to your leader.'},
        {'raw_effect_text': '3. Earth Rite (3) - Deal 4 damage to all enemy followers.'}]),
    "Snowman Army": CardData("Snowman Army", "Snowman Army", 8, CardType.SPELL, ClassType.NEUTRAL, 0, 0, tribes=[], effects=[
		{'raw_effect_text': 'On Spellboost: Reduce the cost of this card by 1.'},
        {       'raw_effect_text': 'Select an enemy follower on the field, set its defense to 1, and, until the end of '
                                   'your opponent\'s turn, give it "Can\'t attack followers or leaders."'}]),
    "Juno, Visionary Alchemist": CardData("Juno, Visionary Alchemist", "Juno, Visionary Alchemist", 5, CardType.FOLLOWER, ClassType.NEUTRAL, 3, 3, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Select an enemy follower on the field and deal it X damage. X is the number of earth sigils you have.'},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Gain Crest: Juno, Visionary Alchemist.'}]),
    "Penelope, Potions Prodigy": CardData("Penelope, Potions Prodigy", "Penelope, Potions Prodigy", 2, CardType.FOLLOWER, ClassType.NEUTRAL, 2, 2, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Gain 2 earth sigils.'},
        {'type': EffectType.ON_SUPER_EVOLVE, 'process': ProcessType.DRAW, 'target': TargetType.OWN_LEADER, 'value': 2}]),
    "Edelweiss, Sagelight Ward": CardData("Edelweiss, Sagelight Ward", "Edelweiss, Sagelight Ward", 4, CardType.FOLLOWER, ClassType.NEUTRAL, 2, 2, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Earth Rite (2) - Evolve this follower.'},
        {       'raw_effect_text': 'When this follower evolves, deal 4 damage to a random enemy follower and recover 2 '
                                   'play points.'}]),
    "Homework Time!": CardData("Homework Time!", "Homework Time!", 3, CardType.SPELL, ClassType.NEUTRAL, 0, 0, tribes=[TribeType.MYSTERIA], effects=[
		{'raw_effect_text': 'X starts at 0.'},
        {       'raw_effect_text': 'On Spellboost: Increase X by 1. Then, if X is at least 5, transform this card into '
                                   'a Looking Smart!'},
        {'raw_effect_text': 'Draw 2 cards.'}]),
    "Demonic Call": CardData("Demonic Call", "Demonic Call", 7, CardType.SPELL, ClassType.NEUTRAL, 0, 0, tribes=[], effects=[
		{'raw_effect_text': 'On Spellboost: Reduce the cost of this card by 1.'},
        {'raw_effect_text': 'Summon a Demonic Shikigami.'}]),
    "Kuon, Fivefold Master": CardData("Kuon, Fivefold Master", "Kuon, Fivefold Master", 7, CardType.FOLLOWER, ClassType.NEUTRAL, 3, 3, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Summon a Celestial Shikigami, Demonic Shikigami, and Paper Shikigami.'},
        {'type': EffectType.ENHANCE, 'raw_action_text': 'Destroy all allied Shikigami followers. Summon a Noble Shikigami.', 'enhance_cost': 10},
        {'type': EffectType.ON_SUPER_EVOLVE, 'raw_action_text': 'Select an allied Shikigami follower on the field and give it Storm.'}]),
    "Anne & Grea, Mysterian Duo": CardData("Anne & Grea, Mysterian Duo", "Anne & Grea, Mysterian Duo", 5, CardType.FOLLOWER, ClassType.NEUTRAL, 4, 4, tribes=[TribeType.MYSTERIA], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': "Summon an Anne's Summoning. Spellboost your hand 3 times."},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Select an enemy follower on the field and deal it 3 damage.'}]),
    "Dimension Climb": CardData("Dimension Climb", "Dimension Climb", 18, CardType.SPELL, ClassType.NEUTRAL, 0, 0, tribes=[], effects=[
		{'raw_effect_text': 'On Spellboost: Reduce the cost of this card by 1.'},
        {       'raw_effect_text': 'Return your hand to deck. Draw 5 cards. Spellboost your hand 5 times. Fully '
                                   'recover your play points.'}]),
    "Silvercloud Dragonrider": CardData("Silvercloud Dragonrider", "Silvercloud Dragonrider", 8, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 6, 6, tribes=[], effects=[
		{'type': EffectType.WARD}, {'type': EffectType.LAST_WORDS, 'raw_action_text': 'Summon a Vastwing Dragon.'}]),
    "Swordsnout Trencher": CardData("Swordsnout Trencher", "Swordsnout Trencher", 5, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 4, 6, tribes=[], effects=[{'type': EffectType.FANFARE, 'raw_action_text': "If you're in Overflow, give this follower Storm."}]),
    "Fledgling Dragonslayer": CardData("Fledgling Dragonslayer", "Fledgling Dragonslayer", 4, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 2, 2, tribes=[], effects=[{'type': EffectType.FANFARE, 'raw_action_text': 'Select an enemy follower on the field and destroy it.'}]),
    "Little Dragon Nanny": CardData("Little Dragon Nanny", "Little Dragon Nanny", 2, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 1, 1, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Summon a Fire Drake Whelp.'},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': "Replicate the effects of this card's Fanfare ability."}]),
    "Whitescale Herald": CardData("Whitescale Herald", "Whitescale Herald", 4, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 4, 4, tribes=[], effects=[{'type': EffectType.FANFARE, 'raw_action_text': "If you're in Overflow, restore 4 defense to your leader."}]),
    "Calamity Breath": CardData("Calamity Breath", "Calamity Breath", 6, CardType.SPELL, ClassType.DRAGONCRAFT, 0, 0, tribes=[], effects=[{'raw_effect_text': 'Deal 5 damage to all followers.'}]),
    "Kit, Luxfang Champion": CardData("Kit, Luxfang Champion", "Kit, Luxfang Champion", 6, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 8, 7, tribes=[], effects=[
		{'raw_effect_text': 'When this card is discarded, give a random allied follower on the field +1/+0.'},
        {'type': EffectType.RUSH}]),
    "Eyfa, Windrider": CardData("Eyfa, Windrider", "Eyfa, Windrider", 3, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 2, 1, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': "If you're in Overflow, give this follower Intimidate."},
        {'type': EffectType.STORM}]),
    "Zell, Windreader": CardData("Zell, Windreader", "Zell, Windreader", 3, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 3, 3, tribes=[], effects=[{'type': EffectType.ON_SUPER_EVOLVE, 'raw_action_text': 'Select another allied follower on the field and give it Storm.'}]),
    "Marion, Ravishing Dragonewt": CardData("Marion, Ravishing Dragonewt", "Marion, Ravishing Dragonewt", 4, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 3, 3, tribes=[], effects=[{'type': EffectType.FANFARE, 'raw_action_text': "Select another allied follower on the field and give it +2/+2. If you're in Overflow, give +3/+3 instead."}]),
    "Goldennote Melody": CardData("Goldennote Melody", "Goldennote Melody", 3, CardType.SPELL, ClassType.DRAGONCRAFT, 0, 0, tribes=[], effects=[{'raw_effect_text': "Draw 2 cards. If you're in Overflow, restore 2 defense to your leader."}]),
    "Genesis Dragon Reborn": CardData("Genesis Dragon Reborn", "Genesis Dragon Reborn", 10, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 9, 10, tribes=[], effects=[{'type': EffectType.STORM}]),
    "Liu Feng, Goldennote Ward": CardData("Liu Feng, Goldennote Ward", "Liu Feng, Goldennote Ward", 4, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 3, 3, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': "If you're in Overflow, evolve this follower."},
        {'raw_effect_text': 'When this follower evolves, gain 1 max play point.'}]),
    "Zahar, Stormwave Dragoon": CardData("Zahar, Stormwave Dragoon", "Zahar, Stormwave Dragoon", 6, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 3, 3, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Summon a Vastwing Dragon.'}, {'type': EffectType.WARD}]),
    "Twilight Dragon": CardData("Twilight Dragon", "Twilight Dragon", 9, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 9, 9, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Give all enemy followers on the field -0/-9.'},
        {'type': EffectType.ON_SUPER_EVOLVE, 'process': ProcessType.DRAW, 'target': TargetType.OWN_LEADER, 'value': 3}]),
    "Fan of Otohime": CardData("Fan of Otohime", "Fan of Otohime", 1, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 0, 0, tribes=[], effects=[{'type': EffectType.ACTIVATE, 'raw_action_text': "Summon an Otohime's Bodyguard. Select a card in your hand and discard it.", 'cost': 3}]),
    "Burnite, Anathema of Flame": CardData("Burnite, Anathema of Flame", "Burnite, Anathema of Flame", 7, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 7, 7, tribes=[TribeType.ANATHEMA], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Select a card in your hand and discard it. Deal X damage to all enemy followers. X is the cost of the selected card.'},
        {'type': EffectType.ON_SUPER_EVOLVE, 'raw_action_text': 'Give your opponent Crest: Burnite, Anathema of Flame.'}]),
    "Forte, Blackwing Dragoon": CardData("Forte, Blackwing Dragoon", "Forte, Blackwing Dragoon", 6, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 5, 2, tribes=[], effects=[
		{'type': EffectType.STORM}, {'type': EffectType.INTIMIDATE}]),
    "Garyu, Fabled Dragonkin": CardData("Garyu, Fabled Dragonkin", "Garyu, Fabled Dragonkin", 8, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 5, 5, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Summon a Supreme Golden Dragon and Supreme Silver Dragon.'},
        {'type': EffectType.ON_SUPER_EVOLVE, 'raw_action_text': 'Give all allied copies of Supreme Golden Dragon on the field Storm. Give all allied copies of Supreme Silver Dragon on the field Barrier.'}]),
    "Aryll, Moonstruck Vampire": CardData("Aryll, Moonstruck Vampire", "Aryll, Moonstruck Vampire", 3, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 1, 1, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Summon a Bat.'},
        {'raw_effect_text': 'Whenever an allied Bat enters the field, give it Storm and deal 1 damage to your leader.'}]),
    "Nameless Demon": CardData("Nameless Demon", "Nameless Demon", 2, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 2, 2, tribes=[], effects=[{'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Summon 2 copies of Bat.'}]),
    "Little Miss Bonemancer": CardData("Little Miss Bonemancer", "Little Miss Bonemancer", 3, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 1, 2, tribes=[], effects=[{'type': EffectType.LAST_WORDS, 'raw_action_text': 'Summon 2 copies of Skeleton.'}]),
    "Ghost Juggler": CardData("Ghost Juggler", "Ghost Juggler", 6, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 5, 5, tribes=[], effects=[{'type': EffectType.FANFARE, 'raw_action_text': 'Reanimate (4).'}]),
    "Darkseal Demon": CardData("Darkseal Demon", "Darkseal Demon", 5, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 4, 4, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'process': ProcessType.DRAW, 'target': TargetType.OWN_LEADER, 'value': 2},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Select an enemy follower on the field and deal it 6 damage.'}]),
    "Reaper's Deathslash": CardData("Reaper's Deathslash", "Reaper's Deathslash", 1, CardType.SPELL, ClassType.ABYSSCRAFT, 0, 0, tribes=[], effects=[{'raw_effect_text': 'Select an allied and enemy follower on the field and destroy them.'}]),
    "Mino, Shrewd Reaper": CardData("Mino, Shrewd Reaper", "Mino, Shrewd Reaper", 2, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 2, 1, tribes=[], effects=[
		{'type': EffectType.ENHANCE, 'raw_action_text': 'Give this follower Rush and Bane.', 'enhance_cost': 4},
        {'type': EffectType.LAST_WORDS, 'raw_action_text': 'Add a Skeleton to your hand.'}]),
    "Beryl, Nightmare Incarnate": CardData("Beryl, Nightmare Incarnate", "Beryl, Nightmare Incarnate", 2, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 3, 3, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Deal 3 damage to your leader.'},
        {'type': EffectType.ON_EVOLVE, 'process': ProcessType.HEAL, 'target': TargetType.OWN_LEADER, 'value': 5}]),
    "Yuna, Occult Hunter": CardData("Yuna, Occult Hunter", "Yuna, Occult Hunter", 4, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 3, 5, tribes=[], effects=[
		{'type': EffectType.WARD}, {'type': EffectType.LAST_WORDS, 'raw_action_text': 'Add a Ghost and Bat to your hand.'}]),
    "Vlad, Impaler": CardData("Vlad, Impaler", "Vlad, Impaler", 8, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 5, 8, tribes=[], effects=[{'type': EffectType.FANFARE, 'process': ProcessType.HEAL, 'target': TargetType.OWN_LEADER, 'value': 5}]),
    "Shadowcrypt Memorial": CardData("Shadowcrypt Memorial", "Shadowcrypt Memorial", 3, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 0, 0, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Add 2 shadows to your cemetery.'},
        {'type': EffectType.ACTIVATE, 'raw_action_text': 'Destroy this card. Summon 2 copies of Ghost.'}]),
    "Ceres, Blue Rose Maiden": CardData("Ceres, Blue Rose Maiden", "Ceres, Blue Rose Maiden", 4, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 1, 4, tribes=[], effects=[
		{'type': EffectType.BANE},
        {       'raw_effect_text': 'At the end of your turn, restore 2 defense to your leader. If this follower is '
                                   'super-evolved, restore 4 instead and give this follower Barrier.'}]),
    "Orthrus, Hellhound Blader": CardData("Orthrus, Hellhound Blader", "Orthrus, Hellhound Blader", 2, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 2, 2, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Add 2 shadows to your cemetery.'},
        {'type': EffectType.WARD},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Necromancy (4) - Do this 2 times: "Deal 2 damage to a random enemy follower."'}]),
    "Mukan, Shadowcrypt Ward": CardData("Mukan, Shadowcrypt Ward", "Mukan, Shadowcrypt Ward", 4, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 3, 3, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Necromancy (8) - Evolve this follower.'},
        {'raw_effect_text': 'Whenever an allied Departed follower enters the field, give it Bane.'},
        {'raw_effect_text': 'When this follower evolves, summon a Ghost.'}]),
    "Balto, Dusk Bounty Hunter": CardData("Balto, Dusk Bounty Hunter", "Balto, Dusk Bounty Hunter", 3, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 3, 1, tribes=[], effects=[{'type': EffectType.FANFARE, 'raw_action_text': 'Gain Crest: Balto, Dusk Bounty Hunter.'}]),
    "Rage of Serpents": CardData("Rage of Serpents", "Rage of Serpents", 2, CardType.SPELL, ClassType.ABYSSCRAFT, 0, 0, tribes=[], effects=[{       'raw_effect_text': 'Select an enemy follower on the field or the enemy leader and deal it 3 damage. '
                                   'Deal 2 damage to your leader.'}]),
    "Cerberus, Hellfire Unleashed": CardData("Cerberus, Hellfire Unleashed", "Cerberus, Hellfire Unleashed", 8, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 6, 6, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Summon a Mimi, Right Paw Hellhound and Coco, Left Paw Hellhound. Necromancy (6) - Give all other allied followers on the field +2/+0.'},
        {'type': EffectType.ON_SUPER_EVOLVE, 'raw_action_text': 'Do this 2 times: "Reanimate (1)."'}]),
    "Medusa, Venomfang Royalty": CardData("Medusa, Venomfang Royalty", "Medusa, Venomfang Royalty", 7, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 3, 7, tribes=[], effects=[
		{'type': EffectType.RUSH},
        {'raw_effect_text': 'Can attack 3 times per turn.'},
        {'raw_effect_text': 'Follower Strike: Destroy the opposing follower.'}]),
    "Aragavy, Eternal Hunter": CardData("Aragavy, Eternal Hunter", "Aragavy, Eternal Hunter", 5, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 4, 3, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Deal 7 damage split between all enemy followers.'},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Deal 3 damage to both leaders.'}]),
    "Angelic Prism Priestess": CardData("Angelic Prism Priestess", "Angelic Prism Priestess", 3, CardType.FOLLOWER, ClassType.HAVENCRAFT, 2, 2, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Draw an amulet.'},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Select an amulet in your hand and reduce its cost by 1.'}]),
    "Holy Shieldmaiden": CardData("Holy Shieldmaiden", "Holy Shieldmaiden", 3, CardType.FOLLOWER, ClassType.HAVENCRAFT, 2, 1, tribes=[], effects=[
		{'type': EffectType.WARD}, {'type': EffectType.BARRIER}]),
    "Radiant Guiding Angel": CardData("Radiant Guiding Angel", "Radiant Guiding Angel", 5, CardType.FOLLOWER, ClassType.HAVENCRAFT, 2, 3, tribes=[], effects=[{'type': EffectType.FANFARE, 'process': ProcessType.DRAW, 'target': TargetType.OWN_LEADER, 'value': 2}]),
    "Mainyu, Darkdweller": CardData("Mainyu, Darkdweller", "Mainyu, Darkdweller", 2, CardType.FOLLOWER, ClassType.HAVENCRAFT, 2, 2, tribes=[], effects=[
		{'raw_effect_text': 'Aura'},
        {'raw_effect_text': 'Whenever you Engage an amulet, give this follower +1/+0 until the end of the turn.'}]),
    "Serene Sanctuary": CardData("Serene Sanctuary", "Serene Sanctuary", 1, CardType.FOLLOWER, ClassType.HAVENCRAFT, 0, 0, tribes=[], effects=[
		{'raw_effect_text': 'Countdown (3)'},
        {'type': EffectType.LAST_WORDS, 'process': ProcessType.DRAW, 'target': TargetType.OWN_LEADER, 'value': 2},
        {'type': EffectType.ACTIVATE, 'raw_action_text': "Advance this amulet's count by 1.", 'cost': 1}]),
    "Featherfall": CardData("Featherfall", "Featherfall", 6, CardType.SPELL, ClassType.HAVENCRAFT, 0, 0, tribes=[], effects=[{'raw_effect_text': 'Deal 3 damage to all enemy followers. Summon a Holy Falcon.'}]),
    "Sarissa, Luxspear Al-mi'raj": CardData("Sarissa, Luxspear Al-mi'raj", "Sarissa, Luxspear Al-mi'raj", 2, CardType.FOLLOWER, ClassType.HAVENCRAFT, 2, 2, tribes=[], effects=[
		{'raw_effect_text': 'Whenever an allied follower with Ward is destroyed, give this follower +1/+1.'},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Give this follower Barrier.'}]),
    "Reno, Luxwing Featherfolk": CardData("Reno, Luxwing Featherfolk", "Reno, Luxwing Featherfolk", 4, CardType.FOLLOWER, ClassType.HAVENCRAFT, 3, 5, tribes=[], effects=[
		{'raw_effect_text': 'Clash: Deal 1 damage to the enemy leader.'},
        {'type': EffectType.ON_SUPER_EVOLVE, 'raw_action_text': 'Give this follower "Can attack 2 times per turn."'}]),
    "Maeve, Guardian of Earth": CardData("Maeve, Guardian of Earth", "Maeve, Guardian of Earth", 7, CardType.FOLLOWER, ClassType.HAVENCRAFT, 5, 7, tribes=[], effects=[
		{'type': EffectType.WARD},
        {'type': EffectType.LAST_WORDS, 'raw_action_text': 'Summon a copy of a random allied amulet destroyed this match with the highest base cost.'}]),
    "Darkhaven Grace": CardData("Darkhaven Grace", "Darkhaven Grace", 2, CardType.FOLLOWER, ClassType.HAVENCRAFT, 0, 0, tribes=[], effects=[{'type': EffectType.ACTIVATE, 'process': ProcessType.HEAL, 'target': TargetType.OWN_LEADER, 'value': 1, 'cost': 1}]),
    "Dose of Holiness": CardData("Dose of Holiness", "Dose of Holiness", 3, CardType.FOLLOWER, ClassType.HAVENCRAFT, 0, 0, tribes=[], effects=[{'type': EffectType.ACTIVATE, 'process': ProcessType.HEAL, 'target': TargetType.OWN_LEADER, 'value': 1}]),
    "Skullfane of Demise": CardData("Skullfane of Demise", "Skullfane of Demise", 6, CardType.FOLLOWER, ClassType.HAVENCRAFT, 4, 4, tribes=[], effects=[{'type': EffectType.FANFARE, 'raw_action_text': 'Destroy all allied amulets. Deal X damage to all enemies. X is the number of amulets destroyed by this ability.'}]),
    "Ronavero, Darkhaven Ward": CardData("Ronavero, Darkhaven Ward", "Ronavero, Darkhaven Ward", 4, CardType.FOLLOWER, ClassType.HAVENCRAFT, 1, 3, tribes=[], effects=[
		{'type': EffectType.AMBUSH},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Select an enemy follower on the field and destroy it.'}]),
    "Lapis, Shining Seraph": CardData("Lapis, Shining Seraph", "Lapis, Shining Seraph", 8, CardType.FOLLOWER, ClassType.HAVENCRAFT, 7, 6, tribes=[], effects=[{'type': EffectType.LAST_WORDS, 'raw_action_text': 'Gain Crest: Lapis, Shining Seraph.'}]),
    "Pact of the Beast Princess": CardData("Pact of the Beast Princess", "Pact of the Beast Princess", 2, CardType.FOLLOWER, ClassType.HAVENCRAFT, 0, 0, tribes=[], effects=[
		{'raw_effect_text': 'Countdown (2)'},
        {'type': EffectType.LAST_WORDS, 'raw_action_text': 'Summon a Holyflame Tiger.'},
        {'type': EffectType.ACTIVATE, 'raw_action_text': "Advance this amulet's count by 1.", 'cost': 1}]),
    "Unholy Vessel": CardData("Unholy Vessel", "Unholy Vessel", 6, CardType.FOLLOWER, ClassType.HAVENCRAFT, 0, 0, tribes=[], effects=[{'type': EffectType.ACTIVATE, 'raw_action_text': 'Destroy this card and all followers.'}]),
    "Rodeo, Anathema of Judgment": CardData("Rodeo, Anathema of Judgment", "Rodeo, Anathema of Judgment", 7, CardType.FOLLOWER, ClassType.HAVENCRAFT, 5, 5, tribes=[TribeType.ANATHEMA], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Select a card in your hand and discard it. Summon 3 random differently named amulets from your deck that cost 3 or less.'},
        {'type': EffectType.ON_SUPER_EVOLVE, 'raw_action_text': 'Destroy a random enemy follower with the highest attack. Deal 1 damage to all enemy followers.'}]),
    "Jeanne, Saintly Knight": CardData("Jeanne, Saintly Knight", "Jeanne, Saintly Knight", 8, CardType.FOLLOWER, ClassType.HAVENCRAFT, 6, 6, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Deal 6 damage to all enemy followers. Give all other allied followers on the field +2/+4.'},
        {'type': EffectType.WARD}]),
    "Salefa, Guardian of Water": CardData("Salefa, Guardian of Water", "Salefa, Guardian of Water", 5, CardType.FOLLOWER, ClassType.HAVENCRAFT, 3, 3, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'process': ProcessType.HEAL, 'target': TargetType.OWN_LEADER, 'value': 3},
        {'type': EffectType.WARD},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Deal 3 damage to all enemy followers.'}]),
    "Elise, Electrifying Inventor": CardData("Elise, Electrifying Inventor", "Elise, Electrifying Inventor", 1, CardType.FOLLOWER, ClassType.PORTALCRAFT, 1, 1, tribes=[], effects=[{'type': EffectType.LAST_WORDS, 'raw_action_text': 'Add a Gear of Remembrance to your hand.'}]),
    "Dirk, Metal Mercenary": CardData("Dirk, Metal Mercenary", "Dirk, Metal Mercenary", 5, CardType.FOLLOWER, ClassType.PORTALCRAFT, 5, 5, tribes=[], effects=[{'type': EffectType.FANFARE, 'raw_action_text': 'Summon a Fortifier Artifact.'}]),
    "Ironheart Hunter": CardData("Ironheart Hunter", "Ironheart Hunter", 2, CardType.FOLLOWER, ClassType.PORTALCRAFT, 2, 2, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Add a Gear of Ambition to your hand.'},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Select an enemy follower on the field and deal it 3 damage.'}]),
    "Medical-Grade Assassin": CardData("Medical-Grade Assassin", "Medical-Grade Assassin", 3, CardType.FOLLOWER, ClassType.PORTALCRAFT, 2, 2, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Add an Enhanced Puppet to your hand.'},
        {       'raw_effect_text': 'Once on each of your turns, when an allied Puppetry follower enters the field, '
                                   'give it Bane.'}]),
    "Puppet Shield": CardData("Puppet Shield", "Puppet Shield", 3, CardType.SPELL, ClassType.PORTALCRAFT, 0, 0, tribes=[], effects=[{'raw_effect_text': 'Summon 2 copies of Enhanced Puppet.'}]),
    "Artifact Recharge": CardData("Artifact Recharge", "Artifact Recharge", 1, CardType.SPELL, ClassType.PORTALCRAFT, 0, 0, tribes=[], effects=[{'raw_effect_text': 'Add a Gear of Ambition and Gear of Remembrance to your hand.'}]),
    "Rukina, Resistance Leader": CardData("Rukina, Resistance Leader", "Rukina, Resistance Leader", 4, CardType.FOLLOWER, ClassType.PORTALCRAFT, 3, 3, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Add a Gear of Ambition and Gear of Remembrance to your hand.'},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Summon a Striker Artifact.'}]),
    "Lovestruck Puppeteer": CardData("Lovestruck Puppeteer", "Lovestruck Puppeteer", 2, CardType.FOLLOWER, ClassType.PORTALCRAFT, 2, 2, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Add a Puppet to your hand.'},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': "Replicate the effects of this card's Fanfare ability."}]),
    "Noah, Thread of Death": CardData("Noah, Thread of Death", "Noah, Thread of Death", 6, CardType.FOLLOWER, ClassType.PORTALCRAFT, 5, 6, tribes=[], effects=[{'type': EffectType.FANFARE, 'raw_action_text': 'Add 3 copies of Puppet to your hand. Give all Puppetry followers in your hand +1/+0.'}]),
    "Stream of Life": CardData("Stream of Life", "Stream of Life", 2, CardType.SPELL, ClassType.PORTALCRAFT, 0, 0, tribes=[], effects=[{       'raw_effect_text': 'Select an enemy follower on the field and deal it 3 damage. Add a Gear of '
                                   'Remembrance to your hand.'}]),
    "Doomwright Resurgence": CardData("Doomwright Resurgence", "Doomwright Resurgence", 5, CardType.SPELL, ClassType.PORTALCRAFT, 0, 0, tribes=[], effects=[{       'raw_effect_text': 'Select 2 Artifact followers in your hand that cost 5 or less, summon an exact copy '
                                   'of each, and give the exact copies "At the end of your opponent\'s turn, destroy '
                                   'this card."'}]),
    "Miriam, the Resolute": CardData("Miriam, the Resolute", "Miriam, the Resolute", 3, CardType.FOLLOWER, ClassType.PORTALCRAFT, 2, 3, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Add a Gear of Ambition and Gear of Remembrance to your hand.'},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': "Replicate the effects of this card's Fanfare ability."}]),
    "Sylvia, Garden Executioner": CardData("Sylvia, Garden Executioner", "Sylvia, Garden Executioner", 6, CardType.FOLLOWER, ClassType.PORTALCRAFT, 5, 5, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Select a Mode to activate.'},
        {'raw_effect_text': '1. Draw 2 cards.'},
        {'raw_effect_text': '2. Restore 4 defense to your leader.'},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Select an enemy follower on the field and destroy it.'},
        {'type': EffectType.ON_SUPER_EVOLVE, 'raw_action_text': 'Select 2 instead.'}]),
    "Liam, Crazed Creator": CardData("Liam, Crazed Creator", "Liam, Crazed Creator", 10, CardType.FOLLOWER, ClassType.PORTALCRAFT, 8, 8, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Summon 3 copies of Enhanced Puppet.'},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Give all allied Puppetry followers on the field Ward and "Last Words: Deal 2 damage to the enemy leader."'}]),
    "Alouette, Doomwright Ward": CardData("Alouette, Doomwright Ward", "Alouette, Doomwright Ward", 5, CardType.FOLLOWER, ClassType.PORTALCRAFT, 2, 4, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Add a Gear of Ambition and Gear of Remembrance to your hand.'},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Select an Artifact follower in your hand that costs 5 or less and summon an exact copy of it.'}]),
    "Ancient Cannon": CardData("Ancient Cannon", "Ancient Cannon", 5, CardType.FOLLOWER, ClassType.PORTALCRAFT, 0, 0, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Add a Gear of Ambition to your hand.'},
        {'raw_effect_text': 'Whenever you Fuse, deal 2 damage to a random enemy follower.'}]),
    "Eudie, Maiden Reborn": CardData("Eudie, Maiden Reborn", "Eudie, Maiden Reborn", 3, CardType.FOLLOWER, ClassType.PORTALCRAFT, 3, 3, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'process': ProcessType.DRAW, 'target': TargetType.OWN_LEADER, 'value': 1},
        {'type': EffectType.ON_EVOLVE, 'raw_action_text': 'Gain Crest: Eudie, Maiden Reborn.'}]),
    "Orchis, Newfound Heart": CardData("Orchis, Newfound Heart", "Orchis, Newfound Heart", 8, CardType.FOLLOWER, ClassType.PORTALCRAFT, 5, 5, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Summon a Lloyd.'},
        {'raw_effect_text': 'Whenever an allied Puppetry follower enters the field, give it Storm and Bane.'},
        {'type': EffectType.ON_SUPER_EVOLVE, 'raw_action_text': 'Summon 2 copies of Enhanced Puppet.'}]),
    "Ralmia, Sonic Boom": CardData("Ralmia, Sonic Boom", "Ralmia, Sonic Boom", 8, CardType.FOLLOWER, ClassType.PORTALCRAFT, 2, 2, tribes=[], effects=[
		{'type': EffectType.FANFARE, 'raw_action_text': 'Select 3 Artifact followers in your hand that cost 5 or less and summon an exact copy of each.'},
        {'type': EffectType.ON_SUPER_EVOLVE, 'raw_action_text': 'Give all allied Artifact followers on the field +1/+1.'}]),
}

TOKEN_CARD_DATABASE = {
    "Goblin": CardData("Goblin", "Goblin", 1, CardType.FOLLOWER, ClassType.NEUTRAL, 1, 2, tribes=[], effects=[]),
    "Silent Rider": CardData("Silent Rider", "Silent Rider", 6, CardType.FOLLOWER, ClassType.NEUTRAL, 10, 10, tribes=[], effects=[{'type': EffectType.STORM}]),
    "Servant of Cocytus": CardData("Servant of Cocytus", "Servant of Cocytus", 1, CardType.FOLLOWER, ClassType.NEUTRAL, 13, 13, tribes=[], effects=[]),
    "Demon of Purgatory": CardData("Demon of Purgatory", "Demon of Purgatory", 5, CardType.FOLLOWER, ClassType.NEUTRAL, 9, 6, tribes=[], effects=[{'type': EffectType.FANFARE, 'raw_action_text': 'Select 2 enemy followers on the field and deal 6 damage to them and the enemy leader.'}]),
    "Astaroth's Reckoning": CardData("Astaroth's Reckoning", "Astaroth's Reckoning", 10, CardType.SPELL, ClassType.NEUTRAL, 0, 0, tribes=[], effects=[{'raw_effect_text': "Set the enemy leader's max defense to 1."}]),
    "Fairy": CardData("Fairy", "Fairy", 1, CardType.FOLLOWER, ClassType.FORESTCRAFT, 1, 1, tribes=[], effects=[{'type': EffectType.RUSH}]),
    "Deepwood Bounty": CardData("Deepwood Bounty", "Deepwood Bounty", 0, CardType.SPELL, ClassType.FORESTCRAFT, 0, 0, tribes=[], effects=[{'raw_effect_text': 'Restore 1 defense to your leader.'}]),
    "Bramble Burst": CardData("Bramble Burst", "Bramble Burst", 1, CardType.SPELL, ClassType.FORESTCRAFT, 0, 0, tribes=[], effects=[{'raw_effect_text': 'Select an enemy follower on the field or the enemy leader and deal it 3 damage.'}]),
    "Knight": CardData("Knight", "Knight", 0, CardType.FOLLOWER, ClassType.SWORDCRAFT, 1, 1, tribes=[TribeType.OFFICER], effects=[]),
    "Steelclad Knight": CardData("Steelclad Knight", "Steelclad Knight", 1, CardType.FOLLOWER, ClassType.SWORDCRAFT, 2, 2, tribes=[TribeType.OFFICER], effects=[]),
    "Clay Golem": CardData("Clay Golem", "Clay Golem", 1, CardType.FOLLOWER, ClassType.NEUTRAL, 2, 2, tribes=[TribeType.GOLEM], effects=[]),
    "Guardian Golem": CardData("Guardian Golem", "Guardian Golem", 3, CardType.FOLLOWER, ClassType.NEUTRAL, 3, 3, tribes=[TribeType.GOLEM], effects=[{'type': EffectType.WARD}]),
    "Paper Shikigami": CardData("Paper Shikigami", "Paper Shikigami", 2, CardType.FOLLOWER, ClassType.NEUTRAL, 2, 1, tribes=[TribeType.SHIKIGAMI], effects=[
		{'type': EffectType.RUSH}, {'type': EffectType.LAST_WORDS, 'raw_action_text': 'Spellboost your hand.'}]),
    "Demonic Shikigami": CardData("Demonic Shikigami", "Demonic Shikigami", 3, CardType.FOLLOWER, ClassType.NEUTRAL, 3, 3, tribes=[TribeType.SHIKIGAMI], effects=[
		{'type': EffectType.RUSH}, {'type': EffectType.LAST_WORDS, 'raw_action_text': 'Spellboost your hand.'}]),
    "Magic Sediment": CardData("Magic Sediment", "Magic Sediment", 1, CardType.FOLLOWER, ClassType.NEUTRAL, 0, 0, tribes=[TribeType.EARTH_SIGIL], effects=[
		{'raw_effect_text': 'Earth Sigil'},
        {'type': EffectType.ACTIVATE, 'raw_action_text': 'Gain an earth sigil.', 'cost': 1}]),
    "Looking Smart!": CardData("Looking Smart!", "Looking Smart!", 1, CardType.SPELL, ClassType.NEUTRAL, 0, 0, tribes=[TribeType.MYSTERIA], effects=[{'raw_effect_text': 'Draw 2 cards. Deal 2 damage to a random enemy follower.'}]),
    "Celestial Shikigami": CardData("Celestial Shikigami", "Celestial Shikigami", 4, CardType.FOLLOWER, ClassType.NEUTRAL, 4, 5, tribes=[TribeType.SHIKIGAMI], effects=[
		{'type': EffectType.WARD}, {'type': EffectType.LAST_WORDS, 'raw_action_text': 'Spellboost your hand 3 times.'}]),
    "Noble Shikigami": CardData("Noble Shikigami", "Noble Shikigami", 10, CardType.FOLLOWER, ClassType.NEUTRAL, 1, 1, tribes=[TribeType.SHIKIGAMI], effects=[
		{       'raw_effect_text': 'When this follower enters the field, give it +X/+Y. X/Y is the total base '
                                   'attack/defense of allied Shikigami followers destroyed this turn.'},
        {'type': EffectType.WARD},
        {'raw_effect_text': 'Aura'}]),
    "Anne's Summoning": CardData("Anne's Summoning", "Anne's Summoning", 3, CardType.FOLLOWER, ClassType.NEUTRAL, 5, 5, tribes=[TribeType.MYSTERIA], effects=[
		{'type': EffectType.RUSH},
        {'type': EffectType.WARD},
        {'raw_effect_text': "At the end of your opponent's turn, destroy this card."}]),
    "Fire Drake Whelp": CardData("Fire Drake Whelp", "Fire Drake Whelp", 1, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 1, 1, tribes=[], effects=[{'type': EffectType.INTIMIDATE}]),
    "Vastwing Dragon": CardData("Vastwing Dragon", "Vastwing Dragon", 5, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 5, 5, tribes=[], effects=[{'type': EffectType.INTIMIDATE}]),
    "Otohime's Bodyguard": CardData("Otohime's Bodyguard", "Otohime's Bodyguard", 3, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 2, 2, tribes=[TribeType.MARINE], effects=[
		{'type': EffectType.STORM}, {'type': EffectType.WARD}]),
    "Supreme Golden Dragon": CardData("Supreme Golden Dragon", "Supreme Golden Dragon", 4, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 4, 5, tribes=[], effects=[{'type': EffectType.WARD}]),
    "Supreme Silver Dragon": CardData("Supreme Silver Dragon", "Supreme Silver Dragon", 4, CardType.FOLLOWER, ClassType.DRAGONCRAFT, 5, 4, tribes=[], effects=[{'type': EffectType.RUSH}]),
    "Skeleton": CardData("Skeleton", "Skeleton", 0, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 1, 1, tribes=[TribeType.DEPARTED], effects=[]),
    "Bat": CardData("Bat", "Bat", 1, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 1, 1, tribes=[], effects=[{'type': EffectType.DRAIN}]),
    "Ghost": CardData("Ghost", "Ghost", 1, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 1, 1, tribes=[TribeType.DEPARTED], effects=[
		{'type': EffectType.STORM},
        {'raw_effect_text': 'When this card leaves the field, banish it.'},
        {'raw_effect_text': 'At the end of your turn, banish this card.'}]),
    "Mimi, Right Paw Hellhound": CardData("Mimi, Right Paw Hellhound", "Mimi, Right Paw Hellhound", 1, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 2, 1, tribes=[], effects=[
		{'type': EffectType.RUSH}, {'type': EffectType.LAST_WORDS, 'raw_action_text': 'Deal 2 damage to the enemy leader.'}]),
    "Coco, Left Paw Hellhound": CardData("Coco, Left Paw Hellhound", "Coco, Left Paw Hellhound", 1, CardType.FOLLOWER, ClassType.ABYSSCRAFT, 1, 2, tribes=[], effects=[
		{'type': EffectType.RUSH},
        {'type': EffectType.LAST_WORDS, 'process': ProcessType.HEAL, 'target': TargetType.OWN_LEADER, 'value': 2}]),
    "Holy Falcon": CardData("Holy Falcon", "Holy Falcon", 3, CardType.FOLLOWER, ClassType.HAVENCRAFT, 2, 2, tribes=[], effects=[{'type': EffectType.STORM}]),
    "Holyflame Tiger": CardData("Holyflame Tiger", "Holyflame Tiger", 4, CardType.FOLLOWER, ClassType.HAVENCRAFT, 4, 4, tribes=[], effects=[{'type': EffectType.RUSH}]),
    "Regal Falcon": CardData("Regal Falcon", "Regal Falcon", 6, CardType.FOLLOWER, ClassType.HAVENCRAFT, 4, 4, tribes=[], effects=[{'type': EffectType.STORM}]),
    "Puppet": CardData("Puppet", "Puppet", 0, CardType.FOLLOWER, ClassType.PORTALCRAFT, 1, 1, tribes=[TribeType.PUPPETRY], effects=[
		{'type': EffectType.RUSH}, {'raw_effect_text': "At the end of your opponent's turn, destroy this card."}]),
    "Enhanced Puppet": CardData("Enhanced Puppet", "Enhanced Puppet", 1, CardType.FOLLOWER, ClassType.PORTALCRAFT, 3, 3, tribes=[TribeType.PUPPETRY], effects=[
		{'type': EffectType.RUSH}, {'raw_effect_text': "At the end of your opponent's turn, destroy this card."}]),
    "Gear of Ambition": CardData("Gear of Ambition", "Gear of Ambition", 1, CardType.FOLLOWER, ClassType.PORTALCRAFT, 0, 0, tribes=[TribeType.ARTIFACT], effects=[
		{'raw_effect_text': 'Fuse: Artifact amulets'},
        {'raw_effect_text': 'When you Fuse to this card, transform it into a Striker Artifact.'},
        {'raw_effect_text': "Can't be played."}]),
    "Gear of Remembrance": CardData("Gear of Remembrance", "Gear of Remembrance", 1, CardType.FOLLOWER, ClassType.PORTALCRAFT, 0, 0, tribes=[TribeType.ARTIFACT], effects=[
		{'raw_effect_text': 'Fuse: Artifact amulets'},
        {'raw_effect_text': 'When you Fuse to this card, transform it into a Fortifier Artifact.'},
        {'raw_effect_text': "Can't be played."}]),
    "Striker Artifact": CardData("Striker Artifact", "Striker Artifact", 3, CardType.FOLLOWER, ClassType.PORTALCRAFT, 5, 1, tribes=[TribeType.ARTIFACT], effects=[
		{'raw_effect_text': 'Fuse: Artifact cards'},
        {'raw_effect_text': 'When you Fuse to this card, transform it based on the total cost of the cards fused.'},
        {'raw_effect_text': '1: Ominous Artifact α'},
        {'raw_effect_text': '2: Ominous Artifact β'},
        {'raw_effect_text': '3 or more: Ominous Artifact γ'},
        {'type': EffectType.RUSH}]),
    "Fortifier Artifact": CardData("Fortifier Artifact", "Fortifier Artifact", 3, CardType.FOLLOWER, ClassType.PORTALCRAFT, 1, 5, tribes=[TribeType.ARTIFACT], effects=[
		{'raw_effect_text': 'Fuse: Artifact cards'},
        {'raw_effect_text': 'When you Fuse to this card, transform it based on the total cost of the cards fused.'},
        {'raw_effect_text': '1: Ominous Artifact α'},
        {'raw_effect_text': '2: Ominous Artifact β'},
        {'raw_effect_text': '3 or more: Ominous Artifact γ'},
        {'type': EffectType.WARD}]),
    "Ominous Artifact α": CardData("Ominous Artifact α", "Ominous Artifact α", 5, CardType.FOLLOWER, ClassType.PORTALCRAFT, 3, 5, tribes=[TribeType.ARTIFACT], effects=[
		{'raw_effect_text': 'Fuse: Ominous Artifact β and Ominous Artifact γ'},
        {'raw_effect_text': "When you've Fused both to this card, transform it into a Masterwork Artifact Ω."},
        {'raw_effect_text': 'At the end of your turn, restore 3 defense to your leader.'}]),
    "Ominous Artifact β": CardData("Ominous Artifact β", "Ominous Artifact β", 5, CardType.FOLLOWER, ClassType.PORTALCRAFT, 4, 4, tribes=[TribeType.ARTIFACT], effects=[{'raw_effect_text': 'At the end of your turn, deal 3 damage to the enemy leader.'}]),
    "Ominous Artifact γ": CardData("Ominous Artifact γ", "Ominous Artifact γ", 5, CardType.FOLLOWER, ClassType.PORTALCRAFT, 5, 3, tribes=[TribeType.ARTIFACT], effects=[{'raw_effect_text': 'At the end of your turn, deal 3 damage to all enemy followers.'}]),
    "Masterwork Artifact Ω": CardData("Masterwork Artifact Ω", "Masterwork Artifact Ω", 10, CardType.FOLLOWER, ClassType.PORTALCRAFT, 10, 10, tribes=[TribeType.ARTIFACT], effects=[
		{'type': EffectType.FANFARE, 'process': ProcessType.HEAL, 'target': TargetType.OWN_LEADER, 'value': 5},
        {'type': EffectType.STORM},
        {'type': EffectType.WARD},
        {'raw_effect_text': 'Aura'}]),
    "Lloyd": CardData("Lloyd", "Lloyd", 3, CardType.FOLLOWER, ClassType.PORTALCRAFT, 1, 6, tribes=[TribeType.PUPPETRY], effects=[
		{'type': EffectType.WARD},
        {'raw_effect_text': "Your opponent can't select any cards other than this one for abilities."}]),
}

