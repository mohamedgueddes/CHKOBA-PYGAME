"""
Chkobba Card Game - Main Game Engine
A Tunisian card game using a 40-card deck
"""

from enum import Enum
from typing import List, Optional, Tuple


class CardRank(Enum):
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    JACK = 8      # Kawwal
    QUEEN = 9     # Moujira
    KING = 10     # Rayy


class CardSuit(Enum):
    COEUR = "Coeur"      # Hearts
    DINARI = "Dinari"    # Diamonds
    PIQUE = "Pique"      # Spades
    TREFELE = "Trefele"  # Clubs


class Card:
    """Represents a single card"""
    
    def __init__(self, rank: CardRank, suit: CardSuit):
        self.rank = rank
        self.suit = suit
        self.value = rank.value
    
    def __str__(self):
        rank_name = {
            1: "A", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7",
            8: "J", 9: "Q", 10: "K"
        }.get(self.value, "?")
        return f"{rank_name}♦" if self.suit == CardSuit.DINARI else f"{rank_name}{self.suit.value[0]}"
    
    def __repr__(self):
        return str(self)
    
    def __eq__(self, other):
        if isinstance(other, Card):
            return self.rank == other.rank and self.suit == other.suit
        return False
    
    def __hash__(self):
        return hash((self.rank, self.suit))


class Deck:
    """40-card Chkobba deck"""
    
    def __init__(self):
        self.cards = []
        self.create_deck()
        self.shuffle()
    
    def create_deck(self):
        """Create a 40-card Chkobba deck"""
        self.cards = []
        for suit in CardSuit:
            for rank in CardRank:
                card = Card(rank, suit)
                self.cards.append(card)
    
    def shuffle(self):
        """Shuffle the deck"""
        import random
        random.shuffle(self.cards)
    
    def deal_card(self) -> Optional[Card]:
        """Deal a card from the deck"""
        if self.cards:
            return self.cards.pop(0)
        return None
    
    def remaining(self) -> int:
        """Get number of cards remaining"""
        return len(self.cards)


class Hand:
    """Player's hand of cards"""
    
    def __init__(self, player_id: int):
        self.player_id = player_id
        self.cards = []
    
    def add_card(self, card: Card):
        """Add card to hand"""
        self.cards.append(card)
    
    def play_card(self, card: Card) -> bool:
        """Remove and play card from hand"""
        if card in self.cards:
            self.cards.remove(card)
            return True
        return False
    
    def has_card(self, card: Card) -> bool:
        """Check if hand has card"""
        return card in self.cards
    
    def get_card_by_value(self, value: int) -> Optional[Card]:
        """Get first card with matching value"""
        for card in self.cards:
            if card.value == value:
                return card
        return None
    
    def get_cards_by_suit(self, suit: CardSuit) -> List[Card]:
        """Get all cards of specific suit"""
        return [card for card in self.cards if card.suit == suit]
    
    def clear(self):
        """Clear all cards from hand"""
        self.cards = []


class Table:
    """Cards on the playing table"""
    
    def __init__(self):
        self.cards = []
    
    def add_card(self, card: Card):
        """Add card to table"""
        self.cards.append(card)
    
    def add_cards(self, cards: List[Card]):
        """Add multiple cards to table"""
        self.cards.extend(cards)
    
    def remove_cards(self, cards_to_remove: List[Card]):
        """Remove cards from table"""
        for card in cards_to_remove:
            if card in self.cards:
                self.cards.remove(card)
    
    def clear(self):
        """Clear all cards from table"""
        self.cards = []
    
    def get_cards_with_sum(self, target_sum: int) -> List[List[Card]]:
        """Find all combinations of cards that sum to target"""
        combinations = []
        
        # Single cards matching value
        for card in self.cards:
            if card.value == target_sum:
                combinations.append([card])
        
        # Multiple card combinations
        self._find_combinations(self.cards, target_sum, [], combinations)
        
        return combinations
    
    def _find_combinations(self, cards: List[Card], target: int, current: List[Card], result: List[List[Card]]):
        """Helper to find card combinations recursively"""
        if target == 0 and len(current) > 1:
            result.append(current[:])
            return
        
        if target < 0 or not cards:
            return
        
        for i, card in enumerate(cards):
            if card.value <= target:
                current.append(card)
                self._find_combinations(cards[i+1:], target - card.value, current, result)
                current.pop()
    
    def is_empty(self) -> bool:
        """Check if table is empty"""
        return len(self.cards) == 0
    
    def get_card_count(self) -> int:
        """Get number of cards on table"""
        return len(self.cards)


class GameRound:
    """Represents one round of Chkobba"""
    
    def __init__(self, num_players: int = 2):
        self.num_players = num_players
        self.players = [{'hand': Hand(i), 'captured': []} for i in range(num_players)]
        self.table = Table()
        self.deck = Deck()
        self.current_player = 0
        self.round_over = False
        self.last_capture_player = None
    
    def deal_initial_hands(self):
        """Deal 3 cards to each player and 4 to table"""
        self._reset_round_state()

        # Redeal if 3 or more initial table cards are kings.
        while True:
            self._deal_opening_cards()
            kings_on_table = len([c for c in self.table.cards if c.rank == CardRank.KING])
            if kings_on_table < 3:
                break
            self._reset_round_state()

    def _reset_round_state(self):
        """Reset deck, hands, table and transient round state."""
        self.deck = Deck()
        self.table.clear()
        self.last_capture_player = None
        for player in self.players:
            player['hand'].clear()
            player['captured'] = []
            player['sweeps'] = 0

    def _deal_opening_cards(self):
        """Deal the opening 3-hand and 4-table setup once."""
        # Deal 3 cards to each player
        for _ in range(3):
            for player_idx in range(self.num_players):
                card = self.deck.deal_card()
                if card:
                    self.players[player_idx]['hand'].add_card(card)
        
        # Deal 4 cards to table
        for _ in range(4):
            card = self.deck.deal_card()
            if card:
                self.table.add_card(card)
    
    def can_capture(self, played_card: Card) -> List[Card]:
        """
        Check what cards from table can be captured by the played card
        Returns list of cards that can be captured
        """
        captures = []
        
        # Exact match
        for table_card in self.table.cards:
            if table_card.value == played_card.value:
                captures.append(table_card)
                break  # Only one exact match per card
        
        # Combination captures (sum) only if no exact match.
        if not captures:
            combinations = self.table.get_cards_with_sum(played_card.value)
            if combinations:
                multi_card_combos = [combo for combo in combinations if len(combo) > 1]
                if multi_card_combos:
                    # Prefer the largest valid set for deterministic digital behavior.
                    multi_card_combos.sort(key=lambda combo: (-len(combo), [c.value for c in combo]))
                    captures = multi_card_combos[0]
        
        return captures
    
    def play_card(self, played_card: Card) -> bool:
        """
        Play a single card for the current player following capture priority.
        Returns True if card was played successfully.
        """
        hand = self.players[self.current_player]['hand']
        if not hand.has_card(played_card):
            return False

        hand.play_card(played_card)
        captures = self.can_capture(played_card)

        if captures:
            self.players[self.current_player]['captured'].append(played_card)
            self.players[self.current_player]['captured'].extend(captures)
            self.table.remove_cards(captures)
            self.last_capture_player = self.current_player

            # Chkobba: table was cleared and this is not the final card of the round.
            if self.table.is_empty() and not self._is_last_card_of_round():
                self.players[self.current_player]['sweeps'] = self.players[self.current_player].get('sweeps', 0) + 1
        else:
            # No capture, card trails on table.
            self.table.add_card(played_card)

        return True

    def _is_last_card_of_round(self) -> bool:
        """True only when deck is empty and every player has no cards in hand."""
        return self.deck.remaining() == 0 and self.all_hands_empty()

    def collect_last_sweep(self):
        """At round end, remaining table cards go to the player who captured last."""
        if self.table.cards and self.last_capture_player is not None:
            self.players[self.last_capture_player]['captured'].extend(self.table.cards)
            self.table.clear()
    
    def refill_all_hands(self):
        """Refill all hands to 3 cards from deck."""
        for player_idx in range(self.num_players):
            while len(self.players[player_idx]['hand'].cards) < 3:
                card = self.deck.deal_card()
                if card:
                    self.players[player_idx]['hand'].add_card(card)
                else:
                    break
    
    def all_hands_empty(self) -> bool:
        """Check if all players have empty hands"""
        for player_idx in range(self.num_players):
            if self.players[player_idx]['hand'].cards:
                return False
        return True
    
    def get_player_hand(self, player_idx: int) -> Hand:
        """Get player's hand"""
        return self.players[player_idx]['hand']
    
    def get_player_captured(self, player_idx: int) -> List[Card]:
        """Get player's captured cards"""
        return self.players[player_idx]['captured']
    
    def next_turn(self):
        """Move to next player"""
        self.current_player = (self.current_player + 1) % self.num_players
    
    def refill_hands(self):
        """Refill hands with 3 cards from deck (if available)"""
        for player_idx in range(self.num_players):
            while len(self.players[player_idx]['hand'].cards) < 3:
                card = self.deck.deal_card()
                if card:
                    self.players[player_idx]['hand'].add_card(card)
                else:
                    break
    
    def is_hand_empty(self, player_idx: int) -> bool:
        """Check if player's hand is empty"""
        return len(self.players[player_idx]['hand'].cards) == 0
    
    def are_all_hands_empty(self) -> bool:
        """Check if all hands are empty (end of hand)"""
        for player_idx in range(self.num_players):
            if not self.is_hand_empty(player_idx):
                return False
        return True


class ChkobbaScoring:
    """Scoring system for Chkobba"""
    
    @staticmethod
    def calculate_scores(players_captured: List[List[Card]], sweeps: Tuple[int, int] = (0, 0)) -> Tuple[int, int]:
        """
        Calculate points for each player
        Returns: (player_0_points, player_1_points)
        """
        points = [0, 0]
        
        # Il Karta - 1 point for most cards (>20)
        card_counts = [len(captured) for captured in players_captured]
        if card_counts[0] > 20:
            points[0] += 1
        elif card_counts[1] > 20:
            points[1] += 1
        
        # Il Dineri - 1 point for most diamonds
        diamonds = [
            len([c for c in captured if c.suit == CardSuit.DINARI]) 
            for captured in players_captured
        ]
        if diamonds[0] > diamonds[1]:
            points[0] += 1
        elif diamonds[1] > diamonds[0]:
            points[1] += 1
        
        # Il Barmila - 1 point for most 7s, then 6s, 5s... down to A.
        sevens = [
            len([c for c in captured if c.rank == CardRank.SEVEN]) 
            for captured in players_captured
        ]
        if sevens[0] > sevens[1]:
            points[0] += 1
        elif sevens[1] > sevens[0]:
            points[1] += 1
        else:
            for value in [6, 5, 4, 3, 2, 1, 8, 9, 10]:
                counts = [
                    len([c for c in captured if c.value == value])
                    for captured in players_captured
                ]
                if counts[0] > counts[1]:
                    points[0] += 1
                    break
                if counts[1] > counts[0]:
                    points[1] += 1
                    break
        
        # Sab'a l-hayya - 7 of Diamonds
        for player_idx, captured in enumerate(players_captured):
            for card in captured:
                if card.rank == CardRank.SEVEN and card.suit == CardSuit.DINARI:
                    points[player_idx] += 1
                    break

        # Chkobbas (sweeps)
        points[0] += sweeps[0]
        points[1] += sweeps[1]
        
        return tuple(points)
    
    @staticmethod
    def count_sweeps(game_round: GameRound) -> Tuple[int, int]:
        """
        Count sweeps for each player
        Count chkobbas tracked during the round
        """
        return (
            game_round.players[0].get('sweeps', 0),
            game_round.players[1].get('sweeps', 0),
        )
