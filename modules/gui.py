import customtkinter as ctk  
from modules import classes  
import threading  # For running tasks in separate threads
import sys 
from PIL import Image, ImageTk 

# Fix for charmap encoding issue in the console
sys.stdout.reconfigure(encoding='utf-8')

class CasinoGUI(ctk.CTk):
    """
    Main GUI class for the Golden Casino Requiem game.
    Handles the user interface and interactions.
    """

    def slow_print(self, text, textbox, delay=25):
        """
        Print text slowly into the given textbox, simulating a typing effect.
        :param text: The text to display.
        :param textbox: The textbox widget where the text will be displayed.
        :param delay: Delay in milliseconds between each character.
        """
        def type_character(index=0):
            if index < len(text):
                textbox.insert(ctk.END, text[index])  # Insert one character at a time
                textbox.see(ctk.END)  # Scroll to the end of the textbox
                self.after(delay, type_character, index + 1)  # Schedule the next character

        textbox.delete("1.0", ctk.END)  # Clear the textbox
        type_character()  # Start typing characters

    def __init__(self):
        """
        Initialize the CasinoGUI application.
        Sets up the main window, appearance, and initializes game variables.
        """
        super().__init__()
        self.title('Golden Casino Requiem')  # Set the window title
        self.geometry('1100x700')  # Set the window size
        
        # Configure appearance and theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        self.configure(bg="#1b1b1b")  # Set background color
        
        # Initialize game-related variables
        self.player = None
        self.game = None
        self.bet_history = []
        self.difficulty = "normal"

        # Create frames for different screens
        self.start_screen = ctk.CTkFrame(self, fg_color="#1b1b1b")
        self.loading_screen = ctk.CTkFrame(self, fg_color="#1b1b1b")
        self.main_game_screen = ctk.CTkFrame(self, fg_color="#1b1b1b")
        self.end_screen = ctk.CTkFrame(self, fg_color="#1b1b1b")

        # Initialize the start screen
        self.create_start_screen()

    def create_start_screen(self):
        """
        Create the start screen with a name entry, difficulty switch, and start button.
        This is the first screen the user sees when launching the application.
        """
        self.start_screen.pack(fill="both", expand=True)

        # Load and display the background image
        bg_image = Image.open(r"images\Start_Image.png")
        bg_image = bg_image.resize((1100, 500), Image.Resampling.LANCZOS)  # Resize to fit the top portion of the screen
        self.bg_image_tk = ImageTk.PhotoImage(bg_image)

        bg_label = ctk.CTkLabel(self.start_screen, image=self.bg_image_tk, text="")
        bg_label.pack(fill="x", pady=10)  # Place the image at the top

        # Create a frame for the inputs below the image
        input_frame = ctk.CTkFrame(self.start_screen, fg_color="#1b1b1b", corner_radius=10)
        input_frame.pack(fill="x", padx=20, pady=20)

        # Name entry field
        name_label = ctk.CTkLabel(input_frame, text="Enter your name:", font=("Arial", 18), text_color="white")
        name_label.pack(pady=10)

        self.name_entry = ctk.CTkEntry(input_frame, width=300, font=("Arial", 16))
        self.name_entry.pack(pady=10)

        self.error_label = ctk.CTkLabel(input_frame, text="", font=("Arial", 14), text_color="red")
        self.error_label.pack(pady=5)

        # Difficulty switch
        difficulty_label = ctk.CTkLabel(input_frame, text="Select Difficulty:", font=("Arial", 18), text_color="white")
        difficulty_label.pack(pady=10)

        self.difficulty_switch = ctk.CTkSwitch(
            input_frame,
            text="Easy Mode",
            font=("Arial", 16),
            command=self.toggle_difficulty
        )
        self.difficulty_switch.pack(pady=10)

        # Start button
        start_button = ctk.CTkButton(
            input_frame,
            text="Start Game",
            font=("Arial", 18, "bold"),
            fg_color="gold",
            hover_color="darkred",
            text_color="black",
            command=self.start_game
        )
        start_button.pack(pady=20)

    def toggle_difficulty(self):
        """
        Toggle the difficulty between 'easy' and 'normal' based on the state of the difficulty switch.
        Updates the `self.difficulty` attribute accordingly.
        """
        self.difficulty = "easy" if self.difficulty_switch.get() else "normal"

    def create_quit_screen(self):
        """
        Create the quit screen to display the player's bet history and remaining coins.
        Provides options to quit the game or return to the main game screen.
        """
        self.main_game_screen.pack_forget()  # Hide the main game screen
        self.quit_screen = ctk.CTkFrame(self, fg_color="#1b1b1b")
        self.quit_screen.pack(fill="both", expand=True)

        # Title label
        title_label = ctk.CTkLabel(self.quit_screen, text="Quit Game", font=("Arial", 32, "bold"), text_color="gold")
        title_label.pack(pady=20)

        # Display player's money
        money_label = ctk.CTkLabel(self.quit_screen, text=f"Coins: {self.player.money}", font=("Arial", 18), text_color="white")
        money_label.pack(pady=10)

        # Display bet history
        history_label = ctk.CTkLabel(self.quit_screen, text="Bet History:", font=("Arial", 18), text_color="white")
        history_label.pack(pady=10)

        history_textbox = ctk.CTkTextbox(self.quit_screen, width=800, height=300, wrap="word", font=("Arial", 14), fg_color="#222222", text_color="white")
        history_textbox.pack(pady=10, fill="both", expand=True)

        # Populate the history textbox
        for bet in self.bet_history:
            history_textbox.insert(ctk.END, f"{bet}\n")

        # Add buttons to confirm quit or return to the game
        button_frame = ctk.CTkFrame(self.quit_screen, fg_color="#1b1b1b")
        button_frame.pack(pady=20)

        quit_button = ctk.CTkButton(button_frame, text="Quit", font=("Arial", 18, "bold"), fg_color="red", hover_color="darkred", text_color="white", command=self.quit_game)
        quit_button.pack(side="left", padx=10)

        return_button = ctk.CTkButton(button_frame, text="Return to Game", font=("Arial", 18, "bold"), fg_color="green", hover_color="darkgreen", text_color="white", command=self.return_to_game)
        return_button.pack(side="right", padx=10)

    def start_game(self):
        """
        Start the game by initializing the player and game objects.
        Switches from the start screen to the loading screen.
        """
        # Get the player's name or use a default name
        player_name = self.name_entry.get().strip()
        if not player_name:
            player_name = "Player"
        
        self.error_label.configure(text="")

        # Initialize the player and game
        self.player = classes.Player(player_name)
        self.game = classes.Game(player_name, "story.json", "normal")
        self.game.create_rooms()

        # Switch to the loading screen
        self.start_screen.pack_forget()
        self.create_loading_screen(
            story_text=self.game.story.data["game"].get("disclaimer", "") + "\n\n" + \
                        self.game.story.data["game"].get("welcome", "") + "\n\n" + \
                        self.game.story.data["game"].get("casino_tour", "") + "\n\n" + \
                        "\n".join(self.game.story.data["game"].get("casino_tour_rooms", [])), callback=self.create_main_game_screen)

    def create_loading_screen(self, story_text=None, callback=None):
        """
        Create the loading screen to display story text with a typing effect.
        Includes a "Continue" button to proceed to the next screen.
        :param story_text: The story text to display on the loading screen.
        :param callback: The function to call when the "Continue" button is pressed.
        """
        self.loading_screen.pack(fill="both", expand=True)

        # Clear the loading screen and add the loading label
        for widget in self.loading_screen.winfo_children():
            widget.destroy()

        # Decorative frame for the loading screen
        decorative_frame = ctk.CTkFrame(self.loading_screen, fg_color="#333333", corner_radius=15)
        decorative_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Loading label
        story_label = ctk.CTkLabel(decorative_frame, text="Loading...", font=("Arial", 28, "bold"), text_color="gold")
        story_label.pack(pady=20)

        # Textbox to display the story text
        self.story_textbox = ctk.CTkTextbox(decorative_frame, width=800, height=400, wrap="word", font=("Arial", 16), fg_color="#222222", text_color="white", corner_radius=10)
        self.story_textbox.pack(pady=10, fill="both", expand=True)

        # Display the story text with a slow print effect
        if story_text:
            self.story_textbox.delete("1.0", ctk.END)  # Clear any existing text
            self.after(500, lambda: self.slow_print(story_text, self.story_textbox))  # Add a slight delay before slow print

        # "Continue" button to proceed
        continue_button = ctk.CTkButton(
            decorative_frame,
            text="Continue",
            font=("Arial", 18, "bold"),
            fg_color="gold",
            hover_color="darkred",
            text_color="black",
            command=lambda: self.proceed_from_loading(callback))
        continue_button.pack(pady=20)

    def proceed_from_loading(self, callback):
        """
        Proceed from the loading screen to the next screen.
        Calls the provided callback function to determine the next screen.
        :param callback: The function to call to load the next screen.
        """
        self.loading_screen.pack_forget()  # Hide the loading screen
        if callback:
            callback()  # Execute the callback to load the next screen
        else:
            self.create_main_game_screen()

    def create_main_game_screen(self):
        """
        Create the main game screen where the player interacts with rooms and games.
        Sets up the layout and initializes the UI components for the main game.
        """
        self.loading_screen.pack_forget()
        self.main_game_screen.pack(fill="both", expand=True)

        # Create the layout and update the UI
        self.create_layout()
        self.update_money_display()
        self.update_room_list()
        self.update_game_buttons()
        self.display_story(self.game.story.data["game"].get("welcome", "Welcome to the Casino Game!"))

    def create_layout(self):
        """
        Create the layout for the main game screen.
        Includes sections for the header, room list, game controls, and story display.
        """
        # Header with Money Display
        self.header_frame = ctk.CTkFrame(self.main_game_screen, fg_color="#222222", corner_radius=10)
        self.header_frame.pack(fill='x', padx=10, pady=10)

        self.money_label = ctk.CTkLabel(self.header_frame, text=f"Coins: {self.player.money}", font=("Arial", 18, "bold"), text_color="gold")
        self.money_label.pack(pady=10)
        
        self.name_label = ctk.CTkLabel(self.header_frame, text=f"Player: {self.player.get_name()}", font=("Arial", 18, "bold"), text_color="white")
        self.name_label.pack(side="left", padx=10, pady=10)
        # Main Layout with 3 Sections
        self.main_frame = ctk.CTkFrame(self.main_game_screen, fg_color="#2e2e2e", corner_radius=10)
        self.main_frame.pack(expand=1, fill='both', padx=10, pady=10)

        # Left Panel (Room List)
        self.room_frame = ctk.CTkFrame(self.main_frame, fg_color="#333333", corner_radius=10)
        self.room_frame.pack(side='left', fill='y', padx=10, pady=10)

        self.room_label = ctk.CTkLabel(self.room_frame, text="Rooms:", font=("Arial", 14, "bold"), text_color="gold")
        self.room_label.pack(pady=5)
        
        self.room_listbox = ctk.CTkFrame(self.room_frame, fg_color="#444444", corner_radius=10)
        self.room_listbox.pack(pady=5, fill='both', expand=True)

        self.room_buttons = []

        # Center Panel (Game Controls)
        self.center_frame = ctk.CTkFrame(self.main_frame, fg_color="#444444", corner_radius=10)
        self.center_frame.pack(expand=1, fill='both', padx=10, pady=10)

        self.bet_label = ctk.CTkLabel(self.center_frame, text="Place Your Bet:", font=("Arial", 14, "bold"), text_color="gold")
        self.bet_label.pack(pady=5)
        
        self.bet_entry = ctk.CTkEntry(self.center_frame, width=200)
        self.bet_entry.pack(pady=5)
        
        self.game_buttons_frame = ctk.CTkFrame(self.center_frame, fg_color="#555555", corner_radius=10)
        self.game_buttons_frame.pack(fill='x', padx=10, pady=10)
        
        self.game_buttons = []

        # Add a label to display game results
        self.result_label = ctk.CTkLabel(self.center_frame, text="", font=("Arial", 14, "bold"), text_color="white")
        self.result_label.pack(pady=10)

        # Right Panel (Tabbed Story Display)
        self.story_tabview = ctk.CTkTabview(self.main_frame, width=300, corner_radius=10)
        self.story_tabview.pack(side='right', fill='both', padx=10, pady=10)

        # Add tabs for the story
        self.story_tab = self.story_tabview.add("Story")
        self.story_textbox = ctk.CTkTextbox(self.story_tab, width=300, height=400, wrap="word")
        self.story_textbox.pack(pady=5, fill='both', expand=True)

        # Add a history tab
        self.history_tab = self.story_tabview.add("History")
        self.history_listbox = ctk.CTkTextbox(self.history_tab, width=300, height=150, wrap="word", font=("Arial", 12))
        self.history_listbox.pack(pady=10, fill="both", expand=True)
        
        # Inside the create_layout method, add this to the header frame
        quit_button = ctk.CTkButton(self.header_frame, text="Quit", font=("Arial", 14, "bold"), fg_color="red", hover_color="darkred", text_color="white", command=self.create_quit_screen)
        quit_button.pack(side="right", padx=10, pady=10)

    def update_room_list(self):
        """
        Update the room list with buttons for each room.
        Displays locked rooms with an unlock button and unlocked rooms with a checkmark.
        """
        # Clear all existing widgets in the room_listbox
        for widget in self.room_listbox.winfo_children():
            widget.destroy()

        self.room_buttons.clear()  # Clear the room_buttons list

        # Iterate through all rooms in the game
        for room_name, room in self.game.rooms.items():
            status = "✅" if not room.locked else "🔒"  # Show a lock or checkmark based on room status
            room_frame = ctk.CTkFrame(self.room_listbox, fg_color="#555555", corner_radius=10)
            room_frame.pack(fill='x', pady=2)

            # Create a button for the room
            room_button = ctk.CTkButton(
                room_frame,
                text=f"{status} {room_name}",
                command=lambda rn=room_name: self.move_to_room(rn),  # Move to the room when clicked
                fg_color="#555555",
                hover_color="#777777",
                width=200
            )
            room_button.pack(side="left", padx=5, pady=2)
            self.room_buttons.append(room_button)

            # If the room is locked, add an unlock button
            if room.locked:
                unlock_button = ctk.CTkButton(
                    room_frame,
                    text=f"Unlock ({room.unlock_cost} coins)",
                    command=lambda rn=room_name: self.unlock_room(rn),  # Unlock the room when clicked
                    fg_color="gold",
                    hover_color="darkred",
                    text_color="black",
                    width=150
                )
                unlock_button.pack(side="right", padx=5, pady=2)
                self.room_buttons.append(unlock_button)

    def unlock_room(self, room_name):
        """
        Unlock a room if the player has enough coins.
        Deducts the unlock cost from the player's coins and updates the room list.
        :param room_name: The name of the room to unlock.
        """
        room = self.game.rooms.get(room_name)  # Get the room object
        if room and room.locked:
            if self.player.money >= room.unlock_cost:  # Check if the player has enough coins
                self.player.deduct_money(room.unlock_cost)  # Deduct the unlock cost
                room.locked = False  # Unlock the room
                self.update_money_display()  # Update the money display
                self.update_room_list()  # Refresh the room list
                self.result_label.configure(text=f"{room_name} unlocked!", text_color="green")

                # Show the loading screen after unlocking the room
                self.create_loading_screen(
                    story_text=f"{room_name} has been unlocked!\n\n{room.description}",
                    callback=lambda: self.enter_room(room)  # Enter the room after unlocking
                )
            else:
                self.result_label.configure(text="Not enough coins to unlock this room!", text_color="red")

    def move_to_room(self, room_name):
        """
        Move to the selected room and update the GUI.
        Displays a loading screen with the room's description before entering.
        :param room_name: The name of the room to move to.
        """
        room = self.game.rooms.get(room_name)  # Get the room object
        if room:
            if room.locked:  # Prevent moving to locked rooms
                self.result_label.configure(
                    text=f"{room_name} is locked. Unlock cost: {room.unlock_cost} coins.",
                    text_color="red"
                )
                return
            self.main_game_screen.pack_forget()  # Hide the main game screen

            # Show the loading screen with the room description
            self.create_loading_screen(
                story_text=f"Entering {room_name}...\n\n{room.description}",
                callback=lambda: self.enter_room(room)
            )

            self.loading_screen.pack(fill="both", expand=True)  # Show the loading screen

            # Update the current room and GUI
            self.game.current_room = room
            self.update_room_list()
            self.update_game_buttons()
            self.display_story(room.description)
            self.result_label.configure(
                text=f"You have entered {room.name}.",
                text_color="green"
            )

    def enter_room(self, room):
        """
        Enter the specified room after the loading screen.
        Updates the current room and refreshes the UI components.
        :param room: The room object to enter.
        """
        self.loading_screen.pack_forget()  # Hide the loading screen
        self.main_game_screen.pack(fill="both", expand=True)  # Show the main game screen

        # Update the current room and GUI
        self.game.current_room = room
        self.update_room_list()  # Update the room list to reflect the current room
        self.update_game_buttons()  # Update the game buttons for the new room
        self.display_story(room.description)  # Update the story display with the room description
        self.result_label.configure(
            text=f"You have entered {room.name}.",
            text_color="green"
        )

    def update_game_buttons(self):
        """
        Update the game buttons for the current room.
        Adds a button to play the game available in the current room.
        """
        for widget in self.game_buttons:
            widget.destroy()  # Clear all existing game buttons
        self.game_buttons.clear()

        current_room = self.game.current_room
        if current_room and current_room.game:  # Check if the current room has a game
            game_button = ctk.CTkButton(
                self.game_buttons_frame,
                text=f"Play {current_room.game.name}",  # Button text includes the game name
                command=lambda: self.play_game(current_room.game.name),  # Play the game when clicked
                fg_color="gold",
                hover_color="darkred"
            )
            game_button.pack(pady=2, fill='x')  # Add padding and make the button fill horizontally
            self.game_buttons.append(game_button)

    def play_game(self, game_name):
        """
        Start the game logic in a separate thread to avoid blocking the GUI
        """
        threading.Thread(target=self._play_game_logic, args=(game_name,), daemon=True).start()

    def _play_game_logic(self, game_name):
        """
        Handle the game logic for playing a game.
        Deducts the player's bet, plays the game, and updates the UI with the result.
        :param game_name: The name of the game to play.
        """
        bet = self.get_bet()  # Get the player's bet
        if bet is None:  # Check if the bet is valid
            self.result_label.configure(text="Invalid bet! Please try again.", text_color="red")
            return

        current_room = self.game.current_room
        if current_room and current_room.game:  # Check if the current room has a game
            try:
                # Deduct the bet and play the game
                result = current_room.game.play(self.player, bet)  # Pass the bet to the play method

                # Add the result to the bet history
                self.bet_history.append(f"{game_name}: {bet} coins - {result}")
                self.update_bet_history()  # Update the bet history display

                # Update the player's money display
                self.update_money_display()

                # Display the result in the result label
                self.result_label.configure(text=result, text_color="gold")
            except ValueError as e:  # Handle invalid bets
                self.result_label.configure(text=str(e), text_color="red")
            except Exception as e:  # Handle unexpected errors
                import traceback
                error_message = traceback.format_exc()  # Get the full stack trace
                print(error_message)  # Print the error to the console for debugging
                self.result_label.configure(text=f"Error: {str(e)}", text_color="red")
        else:
            self.result_label.configure(text="No game available in this room!", text_color="red")

    def update_money_display(self):
        """
        Update the money display in the header with the player's current coin balance.
        """
        self.money_label.configure(text=f"Coins: {self.player.money}")

    def update_bet_history(self):
        """
        Update the bet history display with the last 10 bets made by the player.
        """
        self.history_listbox.delete("1.0", ctk.END)  # Clear the history listbox
        for bet in self.bet_history[-10:]:  # Show only the last 10 bets
            self.history_listbox.insert(ctk.END, f"{bet}\n")

    def get_bet(self):
        """
        Get the player's bet from the bet entry field.
        Validates the input and ensures the bet is within the player's coin balance.
        :return: The bet amount as an integer, or None if invalid.
        """
        try:
            bet_input = self.bet_entry.get().strip()  # Get the input from the entry field
            bet = int(bet_input)  # Convert the input to an integer
            if bet <= 0 or bet > self.player.money:  # Check if the bet is valid
                return None
            return bet
        except ValueError:  # Handle non-integer inputs
            return None

    def display_story(self, story_text):
        """
        Update the story display with the given text.
        Clears the existing text and inserts the new story text.
        :param story_text: The text to display in the story textbox.
        """
        self.story_textbox.delete("1.0", ctk.END)  # Clear the story textbox
        self.story_textbox.insert(ctk.END, story_text)  # Insert the new story text
        
    def quit_game(self):
        """
        Quit the game and close the application window.
        """
        self.destroy()  # Close the application window
        
    def return_to_game(self):
        """
        Return to the main game screen from the quit screen.
        Hides the quit screen and shows the main game screen.
        """
        self.quit_screen.pack_forget()  # Hide the quit screen
        self.main_game_screen.pack(fill="both", expand=True)  # Show the main game screen

# Run the application if this file is executed directly
if __name__ == "__main__":
    app = CasinoGUI()  # Create an instance of the CasinoGUI class
    app.mainloop()  # Start the main event loop