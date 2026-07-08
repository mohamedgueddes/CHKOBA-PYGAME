"""
Main Chkobba Game Controller
Manages game flow and state
"""

from chkobba_game import GameRound, ChkobbaScoring, Card
from ai import ChkobbaAI


class ChkobbaGameController:
    """Controls the Chkobba game flow"""
    
    def __init__(self, player_difficulty: str = "medium"):
        self.player_id = 0  # Human player
        self.ai_id = 1      # AI opponent
        
        self.current_round = None
        self.ai_opponent = ChkobbaAI(self.ai_id)
        self.ai_opponent.set_difficulty(player_difficulty)
        
        self.game_over = False
        self.current_state = "WAITING_PLAYER_CARD"  # WAITING_PLAYER_CARD, AI_PLAYING, GAME_OVER
        self.round_scores = (0, 0)
        self.total_scores = (0, 0)
        
        # Start new game
        self.start_new_round()
    
    def start_new_round(self):
        """Start a new round"""
        self.current_round = GameRound(num_players=2)
        self.current_round.deal_initial_hands()
        self.current_state = "WAITING_PLAYER_CARD"
        self.current_round.current_player = 0
    
    def play_card(self, card) -> bool:
        """Player plays one card."""
        if self.current_round.current_player != self.player_id:
            return False

        hand = self.current_round.get_player_hand(self.player_id)
        if not hand.has_card(card):
            return False

        success = self.current_round.play_card(card)
        if success:
            self._check_turn_progression()
        return success
    
    def _check_turn_progression(self):
        """Check what happens next in the game"""
        # Next player's turn
        self.current_round.next_turn()

        # Refill only when both players finished their current 3-card hands.
        if self.current_round.all_hands_empty() and self.current_round.deck.remaining() > 0:
            self.current_round.refill_all_hands()

        # End of round: deck empty and hands empty after a turn.
        if self.current_round.deck.remaining() == 0 and self.current_round.all_hands_empty():
            self._end_round()
            return
        
        if self.current_round.current_player == self.ai_id:
            self.current_state = "AI_PLAYING"
        else:
            self.current_state = "WAITING_PLAYER_CARD"
    
    def ai_play_turn(self):
        """Execute AI's turn"""
        hand = self.current_round.get_player_hand(self.ai_id)

        if not hand.cards:
            self.current_round.next_turn()
            if self.current_round.deck.remaining() == 0 and self.current_round.all_hands_empty():
                self._end_round()
            else:
                self.current_round.refill_all_hands()
            return

        card = self.ai_opponent.choose_card_to_play(self.current_round)
        self.current_round.play_card(card)

        # Check turn progression
        self._check_turn_progression()
    
    def _end_round(self):
        """End the round and calculate scores"""
        self.game_over = True
        self.current_state = "GAME_OVER"

        # Last sweep rule: remaining table cards go to last capture player.
        self.current_round.collect_last_sweep()
        
        # Get captured cards for each player
        player_0_captured = self.current_round.get_player_captured(self.player_id)
        player_1_captured = self.current_round.get_player_captured(self.ai_id)
        
        # Calculate scores
        sweeps = ChkobbaScoring.count_sweeps(self.current_round)
        scores = ChkobbaScoring.calculate_scores([player_0_captured, player_1_captured], sweeps)
        self.round_scores = scores
        self.total_scores = (
            self.total_scores[0] + scores[0],
            self.total_scores[1] + scores[1],
        )
        
        return scores
    
    def _calculate_detailed_scores(self):
        """Calculate detailed breakdown of scoring for each category"""
        player_0_captured = self.current_round.get_player_captured(self.player_id)
        player_1_captured = self.current_round.get_player_captured(self.ai_id)
        sweeps = ChkobbaScoring.count_sweeps(self.current_round)
        
        from chkobba_game import CardSuit, CardRank
        
        breakdown = {
            'player': {'points': 0, 'categories': {}},
            'ai': {'points': 0, 'categories': {}}
        }
        
        # 1. Il Karta - Most cards (>20)
        card_counts = [len(player_0_captured), len(player_1_captured)]
        if card_counts[0] > 20:
            breakdown['player']['categories']['Most Cards'] = 1
            breakdown['player']['points'] += 1
        elif card_counts[1] > 20:
            breakdown['ai']['categories']['Most Cards'] = 1
            breakdown['ai']['points'] += 1
        
        # 2. Il Dineri - Most Diamonds
        diamonds = [
            len([c for c in player_0_captured if c.suit == CardSuit.DINARI]),
            len([c for c in player_1_captured if c.suit == CardSuit.DINARI])
        ]
        if diamonds[0] > diamonds[1]:
            breakdown['player']['categories']['Most Diamonds'] = 1
            breakdown['player']['points'] += 1
        elif diamonds[1] > diamonds[0]:
            breakdown['ai']['categories']['Most Diamonds'] = 1
            breakdown['ai']['points'] += 1
        
        # 3. Il Barmila - Most 7s or highest card
        sevens = [
            len([c for c in player_0_captured if c.rank == CardRank.SEVEN]),
            len([c for c in player_1_captured if c.rank == CardRank.SEVEN])
        ]
        if sevens[0] > sevens[1]:
            breakdown['player']['categories']['Most 7s (Primiera)'] = 1
            breakdown['player']['points'] += 1
        elif sevens[1] > sevens[0]:
            breakdown['ai']['categories']['Most 7s (Primiera)'] = 1
            breakdown['ai']['points'] += 1
        else:
            for value in [6, 5, 4, 3, 2, 1, 8, 9, 10]:
                counts = [
                    len([c for c in player_0_captured if c.value == value]),
                    len([c for c in player_1_captured if c.value == value])
                ]
                if counts[0] > counts[1]:
                    breakdown['player']['categories']['Primiera (Most High Cards)'] = 1
                    breakdown['player']['points'] += 1
                    break
                if counts[1] > counts[0]:
                    breakdown['ai']['categories']['Primiera (Most High Cards)'] = 1
                    breakdown['ai']['points'] += 1
                    break
        
        # 4. Sab'a l-hayya - 7 of Diamonds
        for card in player_0_captured:
            if card.rank == CardRank.SEVEN and card.suit == CardSuit.DINARI:
                breakdown['player']['categories']['7 of Diamonds'] = 1
                breakdown['player']['points'] += 1
                break
        for card in player_1_captured:
            if card.rank == CardRank.SEVEN and card.suit == CardSuit.DINARI:
                breakdown['ai']['categories']['7 of Diamonds'] = 1
                breakdown['ai']['points'] += 1
                break
        
        # 5. Chkobbas - Sweeps
        if sweeps[0] > 0:
            breakdown['player']['categories']['Sweeps (Chkobbas)'] = sweeps[0]
            breakdown['player']['points'] += sweeps[0]
        if sweeps[1] > 0:
            breakdown['ai']['categories']['Sweeps (Chkobbas)'] = sweeps[1]
            breakdown['ai']['points'] += sweeps[1]
        
        return breakdown
    
    def get_game_state(self) -> dict:
        """Get current game state for UI"""
        hand = self.current_round.get_player_hand(self.player_id)
        ai_hand = self.current_round.get_player_hand(self.ai_id)
        ai_captured = len(self.current_round.get_player_captured(self.ai_id))
        player_captured = len(self.current_round.get_player_captured(self.player_id))
        
        state = {
            'current_player': self.current_round.current_player,
            'player_hand': hand.cards,
            'ai_hand_size': len(ai_hand.cards),
            'table_cards': self.current_round.table.cards,
            'player_captured_count': player_captured,
            'ai_captured_count': ai_captured,
            'deck_remaining': self.current_round.deck.remaining(),
            'is_player_turn': self.current_round.current_player == self.player_id and self.current_state == "WAITING_PLAYER_CARD",
            'game_state': self.current_state,
            'game_over': self.game_over,
            'player_sweeps': self.current_round.players[self.player_id].get('sweeps', 0),
            'ai_sweeps': self.current_round.players[self.ai_id].get('sweeps', 0),
            'round_player_points': self.round_scores[0],
            'round_ai_points': self.round_scores[1],
            'total_player_points': self.total_scores[0],
            'total_ai_points': self.total_scores[1],
        }
        
        # Add detailed scoring breakdown if game is over
        if self.game_over:
            state['scoring_breakdown'] = self._calculate_detailed_scores()
        
        return state
    
    def restart_game(self):
        """Restart the game"""
        self.game_over = False
        self.current_state = "WAITING_PLAYER_CARD"
        self.round_scores = (0, 0)
        self.total_scores = (0, 0)
        self.start_new_round()
