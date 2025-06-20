import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from instagram_downloader import get_instagram_story_links
import re

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get the token from environment variable
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable not set!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) started the bot")
    await update.message.reply_text(
        f"Hi {user.first_name}! Send me an Instagram username and I'll provide the download links for their stories."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    logger.info(f"User {update.effective_user.id} requested help")
    await update.message.reply_text(
        "Simply send me an Instagram username (without @ symbol) and I'll provide "
        "download links for their stories. For example: 'jiri_mdf'"
    )

async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process the user message and extract Instagram username."""
    user_message = update.message.text
    user_id = update.effective_user.id
    username = user_message.strip()
    
    # Remove @ if present
    if username.startswith('@'):
        username = username[1:]
    
    # Validate username format
    if not re.match(r'^[A-Za-z0-9._]+$', username):
        logger.warning(f"User {user_id} sent invalid Instagram username format: {username}")
        await update.message.reply_text(
            "Please send a valid Instagram username. Usernames can only contain letters, "
            "numbers, periods, and underscores."
        )
        return
    
    logger.info(f"User {user_id} requested stories for Instagram username: {username}")
    await update.message.reply_text(f"Fetching stories for {username}... Please wait, this may take a minute.")
    
    try:
        # Get the story links
        status_message = await update.message.reply_text("📱 Connecting to Instagram...", disable_notification=True)
        story_links = await asyncio.to_thread(get_instagram_story_links, username)
        
        await status_message.edit_text("✅ Stories found! Generating download links...")
        
        if not story_links:
            logger.info(f"No stories found for username: {username} requested by user {user_id}")
            await status_message.edit_text("No stories found for this user. They may not have active stories or the account may be private.")
            return
        
        # Send links to user
        response_text = f"Found {len(story_links)} stories for {username}:\n\n"
        
        # Send in batches to avoid message length limits
        for i, link in enumerate(story_links, 1):
            media_type = "Video" if ".mp4" in link else "Image"
            response_text += f"{i}. {media_type}: {link}\n\n"
            
            # Split into multiple messages if needed
            if i % 5 == 0 or i == len(story_links):
                await update.message.reply_text(response_text)
                response_text = ""
        
        logger.info(f"Successfully sent {len(story_links)} story links to user {user_id}")
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error processing request for user {user_id}, username {username}: {error_message}")
        await update.message.reply_text(
            f"Sorry, an error occurred while fetching stories: {error_message}"
        )

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()
    logger.info("Bot stopped")

if __name__ == '__main__':
    logger.info("Starting Instagram Stories Bot")
    main()