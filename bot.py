import logging
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# تنظیمات لاگینگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# توکن ربات خود را اینجا وارد کنید
TOKEN = '6530062072:AAFoDiF0ZysTjWHYvBkFp2rHXLxD9W9YVdk'

async def start(update: Update, context: CallbackContext) -> None:
    logger.info('Received /start command')
    await update.message.reply_text('سلام! لینک فایل را بفرستید تا دانلود و ارسال شود.')

async def download_file(url: str) -> str:
    logger.info(f'Downloading file from {url}')
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    logger.info(f'File downloaded successfully to {local_filename}')
    return local_filename

async def handle_message(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    try:
        logger.info(f'Received file download request for {url}')
        await update.message.reply_text('در حال دانلود فایل...')
        filename = await download_file(url)
        await update.message.reply_text('دانلود تکمیل شد. در حال ارسال فایل...')
        with open(filename, 'rb') as f:
            await update.message.reply_document(f)
        os.remove(filename)
        await update.message.reply_text('فایل ارسال و پاک شد.')
    except requests.exceptions.RequestException as e:
        logger.error(f'Error downloading file: {e}')
        await update.message.reply_text('خطایی در دانلود فایل رخ داد.')
    except Exception as e:
        logger.error(f'An error occurred: {e}')
        await update.message.reply_text('خطای عمومی رخ داد.')

async def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f'Update "{update}" caused error "{context.error}"')

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error)

    application.run_polling()

if __name__ == '__main__':
    main()
