from datetime import datetime
from typing import Optional, Dict, Any
from flask import session
import logging
import random
from models import Game, WordChain
from app import db

logger = logging.getLogger(__name__)

class GameSession:
    @staticmethod
    def initialize_game(game: Game, initial_word: str, mode_settings: Dict[str, Any]) -> bool:
        """Initialize a new game session with proper error handling"""
        try:
            # Basic validation
            if not game or not initial_word or not mode_settings:
                logger.error("Missing required parameters for game initialization")
                return False

            # Set up session data
            session['game_id'] = game.id
            session['current_word'] = initial_word
            session['score'] = 0
            session['previous_words'] = [initial_word]
            session['streak'] = 0
            session['time_limit'] = mode_settings.get('time_limit', 60)
            session['hints_remaining'] = mode_settings.get('hints', 3)
            session['current_level'] = 1
            session['level_progress'] = 0
            session['start_time'] = mode_settings.get('start_time', datetime.utcnow().timestamp())
            session['is_active'] = True
            session['difficulty'] = mode_settings.get('difficulty', 'medium')

            # Initialize first word in chain
            word_chain = WordChain(
                game_id=game.id,
                word=initial_word,
                timestamp=datetime.utcnow()
            )
            db.session.add(word_chain)
            db.session.commit()

            logger.info(f"Game session initialized successfully: Game ID {game.id}")
            return True

        except Exception as e:
            logger.error(f"Error initializing game session: {str(e)}")
            return False

    @staticmethod
    def validate_game_state() -> bool:
        """Validate current game session state"""
        try:
            required_keys = [
                'game_id', 'current_word', 'score', 
                'previous_words', 'streak', 'time_limit',
                'hints_remaining', 'is_active', 'start_time'
            ]

            # Check if all required keys exist
            if not all(key in session for key in required_keys):
                return False

            # Check if session is marked as active
            if not session.get('is_active', False):
                return False

            # Check if game hasn't expired
            elapsed_time = datetime.utcnow().timestamp() - session.get('start_time', 0)
            if elapsed_time > session.get('time_limit', 60):
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating game state: {str(e)}")
            return False

    @staticmethod
    def clear_session() -> None:
        """Safely clear the game session"""
        try:
            session.clear()
            logger.info("Game session cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing session: {str(e)}")
            raise