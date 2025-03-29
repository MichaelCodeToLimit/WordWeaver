import logging
from app import app, socketio
from debug_monitor import debug_monitor

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting the Word Association Game server")
    try:
        # Start the debug monitor
        debug_monitor.start_monitoring()
        logger.info("Debug monitor started successfully")
        
        # Run the Flask app with SocketIO
        socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
    finally:
        # Ensure debug monitor is stopped when app exits
        debug_monitor.stop_monitoring()