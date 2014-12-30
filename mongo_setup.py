from pymongo import Connection
from secrets import MONGOHQ_USER, MONGOHQ_PWD, MONGOHQ_PORT, MONGOHQ_HOST, MONGOHQ_DB_NAME

connection = Connection(MONGOHQ_HOST,MONGOHQ_PORT)
db = connection[MONGOHQ_DB_NAME]

db.authenticate(MONGOHQ_USER, MONGOHQ_PWD)

USER_COLLECTION = db.daniel_users
PENDING_COLLECTION = db.pending_ding_dongs

print 'CONNECCTEEEDD'
