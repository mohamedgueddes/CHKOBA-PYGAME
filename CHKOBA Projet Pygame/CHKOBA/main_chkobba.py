"""
Chkobba Game - Main Entry Point
A Tunisian card capture game
Built with Pygame
"""

from game_controller import ChkobbaGameController
from chkobba_ui_pygame import ChkobbaUI


def main():
    """Start the Chkobba game"""
    print("=" * 50)
    print("Welcome to CHKOBBA!")
    print("A Tunisian Card Game")
    print("=" * 50)
    
    # Create game controller
    game = ChkobbaGameController(player_difficulty="medium")
    
    # Create and run UI
    ui = ChkobbaUI(game)
    ui.run()


if __name__ == "__main__":
    main()
