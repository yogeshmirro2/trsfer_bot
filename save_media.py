# (c) @AbirHasan2005

import asyncio
from configs import Config
from pyrogram import Client,enums
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from database import db
from database2 import db2
from pyrogram.errors import FloodWait
from helpers import str_to_b64
from get_file_size import get_file_size,get_file_attr
from multi_channel import get_working_channel_string, get_working_db_channel_id
from rm import rm_dir,rm_file


async def send_photo(bot,editable,photo_send_channel,media_thumb_id,caption,message_ids_str,log_channel):
    try:
        #await editable.edit("**sending thumbnail with all Content caption to your VIDEO_PHOTO_SEND channel**")
        thumb_path = await bot.download_media(media_thumb_id)
        await bot.send_photo(int(photo_send_channel),thumb_path,caption)
        #await editable.edit("**thumbnail with media_captions has been sent to your VIDEO_PHOTO_SEND channel**")
        await rm_dir()
        return 'true'
    except pyrogram.errors.exceptions.flood_420.FloodWait as sl:
        await asyncio.sleep(sl.value)
        return await send_photo(bot,editable,photo_send_channel,media_thumb_id,caption,message_ids_str)
    except Exception as e:
        #await editabl.edit(f"got error in sending photo with caption\n\n**Error:** `{e}`")
        await bot.send_message(chat_id=int(log_channel),text=f"got error in sending photo with caption message_ids {message_ids_str} \ntype : {str(type(e))}\n\n**Error:** `{e}`")
        return "false"

async def forward_to_channel(DB_CHANNEL, log_channel, bot: Client, message: Message, editable: Message):
    try:
        __SENT = await message.copy(DB_CHANNEL)
        return __SENT
    except FloodWait as sl:
        if sl.value > 45:
            await asyncio.sleep(sl.value)
            if log_channel is not None:
                await bot.send_message(
                    chat_id=int(log_channel),
                    text=f"#FloodWait:\nGot FloodWait of `{str(sl.value)}s` from `{str(editable.chat.id)}` !!",
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("Ban User", callback_data=f"ban_user_{str(editable.chat.id)}")]
                        ]
                    )
                )
        return await forward_to_channel(DB_CHANNEL,log_channel,bot, message, editable)


async def save_batch_media_in_channel(bot: Client, editable: Message, message_ids: list,FROM_CHANNEL_ID):
    try:
        DB_CHANNELS = await get_working_db_channel_id()
        DB_CHANNEL = int("-100"+f"{DB_CHANNELS}")
        log_channel = await db.check_log_channel_id()
        photo_send_channel = await db.check_video_photo_send()
        Channel_string = f"store_{DB_CHANNELS}"#await get_working_channel_string()
        each_short_link = await db.check_short_each_link()
    except Exception as e:
        await editable.edit(f"Something Went Wrong in database!\n\n**Error:** `{e}`")
        return
    try:
        media_thumb_id = ""
        message_ids_str = ""
        media_captions = []
        # db_file_id = []
        # db_file_caption = []
        # db_file_name = []
        # db_file_to64 = []
        for message in (await bot.get_messages(chat_id=FROM_CHANNEL_ID, message_ids=message_ids)):
            sent_message = await forward_to_channel(DB_CHANNEL, log_channel, bot, message, editable)
            if sent_message is None:
                continue
            msg_type = await get_file_attr(sent_message)
            if msg_type is not None:
                try:
                    media_captions.append(f"**👉  {sent_message.caption} {await get_file_size(sent_message)}**" if sent_message.caption else f"**👉 **")
                    # db_file_caption.append(f"{sent_message.caption}" if sent_message.caption and len(sent_message.caption)>0 else f"No_Caption")
                    # db_file_name.append(f"{msg_type.file_name}" if msg_type.file_name and len(msg_type.file_name)>0 else "No_file_name")
                    # db_file_to64.append(str_to_b64(str(sent_message.id)))
                    # db_file_id.append(f"{str(msg_type.file_id)}")
                    if not media_thumb_id:
                        try:
                            if msg_type.thumbs:
                                media_thumb_id+=f"{msg_type.thumbs[0].file_id}"
                        except Exception as e:
                            await editable.edit(f"Something Went Wrong to get media thumb!\n\n**Error:** `{err}`")
                            print(e)
                            return
                except Exception as e:
                    await editable.edit(f"Something Went Wrong in get media caption or get file_id!\n\n**Error:** `{err}`")
                    print(e)
                    return
            message_ids_str+=f"{str(sent_message.id)} "
            await asyncio.sleep(4)
        
        #msg_ids_file_ids = (message_ids_str).rstrip()+"|"+(message_file_ids).rstrip("/")
        SaveMessage = await bot.send_message(
            chat_id=DB_CHANNEL,
            text=message_ids_str,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Delete Batch", callback_data="closeMessage")
            ]])
        )
        share_link1 = f"https://t.me/{Config.BOT_USERNAME}?start={Channel_string}_{str_to_b64(str(SaveMessage.id))}"
        if each_short_link:
            try:
                share_link = await get_shortlink(share_link)
                if not share_link:
                    await editable.edit("**SHORT_EACH_LINK is enabled but there are no shortner available OR getting any error from shortner site.\nfor shortner site error check logs**")
                    return
            except Exception as e:
                await editable.edit(f"Something Went Wrong in short each link!\n\n**Error:** `{e}`")
                return
        else:
            share_link = share_link1
        
        await bot.send_message(
            chat_id=int(DB_CHANNEL),
            text=f"#BATCH_SAVE:\n\nGot Batch Link!\n\nOpen Link - {share_link1}\n\nwithout shorted Link - {share_link1}",
            disable_web_page_preview=True
        )
        
        if not media_thumb_id and await db.get_default_thumb_status():
            try:
                media_thumb_id = await db.get_thumb_id()
                if media_thumb_id is None:
                    await editable.reply_text("**set_default_thumb is enable but there is not thubmnail set by you.\nplz set a thumbnail first to get all media caption with thumbnail in photo_send_channel**")
                    return
            except Exception as e:
                await editable.edit(f"Something Went Wrong in to get db_default_thumb!\n\n**Error:** `{e}`")
        
        if media_thumb_id and photo_send_channel is not None:
            add_detail = await db.get_add_detail()
            media_captions = sorted(media_captions)
            media_captions = "\n\n".join(media_captions)
            media_captions1=f"Here is the Permanent Link of your Content: <a href={share_link}>Download Link</a>\n\nJust Click on download to get your Content!\n\nyour Content name are:👇\n\n{media_captions}\n\n{add_detail}" 
            mssg = await send_photo(bot,editable,photo_send_channel,media_thumb_id,media_captions1,message_ids_str,log_channel)
            if mssg=='false':
                return 'false'
            
            # try:
            #     await editable.edit("**sending thumbnail with all Content caption to your VIDEO_PHOTO_SEND channel**")
            #     #thumb_path = await bot.download_media(media_thumb_id,f"{Config.DOWNLOAD_DIR}/{media_thumb_id}")
            #     thumb_path = await bot.download_media(media_thumb_id)
            #     add_detail = await db.get_add_detail()
            #     media_captions = sorted(media_captions)
            #     media_captions = "\n\n".join(media_captions)
            #     media_captions1=f"Here is the Permanent Link of your Content: <a href={share_link}>Download Link</a>\n\nJust Click on download to get your Content!\n\nyour Content name are:👇\n\n{media_captions}\n\n{add_detail}" 
            #     await bot.send_photo(int(photo_send_channel),thumb_path,media_captions1)
            #     await editable.edit("**thumbnail with media_captions has been sent to your VIDEO_PHOTO_SEND channel**")
            #     await rm_dir()
            #     await asyncio.sleep(2)
            # except Exception as e:
            #     #await editabl.edit(f"got error in sending photo with caption\n\n**Error:** `{e}`")
            #     await bot.send_message(chat_id=int(log_channel),text=f"got error in sending photo with caption message_ids{message_ids_str} \n\n**Error:** `{e}`")
        # try:
        #     try:
        #         if len(db_file_id)==len(db_file_caption)==len(db_file_name)==len(db_file_to64):
        #             await editable.edit(f"**sending medias to db**")
        #         bot_username = Config.BOT_USERNAME
        #         channel_string = Channel_string
        #         for i in range(len(db_file_id)):
        #             await db2.adding_media_to_db(bot_username,channel_string,db_file_to64[i],db_file_id[i],db_file_caption[i],db_file_name[i])
        #         await editable.edit(f"successfully send medias to db")                        
        #     except Exception as e:
        #         await editable.edit(f"got error in getting db_media_database\n\n**Error:** `{e}`")
        #         return
        # except Exception as e:
        #     await editable.edit(f"got error in sending to db\n\n**Error:** `{e}`")
        #     return
        # if type(media_captions) is list:
        #     media_captions = sorted(media_captions)
        #     media_captions = "\n\n".join(media_captions)
        
        # await editable.edit(
        #     f"Here is the Permanent Link of your Content: <a href={share_link}>Download Link</a>\n\n{media_captions}",
        #     reply_markup=InlineKeyboardMarkup(
        #         [[InlineKeyboardButton("Open Link", url=share_link)],[InlineKeyboardButton("without shorted Link", url=share_link1)]
        #         ]
        #     ),
        #     disable_web_page_preview=True
        # )
        
        
    except Exception as err:
        await editable.edit(f"Something Went Wrong!type : {str(type(err))}\n\n**Error:** `{err}`")
        if log_channel is not None:
            await bot.send_message(
                chat_id=int(log_channel),
                text=f"#ERROR_TRACEBACK:\nGot Error from `{str(editable.chat.id)}` !!\n\n**Traceback:** `{err}`",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Ban User", callback_data=f"ban_user_{str(editable.chat.id)}")]
                    ]
                )
            )
        return
async def save_media_in_channel(bot: Client, editable: Message, message: Message):
    try:
        DB_CHANNELS = await get_working_db_channel_id()
        DB_CHANNEL = int("-100"+f"{DB_CHANNELS}")
        log_channel = await db.check_log_channel_id()
        photo_send_channel = await db.check_video_photo_send()
        Channel_string = f"store_{DB_CHANNELS}"#await get_working_channel_string()
        each_short_link = await db.check_short_each_link()
    except Exception as err:
        await editable.edit(f"Something Went Wrong in database!\n\n**Error:** `{err}`")
        return
    try:
        media_captions = ""
        message_er_id = ""
        msg_file_id = ""
        thumb_id = ""
        forwarded_msg = await message.copy(DB_CHANNEL)
        msg_type = await get_file_attr(forwarded_msg)
        # if msg_type is not None:
        #     msg_file_id+=f"{msg_type.file_id}"
        # else:
        #     msg_file_id+=f"{forwarded_msg.id}"
            
        message_er_id+=str(forwarded_msg.id)
        #file_id_msg_id = message_er_id+"|"+msg_file_id
        SaveMessage = await bot.send_message(
            chat_id=DB_CHANNEL,
            text=message_er_id,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Delete file", callback_data="closeMessage")
            ]])
        )
        
        share_link1 = f"https://t.me/{Config.BOT_USERNAME}?start={Channel_string}_{str_to_b64(str(SaveMessage.id))}"
        if each_short_link:
            try:
                share_link = await get_shortlink(share_link)
                if not share_link:
                    await editable.edit("**SHORT_EACH_LINK is enabled but there are no shortner available OR getting any error from shortner site.\nfor shortner site error check logs**")
                    return
            except Exception as e:
                await editable.edit(f"Something Went Wrong in short each link!\n\n**Error:** `{e}`")
                return
        else:
            share_link = share_link1
    
        await forwarded_msg.reply_text(
            f"#PRIVATE_FILE:\n\nGot File Link!\n\nOpen Link - {share_link1}\n\nwithout shorted Link - {share_link1}",
            disable_web_page_preview=True)
        
        
        if msg_type is not None:
            try:
                media_captions+=f"**👉 {forwarded_msg.caption} {await get_file_size(forwarded_msg)}**" if forwarded_msg.caption else f"**👉 **"
                thumb_id += msg_type.thumbs[0].file_id if msg_type.thumbs else ""
            except Exception as e:
                await editable.edit(f"Something Went Wrong in to get thumb_id or media_caption!\n\n**Error:** `{e}`")
                return
            
            if not thumb_id and await db.get_default_thumb_status():
                try:
                    thumb_id = await db.get_thumb_id()
                    if thumb_id is None:
                        await editable.reply_text("**set_default_thumb is enable but there is not thubmnail set by you.\nplz set a thumbnail first to get all media caption with thumbnail in photo_send_channel**")
                        return
                except Exception as e:
                    await editable.edit(f"Something Went Wrong in to get db_default_thumb!\n\n**Error:** `{e}`")
        
                
            if thumb_id and photo_send_channel is not None:
                mes = await send_photo(bot,editable,photo_send_channel,thumb_id,media_captions,message_er_id,log_channel)
                if mes=='false':
                    return 'false'
                # await editable.edit("**sending thumbnail with all Content caption to your VIDEO_PHOTO_SEND channel**")
                # try:
                #     add_detail = await db.get_add_detail()
                #     thumb_path = await bot.download_media(thumb_id)
                #     media_captions1=f"Here is the Permanent Link of your Content: <a href={share_link}>Download Link</a>\n\nJust Click on download to get your Content!\n\nyour Content name are:👇\n\n{media_captions}\n\n{add_detail}"
                #     await bot.send_photo(int(photo_send_channel),thumb_path,media_captions1)
                #     await editable.edit("**thumbnail with media_captions has been sent to your VIDEO_PHOTO_SEND channel**")
                #     await rm_dir()
                #     await asyncio.sleep(2)
                # except Exception as e:
                #     await editable.edit(f"got error in sending photo with caption\n\n**Error:** `{e}`")
                #     return
        
        
        # await editable.edit(
        #     f"Here is the Permanent Link of your Content: <a href={share_link}>Download Link</a>\n\n{media_captions}",
        #     reply_markup=InlineKeyboardMarkup(
        #         [[InlineKeyboardButton("Open Link", url=share_link)],[InlineKeyboardButton("without shorted Link", url=share_link1)]
        #         ]
        #     ),
        #     disable_web_page_preview=True
        # )
        # try:
        #     if msg_type is not None:
        #         await editable.edit(f"sending sending media to db")
        #         bot_username = Config.BOT_USERNAME
        #         channel_string = Channel_string
        #         key = str_to_b64(str(forwarded_msg.id))
        #         dbfile_id = msg_type.file_id
        #         dbfile_caption = forwarded_msg.caption if forwarded_msg.caption and len(forwarded_msg.caption)>0 else "No_caption"
        #         dbfile_name = msg_type.file_name if msg_type.file_name and len(msg_type.file_name)>0 else "No_file_name"
        #         await db2.adding_media_to_db(bot_username,channel_string,key,dbfile_id,dbfile_caption,dbfile_name)
        #         await editable.edit(f"successfully send media to db")
        # except Exception as e:
        #     await editable.edit(f"got error in sending media to db\n\n**Error:** `{e}`")
        #     await asyncio.Sleep(5)
        #     return
    except FloodWait as sl:
        if sl.value > 45:
            print(f"Sleep of {sl.value}s caused by FloodWait ...")
            await asyncio.sleep(sl.value)
            if await log_channel is not None:
                await bot.send_message(
                    chat_id=int(log_channel),
                    text="#FloodWait:\n"
                         f"Got FloodWait of `{str(sl.value)}s` from `{str(editable.chat.id)}` !!",
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("Ban User", callback_data=f"ban_user_{str(editable.chat.id)}")]
                        ]
                    )
                )
        await save_media_in_channel(bot, editable, message)
    
    
    except Exception as err:
        await editable.edit(f"Something Went Wrong!\n\n**Error:** `{err}`")
        if log_channel is not None:
            await bot.send_message(
                chat_id=int(log_channel),
                text="#ERROR_TRACEBACK:\n"
                     f"Got Error from `{str(editable.chat.id)}` !!\n\n"
                     f"**Traceback:** `{err}`",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Ban User", callback_data=f"ban_user_{str(editable.chat.id)}")]
                    ]
                )
            )



