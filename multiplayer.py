from flask_socketio import emit, join_room, leave_room
from flask import request
from app import socketio, db
from models import Game, Player, WordChain
import random
import string
from datetime import datetime
import logging
from game_config import WORD_CATEGORIES
from debug_monitor import debug_monitor, monitor_execution

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Store active game rooms
active_rooms = {}

@monitor_execution
def generate_room_code():
    """Generate a unique 6-character room code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if code not in active_rooms:
            return code

@monitor_execution
def are_words_related(word1, word2):
    """Check if two words are related"""
    word1, word2 = word1.lower(), word2.lower()
    # Get categories for both words
    cat1 = get_word_category(word1)
    cat2 = get_word_category(word2)
    # Words are related if they share a category
    return cat1 is not None and cat2 is not None and cat1 == cat2

@monitor_execution
def get_word_category(word):
    """Find which category a word belongs to"""
    word = word.lower()
    for category, content in WORD_CATEGORIES.items():
        if word in content['words'] or word in content['common_words']:
            return category
    return None

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    debug_monitor.log_connection(connected=True)
    emit('connect_response', {'message': 'Connected successfully'})

@socketio.on('create_room')
@monitor_execution
def on_create_room(data):
    """Create a new multiplayer game room"""
    try:
        logger.info(f"Creating room with data: {data}")
        player_name = data.get('player_name')
        if not player_name:
            logger.warning("Player name missing")
            emit('error', {'message': 'Player name is required'})
            return

        room_code = generate_room_code()
        logger.info(f"Generated room code: {room_code}")

        game = Game(
            is_multiplayer=True,
            room_code=room_code,
            difficulty='medium'
        )
        db.session.add(game)
        db.session.commit()
        logger.info(f"Created game with ID: {game.id}")

        host = Player(
            game_id=game.id,
            name=player_name,
            is_host=True
        )
        db.session.add(host)
        db.session.commit()
        logger.info(f"Created host player with ID: {host.id}")

        random_category = random.choice(list(WORD_CATEGORIES.keys()))
        start_word = random.choice(WORD_CATEGORIES[random_category]['words'])
        logger.info(f"Selected start word: {start_word} from category: {random_category}")

        room_state = {
            'game_id': game.id,
            'players': [{
                'id': host.id,
                'name': host.name,
                'score': 0,
                'streak': 0,
                'is_host': True
            }],
            'current_word': start_word,
            'used_words': set([start_word]),
            'turn_index': 0,
            'round_time': 30,
            'last_update': datetime.utcnow().timestamp(),
            'is_paused': False
        }
        active_rooms[room_code] = room_state
        debug_monitor.update_room_state(room_code, room_state)

        join_room(room_code)
        response_data = {
            'room_code': room_code,
            'player_id': host.id,
            'game_state': {**room_state, 'used_words': list(room_state['used_words'])}
        }
        logger.info(f"Emitting room_created event with data: {response_data}")
        emit('room_created', response_data)

    except Exception as e:
        logger.error(f"Error creating room: {str(e)}", exc_info=True)
        debug_monitor.log_error(e, {'event': 'create_room', 'data': data})
        emit('error', {'message': f'Error creating room: {str(e)}'})

@socketio.on('toggle_pause')
@monitor_execution
def on_toggle_pause(data):
    """Handle game pause/resume"""
    try:
        room_code = data.get('room_code')
        player_id = data.get('player_id')
        is_paused = data.get('is_paused', False)

        if not room_code or not player_id:
            emit('error', {'message': 'Invalid request'})
            return

        if room_code not in active_rooms:
            emit('error', {'message': 'Room not found'})
            return

        room = active_rooms[room_code]
        player = next((p for p in room['players'] if p['id'] == player_id), None)

        if not player or not player.get('is_host', False):
            emit('error', {'message': 'Only the host can pause/resume the game'})
            return

        room['is_paused'] = is_paused
        if not is_paused:
            room['last_update'] = datetime.utcnow().timestamp()

        room_state = {**room, 'used_words': list(room['used_words'])}
        debug_monitor.update_room_state(room_code, room_state)
        emit('game_paused', {
            'game_state': room_state,
            'is_paused': is_paused,
            'player_name': player['name']
        }, to=room_code)

    except Exception as e:
        logger.error(f"Error toggling pause: {str(e)}")
        debug_monitor.log_error(e, {'event': 'toggle_pause', 'data': data})
        emit('error', {'message': f'Error toggling pause: {str(e)}'})

@socketio.on('join_room')
@monitor_execution
def on_join_room(data):
    """Join an existing game room"""
    try:
        room_code = data.get('room_code', '').upper()
        player_name = data.get('player_name')

        if not room_code or not player_name:
            emit('error', {'message': 'Room code and player name are required'})
            return

        if room_code not in active_rooms:
            emit('error', {'message': 'Room not found'})
            return

        room = active_rooms[room_code]
        game_id = room['game_id']

        player = Player(
            game_id=game_id,
            name=player_name
        )
        db.session.add(player)
        db.session.commit()

        player_data = {
            'id': player.id,
            'name': player_name,
            'score': 0,
            'streak': 0,
            'is_host': False
        }
        room['players'].append(player_data)
        debug_monitor.update_room_state(room_code, room)

        join_room(room_code)

        room_state = {**room, 'used_words': list(room['used_words'])}
        emit('player_joined', {
            'room_code': room_code,
            'player': player_data,
            'game_state': room_state
        }, to=room_code)

    except Exception as e:
        debug_monitor.log_error(e, {'event': 'join_room', 'data': data})
        emit('error', {'message': f'Error joining room: {str(e)}'})

@socketio.on('submit_word')
@monitor_execution
def on_submit_word(data):
    """Handle word submission in multiplayer game"""
    try:
        room_code = data.get('room_code')
        player_id = data.get('player_id')
        word = data.get('word', '').lower().strip()

        if not all([room_code, player_id, word]):
            emit('error', {'message': 'Invalid submission'})
            return

        if room_code not in active_rooms:
            emit('error', {'message': 'Room not found'})
            return

        room = active_rooms[room_code]

        if room['is_paused']:
            emit('error', {'message': 'Game is paused'})
            return

        current_word = room['current_word'].lower()

        # Find player in room
        player = next((p for p in room['players'] if p['id'] == player_id), None)
        if not player:
            emit('error', {'message': 'Player not found'})
            return

        # Check if it's the player's turn
        current_player = room['players'][room['turn_index']]
        if current_player['id'] != player_id:
            emit('error', {'message': "It's not your turn!"})
            return

        # Check if word was already used
        if word in room['used_words']:
            emit('word_rejected', {
                'message': 'Word already used',
                'game_state': {**room, 'used_words': list(room['used_words'])}
            }, to=room_code)
            return

        # Validate word association
        if not are_words_related(current_word, word):
            emit('word_rejected', {
                'message': f'"{word}" is not related to "{current_word}"',
                'game_state': {**room, 'used_words': list(room['used_words'])}
            }, to=room_code)
            return

        # Update player stats
        player['streak'] += 1
        bonus_points = min(player['streak'] - 1, 4)
        points = 1 + bonus_points
        player['score'] += points

        # Update game state
        room['used_words'].add(word)
        room['current_word'] = word
        room['last_update'] = datetime.utcnow().timestamp()
        room['turn_index'] = (room['turn_index'] + 1) % len(room['players'])
        debug_monitor.update_room_state(room_code, room)

        # Save to database
        word_chain = WordChain(
            game_id=room['game_id'],
            word=word,
            previous_word=current_word,
            points=points,
            player_id=player_id,
            timestamp=datetime.utcnow()
        )
        db.session.add(word_chain)

        # Update player in database
        db_player = Player.query.get(player_id)
        if db_player:
            db_player.score = player['score']
            db_player.streak = player['streak']
            db_player.last_active = datetime.utcnow()

        db.session.commit()

        next_player = room['players'][room['turn_index']]
        room_state = {**room, 'used_words': list(room['used_words'])}

        emit('word_accepted', {
            'word': word,
            'points': points,
            'bonus_points': bonus_points,
            'player': player,
            'game_state': room_state,
            'next_player': next_player['name']
        }, to=room_code)

    except Exception as e:
        debug_monitor.log_error(e, {'event': 'submit_word', 'data': data})
        emit('error', {'message': f'Error submitting word: {str(e)}'})

@socketio.on('disconnect')
@monitor_execution
def on_disconnect():
    """Handle player disconnection"""
    try:
        for room_code, room in active_rooms.items():
            for player in room['players']:
                if player['id'] == request.sid:
                    room['players'].remove(player)
                    leave_room(room_code)

                    if room['players']:
                        # Update turn index if necessary
                        if room['turn_index'] >= len(room['players']):
                            room['turn_index'] = 0
                        room_state = {**room, 'used_words': list(room['used_words'])}
                        debug_monitor.update_room_state(room_code, room_state)
                        emit('player_left', {
                            'player': player,
                            'game_state': room_state
                        }, to=room_code)
                    else:
                        del active_rooms[room_code]
                    return
    except Exception as e:
        debug_monitor.log_error(e, {'event': 'disconnect'})
        print(f"Error handling disconnect: {str(e)}")