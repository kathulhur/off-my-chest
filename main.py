import os
from app import create_app, db
from flask_migrate import Migrate



app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)