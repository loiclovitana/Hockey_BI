from sqlalchemy.orm import Session
from  HMDatabase import models

def get_player(db:Session, player_id : int) -> models.HockeyPlayer:
    return db.query(models.HockeyPlayer).get(player_id)