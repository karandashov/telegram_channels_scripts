import csv
import os
import time
from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.channels import GetChannelsRequest
from telethon.tl.functions.messages import GetDialogsRequest
import logging
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.types import InputChannel
from telethon.errors import ChannelPrivateError
import asyncio
from telethon.tl.types import InputPeerChannel
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

try:
    API_ID = config['telegram']['api_id']
    API_HASH = config['telegram']['api_hash']
except KeyError as e:
    print(f'Error reading config.ini: {e}')
    exit()
SESSION_NAME = config['telegram'].get('session_name')
CSV_FILE = config['telegram'].get('csv_file')
LOG_LEVEL = config['telegram'].get('log_level')

logging.basicConfig(level=LOG_LEVEL if LOG_LEVEL else 'INFO',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def get_all_channels(client):
    all_channels = []  # Инициализация списка каналов
    async for dialog in client.iter_dialogs():
        if dialog.is_channel:  # Проверяем, является ли диалог каналом
            try:
                # Добавляем объект канала в список, включая id и access_hash
                channel_info = {
                    "id": dialog.entity.id,
                    "access_hash": dialog.entity.access_hash,
                    "title": dialog.name
                }
                all_channels.append(channel_info)
                print(f"{dialog.name} - Channel added to the list")
            except Exception as e:
                print(f"Error processing {dialog.name}: {e}")
    return all_channels


async def get_channels_data(client):
    channels_data = []  # Инициализация списка для данных каналов
    for channel_info in all_channels:  # Перебираем информацию о каналах
        # Создаем InputPeerChannel для каждого канала
        channel = InputPeerChannel(
            channel_id=channel_info['id'], access_hash=channel_info['access_hash'])
        # Получаем полную информацию о канале
        full_channel = await client(GetFullChannelRequest(channel=channel))
        channels_data.append(full_channel)
    return channels_data


def save_to_csv(channels_data, csv_file='channels_data.csv'):
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Заголовки для CSV-файла
        writer.writerow(['channel_id', 'access_hash', 'channel_title', 'channel_description',
                        'channel_members_count', 'channel_link', 'channel_username', 'to_unsubscribe'])
        for channel in channels_data:
            # Доступ к атрибутам объекта для получения необходимой информации
            channel_id = channel.chats[0].id
            access_hash = channel.chats[0].access_hash if hasattr(
                channel.chats[0], 'access_hash') else ''
            channel_title = channel.chats[0].title
            channel_description = channel.full_chat.about
            channel_members_count = channel.full_chat.participants_count if hasattr(
                channel.full_chat, 'participants_count') else ''
            channel_username = channel.chats[0].username
            channel_link = f'https://t.me/{
                channel_username}' if channel_username else ''

            # Запись информации о канале в CSV
            writer.writerow([channel_id, access_hash, channel_title, channel_description,
                             channel_members_count, channel_link, channel_username, ''])

    print('Data saved to the csv file')


def mark_to_unsubscribe(csv_file='channels_data.csv'):
    # Чтение данных и запрос на отметку каналов для отписки
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        # Преобразуем итератор в список для многократного доступа
        data = list(reader)

    # Проходим по данным и спрашиваем пользователя, нужно ли отметить канал для отписки
    for row in data:
        print(f'Channel: {row["channel_title"]}')
        unsubscribe = input('Mark to unsubscribe from this channel (y/n): ')
        if unsubscribe.lower() == 'y':
            row['to_unsubscribe'] = 'yes'  # Отмечаем канал для отписки

    # Запись обновленных данных обратно в файл
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['channel_id', 'access_hash', 'channel_title', 'channel_description',
                      'channel_members_count', 'channel_link', 'channel_username', 'to_unsubscribe']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()  # Пишем заголовки столбцов
        writer.writerows(data)  # Записываем обновленные данные

    print('Updated data saved to the CSV file.')


async def unsubscribe_from_channels(client, csv_file='channels_data.csv'):
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = list(reader)

    for row in data:
        if row['to_unsubscribe'].lower() == 'yes':
            channel_id = int(row['channel_id'])
            # Предполагаем, что access_hash есть в CSV
            access_hash = int(row['access_hash'])
            try:
                await client(LeaveChannelRequest(InputChannel(channel_id, access_hash)))
                print(f'Unsubscribed from the channel {row["channel_title"]}')
                # Задержка для предотвращения ограничений Telegram
                await asyncio.sleep(2)
            except Exception as e:
                print(f'Could not unsubscribe from {
                      row["channel_title"]}: {e}')

if __name__ == '__main__':

    api_id = API_ID
    api_hash = API_HASH
    session_name = SESSION_NAME if SESSION_NAME else 'session'
    csv_file = CSV_FILE if CSV_FILE else 'channels_data.csv'

    client = TelegramClient(session_name, api_id, api_hash)
    client.start()

    all_channels = client.loop.run_until_complete(get_all_channels(client))

    channels_data = client.loop.run_until_complete(get_channels_data(client))

    save_to_csv(channels_data, csv_file=csv_file)

    mark_to_unsubscribe(csv_file=csv_file)

    client.loop.run_until_complete(
        unsubscribe_from_channels(client, csv_file=csv_file))

    client.disconnect()

    print('Done')
