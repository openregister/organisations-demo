import os
from organisations_demo.factory import create_app
app = create_app(os.environ['SETTINGS'])
