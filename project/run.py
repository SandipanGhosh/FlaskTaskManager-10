# run.py

import os
from project import app

port = int(os.environ.get('PORT', 5000))
#app.run(debug=True)
app.run(host='0.0.0.0', port=port)