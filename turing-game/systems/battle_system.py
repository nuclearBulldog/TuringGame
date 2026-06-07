import random
import json
import settings

class Move:
    """A battle move. Damage < 0 means healing."""
    def __init__(self, name, damage, description=''):
        self.name = name
        self.damage = damage
        self.description = description

class BattleSystem:
    """Turn-based battle rules with no drawing code."""

    def __init__(self, encounter_id='report_due'):
        data_path = settings.ENCOUNTER_DIR / 'encounters.json'

        with open(data_path, 'r') as file:
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

        self.player_won = False
        self.turns_taken = 0
        self.total_damage_dealt = 0
        self.moves_used = []

        self.score = 0
        self.summary_items = []

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

        self.moves_used.append(move.name)
        self.turns_taken += 1

        if move.name == "Use ChatGPT to write the whole thing":
            self.enemy_hp = 0
            self.message = 'ChatGPT Finished the entire report! ...Your tutor wants to speak with you outside!'
            self.player_won = False
            self.generate_results(win=False)
            return

        if move.damage >= 0:
            actual_damage = min(move.damage, self.enemy_hp)
            self.total_damage_dealt += actual_damage
            self.enemy_hp -= actual_damage
            self.message = f'You decided to {move.name}, {move.description}... dealing {actual_damage} damage!'
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

        if "Use ChatGPT to write the whole thing" in self.moves_used:
            self.score = 0
            self.summary_items.append(("Turned in the assignment", True))
            self.summary_items.append(("Caught by AI Detector", False))
            self.summary_items.append(("Academic Integrity Penalty", False))
            self.summary_items.append(("F in the course", False))
            return

        if win:
            self.score += 100
            self.summary_items.append((f'Defeated {self.enemy_name}', True))

            hp_percent = self.player_hp / self.player_max_hp
            if hp_percent == 1.0:
                self.score += 50
                self.summary_items.append(("Flawless Victory (AMAZING 100%!)", True))
            elif hp_percent >= 0.5:
                self.score += 200
                self.summary_items.append(("Not too bad (>=50%)", True))
            else:
                self.summary_items.append(("Barely survived...(Meh <=50%", False))

            if self.turns_taken <= 3:
                self.score += 200
                self.summary_items.append((f'WOW, That was fast: {self.turns_taken} turns', True))
            else:
                self.summary_items.append((f'Slow and Steady {self.turns_taken} turns', False))

            if "Use ChatGPT to write the whole thing" in self.moves_used:
                self.score -= 500
                self.summary_items.append(('Academic Dishonesty', False))

            if self.score < 1:
                self.summary_items.append(('Failed the assignment anyway', False))

        else:
            self.score += 10
            self.summary_items.append(('Failed the assignment', False))
            self.summary_items.append((f'Dealt {self.total_damage_dealt} damage', True))
            self.summary_items.append((f'Survived {self.turns_taken} turns', True))

    @property
    def battle_over(self):
        return self.player_hp <= 0 or self.enemy_hp <= 0