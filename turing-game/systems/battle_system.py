import random

# AI Generated BoilerPlate

class Move:
    """A battle move. Damage < 0 means healing."""

    def __init__(self, name, damage, description=''):
        self.name = name
        self.damage = damage
        self.description = description


class BattleSystem:
    """Turn-based battle rules with no drawing code."""

    def __init__(self):
        self.player_name = 'You'
        self.enemy_name = 'Report Due'
        self.player_hp = 100
        self.player_max_hp = 100
        self.enemy_hp = 80
        self.enemy_max_hp = 80
        self.turn = 'player'
        self.message = "Uh Oh, looks like you have a report due, it's on monday though...\nA whole weekend, nice."
        self.moves = [
            Move('Studying and trying to get it done', 10, 'Might not be strong enough'),
            Move('Use ChatGPT to write the whole thing', 0, 'It will definitely get all of the work done'),
            Move('Use AI to help with gathering information.', -12, 'Restore a little HP.'),
        ]

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
