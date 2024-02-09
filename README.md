# Telegram Channels Scripts
This is a simple script to get a list of all channels you are subscribed to and save the data to a CSV file.
You can then mark the channels you want to unsubscribe from and run the script to unsubscribe from those channels.

## How to use
1. Install the required packages
```
pip install -r requirements.txt
```
2. Create a new Telegram application and get the API ID and API hash from https://my.telegram.org/auth.
3. Create a new file named `config.ini` and add the following content:
```ini
[telegram]
api_id = YOUR_API_ID
api_hash = YOUR_API_HASH
```
4. Run the script
```
python main.py
```
5. The script will create a CSV file named `channels_data.csv` with the data of all your channels. You can then mark the channels you want to unsubscribe from and run the script again to unsubscribe from those channels.
6. You can also specify the log level, session name and the CSV file name in the `config.ini` file.
```ini
[telegram]
api_id = YOUR_API_ID
api_hash = YOUR_API_HASH
session_name = YOUR_SESSION_NAME
csv_file = YOUR_CSV_FILE
log_level = YOUR_LOG_LEVEL
```
