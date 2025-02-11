from telethon import TelegramClient, events
from config import account_config, chat_config
from typing import Optional
import re
from loguru import logger
from .sniper import Sniper
import asyncio

class TelegramParser:
    def __init__(self, private_key: str):
        self.evm_account = private_key
        self.client: Optional[TelegramClient] = None
        pass

    async def create_session(self):
        client = TelegramClient(account_config.get('session'), account_config.get('api_id'),
                                account_config.get('api_hash'))

        await client.connect()

        if not await client.is_user_authorized():
            await client.send_code_request(account_config.get('phone_number'))
            await client.sign_in(account_config.get('phone_number'), input('Enter the code: '))

        self.client = client

    async def contract_parser(self):
        @self.client.on(events.NewMessage(chats=chat_config['source_channels']))
        async def new_message_handler(event):
            if event.message and event.message.text:
                message_text = event.message.text

                pattern = r"0x[a-fA-F0-9]{40}"

                addresses = re.findall(pattern, message_text)

                for address in addresses:
                    if len(address) == 42:
                        logger.success(f"Found an EVM contract address: {address}")
                        sniper_instance = Sniper(self.evm_account)
                        try:
                            await sniper_instance.snipe_token_v3(address)
                        except Exception as e:
                            logger.error(f"v3 transaction is not possible, trying v2")
                            await sniper_instance.snipe_token_v2(address)

