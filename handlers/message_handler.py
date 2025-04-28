# app/handlers/message_handler.py
from app.services.send_service import SendService
from app.globals.constants import MENU_1, MENU_2

class MessageHandler:
    @staticmethod
    async def process_message(message: dict):
        from_number = message.get("from")
        message_type = message.get("type")

        if message_type == "text":
            text_body = message.get("text", {}).get("body", "")
            if text_body.lower() == "test":
                await SendService.send_message(from_number, "hello world!")
            else:
                await SendService.send_menu(from_number)

        elif message_type == "interactive":
            interactive = message.get("interactive", {})
            if interactive.get("type") == "list_reply":
                list_reply_id = interactive.get("list_reply", {}).get("id")
                if list_reply_id == MENU_1:
                    await SendService.send_message(from_number, "anda memilih menu 1")
                elif list_reply_id == MENU_2:
                    await SendService.send_message(from_number, "anda memilih menu 2")
