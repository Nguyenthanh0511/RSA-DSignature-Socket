# run.py
"""
Application entry point
"""

import os
from server.app import create_app

# Get configuration
config_name = os.environ.get('FLASK_ENV', 'development')

# Create app and socketio
app, socketio = create_app(config_name)

if __name__ == '__main__':
    # Run the application
    socketio.run(
        app,
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )