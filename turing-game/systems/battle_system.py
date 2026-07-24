import random

from systems import encounter_data as encounter_db


class Move:
    """A battle move. Damage < 0 means healing.

    ``outcome`` is an optional dict that, when present, forces the battle to a
    scripted end when the move is used (see ``BattleSystem._apply_outcome``).
    """
    def __init__(self, name, damage, description='', outcome=None):
        self.name = name
        self.damage = damage
        self.description = description
        self.outcome = outcome

class BattleSystem:
    """Turn-based battle rules with no drawing code."""

    def __init__(self, encounter_id='report_due'):
        database = encounter_db.load_encounters()

        encounter_data = database.get(encounter_id)

        if not encounter_data:
            raise ValueError(f"Encounter ID: '{encounter_id}' not found in data file!")

        self.player_name = 'You'
        self.player_hp = 100
        self.player_max_hp = 100

        self.enemy_name = encounter_data['enemy_name']
        # Display-only: which enemy sprite the battle scene blits. Defaults so
        # encounters without art (and the test fixtures) still construct.
        self.sprite_key = encounter_data.get('sprite', 'report_due')
        self.enemy_hp = encounter_data['enemy_hp']
        self.enemy_max_hp = encounter_data['enemy_max_hp']
        self.message = encounter_data['intro_message']
        self.turn = 'player'

        self.player_won = False
        self.turns_taken = 0
        self.total_damage_dealt = 0
        self.moves_used = []

        self.score = 0
        self.summary_items = []

        self.moves = []
        for move_data in encounter_data['moves']:
            new_move = Move(
                name=move_data['name'],
                damage=move_data['damage'],
                description=move_data['description'],
                outcome=move_data.get('outcome'),
            )
            self.moves.append(new_move)

    def clamp_hp(self):
        self.player_hp = max(0, min(self.player_hp, self.player_max_hp))
        self.enemy_hp = max(0, min(self.enemy_hp, self.enemy_max_hp))

    def player_use_move(self, move_index):
        move = self.moves[move_index]

        self.moves_used.append(move.name)
        self.turns_taken += 1

        if move.outcome and move.outcome.get('instant_end'):
            self._apply_outcome(move.outcome)
            return

        if move.damage >= 0:
            actual_damage = min(move.damage, self.enemy_hp)
            self.total_damage_dealt += actual_damage
            self.enemy_hp -= actual_damage
            self.message = (
                f'You decided to {move.name}, {move.description}... '
                f'dealing {actual_damage} damage!'
            )
        else:
            heal = -move.damage
            self.player_hp += heal
            self.message = f'{self.player_name} used {move.name}! Restored {heal} HP.'

        self.clamp_hp()

        if self.enemy_hp > 0:
            self.turn = 'enemy'
        else:
            self.message = f'{self.enemy_name} fainted!'
            self.player_won = True
            self.generate_results(win=True)

    def _apply_outcome(self, outcome):
        """Force the battle to a scripted end defined by a move's JSON outcome.

        Bypasses the normal scoring in ``generate_results``: scripted outcomes
        always score 0 and show their own summary items. Setting ``enemy_hp`` to
        0 flips ``battle_over`` so the battle state advances to the result screen.
        """
        self.enemy_hp = 0
        self.message = outcome['message']
        self.player_won = outcome['win']
        self.score = 0
        self.summary_items = [tuple(item) for item in outcome['summary_items']]

    def enemy_take_turn(self):
        damage = random.choice([5, 7, 9])
        self.player_hp -= damage
        self.clamp_hp()

        if self.player_hp > 0:
            self.message = f'{self.enemy_name} attacked! {damage} damage.'
            self.turn = 'player'
        else:
            self.message = f'{self.player_name} fainted!'
            self.player_won = False
            self.generate_results(win=False)

    def generate_results(self, win):
        """ calculates final score, thus adding to the interactive learning part """
        self.summary_items = []
        self.score = 0

        if win:
            self.score += 100
            self.summary_items.append((f'Defeated {self.enemy_name}', True))

            hp_percent = self.player_hp / self.player_max_hp
            if hp_percent == 1.0:
                self.score += 200
                self.summary_items.append(("Flawless Victory (AMAZING 100%!)", True))
            elif hp_percent >= 0.5:
                self.score += 50
                self.summary_items.append(("Not too bad (>=50%)", True))
            else:
                self.summary_items.append(("Barely survived... (Meh, <50%)", False))

            if self.turns_taken <= 3:
                self.score += 200
                self.summary_items.append((f'WOW, That was fast: {self.turns_taken} turns', True))
            else:
                self.summary_items.append((f'Slow and Steady {self.turns_taken} turns', False))

        else:
            self.score += 10
            self.summary_items.append(('Failed the assignment', False))
            self.summary_items.append((f'Dealt {self.total_damage_dealt} damage', True))
            self.summary_items.append((f'Survived {self.turns_taken} turns', True))

    @property
    def battle_over(self):
        return self.player_hp <= 0 or self.enemy_hp <= 0
