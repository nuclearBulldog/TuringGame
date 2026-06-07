import random
import json
import os

class Move:
    """A battle move. Damage < 0 means healing."""
    def __init__(self, name, damage, description=''):
        self.name = name
        self.damage = damage
        self.description = description

class BattleSystem:
    """Turn-based battle rules with no drawing code."""

    def __init__(self, encounter_id='report_due'):
        with open('../data/encounters.json', 'r') as file:
            database = json.load(file)

        encounter_data = database.get(encounter_id)

        if not encounter_data:
            raise ValueError(f"Encounter ID: '{encounter_id}' not found in data file!")

        self.player_name = 'You'
        self.player_hp = 100
        self.player_max_hp = 100

        self.enemy_name = encounter_data['enemy_name']
        self.enemy_hp = encounter_data['enemy_hp']
        self.enemy_max_hp = encounter_data['enemy_max_hp']
        self.message = encounter_data['intro_message']
        self.turn = 'player'

        # 5. Build the Move objects dynamically
        self.moves = []
        for move_data in encounter_data['moves']:
            new_move = Move(
                name=move_data['name'],
                damage=move_data['damage'],
                description=move_data['description']
            )
            self.moves.append(new_move)

    def clamp_hp(self):
        self.player_hp = max(0, min(self.player_hp, self.player_max_hp))
        self.enemy_hp = max(0, min(self.enemy_hp, self.enemy_max_hp))

    def player_use_move(self, move_index):
        move = self.moves[move_index]
        if move.damage >= 0:
            self.enemy_hp -= move.damage
            self.message = f'You decided to deal with this report by {move.name}'
        else:
            heal = -move.damage
            self.player_hp += heal
            self.message = f'{self.player_name} used {move.name}! Restored {heal} HP.'

        self.clamp_hp()

        if self.enemy_hp > 0:
            self.turn = 'enemy'
        else:
            self.message = f'{self.enemy_name} fainted!'

    def enemy_take_turn(self):
        damage = random.choice([5, 7, 9])
        self.player_hp -= damage
        self.clamp_hp()
        if self.player_hp > 0:
            self.message = f'{self.enemy_name} attacked! {damage} damage.'
            self.turn = 'player'
        else:
            self.message = f'{self.player_name} fainted!'

    @property
    def battle_over(self):
        return self.player_hp <= 0 or self.enemy_hp <= 0