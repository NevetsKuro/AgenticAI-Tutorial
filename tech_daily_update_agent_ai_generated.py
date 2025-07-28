import os
import asyncio
import feedparser
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import openai
import logging

# Configuration
RSS_FEED_URL = "https://www.smashingmagazine.com/feed/"  # Working frontend dev news RSS feed
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")  # Set your email in environment variable
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Set your app password in environment variable
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")  # Set recipient email in environment variable

# OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_frontend_news():
    try:
        feed = await asyncio.to_thread(feedparser.parse, RSS_FEED_URL)
        news_items = []
        for entry in feed.entries[:5]:  # Get top 5 news items
            item = {
                "title": entry.title,
                "link": entry.link,
                "summary": entry.summary if 'summary' in entry else ''
            }
            news_items.append(item)
        return news_items
    except Exception as e:
        logger.error(f"Error fetching RSS feed: {e}")
        return []

async def generate_html_from_ai(news_items):
    if not news_items:
        return "<p>No news items available at the moment.</p>"

    prompt = "Generate a clean, readable HTML snippet to display the following frontend development news items as a list with clickable titles and summaries:\n\n"
    for i, item in enumerate(news_items, 1):
        prompt += f"{i}. Title: {item['title']}\n   Link: {item['link']}\n   Summary: {item['summary']}\n\n"
    prompt += "Return only the HTML code without any explanations."

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an expert HTML developer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7,
        )
        html_content = response.choices[0].message.content.strip()
        return html_content
    except Exception as e:
        logger.error(f"Error generating HTML from AI: {e}")
        return "<p>Failed to generate news content.</p>"

async def send_email(subject, html_content):
    msg = MIMEMultipart('alternative')
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject

    part = MIMEText(html_content, 'html')
    msg.attach(part)

    try:
        await aiosmtplib.send(
            msg,
            hostname=SMTP_SERVER,
            port=SMTP_PORT,
            start_tls=True,
            username=EMAIL_ADDRESS,
            password=EMAIL_PASSWORD,
        )
        logger.info("Email sent successfully.")
    except Exception as e:
        logger.error(f"Error sending email: {e}")

async def main():
    news_items = await fetch_frontend_news()
    news_html = await generate_html_from_ai(news_items)
    subject = "Daily Frontend Development Tech Updates"
    body = f"<h2>Here are today's top frontend development news:</h2>{news_html}"
    await send_email(subject, body)

if __name__ == "__main__":
    asyncio.run(main())