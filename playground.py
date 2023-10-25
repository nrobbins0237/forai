import random
import time
from narratives import player_narratives, enemy_narratives

def create_colored_gradient_bar(current, maximum, length=20):
    blocks = ['█', '▉', '▊', '▋', '▌', '▍', '▎', '▏']
    percentage = current / maximum
    full_blocks = int(length * percentage)
    remainder = (length * percentage) - full_blocks

    if remainder == 0:
        partial_block = ''
    else:
        partial_index = int(remainder * 8) - 1
        partial_block = blocks[partial_index]

    bar = blocks[0] * full_blocks + partial_block
    bar = bar.ljust(length, ' ')
    bar += f' {current}/{maximum}'
    return bar

def create_mana_gradient_bar(current, maximum, length=20):
    blocks = ['█', '▉', '▊', '▋', '▌', '▍', '▎', '▏']

    percentage = current / maximum
    full_blocks = int(length * percentage)
    remainder = (length * percentage) - full_blocks

    if remainder == 0:
        partial_block = ''
    else:
        partial_index = int(remainder * 8) - 1
        partial_block = blocks[partial_index]

    bar = blocks[0] * full_blocks + partial_block
    bar = bar.ljust(length, ' ')
    bar += f' {current}/{maximum}'
    return bar

def pause(message="Press Enter to continue..."):
    print()  # Print an empty line for spacing
    input(message)
    
def dialogue_pause(message="..."):
    print()  # Print an empty line for spacing
    input(message)
    

class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description

class Consumable(Item):
    def __init__(self, name, description, effect, amount):
        super().__init__(name, description)
        self.effect = effect  # This should be a string like "health" or "mana".
        self.amount = amount  # Amount to restore.

    def use(self, target):
        if self.effect == "health":
            target.health += self.amount
            if target.health > target.max_health:
                target.health = target.max_health
        elif self.effect == "mana":
            target.mana += self.amount
            if target.mana > target.max_mana:
                target.mana = target.max_mana
        print(f"{target.name} restored {self.amount} {self.effect}!")

class KeyItem(Item):
    def __init__(self, name, description, quest_related=True):
        super().__init__(name, description)
        self.quest_related = quest_related

    def use(self, target=None):
        if self.quest_related:
            print(f"{self.name} is a key item and cannot be used directly.")
        else:
            # Handle non-quest-related key item interactions (if any)
            print(f"You inspect {self.name}. {self.description}")


class Inventory:
    def __init__(self):
        self.items = []

    def __iter__(self):
        return iter(self.items)

    def add_item(self, item):
        self.items.append(item)
        print(f"{item.name} has been added to your inventory.")

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
            print(f"{item.name} has been removed from your inventory.")
            pause()

    def display(self):
        if not self.items:
            print("Your inventory is empty.")
            return

        for idx, item in enumerate(self.items, 1):
            print(f"{idx}. {item.name} - {item.description}")

    def select_item(self):
        self.display()

        while True:
            item_choice = input("Which item do you want to select? (Enter number or 'b' to go back): ")
            if item_choice.isdigit() and 1 <= int(item_choice) <= len(self.items):
                return self.items[int(item_choice) - 1]
            elif item_choice == 'b':
                return None
            print("Invalid choice! Please select a valid item number.")

    def use_item(self, item, target=None):
        if isinstance(item, Consumable):
            item.use(target)
            self.remove_item(item)
        elif isinstance(item, KeyItem):
            item.use(target)  # This will generally just inform the player that the item can't be used directly
        else:
            print(f"{item.name} cannot be used this way.")

class Skill:
    def __init__(self, name, mana_cost, min_value, max_value, skill_type='damage', level_required=1, description=""):
        self.name = name
        self.mana_cost = mana_cost
        self.min_value = min_value
        self.max_value = max_value
        self.skill_type = skill_type  # 'damage' or 'heal'
        self.level_required = level_required
        self.description = description

    def use(self, user, target=None):
        if user.mana >= self.mana_cost:
            value = random.randint(self.min_value, self.max_value)
            user.mana -= self.mana_cost
            if self.skill_type == 'damage':
                target.health -= value
                print(f"{user.name} used {self.name} on {target.name} for {value} damage!")
                if target.health <= 0:
                    print(f"{target.name} has been defeated!")
            elif self.skill_type == 'heal':
                user.health += value
                if user.health > user.max_health:
                    user.health = user.max_health
                print(f"{user.name} used {self.name} and healed for {value} health!")
        else:
            print("Not enough mana!")

fireball = Skill("Fireball", 15, 10, 20, 'damage')
healing_touch = Skill("Healing Touch", 10, 10, 20, 'heal')
thunder_strike = Skill("Thunder Strike", 20, 15, 30, 'damage', level_required=5)


class Character:

    def __init__(self, name, health, attack_power):
        self.name = name
        self.health = health
        self.attack_power = attack_power
        # Assuming default values for mana attributes
        
    def display_basic_status(self):
        print(f"{self.name} Health: ", end='')
        print(f"{self.name} Mana: ", end='')  # Displaying the mana bar
# Quest class
# Adding back the display_quest method and re-running the example
class Reward:
    def __init__(self, gold=0, xp=0, items=None, skills=None, stat_points=None, story=None):
        self.gold = gold
        self.xp = xp
        self.items = items or []
        self.skills = skills or []
        self.stat_points = stat_points or {}
        self.story = story

class Quest:
    def __init__(self, name, description, goal, reward, key_item_name=None):
        self.name = name
        self.description = description
        self.goal = goal
        self.progress = 0
        self.completed = False
        self.reward = reward
        self.next_quest = None  # The subsequent quest in the sequence
        self.status = "Not Started"  # Quest status
        self.key_item_name = key_item_name
        self.rewards = []


    def add_reward(self, reward):
        self.rewards.append(reward)

    def set_next_quest(self, next_quest):
        self.next_quest = next_quest

    def update_progress(self):
        """Update the progress of the quest."""
        if self.key_item_name and not self.check_for_key_item(self.key_item_name):
            print(f"You need the {self.key_item_name} to progress in this quest!")
            return
        if not self.completed:
            self.progress += 1
            self.status = "In Progress"
            if self.progress >= self.goal:
                self.completed = True
                self.status = "Completed"
                reward_message = f"Quest '{self.name}' completed!"
                for reward in self.rewards:
                    reward_message += f" {reward}"
                print(reward_message)
                if self.next_quest:
                    print(f"You've unlocked a new quest: '{self.next_quest.name}'!")

    def display_quest(self):
        print(f"\nQuest: {self.name}")
        print(self.description)
        print(f"Progress: {self.progress}/{self.goal}")
        print(f"Status: {self.status}\n")
        if self.completed:
            print("Rewards:")
            for reward in self.rewards:
                print(f"- {reward}")
                
    def check_for_key_item(self, item_name):
        return item_name in [item.name for item in self.player.inventory.items]

class QuestManager:
    def __init__(self, player):
        self.player = player
        self.active_quests = []

    def add_quest(self, quest):
        self.active_quests.append(quest)
        print(f"You have accepted the quest: {quest.name}!")

    def check_quest_completion(self):
        for quest in self.active_quests:
            if quest.completed:
                # Handle rewards (like giving the player gold, XP, weapons, etc.)
                # This part depends on your game's logic and Player class methods
                if quest.next_quest:
                    self.add_quest(quest.next_quest)
                self.active_quests.remove(quest)

    def display_active_quests(self):
        if not self.active_quests:
            print("No active quests.")
            return
        for quest in self.active_quests:
            quest.display_quest()

# Weapons Class
class Weapon:

    def __init__(self,
                 name,
                 attack_boost,
                 durability,
                 description,
                 drop_rate=10):
        self.name = name
        self.attack_boost = attack_boost
        self.durability = durability
        self.description = description
        self.drop_rate = drop_rate
        self.upgraded = False

    def decrease_durability(self):
        self.durability -= 1
        if self.durability <= 0:
            return True  # Indicate that the weapon broke
        return False
    
    def upgrade(self, player):
        base_cost = 2  # Fixed base cost for upgrades
        multiplier = 2  # Multiplier for dynamic upgrade cost
        upgrade_cost = base_cost + multiplier * self.attack_boost
        attack_boost_percentage = 1.00
        durability_increase = 3  # Increase in durability
        
        # Notify the player of the upgrade cost
        print(f"The cost to upgrade this weapon is {upgrade_cost} gold.")
        confirmation = input("Do you want to proceed with the upgrade? (y/n): ").lower()
        
        if confirmation == "y":
            # Check if player has enough gold
            if player.gold < upgrade_cost:
                return "You don't have enough gold to upgrade your weapon."
    
            # Check if the weapon has already been upgraded
            if self.upgraded:
                return "This weapon has already been upgraded."
    
            # Apply the upgrades
            old_attack_boost = self.attack_boost
            self.attack_boost += int(self.attack_boost * attack_boost_percentage)
            player.attack_power += (self.attack_boost - old_attack_boost)
            self.durability += durability_increase
            player.gold -= upgrade_cost
            self.upgraded = True
    
            return f'Your weapon has been upgraded! It now provides an attack boost of {self.attack_boost} and has a durability of {self.durability}.'
            
        else:
            return "Upgrade canceled."

        
class Player(Character):

    def __init__(self, name, experience=0, level=1):
        health = 50 + (10 * (level - 1))
        max_health = health
        attack_power = 5 + (level - 1)
        mana = 30 + (5 * (level - 1))
        max_mana = mana
        super().__init__(name, health, attack_power)
        self.experience = experience
        self.level = level
        self.mana = mana
        self.max_health = max_health
        self.max_mana = max_mana
        self.is_defending = False
        self.gold = 0
        self.equipped_weapon = None
        self.inventory = Inventory()
        self.quest_manager = QuestManager(self)
        self.skills = []
    
    # Add a method to accept quests
    def accept_quest(self, quest):
        self.quest_manager.add_quest(quest)

    # Check for quest completions (can be called after battles or actions that progress quests)
    def check_quests(self):
        self.quest_manager.check_quest_completion()

    # Display all active quests
    def display_quests(self):
        self.quest_manager.display_active_quests()

    # Handle rewards from quests or other events
    def apply_reward(self, reward):
        self.gold += reward.gold
        self.gain_experience(reward.xp)
        for item in reward.items:
            self.inventory.add_item(item)
        for skill in reward.skills:
            self.learn_skill(skill)
        for stat, points in reward.stat_points.items():
            self.increase_stat(stat, points)
        if reward.story:
            self.progress_story(reward.story)
        
    def equip_weapon(self, weapon):
        # If a weapon is already equipped, remove its boost before equipping the new one
        
        if self.equipped_weapon:
            self.attack_power -= self.equipped_weapon.attack_boost
        
        # Equip the new weapon and add its attack boost
        self.equipped_weapon = weapon
        self.attack_power += weapon.attack_boost
        print(f"You have equipped the {weapon.name}! It provides an attack boost of {weapon.attack_boost}.")

    def xp_to_next_level(self):
        return 10 * (self.level**2)

    def display_status(self):
        print("\n" + "-" * 30)
        print(f"{self.name}'s Health: {self.health}")
        print(f"{self.name}'s Mana: {self.mana}")
        print(f"Level: {self.level}")
        print(f"Attack Power: {self.attack_power}")
        print(f"Experience: {self.experience}/{10 * (self.level ** 2)}")
        print(f"Gold: {self.gold}")
        print("-" * 30 + "\n")
    
    def learn_skill(self, skill):
        if skill not in self.skills:
            self.skills.append(skill)
            print(f"{self.name} has learned a new skill: {skill.name}!")
    
    def check_for_new_skills(self):
        # Mapping of levels to the skills they unlock
        level_to_skill = {
            2: fireball,
            3: healing_touch,
            5: thunder_strike,
            # You can add more levels and skills as needed
            # 5: ice_spell,
            # 10: lightning_bolt,
            # etc.
            }

        # Check if there's a new skill to learn at the player's current level
        if self.level in level_to_skill:
            self.learn_skill(level_to_skill[self.level])
    
    def attack(self, enemy):
        base_damage = random.randint(self.level + 2, self.level + 5)  # Example fixed range based on player's level
        if self.equipped_weapon:
            damage = base_damage + self.equipped_weapon.attack_boost
            weapon_narrative = random.choice(player_narratives[self.equipped_weapon.name])
            print(f"{self.name} {weapon_narrative} dealing {damage} damage!")
            
            # Decrease weapon durability
            if self.equipped_weapon.decrease_durability():
                # If weapon broke
                self.attack_power -= self.equipped_weapon.attack_boost
                print(f"Your {self.equipped_weapon.name} broke!")
                # Optionally, unequip the weapon (uncomment the next line if desired)
                self.equipped_weapon = None
                
        else:
            damage = base_damage
            print(f"{self.name} attacked {enemy.name} for {damage} damage!")
        enemy.health -= damage
        return damage

    def defend(self):
        self.is_defending = True
        print(f"{self.name} is defending!")
        #time.sleep(1)

    def gain_experience(self, amount):
        self.experience += amount
        print(f"{self.name} gained {amount} experience!")
        #time.sleep(1)

        # Use a loop to account for potential multiple level-ups
        while self.experience >= 10 * (self.level**2):
            self.level_up()

    def level_up(self):
        # Save the old max values
        old_max_health = self.max_health
        old_attack_power = self.attack_power
        old_max_mana = self.max_mana

        # Adjust level and stats
        self.level += 1
        self.max_health += 10
        self.attack_power += 1
        self.max_mana += 5

        # Refresh the current health and mana to the new max values
        self.health = self.max_health
        self.mana = self.max_mana
        
        # Check for new skills after leveling up
        self.check_for_new_skills()

        # Display level-up information
        print(f"{self.name} has leveled up to level {self.level}!")
        print(f"Max Health: {old_max_health} --> {self.max_health}")
        print(f"Attack Power: {old_attack_power} --> {self.attack_power}")
        print(f"Max Mana: {old_max_mana} --> {self.max_mana}")

    def display_skills(self, enemy):
        print("Available skills:")
        for index, skill in enumerate(self.skills, 1):
            if self.level >= skill.level_required:
                print(f"{index}. {skill.name} (Mana cost: {skill.mana_cost})")
        
        choice = input("Select a skill by number: ")
        try:
            selected_skill = self.skills[int(choice) - 1]
            
            if hasattr(selected_skill, 'skill_type'):
                # Checking if it's a damaging skill or a healing skill
                if selected_skill.skill_type == 'damage':
                    selected_skill.use(self, enemy)
                else:
                    selected_skill.use(self)
            else:
                print("This skill doesn't have a defined type.")
        
        except (IndexError, ValueError):
            print("Invalid skill choice.")
            
    def recover_mana(self, amount):
        self.mana += amount
        if self.mana > self.max_mana:  # Ensuring mana doesn't exceed its maximum value
            self.mana = self.max_mana
            
    def use_skill(self, skill, target):
        skill.use(self, target)
                
    

class Enemy(Character):
    def __init__(self, player_level):
        enemy = random.choice(self.enemies)
        adjusted_health = enemy['health'] + (5 * player_level)
        adjusted_power = enemy['attack_power'] + player_level
        self.max_health = adjusted_health  # Initializing max_health attribute
        self.base_experience = enemy['experience']
        self.base_gold = enemy['base_gold']
        self.drop_rate = enemy['drop_rate']
        self.drops = enemy['drops']
        super().__init__(enemy['name'], adjusted_health, adjusted_power)

    health_potion = Consumable("Health Potion", "Restores 20 health.", "health", 20)
    mana_potion = Consumable("Mana Potion", "Restores 15 mana.", "mana", 15)
    
    enemies = [
    {
        "name": "Goblin",
        "health": 15,
        "attack_power": 3,
        "experience": 5,
        "base_gold": 5,
        "drop_rate": 30,  # 30% chance to drop an item
        "drops": [health_potion],  # Goblin can drop a health potion
        "weapons": [
            Weapon("Rusty Sword", 3, 5, "An old and rusty sword."),
            Weapon("Goblin Dagger", 2, 7, "A small but sharp dagger."),
            Weapon("Broken Shield", 1, 8,
                   "Not great for defense, but it can be used to bash.")
        ]
    },
    {
        "name": "Troll",
        "health": 30,
        "attack_power": 4,
        "experience": 10,
        "base_gold": 10,
        "drop_rate": 50,  # 50% chance to drop an item
        "drops": [mana_potion],  # Troll can drop a mana potion
        "weapons": [
            Weapon("Troll Club", 5, 7, "A large club used by trolls."),
            Weapon("Stone Hammer", 6, 6, "A heavy stone hammer."),
            Weapon("Trollish Axe", 4, 10,
                   "A hefty axe with a blunt blade.")
        ]
    }
]


    def gold_drop(self):
      return self.base_gold + random.randint(0, max(0, self.health // 10 + self.attack_power))
    
    def attack(self, target):
      dropped_weapon_name = self.weapon_drop().name
      narrative = random.choice(enemy_narratives[self.name][dropped_weapon_name])
      print(narrative)
      #time.sleep(1)
      damage = random.randint(0, self.attack_power)
      target.health -= damage
      if target.health <= 0:
          print(f"{target.name} has been defeated!")
          #time.sleep(1)
  
      return damage
    
    def weapon_drop(self):
        enemy_data = next(e for e in self.enemies if e['name'] == self.name)
        return random.choice(enemy_data['weapons'])

# Function Definitions
def offer_quest(quest):
    print(f"{quest.name}\n{quest.description}")
    choice = input("Do you accept this quest? [y/n] ").lower()
    if choice == 'y':
        return True
    else:
        print("You decline the quest.")
        return False


def combat(player, enemy, quest=None):
    enemy = Enemy(player.level)
    print(f"\nA wild {enemy.name} appears!\n")
    #time.sleep(1)  # Pause to let the player read

    while player.health > 0 and enemy.health > 0:

        print("\n" + "-" * 40)
        print("PLAYER STATUS")
        print(f"{player.name: <15}")
        print("Health: ", end='')
        print(create_colored_gradient_bar(player.health, player.max_health))
        print("Mana:   ", end='')
        print(create_colored_gradient_bar(player.mana, player.max_mana))
        print("-" * 40)
        print("ENEMY STATUS")
        print(f"{enemy.name: <15}")
        print("Health: ", end='')
        print(create_colored_gradient_bar(enemy.health, enemy.max_health))
        print("-" * 40)
        print("What would you like to do?")
        print("1. Fight")
        print("2. Use Skills")
        print("3. Check Status")
        print("4. Run Away")
        print("5. Access Inventory")
        print("9. [DEBUG] Gain 500 XP")  # Debug option to gain XP
        print("-" * 40)
        action = input("Enter your choice or skill shortcut: ")
        print("-" * 40)

        if action == '1' or action == 'f':
            player_damage = player.attack(enemy)
            print(f"{player.name} dealt {player_damage} damage to {enemy.name}!")
        elif action == '2' or action == 'skills':
            player.display_skills(enemy)
        elif action == '3' or action == 'status':
            player.display_status()
        elif action == '4' or action == 'r':
            print(f"{player.name} runs away!")
            return
        elif action == '5':
            selected_item = player.inventory.select_item()
            if selected_item:
                player.inventory.use_item(selected_item, target=player)
        elif action == 'h':
            player.heal()
        elif action == 'd':
            player.defend()
        elif action == '9':
            player.gain_experience(500)
        else:
            print("\nInvalid choice. Please choose a valid option or use a skill shortcut.\n")
            #time.sleep(1)
        #print ("\n")

        if enemy.health > 0:
            enemy_damage = enemy.attack(player)
            print(f"{enemy.name} dealt {enemy_damage} damage to {player.name}!")
            #time.sleep(1)
            player.recover_mana(5)
            pause()

        if enemy.health <= 0:
            print(f"{enemy.name} has been defeated!")
            experience_gain = int(enemy.base_experience * (1 + 0.1 * player.level))
            player.gain_experience(experience_gain)
            pause()
            drop_chance = random.randint(1, 100)
            if drop_chance <= enemy.drop_rate:
                dropped_item = random.choice(enemy.drops)
                print(f"{enemy.name} dropped a {dropped_item.name}!")
                player.inventory.add_item(dropped_item)
            
            gold_gained = enemy.gold_drop()
            player.gold += gold_gained
            print(f"You have earned {gold_gained} gold!")

            dropped_weapon = None
            weapon_drop_chance = random.randint(1, 100)
            if weapon_drop_chance <= 50:
                dropped_weapon = enemy.weapon_drop()
                print(f"\nThe {enemy.name} has dropped a {dropped_weapon.name}!")
                

            while True:
                pause()
                print("-" * 40)
                print("Post-battle actions:")
                print("1. View Inventory")
                print("2. Upgrade Weapon")
                
                # If there's a dropped weapon, display the option to equip it
                if dropped_weapon:
                    print("3. Equip", dropped_weapon.name)
                else:
                    print("3. Equip a weapon from inventory")

                print("4. Continue")
                print("-" * 40)
                print("PLAYER STATUS")
                print(f"{player.name: <15}")
                print("Health: ", end='')
                print(create_colored_gradient_bar(player.health, player.max_health))
                print("Mana:   ", end='')
                print(create_colored_gradient_bar(player.mana, player.max_mana))
                print("-" * 40)
                choice = input("Enter your choice: ")

                if choice == '1':
                    selected_item = player.inventory.select_item()
                    if selected_item:
                        player.inventory.use_item(selected_item, target=player)

                elif choice == '2':
                    if player.equipped_weapon:
                        print(player.equipped_weapon.upgrade(player))
                    else:
                        print("You don't have a weapon equipped to upgrade.")

                elif choice == '3':
                    # Check if a weapon was dropped. If not, equip from inventory.
                    if dropped_weapon:
                        player.equip_weapon(dropped_weapon)
                    else:
                        # Code to equip a weapon from the inventory goes here.
                        # For example, if you have a function like `player.choose_and_equip_from_inventory()`:
                        # player.choose_and_equip_from_inventory()
                        pass

                elif choice == '4':
                    break  # Break out of the post-battle actions loop to continue with the next enemy or end combat

                else:
                    print("Invalid choice. Please select a valid option.")

        if player.health <= 0:
            print(f"\n{player.name} has been defeated!\n")




# Main function
def main():
    print("Welcome to the Text RPG!")
    name = input("Enter your character's name: ")
    player = Player(name)

    print("You enter a small village. The village elder approaches you with a worried look.")
    # Commenting out the goblin quest
    # goblin_quest = Quest("The Goblin Menace", "Defeat the goblins plaguing the village.", 5)
    # quest_accepted = offer_quest(goblin_quest)

    # if quest_accepted:
    #     print("You have accepted the quest!")
    # else:
    #     print("You continue on your journey without the burden of the quest.")
    # time.sleep(1)

    while player.health > 0:
        enemy = Enemy(player.level)  # Create enemy instance here
        combat(player, enemy)  # Removed the goblin_quest parameter


# Entry point
if __name__ == "__main__":
    main()
    
