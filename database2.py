import datetime
import motor.motor_asyncio
from configs import Config
import datetime

class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.mcol = self.db.media
    
    async def adding_media_to_db(self,bot_username : str ,channel_string : str ,base_to64_key : str ,file_id : str,file_caption : str, file_name : str):
        media_dict = dict(
        bot_username = bot_username,
        channel_string = channel_string,
        key = base_to64_key,
        file_id = file_id,
        file_caption = file_caption,
        file_name = file_name
        )
        
        await self.mcol.insert_one(media_dict)

db2 = Database("mongodb+srv://file-to-link:file-to-link@fille-to-link.9fm5uz3.mongodb.net/?retryWrites=true&w=majority", Config.BOT_USERNAME)