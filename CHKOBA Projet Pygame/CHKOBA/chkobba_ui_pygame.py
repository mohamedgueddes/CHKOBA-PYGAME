"""
Chkobba Game UI using Pygame
A complete rewrite from Tkinter to Pygame
"""

import pygame
import os
import random
from config import *


class ChkobbaUI:
    """Pygame UI for Chkobba game"""
    
    def __init__(self, game_controller):
        self.game = game_controller
        
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        
        # Game state
        self.screen_state = "HOME"  # "HOME" or "GAME"
        self.running = True
        
        # Card sizing
        self.hand_card_width = 90
        self.hand_card_height = 140
        self.hand_spacing = 20
        self.table_card_width = 75
        self.table_card_height = 110
        self.table_spacing = 15
        
        # Canvas dimensions (game area)
        self.canvas_width = WINDOW_WIDTH
        self.canvas_height = WINDOW_HEIGHT - 100
        
        # Fonts
        self.font_large = pygame.font.Font(None, 80)
        self.font_title = pygame.font.Font(None, 60)
        self.font_button = pygame.font.Font(None, 40)
        self.font_normal = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        
        # Load images
        self.card_images = {}
        self.back_card_image = None
        self.home_image = None
        self.game_background = None
        # Load sounds
        self.deal_sound = None
        self.load_images()
        
        # Card click tracking
        self.card_regions = {}
        self.table_card_images = {}
        
        # Buttons
        self.play_button_rect = None
        self.restart_button_rect = None
        self.quit_button_rect = None
    
    def load_images(self):
        """Load all card and background images"""
        card_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load home image
        welcome_path = os.path.join(card_dir, "welcome.png")
        if os.path.exists(welcome_path):
            try:
                img = pygame.image.load(welcome_path)
                self.home_image = pygame.transform.scale(img, (self.canvas_width, self.canvas_height))
            except Exception as e:
                print(f"Error loading home image: {e}")
        
        # Load game background image
        game_bg_path = os.path.join(card_dir, "BACKGROUND.png")
        if os.path.exists(game_bg_path):
            try:
                img = pygame.image.load(game_bg_path)
                self.game_background = pygame.transform.scale(img, (WINDOW_WIDTH, self.canvas_height))
            except Exception as e:
                print(f"Error loading game background: {e}")
        
        # Load back card image
        back_card_path = os.path.join(card_dir, "ARRIERE CARD.png")
        if os.path.exists(back_card_path):
            try:
                img = pygame.image.load(back_card_path)
                self.back_card_image = pygame.transform.scale(img, (self.hand_card_width, self.hand_card_height))
            except Exception as e:
                print(f"Error loading back card: {e}")
        
        # Load card images
        suit_folder_map = {
            "Coeur": "COEUR",
            "Dinari": "DINARI",
            "Pique": "PIQUE",
            "Trefele": "TREFELE"
        }
        
        for suit_name, folder in suit_folder_map.items():
            folder_path = os.path.join(card_dir, folder)
            if not os.path.exists(folder_path):
                print(f"Warning: Card folder not found: {folder_path}")
                continue
            
            for value in range(1, 11):
                filename = f"{value}_{folder}.png"
                image_path = os.path.join(folder_path, filename)
                
                if os.path.exists(image_path):
                    try:
                        img = pygame.image.load(image_path)
                        img = pygame.transform.scale(img, (self.hand_card_width, self.hand_card_height))
                        key = (suit_name, value)
                        self.card_images[key] = img
                    except Exception as e:
                        print(f"Error loading card {image_path}: {e}")

        # Load deal sound (played when cards are dealt / game starts)
        try:
            sound_path = os.path.join(card_dir, "audiomass-output.mp3")
            if os.path.exists(sound_path):
                # Ensure mixer initialized
                try:
                    if not pygame.mixer.get_init():
                        pygame.mixer.init()
                except Exception:
                    pass

                try:
                    self.deal_sound = pygame.mixer.Sound(sound_path)
                    self.deal_sound.set_volume(0.7)
                except Exception as e:
                    print(f"Error loading deal sound: {e}")
        except Exception:
            pass
    
    def _get_card_image(self, card):
        """Get Pygame surface for a card"""
        key = (card.suit.value, card.value)
        return self.card_images.get(key)
    
    def _draw_card(self, surface, x, y, card, width, height):
        """Draw a single card on the surface"""
        card_image = self._get_card_image(card)
        
        if card_image:
            surface.blit(card_image, (x, y))
        else:
            # Fallback: text-based rendering
            pygame.draw.rect(surface, (255, 255, 200), (x, y, width, height))
            pygame.draw.rect(surface, (0, 0, 0), (x, y, width, height), 2)
            
            suit_char = {
                "Coeur": "♥",
                "Dinari": "♦",
                "Pique": "♠",
                "Trefele": "♣"
            }.get(card.suit.value, "?")
            
            suit_color = (255, 0, 0) if card.suit.value in ["Coeur", "Dinari"] else (0, 0, 0)
            
            suit_text = pygame.font.Font(None, 32).render(suit_char, True, suit_color)
            surface.blit(suit_text, (x + 5, y + 5))
            
            rank_display = {
                1: "A", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7",
                8: "J", 9: "Q", 10: "K"
            }.get(card.value, "?")
            
            rank_text = pygame.font.Font(None, 40).render(rank_display, True, (0, 0, 0))
            text_rect = rank_text.get_rect(center=(x + width // 2, y + height // 2))
            surface.blit(rank_text, text_rect)
    
    def _draw_home_screen(self):
        """Draw home screen with image and play button"""
        # Draw background image or solid color
        if self.home_image:
            self.screen.blit(self.home_image, (0, 0))
        else:
            self.screen.fill((30, 30, 80))
        
        # Overlay for button area
        overlay = pygame.Surface((self.canvas_width, 140))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, self.canvas_height - 140))
        
        # Draw PLAY button
        play_button_width = 220
        play_button_height = 70
        play_button_x = (WINDOW_WIDTH - play_button_width) // 2
        play_button_y = (self.canvas_height + 30)
        
        self.play_button_rect = pygame.Rect(play_button_x, play_button_y, play_button_width, play_button_height)
        pygame.draw.rect(self.screen, (255, 215, 0), self.play_button_rect)
        pygame.draw.rect(self.screen, (184, 134, 11), self.play_button_rect, 3)
        
        play_text = self.font_button.render("PLAY", True, (30, 30, 80))
        text_rect = play_text.get_rect(center=self.play_button_rect.center)
        self.screen.blit(play_text, text_rect)
    
    def _draw_game_screen(self):
        """Draw the game board"""
        # Draw background
        if self.game_background:
            self.screen.blit(self.game_background, (0, 0))
        else:
            self.screen.fill((210, 180, 140))
        
        state = self.game.get_game_state()
        
        # Draw AI hand (top)
        self._draw_ai_hand(state['ai_hand_size'])
        
        # Draw AI captured pile
        self._draw_ai_captured_pile(state['ai_captured_count'])
        
        # Draw table cards (center)
        self._draw_table_cards(state['table_cards'])
        
        # Draw player info
        self._draw_player_info(state)
        
        # Draw player captured pile
        self._draw_player_captured_pile(state['player_captured_count'])
        
        # Draw player hand (bottom)
        self._draw_player_hand(state['player_hand'])
        
        # Draw control panel at bottom
        self._draw_control_panel(state)
    
    def _draw_ai_hand(self, num_cards):
        """Draw AI's hidden hand at top"""
        start_y = 10
        
        label_text = self.font_small.render("AI Hand (Opponent)", True, (0, 0, 0))
        self.screen.blit(label_text, (10, start_y))
        
        card_width = self.hand_card_width
        card_height = self.hand_card_height
        total_width = (num_cards * card_width) + ((num_cards - 1) * self.hand_spacing)
        start_x = (WINDOW_WIDTH - total_width) // 2
        card_y = start_y + 25
        
        for i in range(num_cards):
            x = start_x + i * (card_width + self.hand_spacing)
            y = card_y
            
            if self.back_card_image:
                self.screen.blit(self.back_card_image, (x, y))
            else:
                pygame.draw.rect(self.screen, (30, 30, 80), (x, y, card_width, card_height))
                pygame.draw.rect(self.screen, (0, 0, 0), (x, y, card_width, card_height), 2)
                q_text = pygame.font.Font(None, 60).render("?", True, (255, 255, 255))
                q_rect = q_text.get_rect(center=(x + card_width // 2, y + card_height // 2))
                self.screen.blit(q_text, q_rect)
    
    def _draw_table_cards(self, cards):
        """Draw cards on the table (center)"""
        table_label_y = self.canvas_height // 4
        
        label_text = self.font_normal.render("TABLE", True, (0, 0, 0))
        self.screen.blit(label_text, (WINDOW_WIDTH // 2 - 30, table_label_y))
        
        card_width = self.table_card_width
        card_height = self.table_card_height
        
        if not cards:
            empty_text = self.font_small.render("(Empty)", True, (128, 128, 128))
            self.screen.blit(empty_text, (WINDOW_WIDTH // 2 - 40, table_label_y + 50))
        else:
            total_width = (len(cards) * card_width) + ((len(cards) - 1) * self.table_spacing)
            start_x = (WINDOW_WIDTH - total_width) // 2
            card_y = table_label_y + 40
            
            for i, card in enumerate(cards):
                x = start_x + i * (card_width + self.table_spacing)
                y = card_y
                self._draw_card(self.screen, x, y, card, card_width, card_height)
    
    def _draw_player_hand(self, cards):
        """Draw player's hand at bottom"""
        start_y = self.canvas_height - self.hand_card_height - 10
        
        label_text = self.font_small.render("Your Hand (Play 1 card)", True, (0, 0, 0))
        self.screen.blit(label_text, (10, start_y - 20))
        
        card_width = self.hand_card_width
        card_height = self.hand_card_height
        total_width = (len(cards) * card_width) + ((len(cards) - 1) * self.hand_spacing)
        start_x = (WINDOW_WIDTH - total_width) // 2
        
        self.card_regions = {}
        
        for i, card in enumerate(cards):
            x = start_x + i * (card_width + self.hand_spacing)
            y = start_y
            self._draw_card(self.screen, x, y, card, card_width, card_height)
            self.card_regions[card] = pygame.Rect(x, y, card_width, card_height)
    
    def _draw_ai_captured_pile(self, count):
        """Draw AI's captured cards pile"""
        if count == 0:
            return
        
        card_width = self.hand_card_width
        card_height = self.hand_card_height
        pile_x = WINDOW_WIDTH - 80
        pile_y = 60
        
        cards_to_show = min(count, 3)
        for i in range(cards_to_show):
            offset = i * 5
            x = pile_x + offset
            y = pile_y + offset
            
            if self.back_card_image:
                self.screen.blit(self.back_card_image, (x, y))
            else:
                pygame.draw.rect(self.screen, (34, 139, 34), (x, y, card_width, card_height))
                pygame.draw.rect(self.screen, (0, 0, 0), (x, y, card_width, card_height), 2)
        
        won_text = self.font_small.render(f"Won: {count}", True, (34, 139, 34))
        self.screen.blit(won_text, (pile_x, pile_y + card_height + 20))
    
    def _draw_player_captured_pile(self, count):
        """Draw player's captured cards pile"""
        if count == 0:
            return
        
        card_width = self.hand_card_width
        card_height = self.hand_card_height
        pile_x = WINDOW_WIDTH - 80
        pile_y = self.canvas_height - 100
        
        cards_to_show = min(count, 3)
        for i in range(cards_to_show):
            offset = i * 5
            x = pile_x + offset
            y = pile_y - card_height - offset
            
            if self.back_card_image:
                self.screen.blit(self.back_card_image, (x, y))
            else:
                pygame.draw.rect(self.screen, (30, 30, 80), (x, y, card_width, card_height))
                pygame.draw.rect(self.screen, (0, 0, 0), (x, y, card_width, card_height), 2)
        
        won_text = self.font_small.render(f"Won: {count}", True, (30, 30, 80))
        self.screen.blit(won_text, (pile_x, pile_y + 10))
    
    def _draw_game_over_screen(self, state):
        """Draw the final scores screen with detailed breakdown"""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((30, 30, 80))
        self.screen.blit(overlay, (0, 0))
        
        # Title
        if state['total_player_points'] > state['total_ai_points']:
            title = "YOU WIN!"
            title_color = (0, 255, 0)
        elif state['total_player_points'] < state['total_ai_points']:
            title = "AI WINS!"
            title_color = (255, 0, 0)
        else:
            title = "IT'S A TIE!"
            title_color = (255, 215, 0)
        
        title_text = self.font_large.render(title, True, title_color)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 30))
        self.screen.blit(title_text, title_rect)
        
        # Get scoring breakdown
        scoring = state.get('scoring_breakdown', {})
        player_breakdown = scoring.get('player', {}).get('categories', {})
        ai_breakdown = scoring.get('ai', {}).get('categories', {})
        
        # Left column - Player scores
        player_x = 20
        player_y = 90
        pygame.draw.rect(self.screen, (100, 100, 200), (player_x, player_y - 5, 340, WINDOW_HEIGHT - 200))
        pygame.draw.rect(self.screen, (0, 0, 128), (player_x, player_y - 5, 340, WINDOW_HEIGHT - 200), 2)
        
        player_title = self.font_button.render(f"YOU: {state['total_player_points']} points", True, (255, 255, 255))
        self.screen.blit(player_title, (player_x + 10, player_y))
        
        player_y += 50
        for category, points in player_breakdown.items():
            category_text = self.font_small.render(f"• {category}: +{points}", True, (255, 255, 200))
            self.screen.blit(category_text, (player_x + 20, player_y))
            player_y += 28
        
        # Right column - AI scores
        ai_x = 440
        ai_y = 90
        pygame.draw.rect(self.screen, (200, 100, 100), (ai_x, ai_y - 5, 340, WINDOW_HEIGHT - 200))
        pygame.draw.rect(self.screen, (128, 0, 0), (ai_x, ai_y - 5, 340, WINDOW_HEIGHT - 200), 2)
        
        ai_title = self.font_button.render(f"AI: {state['total_ai_points']} points", True, (255, 255, 255))
        self.screen.blit(ai_title, (ai_x + 10, ai_y))
        
        ai_y += 50
        for category, points in ai_breakdown.items():
            category_text = self.font_small.render(f"• {category}: +{points}", True, (255, 200, 200))
            self.screen.blit(category_text, (ai_x + 20, ai_y))
            ai_y += 28
        
        # Buttons at bottom
        restart_width = 140
        restart_height = 50
        restart_x = (WINDOW_WIDTH // 2) - 150
        restart_y = WINDOW_HEIGHT - 80
        
        self.restart_button_rect = pygame.Rect(restart_x, restart_y, restart_width, restart_height)
        pygame.draw.rect(self.screen, (0, 128, 0), self.restart_button_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.restart_button_rect, 2)
        
        restart_text = self.font_normal.render("PLAY AGAIN", True, (255, 255, 255))
        self.screen.blit(restart_text, (restart_x + 10, restart_y + 10))
        
        # Quit button
        quit_width = 140
        quit_height = 50
        quit_x = (WINDOW_WIDTH // 2) + 10
        quit_y = WINDOW_HEIGHT - 80
        
        self.quit_button_rect = pygame.Rect(quit_x, quit_y, quit_width, quit_height)
        pygame.draw.rect(self.screen, (128, 0, 0), self.quit_button_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.quit_button_rect, 2)
        
        quit_text = self.font_normal.render("QUIT", True, (255, 255, 255))
        self.screen.blit(quit_text, (quit_x + 40, quit_y + 10))
    
    def _draw_player_info(self, state):
        """Draw scores and info"""
        # AI info (top right)
        ai_x = WINDOW_WIDTH - 30
        ai_y = 35
        
        ai_opponent_text = self.font_small.render("AI Opponent", True, (0, 0, 0))
        self.screen.blit(ai_opponent_text, (ai_x - ai_opponent_text.get_width(), ai_y))
        
        ai_cards_text = self.font_small.render(f"Cards: {state['ai_captured_count']}", True, (0, 0, 0))
        self.screen.blit(ai_cards_text, (ai_x - ai_cards_text.get_width(), ai_y + 18))
        
        ai_round_text = self.font_small.render(f"Round: {state['round_ai_points']}", True, (0, 0, 0))
        self.screen.blit(ai_round_text, (ai_x - ai_round_text.get_width(), ai_y + 36))
        
        ai_total_text = self.font_small.render(f"Total: {state['total_ai_points']}", True, (0, 0, 0))
        self.screen.blit(ai_total_text, (ai_x - ai_total_text.get_width(), ai_y + 54))
        
        # Player info (bottom left)
        player_x = 30
        player_y = self.canvas_height - 50
        
        player_label_text = self.font_small.render("Your Captured:", True, (0, 0, 0))
        self.screen.blit(player_label_text, (player_x, player_y))
        
        player_cards_text = self.font_small.render(f"Cards: {state['player_captured_count']}", True, (0, 0, 0))
        self.screen.blit(player_cards_text, (player_x, player_y + 18))
        
        player_round_text = self.font_small.render(f"Round: {state['round_player_points']}", True, (0, 0, 0))
        self.screen.blit(player_round_text, (player_x, player_y + 36))
        
        player_total_text = self.font_small.render(f"Total: {state['total_player_points']}", True, (0, 0, 0))
        self.screen.blit(player_total_text, (player_x, player_y + 54))
        
        # Deck info (center bottom)
        deck_text = self.font_small.render(f"Deck: {state['deck_remaining']} cards", True, (128, 128, 128))
        self.screen.blit(deck_text, (WINDOW_WIDTH // 2 - deck_text.get_width() // 2, self.canvas_height - 15))
    
    def _draw_control_panel(self, state):
        """Draw the control panel with status and buttons"""
        # Panel background
        pygame.draw.rect(self.screen, (192, 192, 192), (0, self.canvas_height, WINDOW_WIDTH, 100))
        
        # Status text
        if state['game_over']:
            if state['total_player_points'] > state['total_ai_points']:
                status = "YOU WIN! Click Restart to play again."
                status_color = (0, 128, 0)
            elif state['total_player_points'] < state['total_ai_points']:
                status = "AI WINS! Click Restart to play again."
                status_color = (128, 0, 0)
            else:
                status = "It's a TIE! Click Restart to play again."
                status_color = (0, 0, 128)
        elif state['is_player_turn']:
            status = "YOUR TURN: Click a card to play"
            status_color = (0, 0, 0)
        else:
            status = "AI is playing..."
            status_color = (0, 0, 0)
        
        status_text = self.font_normal.render(status, True, status_color)
        self.screen.blit(status_text, (10, self.canvas_height + 10))
        
        # Restart button
        restart_width = 120
        restart_height = 50
        restart_x = WINDOW_WIDTH // 2 - 70
        restart_y = self.canvas_height + 40
        
        self.restart_button_rect = pygame.Rect(restart_x, restart_y, restart_width, restart_height)
        pygame.draw.rect(self.screen, (0, 0, 255), self.restart_button_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.restart_button_rect, 2)
        
        restart_text = self.font_small.render("Restart", True, (255, 255, 255))
        self.screen.blit(restart_text, (restart_x + 15, restart_y + 12))
        
        # Quit button
        quit_width = 80
        quit_height = 50
        quit_x = WINDOW_WIDTH // 2 + 80
        quit_y = self.canvas_height + 40
        
        self.quit_button_rect = pygame.Rect(quit_x, quit_y, quit_width, quit_height)
        pygame.draw.rect(self.screen, (255, 0, 0), self.quit_button_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.quit_button_rect, 2)
        
        quit_text = self.font_small.render("Quit", True, (255, 255, 255))
        self.screen.blit(quit_text, (quit_x + 12, quit_y + 12))
    
    def _handle_events(self):
        """Handle Pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                if self.screen_state == "HOME":
                    if self.play_button_rect and self.play_button_rect.collidepoint(mouse_pos):
                        self.screen_state = "GAME"
                        # Play deal sound when entering the game (cards are dealt)
                        try:
                            if self.deal_sound:
                                self.deal_sound.play()
                        except Exception as e:
                            print(f"Error playing deal sound: {e}")
                
                elif self.screen_state == "GAME":
                    state = self.game.get_game_state()
                    
                    # Check restart button
                    if self.restart_button_rect and self.restart_button_rect.collidepoint(mouse_pos):
                        self.game.restart_game()
                        # Play deal sound on restart (new round)
                        try:
                            if self.deal_sound:
                                self.deal_sound.play()
                        except Exception as e:
                            print(f"Error playing deal sound: {e}")
                    
                    # Check quit button
                    elif self.quit_button_rect and self.quit_button_rect.collidepoint(mouse_pos):
                        self.running = False
                    
                    # Check card click (only if game not over)
                    elif not state['game_over']:
                        if state['is_player_turn']:
                            for card, card_rect in self.card_regions.items():
                                if card_rect.collidepoint(mouse_pos):
                                    if self.game.play_card(card):
                                        state = self.game.get_game_state()
                                        if state['game_state'] == "AI_PLAYING":
                                            self.ai_play_scheduled = True
                                    break
    
    def _update_ai(self):
        """Update AI logic"""
        state = self.game.get_game_state()
        if state['game_state'] == "AI_PLAYING" and not state['is_player_turn']:
            self.game.ai_play_turn()
    
    def run(self):
        """Main game loop"""
        self.ai_play_scheduled = False
        ai_play_delay = 0
        
        while self.running:
            self._handle_events()
            
            # Handle AI play with delay
            state = self.game.get_game_state()
            if state['game_state'] == "AI_PLAYING" and not state['is_player_turn']:
                ai_play_delay += 1
                if ai_play_delay > 30:  # ~0.5 second delay at 60 FPS
                    self._update_ai()
                    ai_play_delay = 0
            
            # Draw
            if self.screen_state == "HOME":
                self._draw_home_screen()
            elif self.screen_state == "GAME":
                state = self.game.get_game_state()
                if state['game_over']:
                    self._draw_game_screen()
                    self._draw_game_over_screen(state)
                else:
                    self._draw_game_screen()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
