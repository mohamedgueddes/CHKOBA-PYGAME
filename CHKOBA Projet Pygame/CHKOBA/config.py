# Configuration and Constants for Chkoba Game

# Window Settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Chkoba - Tunisian Game"
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)

# Player Colors
PLAYER_COLORS = [RED, BLUE, GREEN, YELLOW]

# Game Settings
NUM_PLAYERS = 2  # Can be 2-4
PIECES_PER_PLAYER = 4
BOARD_SIZE = 40  # Total squares on board
HOME_STRETCH = 4  # Safe home squares

# Asset Paths (to be filled with your images)
ASSET_PATH = "assets/"
BG_IMAGE = "BACKGROUND.png"  # Your board background image
CARD_BACK = "ARRIERE CARD.png"  # Card back image
PIECE_IMAGE = f"{ASSET_PATH}images/pieces.png"  # Optional

# Game Speed
ANIMATION_SPEED = 0.1  # seconds per square movement
