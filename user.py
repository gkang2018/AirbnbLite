from database import DatabaseConnection
from app import db, login_manager



# Authentication
@login_manager.user_loader
def loadUser(userId): 
    return db.findOne("users", {"_id": userId})







