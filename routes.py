from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
import logging
import random
import os
import time
from datetime import datetime
from models import Game, WordChain, db
from game_session import GameSession

logger = logging.getLogger(__name__)
main = Blueprint('main', __name__)

from flask_wtf import FlaskForm

@main.route('/')
def index():
    """Home page"""
    try:
        form = FlaskForm()
        form.csrf_token.data = form.csrf_token._value()  # Generate CSRF token
        top_scores = []  # You can add logic to get top scores here
        return render_template('index.html', top_scores=top_scores, form=form)
    except Exception as e:
        logger.error(f"Error loading index page: {e}")
        return "Server error", 500

@main.route('/start_game', methods=['POST'])
def start_game():
    """Start a new game session"""
    try:
        if not request.form.get('csrf_token'):
            flash('Invalid form submission', 'error')
            return redirect(url_for('main.index'))

        # Get game mode
        mode = request.form.get('mode', 'standard')
        difficulty = request.form.get('difficulty', 'medium')
        time_limit = 60  # Default time limit
        
        # Configure game settings based on mode
        if mode == 'time_attack':
            time_limit = int(request.form.get('time_limit', 60))
            difficulty = 'time_attack'
            is_time_attack = True
        elif mode == 'category_challenge':
            category = request.form.get('category', 'animals')
            difficulty = 'category'
            is_time_attack = False
        else:
            # Standard mode
            if difficulty == 'easy':
                time_limit = 90
            elif difficulty == 'hard':
                time_limit = 30
            is_time_attack = False

        # Create new game
        game = Game(
            difficulty=difficulty,
            time_limit=time_limit,
            start_time=datetime.utcnow()
        )
        if current_user.is_authenticated:
            game.user_id = current_user.id

        db.session.add(game)
        db.session.commit()

        # Initialize game session with session data
        session.clear()  # Clear any existing session data
        from game_config import WORD_LIST
        initial_word = random.choice(WORD_LIST)
        
        # Prepare mode settings
        mode_settings = {
            'time_limit': time_limit,
            'hints': 3,
            'difficulty': difficulty,
            'is_time_attack': is_time_attack,
            'start_time': game.start_time.timestamp()
        }
        
        # Add mode-specific settings
        if mode == 'category_challenge':
            mode_settings['category'] = category
            mode_settings['is_category_challenge'] = True
        
        success = GameSession.initialize_game(
            game=game,
            initial_word=initial_word,
            mode_settings=mode_settings
        )
        
        if not success or not GameSession.validate_game_state():
            db.session.delete(game)
            db.session.commit()
            flash('Failed to initialize game. Please try again.', 'error')
            
            # Redirect based on mode
            if mode == 'time_attack':
                return redirect(url_for('main.time_attack'))
            elif mode == 'category_challenge':
                return redirect(url_for('main.category_challenge'))
            else:
                return redirect(url_for('main.index'))

        logger.info(f"Started new {mode} game (ID: {game.id}) with difficulty: {difficulty}")
        return redirect(url_for('main.game'))

    except Exception as e:
        logger.error(f"Error starting game: {str(e)}")
        flash('Failed to start game. Please try again.', 'error')
        
        # Redirect based on mode
        mode = request.form.get('mode', 'standard')
        if mode == 'time_attack':
            return redirect(url_for('main.time_attack'))
        elif mode == 'category_challenge':
            return redirect(url_for('main.category_challenge'))
        else:
            return redirect(url_for('main.index'))

@main.route('/daily_challenge')
def daily_challenge():
    """Daily challenge page"""
    # Create a dictionary with daily challenge data
    daily_challenge_data = {
        'top_score': 0  # Default value, replace with actual logic later
    }
    # Get top games for leaderboard (empty list for now)
    top_games = []
    
    # Create form for CSRF protection
    form = FlaskForm()
    form.csrf_token.data = form.csrf_token._value()  # Generate CSRF token
    
    return render_template('daily_challenge.html', daily_challenge=daily_challenge_data, top_games=top_games, form=form)

@main.route('/start_daily_challenge', methods=['POST'])
def start_daily_challenge():
    """Start a new daily challenge game"""
    try:
        # Create a form for CSRF validation
        form = FlaskForm()
        if not form.validate_on_submit():
            flash('Invalid form submission', 'error')
            return redirect(url_for('main.daily_challenge'))
        
        # Similar logic to the start_game function but with daily challenge specific settings
        time_limit = 60  # Default time limit for daily challenge
        
        # Create new game
        game = Game(
            difficulty='daily',
            time_limit=time_limit,
            start_time=datetime.utcnow()
        )
        if current_user.is_authenticated:
            game.user_id = current_user.id

        db.session.add(game)
        db.session.commit()

        # Initialize game session with session data
        session.clear()  # Clear any existing session data
        from game_config import DAILY_CHALLENGE_WORDS
        # Use daily challenge words list for better experience
        initial_word = random.choice(DAILY_CHALLENGE_WORDS)
        
        success = GameSession.initialize_game(
            game=game,
            initial_word=initial_word,
            mode_settings={
                'time_limit': time_limit,
                'hints': 3,
                'difficulty': 'daily',
                'is_time_attack': False,
                'is_daily_challenge': True,
                'start_time': game.start_time.timestamp()
            }
        )
        
        if not success or not GameSession.validate_game_state():
            db.session.delete(game)
            db.session.commit()
            flash('Failed to initialize daily challenge. Please try again.', 'error')
            return redirect(url_for('main.daily_challenge'))

        logger.info(f"Started new daily challenge (ID: {game.id})")
        return redirect(url_for('main.game'))

    except Exception as e:
        logger.error(f"Error starting daily challenge: {str(e)}")
        flash('Failed to start daily challenge. Please try again.', 'error')
        return redirect(url_for('main.daily_challenge'))

@main.route('/time_attack')
def time_attack():
    """Time attack mode page"""
    time_options = [30, 60, 90, 120, 180, 300]  # Time options in seconds
    return render_template('time_attack.html', time_options=time_options)

@main.route('/category_challenge')
def category_challenge():
    """Category challenge page"""
    categories = ['animals', 'nature', 'weather', 'colors', 'emotions', 'food', 'sports', 'music']
    return render_template('category_challenge.html', categories=categories)

@main.route('/achievements')
def achievements():
    """Achievements page"""
    return render_template('achievements.html')

@main.route('/multiplayer')
def multiplayer():
    """Multiplayer game page"""
    return render_template('multiplayer.html')

@main.route('/profile')
@login_required
def profile():
    """User profile page"""
    try:
        # Get user's game statistics
        from game_config import ACHIEVEMENTS
        
        user_games = Game.query.filter_by(user_id=current_user.id).all()
        
        # Calculate statistics
        stats = {
            'total_games': len(user_games),
            'total_score': sum(game.final_score for game in user_games if game.final_score),
            'highest_score': max([game.final_score for game in user_games if game.final_score] or [0]),
            'highest_streak': 0,  # Would be calculated from word chains
            'mode_distribution': {
                'regular': sum(1 for game in user_games if game.difficulty == 'medium'),
                'daily_challenge': sum(1 for game in user_games if game.difficulty == 'daily'),
                'category_challenge': sum(1 for game in user_games if game.difficulty == 'category'),
                'time_attack': sum(1 for game in user_games if game.difficulty == 'time_attack'),
                'multiplayer': 0,  # Would come from a different table
                'word_ladder': 0,  # For future implementation
                'reverse_mode': 0   # For future implementation
            }
        }
        
        # Prepare achievements
        achievements = [
            {
                'id': key,
                'name': data['name'],
                'description': data['description'],
                'icon': data['icon']
            } 
            for key, data in ACHIEVEMENTS.items()
        ]
        
        # In a real implementation, earned achievements would come from a database
        earned_achievement_ids = []
        
        return render_template(
            'profile.html',
            stats=stats,
            achievements=achievements,
            earned_achievement_ids=earned_achievement_ids
        )
    except Exception as e:
        logger.error(f"Error loading profile: {str(e)}")
        flash('Error loading profile data', 'error')
        return redirect(url_for('main.index'))

@main.route('/game')
def game():
    """Game page"""
    try:
        # Validate game session
        if not GameSession.validate_game_state():
            session.clear()
            flash('No active game session. Please start a new game.', 'warning')
            return redirect(url_for('main.index'))

        game_id = session.get('game_id')
        if not game_id:
            session.clear()
            flash('Invalid game session. Please start a new game.', 'error')
            return redirect(url_for('main.index'))

        game = Game.query.get(game_id)
        if not game:
            session.clear()
            flash('Game not found. Please start a new game.', 'error')
            return redirect(url_for('main.index'))

        # Check if game has expired
        elapsed_time = (datetime.utcnow() - game.start_time).total_seconds()
        if elapsed_time > session.get('time_limit', 60):
            session.clear()
            flash('Game has expired. Please start a new game.', 'info')
            return redirect(url_for('main.index'))
        
        # Render the game template with session data
        return render_template(
            'game.html',
            current_word=session.get('current_word', ''),
            score=session.get('score', 0),
            streak=session.get('streak', 0),
            previous_words=session.get('previous_words', []),
            time_limit=session.get('time_limit', 60),
            hints_remaining=session.get('hints_remaining', 3),
            current_level=session.get('current_level', 1),
            level_progress=session.get('level_progress', 0),
            time_remaining=int(session.get('time_limit', 60) - elapsed_time),
            is_word_ladder=False,
            current_category=None
        )
    except Exception as e:
        logger.error(f"Error in game route: {str(e)}")
        session.clear()
        flash('An error occurred. Please try again.', 'error')
        return redirect(url_for('main.index'))

@main.route('/word_ladder')
def word_ladder():
    """Word ladder game page"""
    return render_template('word_ladder.html')

@main.route('/reverse_mode')
def reverse_mode():
    """Reverse mode game page"""
    return render_template('reverse_mode.html')

@main.route('/admin/debug')
@login_required
def admin_debug_dashboard():
    """Admin debug dashboard"""
    try:
        from debug_monitor import debug_monitor
        import psutil
        
        # Get system stats
        process = psutil.Process(os.getpid())
        system_stats = {
            'cpu_percent': process.cpu_percent(),
            'memory_usage': process.memory_info().rss / 1024 / 1024,  # MB
            'thread_count': len(process.threads()),
            'uptime': time.time() - debug_monitor.start_time,
            'connection_count': debug_monitor.connection_count,
            'error_count': debug_monitor.error_count,
        }
        
        # Get active rooms
        active_rooms = debug_monitor.active_rooms
        
        # Get game metrics
        game_count = Game.query.count()
        recent_games = Game.query.order_by(Game.start_time.desc()).limit(10).all()
        word_chains = WordChain.query.order_by(WordChain.timestamp.desc()).limit(20).all()
        
        # Create now function for template to get current datetime
        def now():
            return datetime.now()
        
        return render_template(
            'admin/debug_dashboard.html',
            system_stats=system_stats,
            active_rooms=active_rooms,
            game_count=game_count,
            recent_games=recent_games,
            word_chains=word_chains,
            now=now,
            time=time
        )
    except Exception as e:
        logger.error(f"Error loading debug dashboard: {str(e)}")
        flash('Error loading debug dashboard', 'error')
        return redirect(url_for('main.index'))

@main.route('/submit_word', methods=['POST'])
def submit_word():
    """Handle word submission during a game"""
    try:
        # Get submitted word from request
        data = request.get_json()
        submitted_word = data.get('word', '').strip().lower()
        
        # Validate active game session
        if not GameSession.validate_game_state():
            return jsonify({
                'success': False,
                'error': 'No active game session.',
                'redirect': url_for('main.index')
            }), 400
        
        # Get current game state from session
        current_word = session.get('current_word', '')
        previous_words = session.get('previous_words', [])
        score = session.get('score', 0)
        streak = session.get('streak', 0)
        
        # Validate submitted word
        if not submitted_word:
            return jsonify({
                'success': False,
                'error': 'Please enter a word.'
            }), 400
        
        # Check if word is already used
        if submitted_word in previous_words:
            return jsonify({
                'success': False,
                'error': 'Word already used in this game!'
            }), 400
        
        # Logic to determine if words are related (simplified for now)
        # Would be improved with actual word association API or algorithm
        from multiplayer import are_words_related
        if not are_words_related(current_word, submitted_word):
            # Decrement streak when words aren't related
            streak = 0
            return jsonify({
                'success': False,
                'error': f"'{submitted_word}' doesn't seem related to '{current_word}'."
            }), 400
        
        # Calculate points for this word
        # Base points, can be modified based on word length, difficulty, etc.
        points = 10
        
        # Apply streak bonus
        multiplier = min(3, 1 + (streak * 0.5))  # Maximum multiplier of 3x
        bonus_points = int(points * multiplier)
        
        # Update game state
        streak += 1
        previous_words.append(current_word)
        score += bonus_points
        
        # Update session data
        session['current_word'] = submitted_word
        session['previous_words'] = previous_words
        session['score'] = score
        session['streak'] = streak
        
        # If user is authenticated, save word chain to database
        game_id = session.get('game_id')
        if game_id and current_user.is_authenticated:
            word_chain = WordChain(
                game_id=game_id,
                word=submitted_word,
                previous_word=current_word,
                points=bonus_points,
                player_id=current_user.id
            )
            db.session.add(word_chain)
            db.session.commit()
        
        # Return success response with updated game state
        return jsonify({
            'success': True,
            'points': bonus_points,
            'multiplier': multiplier,
            'newWord': submitted_word,
            'score': score,
            'streak': streak
        })
    
    except Exception as e:
        logger.error(f"Error processing word submission: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred. Please try again.'
        }), 500
        
@main.route('/get_hint', methods=['POST'])
def get_hint():
    """Provide a hint for the current word"""
    try:
        # Check for active game session
        if not GameSession.validate_game_state():
            return jsonify({
                'success': False,
                'error': 'No active game session.'
            }), 400
        
        # Ensure player has hints remaining
        hints_remaining = session.get('hints_remaining', 0)
        if hints_remaining <= 0:
            return jsonify({
                'success': False,
                'error': 'No hints remaining!'
            }), 400
        
        # Get current word
        current_word = session.get('current_word', '')
        if not current_word:
            return jsonify({
                'success': False,
                'error': 'No current word found.'
            }), 400
        
        # Generate hint based on word
        # This is a simplified hint generator - would be improved with a real word API
        if len(current_word) <= 3:
            hint = f"This word has {len(current_word)} letters."
        else:
            # Reveal first and last letter with rest obscured
            hint = f"Starts with '{current_word[0]}' and ends with '{current_word[-1]}'"
        
        # Decrement hints remaining
        session['hints_remaining'] = hints_remaining - 1
        
        return jsonify({
            'success': True,
            'hint': hint,
            'hintsRemaining': hints_remaining - 1
        })
    
    except Exception as e:
        logger.error(f"Error generating hint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate hint.'
        }), 500

@main.route('/get_definition', methods=['POST'])
def get_definition():
    """Get the definition of the current word"""
    try:
        # Check for active game session
        if not GameSession.validate_game_state():
            return jsonify({
                'success': False,
                'error': 'No active game session.'
            }), 400
        
        # Get current word
        current_word = session.get('current_word', '')
        if not current_word:
            return jsonify({
                'success': False,
                'error': 'No current word found.'
            }), 400
        
        # For a real implementation, this would call a dictionary API
        # For now, generate a placeholder definition
        definition = f"Definition for '{current_word}': (This would fetch from a real dictionary API)"
        
        return jsonify({
            'success': True,
            'definition': definition
        })
    
    except Exception as e:
        logger.error(f"Error getting definition: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get definition.'
        }), 500

@main.route('/get_etymology', methods=['POST'])
def get_etymology():
    """Get the etymology of the current word"""
    try:
        # Check for active game session
        if not GameSession.validate_game_state():
            return jsonify({
                'success': False,
                'error': 'No active game session.'
            }), 400
        
        # Get current word
        current_word = session.get('current_word', '')
        if not current_word:
            return jsonify({
                'success': False,
                'error': 'No current word found.'
            }), 400
        
        # For a real implementation, this would call an etymology API
        # For now, generate a placeholder etymology
        etymology = f"Etymology of '{current_word}': (This would fetch from a real etymology API)"
        
        return jsonify({
            'success': True,
            'etymology': etymology
        })
    
    except Exception as e:
        logger.error(f"Error getting etymology: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get etymology.'
        }), 500