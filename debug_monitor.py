import logging
import time
from datetime import datetime
from functools import wraps
import traceback
from threading import Thread
import psutil
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DebugMonitor:
    def __init__(self):
        self.active_rooms = {}
        self.connection_count = 0
        self.error_count = 0
        self.start_time = time.time()
        self.last_check = time.time()
        self.monitoring = False
        self.monitor_thread = None

    def start_monitoring(self):
        """Start the background monitoring thread"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            logger.info("Debug monitor started")

    def stop_monitoring(self):
        """Stop the background monitoring thread"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
            logger.info("Debug monitor stopped")

    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                self._check_system_health()
                self._check_room_health()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in monitor loop: {str(e)}")

    def _check_system_health(self):
        """Monitor system resources"""
        try:
            process = psutil.Process(os.getpid())
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            cpu_percent = process.cpu_percent()

            if memory_usage > 500:  # Alert if memory usage > 500MB
                logger.warning(f"High memory usage: {memory_usage:.2f}MB")
            if cpu_percent > 80:  # Alert if CPU usage > 80%
                logger.warning(f"High CPU usage: {cpu_percent}%")
        except Exception as e:
            logger.error(f"Error checking system health: {str(e)}")

    def _check_room_health(self):
        """Check health of game rooms"""
        try:
            current_time = time.time()
            for room_code, room in list(self.active_rooms.items()):
                # Check for inactive rooms (no activity for 1 hour)
                if current_time - room.get('last_update', 0) > 3600:
                    logger.warning(f"Room {room_code} inactive for over an hour")
                    if room_code in self.active_rooms:
                        del self.active_rooms[room_code]

                # Check for player count consistency
                if len(room.get('players', [])) == 0:
                    logger.warning(f"Room {room_code} has no players")
                    if room_code in self.active_rooms:
                        del self.active_rooms[room_code]
        except Exception as e:
            logger.error(f"Error checking room health: {str(e)}")

    def log_connection(self, connected=True):
        """Log connection events"""
        try:
            if connected:
                self.connection_count += 1
                logger.info(f"New connection. Total connections: {self.connection_count}")
            else:
                self.connection_count -= 1
                logger.info(f"Connection closed. Total connections: {self.connection_count}")
        except Exception as e:
            logger.error(f"Error logging connection: {str(e)}")

    def log_error(self, error, context=None):
        """Log error events"""
        try:
            self.error_count += 1
            error_info = {
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(error),
                'traceback': traceback.format_exc(),
                'context': context
            }
            logger.error(f"Error #{self.error_count}: {error_info}")
        except Exception as e:
            logger.error(f"Error in error logging: {str(e)}")

    def update_room_state(self, room_code, room_state):
        """Update monitored room state"""
        try:
            self.active_rooms[room_code] = room_state.copy()
            self.active_rooms[room_code]['last_update'] = time.time()
            logger.debug(f"Updated state for room {room_code}")
        except Exception as e:
            logger.error(f"Error updating room state: {str(e)}")

    def remove_room(self, room_code):
        """Remove room from monitoring"""
        try:
            if room_code in self.active_rooms:
                del self.active_rooms[room_code]
                logger.info(f"Removed room {room_code} from monitoring")
        except Exception as e:
            logger.error(f"Error removing room: {str(e)}")

# Create singleton instance
debug_monitor = DebugMonitor()

# Decorator for monitoring function execution time
def monitor_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            if execution_time > 1.0:  # Log slow operations (>1s)
                logger.warning(f"Slow operation in {func.__name__}: {execution_time:.2f}s")
            return result
        except Exception as e:
            debug_monitor.log_error(e, {
                'function': func.__name__,
                'args': args,
                'kwargs': kwargs
            })
            raise
    return wrapper