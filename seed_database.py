import os
import json
from random import choice, randint

import crud
import model
import server


os.system('dropdb books')
os.system('createdb books')

model.connect_to_db(server.app)
model.db.create_all()


