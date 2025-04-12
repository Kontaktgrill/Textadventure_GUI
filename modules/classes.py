import pickle
import json
import os
import time
import random
from typing import List, Dict



class Slowprint:
    @staticmethod
    def slow_print(text: str, delay: float = 0.0005):
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()  # Newline after the entire text

class Story:
    def __init__(self, file_name: str):
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, file_name)
        self.data = self.load_data(file_path)

    def load_data(self, file_path: str) -> dict:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def get_text(self, scene: str) -> str:
        for item in self.data["rooms"]:
            if item["name"] == scene:
                return item["description"]
        return ""

    def get_disclaimer(self) -> str:
        return self.data["game"].get("disclaimer", "")

class Character:
    def __init__(self, name: str):
        self._name = name

    def get_name(self) -> str:
        return self._name

class Player(Character):
    def __init__(self, name: str, starting_money: int = 40):
        super().__init__(name)
        self._money = starting_money
        self.jackpot_wins = 0

    @property
    def money(self):
        return self._money

    @money.setter
    def money(self, amount: int):
        if amount < 0:
            raise ValueError("Money amount cannot be negative.")
        self._money = amount

    def add_money(self, amount: int):
        if amount < 0:
            raise ValueError("Amount must be positive.")
        self._money += amount

    def deduct_money(self, amount: int):
        if amount > self._money:
            raise ValueError("Not enough money available.")
        self._money -= amount

    def interact(self) -> str:
        return f"{self.get_name()} looks around curiously, ready to explore the casino."

    def increment_jackpot_wins(self):
        self.jackpot_wins += 1

class Room:
    def __init__(self, name: str, description: str, locked: bool = False, unlock_cost: int = 0):
        self.name = name
        self.description = description
        self.locked = locked
        self.unlock_cost = unlock_cost
        self.exits: Dict[str, 'Room'] = {}
        self.characters: List[Character] = []
        self.game = None

    def add_exit(self, direction: str, room: 'Room'):
        self.exits[direction] = room

    def add_character(self, character: Character):
        self.characters.append(character)

    def add_game(self, game: 'CasinoGame'):
        self.game = game

    def get_details(self) -> str:
        details = f"\n--- {self.name} ---\n{self.description}\n"
        if self.locked:
            details += f"\nThis area is locked! Unlock cost: {self.unlock_cost} coins."
        if self.exits:
            details += f"\nAvailable exits: {', '.join(self.exits.keys())}"
        if self.characters:
            details += f"\nPresent characters: {', '.join([char.get_name() for char in self.characters])}"
        if self.game:
            details += f"\nYou can play: {self.game.name}"
        return details

    def display_details(self):
        Slowprint.slow_print(self.get_details())

class CasinoGame:
    def __init__(self, name: str):
        self.name = name

    def play(self, player: Player, bet: int) -> str:
        """
        Play the game with the specified bet.
        This method must be implemented in subclasses.
        """
        raise NotImplementedError("This method has to be implemented in a subclass.")

class Slots(CasinoGame):
    def __init__(self):
        super().__init__("Slots")
        self.reel_symbols = ["🍒", "🍋", "🔔", "⭐", "7️⃣"]

    def play(self, player: Player, bet: int) -> str:
        min_bet = 2
        if bet < min_bet:
            return f"The minimum bet for Slots is {min_bet} coins."
        if player.money < bet:
            return "You don't have enough coins to spin the reels."

        player.deduct_money(bet)
        result = [random.choice(self.reel_symbols) for _ in range(5)]
        reels_display = " | ".join(result)

        # Check for at least two matching symbols
        if len(set(result)) <= 3:  # At least two symbols are the same
            winnings = bet * 2  # Adjust the multiplier as needed
            player.add_money(winnings)
            return f"The reels are spinning... {reels_display}\n\nYou win! At least two symbols matched. You win {winnings} coins!"
        elif len (set(result)) == 1:  # All symbols are the same
            winnings = bet * 10
            player.add_money(winnings)
            player.increment_jackpot_wins()
            return f"The reels are spinning... {reels_display}\n\nJackpot! All symbols matched. You win {winnings} coins!"
        elif len(set(result)) == 2:  # Two symbols are the same and three are different
            winnings = bet * 5
            player.add_money(winnings)
            return f"The reels are spinning... {reels_display}\n\nYou win! Two symbols matched. You win {winnings} coins!"
        else:  # No matching symbols
            return f"The reels are spinning... {reels_display}\n\nTough luck! Try again - maybe it will work next time."
# Blackjack Game
class Blackjack(CasinoGame):
    def __init__(self):
        super().__init__("Blackjack")

    def play(self, player: Player, bet: int) -> str:
        min_bet = 5
        if bet < min_bet:
            return f"The minimum bet for Blackjack is {min_bet} coins."
        if player.money < bet:
            return "You don't have enough coins to play Blackjack."

        player.deduct_money(bet)
        player_score = random.randint(16, 21)
        dealer_score = random.randint(16, 21)
        Slowprint.slow_print(f"\nYour score: {player_score}, dealer's score: {dealer_score}")

        if player_score > dealer_score and player_score <= 21:
            winnings = bet * 2
            player.add_money(winnings)
            player.increment_jackpot_wins()
            return f"\nBlackjack! You beat the dealer and win {winnings} coins."
        elif player_score == dealer_score:
            player.add_money(bet)  
            return "\nDraw! Your stake will be refunded."
        return "\nOh no! The dealer won. Try again."

# Horse Race Game
class HorseRace(CasinoGame):
    def __init__(self):
        super().__init__("Horse Race")

    def play(self, player: Player, bet: int) -> str:
        min_bet = 8
        if bet < min_bet:
            return f"The minimum bet for Horse Race is {min_bet} coins."
        if player.money < bet:
            return "You don't have enough coins to take part in the horse races."

        player.deduct_money(bet)
        horses = ["Blitz", "Donner", "Wind", "Sturm"]
        print(f"Available horses: {', '.join(horses)}")
        player_choice = input("Choose your horse: ").strip()

        if player_choice not in horses:
            return "Invalid horse selection. Please try again."

        winning_horse = random.choice(horses)
        Slowprint.slow_print(f"\nThe horses are running! You chose {player_choice}.")
        Slowprint.slow_print(f"\nThe winning horse is: {winning_horse}")

        if player_choice == winning_horse:
            winnings = bet * 3
            player.add_money(winnings)
            return f"\nCongratulations! Your horse has won. You will receive {winnings} coins."
        return "\nUnfortunately your horse didn't win. Good luck next time."

# Baccarat Game
class Baccarat(CasinoGame):
    def __init__(self):
        super().__init__("Baccarat")

    def play(self, player: Player, bet: int) -> str:
        min_bet = 10
        if bet < min_bet:
            return f"The minimum bet for Baccarat is {min_bet} coins."
        if player.money < bet:
            return "You don't have enough coins to play baccarat."

        player.deduct_money(bet)
        player_score = random.randint(1, 9)
        banker_score = random.randint(1, 9)
        Slowprint.slow_print(f"\nYour card: {player_score}, bank card: {banker_score}")

        if player_score > banker_score:
            winnings = bet * 2
            player.add_money(winnings)
            return f"\nYou won! Your reward: {winnings} coins."
        elif player_score == banker_score:
            player.add_money(bet)  
            return "\nDraw! Your stake will be refunded."
        return "\nThe bank won. Try again."

# Poker Game
class Poker(CasinoGame):
    def __init__(self):
        super().__init__("Poker")

    def play(self, player: Player, bet: int) -> str:
        min_bet = 15
        if bet < min_bet:
            return f"The minimum bet for Poker is {min_bet} coins."
        if player.money < bet:
            return "You don't have enough coins to play poker."

        player.deduct_money(bet)
        player_hand = random.randint(1, 100)
        dealer_hand = random.randint(1, 100)
        Slowprint.slow_print(f"\nYour hand: {player_hand}, dealer's hand: {dealer_hand}")

        if player_hand > dealer_hand:
            winnings = bet * 4
            player.add_money(winnings)
            return f"\nYou won! Your reward: {winnings} coins."
        elif player_hand == dealer_hand:
            player.add_money(bet)  
            return "\nDraw! Your stake will be refunded."
        return "\nThe dealer hand was better. Try again."

# Roulette Game
class Roulette(CasinoGame):
    def __init__(self):
        super().__init__("Roulette")

    def play(self, player: Player, bet: int) -> str:
        min_bet = 12
        if bet < min_bet:
            return f"The minimum bet for Roulette is {min_bet} coins."
        if player.money < bet:
            return "You don't have enough coins to play roulette."

        player.deduct_money(bet)
        try:
            player_choice = int(input("Choose a number between 0 and 36: ").strip())
        except ValueError:
            return "Invalid input. Please enter a number between 0 and 36."

        if player_choice < 0 or player_choice > 36:
            return "Invalid number. Please choose a number between 0 and 36."

        winning_number = random.randint(0, 36)
        Slowprint.slow_print(f"\nThe ball is rolling... You bet on {player_choice}.")
        Slowprint.slow_print(f"\nThe ball lands on: {winning_number}")

        if player_choice == winning_number:
            winnings = bet * 20
            player.add_money(winnings)
            return f"\nJackpot! Your number was hit. You win {winnings} coins."
        return "\nUnfortunately no match. Try again."


class Game:
    def __init__(self, player_name: str, story_file: str, mode: str):
        self.player = Player(name=player_name)
        self.rooms: Dict[str, Room] = {}
        self.current_room = None
        self.story = Story(story_file)
        self.mode = mode

    def create_rooms(self):
        lobby = Room("Lobby", self.story.get_text("Lobby"))
        slots_room = Room("Slots Room", self.story.get_text("Slots Room"), locked=False)
        blackjack_room = Room("Blackjack Room", self.story.get_text("Blackjack Room"), locked=True, unlock_cost=50)
        horse_race_room = Room("Horse Race Room", self.story.get_text("Horse Race Room"), locked=True, unlock_cost=100)
        baccarat_room = Room("Baccarat Room", self.story.get_text("Baccarat Room"), locked=True, unlock_cost=120)
        poker_room = Room("Poker Room", self.story.get_text("Poker Room"), locked=True, unlock_cost=150)
        roulette_room = Room("Roulette Room", self.story.get_text("Roulette Room"), locked=True, unlock_cost=175)
        vip_room = Room("VIP Lounge", self.story.get_text("VIP Lounge"), locked=True, unlock_cost=999)

        lobby.add_exit("slots", slots_room)
        slots_room.add_exit("lobby", lobby)
        slots_room.add_exit("blackjack", blackjack_room)
        blackjack_room.add_exit("slots", slots_room)
        blackjack_room.add_exit("horse_race", horse_race_room)
        horse_race_room.add_exit("blackjack", blackjack_room)
        horse_race_room.add_exit("baccarat", baccarat_room)
        baccarat_room.add_exit("horse_race", baccarat_room)
        baccarat_room.add_exit("poker", poker_room)
        poker_room.add_exit("baccarat", baccarat_room)
        poker_room.add_exit("roulette", roulette_room)
        roulette_room.add_exit("poker", poker_room)
        roulette_room.add_exit("vip", vip_room)
        vip_room.add_exit("horse_race", horse_race_room)

        slots_room.add_game(Slots())
        blackjack_room.add_game(Blackjack())

        self.rooms = {
            "Lobby": lobby,
            "Slots Room": slots_room,
            "Blackjack Room": blackjack_room,
            "Horse Race Room": horse_race_room,
            "Baccarat Room": baccarat_room,
            "Poker Room": poker_room,
            "Roulette Room": roulette_room,
            "VIP Lounge": vip_room,
        }
        self.current_room = lobby

    def display_current_room(self):
        if self.current_room:
            self.current_room.display_details()

    def move_player(self, direction: str):
        if self.current_room and direction in self.current_room.exits:
            next_room = self.current_room.exits[direction]
            if next_room.locked:
                if self.player.money >= next_room.unlock_cost:
                    choice = input(f"This room is locked and costs {next_room.unlock_cost} coins to unlock. Do you want to unlock it? (yes/no): ").strip().lower()
                    if choice == "yes":
                        self.player.deduct_money(next_room.unlock_cost)
                        next_room.locked = False
                        print(f"You have successfully unlocked {next_room.name}!")
                    else:
                        print("You chose not to unlock the room.")
                        return
                else:
                    print("You don't have enough coins to unlock this room.")
                    return

            self.current_room = next_room
            print(f"You move to the {direction}.")
            self.display_current_room()  # Display the room details after moving
        else:
            print("You can't go that way.")

    def play_game(self):
        if self.current_room and self.current_room.game:
            print(self.current_room.game.play(self.player))
        else:
            print("There is no game to play here.")

    def save_game(self, filename: str = "casino_save.pkl"):
        try:
            with open(filename, "wb") as save_file:
                pickle.dump(self, save_file)
            Slowprint.slow_print("Game saved successfully!")
        except Exception as e:
            Slowprint.slow_print(f"Error saving game: {e}")

    @staticmethod
    def load_game(filename: str = "casino_save.pkl") -> 'Game':
        try:
            with open(filename, "rb") as save_file:
                game = pickle.load(save_file)
            Slowprint.slow_print("Game loaded successfully!")
            return game
        except FileNotFoundError:
            Slowprint.slow_print("No saved game found.")
        except Exception as e:
            print(f"Error loading game: {e}")
        return None

    def start(self):
        welcome_message = self.story.data["game"].get("welcome", "Welcome to the Casino Game!")
        Slowprint.slow_print(welcome_message)
        casino_tour = self.story.data["game"].get("casino_tour", "")
        casino_tour_rooms = self.story.data["game"].get("casino_tour_rooms", [])
        if casino_tour:
            Slowprint.slow_print(casino_tour)
            for room in casino_tour_rooms:
                Slowprint.slow_print(room)
        self.display_current_room()

        while True:
            if self.player.money <= 0:
                if self.mode == "easy":
                    print("You have run out of money. A stranger in the casino gives you some money to continue playing.")
                    self.player.add_money(50)  # Give the player some money to continue
                else:
                    print("You have run out of money. You are being kicked out of the casino. Game over.")
                    break

            Slowprint.slow_print("\nWhat would you like to do? (e.g., 'slots' to enter the Slots Room, 'exit' to leave, 'play' to play a game, 'purse' to check your money, 'save' to save the game, 'load' to load a game): ")
            action = input().strip().lower()
            if action == "exit":
                print("You leave the game.")
                break
            elif action == "purse":
                print(f"You have {self.player.money} coins.")
            elif action == "save":
                self.save_game()
            elif action == "load":
                loaded_game = self.load_game()
                if loaded_game:
                    self.__dict__.update(loaded_game.__dict__)
                    self.display_current_room()
            elif action in self.current_room.exits:
                self.move_player(action)
            elif action == "play":
                self.play_game()
            else:
                print("Unknown action. Please try again.")

    def move_to_room(self, room_name: str) -> str:
        """
        Move the player to a specified room if it's unlocked.
        Returns a message indicating success or failure.
        """
        if room_name in self.rooms:
            room = self.rooms[room_name]
            if room.locked:
                return f"{room_name} is locked. Unlock cost: {room.unlock_cost} coins."
            self.current_room = room
            return f"You moved to {room_name}."
        return "Room not found."

    def play_current_room_game(self, bet: int) -> str:
        """
        Play the game in the current room with the specified bet.
        Returns the result of the game.
        """
        if self.current_room and self.current_room.game:
            if bet > self.player.money:
                return "You don't have enough coins to place this bet."
            return self.current_room.game.play(self.player, bet)
        return "No game available in this room."

    def get_current_room_details(self) -> str:
        """
        Get the details of the current room.
        """
        if self.current_room:
            return self.current_room.get_details()
        return "No room selected."

    def get_player_money(self) -> int:
        """
        Get the player's current money.
        """
        return self.player.money

class Main:
    def __init__(self):
        self.game = None

    def setup_game(self):
        self.game = Game("", "story.json", "")
        disclaimer = self.game.story.get_disclaimer()
        if disclaimer:
            Slowprint.slow_print(disclaimer)
            choice = input("Do you still want to play? (yes/no): ").strip().lower()
            if choice != "yes":
                print("You chose not to play. Exiting the game.")
                return

        mode_choice = input("Select mode: easy or normal: ").strip().lower()
        if mode_choice not in ["easy", "normal"]:
            print("Invalid mode selected. Defaulting to normal mode.")
            mode_choice = "normal"

        load_choice = input("Do you want to load a game or create a new one? (load/new): ").strip().lower()
        if load_choice == "load":
            loaded_game = Game.load_game("casino_save.pkl")
            if loaded_game:
                self.game = loaded_game
                self.game.mode = mode_choice
                self.game.start()
                return
            else:
                print("No saved game found. Starting a new game.")
        
        name = input("Enter your name: ")
        self.game = Game(name, "story.json", mode_choice)
        self.game.create_rooms()
        self.game.start()

