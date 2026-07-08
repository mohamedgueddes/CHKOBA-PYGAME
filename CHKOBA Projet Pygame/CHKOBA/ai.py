"""
AI Opponent Logic for Chkobba
"""

import random
from typing import Optional, List, Tuple
from chkobba_game import Card, CardRank, CardSuit, GameRound


class ChkobbaAI:
    """AI player for Chkobba game"""
    
    def __init__(self, player_id: int = 1):
        self.player_id = player_id
        self.memory = {}  # Track cards seen
        self.difficulty = "medium"  # easy, medium, hard
    
    def choose_card_to_play(self, game_round: GameRound) -> Card:
        """
        Choose which card to play from hand
        Returns the card to play
        """
        hand = game_round.get_player_hand(self.player_id)
        
        if not hand.cards:
            return None
        
        # Calculate the best card to play
        best_card = None
        best_score = -1
        
        for card in hand.cards:
            score = self._evaluate_card(card, game_round)
            if score > best_score:
                best_score = score
                best_card = card
        
        return best_card if best_card else hand.cards[0]
    
    def _evaluate_card(self, card: Card, game_round: GameRound) -> float:
        """
        Evaluate how good a card is to play
        Higher score = better card to play
        """
        score = 0.0
        
        # Check what can be captured
        captured = game_round.can_capture(card)
        
        if captured:
            # Prioritize captures
            score += 10
            
            # Bonus for capturing diamonds (Il Dineri)
            diamonds_captured = len([c for c in captured if c.suit == CardSuit.DINARI])
            score += diamonds_captured * 2
            
            # Bonus for capturing 7s (Il Barmila)
            sevens_captured = len([c for c in captured if c.rank == CardRank.SEVEN])
            score += sevens_captured * 3
            
            # Extra bonus for 7 of Diamonds
            if any(c.rank == CardRank.SEVEN and c.suit == CardSuit.DINARI for c in captured):
                score += 5
            
            # Bonus for clearing table (Chkobba)
            if game_round.table.is_empty() or len(game_round.table.cards) == len(captured):
                score += 20
            
            # Bonus for capturing more cards
            score += len(captured) * 0.5
        else:
            # No capture - put card on table
            score = 1.0
            
            # Penalty for putting down high value cards (might get captured)
            if card.value >= 8:
                score -= card.value * 0.5
        
        # Add difficulty variance
        if self.difficulty == "easy":
            score += random.uniform(-5, 5)
        elif self.difficulty == "medium":
            score += random.uniform(-2, 2)
        # hard: no variance
        
        return score
    
    def update_memory(self, card: Card, player_id: int, location: str):
        """
        Update memory of seen cards
        location: 'hand', 'table', 'discarded'
        """
        key = (player_id, location)
        if key not in self.memory:
            self.memory[key] = []
        self.memory[key].append(card)
    
    def remember_table_cards(self, game_round: GameRound):
        """Remember what's on the table"""
        for card in game_round.table.cards:
            self.update_memory(card, -1, 'table')
    
    def set_difficulty(self, difficulty: str):
        """Set AI difficulty level"""
        if difficulty in ["easy", "medium", "hard"]:
            self.difficulty = difficulty
