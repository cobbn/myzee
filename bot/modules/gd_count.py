from nekozee.filters import command
from nekozee.handlers import MessageHandler

from bot import bot
from ..helper.ext_utils.bot_utils import (
    new_task,
    sync_to_async
)
from ..helper.ext_utils.links_utils import is_gdrive_link
from ..helper.ext_utils.status_utils import get_readable_file_size
from ..helper.task_utils.gdrive_utils.count import GoogleDriveCount
from ..helper.telegram_helper.bot_commands import BotCommands
from ..helper.telegram_helper.filters import CustomFilters
from ..helper.telegram_helper.message_utils import (
    anno_checker,
    auto_delete_message,
    delete_message,
    send_message
)


@new_task
async def count_node(_, message):
    args = message.text.split()
    from_user = message.from_user
    if not from_user:
        from_user = await anno_checker(message)
    if username := from_user.username:
        tag = f"@{username}"
    else:
        tag = from_user.mention
    link = (
        args[1]
        if len(args) > 1
        else ""
    )
    if (
        len(link) == 0
        and (reply_to := message.reply_to_message)
    ):
        link = reply_to.text.split(maxsplit=1)[0].strip()

    if is_gdrive_link(link):
        msg = await send_message(
            message,
            f"Counting: <code>{link}</code>"
        )
        (
            name,
            mime_type,
            size, files,
            folders
        ) = await sync_to_async(
            GoogleDriveCount().count,
            link,
            from_user.id
        )
        if mime_type is None:
            smsg = await send_message(
                message,
                name
            )
            await auto_delete_message(
                message,
                smsg
            )
            return
        await delete_message(msg)
        msg = f"<b>Name: {name}</b>"
        msg += f"\n\n<b>Size: </b>{get_readable_file_size(size)}"
        msg += f"\n\n<b>Type: </b>{mime_type}"
        if mime_type == "Folder":
            msg += f"\n<b>SubFolders: </b>{folders}"
            msg += f"\n<b>Files: </b>{files}"
        msg += f"\n\n<b>cc: </b>{tag}"
    else:
        msg = (
            "Send Gdrive link along with command or by replying to the link by command"
        )

    smsg = await send_message(
        message,
        msg
    )
    await auto_delete_message(
        message,
        smsg
    )


bot.add_handler( # type: ignore
    MessageHandler(
        count_node,
        filters=command(
            BotCommands.CountCommand,
            case_sensitive=True
        ) & CustomFilters.authorized
    )
)
