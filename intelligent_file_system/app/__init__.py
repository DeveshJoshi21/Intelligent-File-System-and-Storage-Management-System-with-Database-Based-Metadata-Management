import os
from flask import Flask
from .db import init_db
from .routes import bp
def create_app(test_config=None):
 app=Flask(__name__,instance_relative_config=True)
 app.config.from_mapping(SECRET_KEY=os.environ.get("IFS_SECRET","local-only-change-me"),DATABASE=os.path.join(app.instance_path,"intellifs.sqlite3"))
 if test_config: app.config.update(test_config)
 os.makedirs(app.instance_path,exist_ok=True); init_db(app); app.register_blueprint(bp)
 return app
