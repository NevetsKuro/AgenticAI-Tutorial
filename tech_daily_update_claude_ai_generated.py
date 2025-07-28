import os
import asyncio
import feedparser
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from openai_agents import Agent
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_frontend_news():
    """Fetch frontend development news from RSS feed"""
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

def format_news_data(news_items):
    """Format news items into a structured string for the agent"""
    if not news_items:
        return "No news items available."
    
    formatted_data = "Frontend Development News Items:\n\n"
    for i, item in enumerate(news_items, 1):
        formatted_data += f"{i}. {item['title']}\n"
        formatted_data += f"   Link: {item['link']}\n"
        formatted_data += f"   Summary: {item['summary']}\n\n"
    
    return formatted_data

def create_html_formatter_tool():
    """Tool function for formatting news into HTML"""
    def format_to_html(news_data: str) -> str:
        """
        Convert news data into clean, professional HTML format.
        
        Args:
            news_data: String containing formatted news items
            
        Returns:
            HTML formatted news content
        """
        if "No news items available" in news_data:
            return "<p>No news items available at the moment.</p>"
        
        # This is a simple formatter - the agent will enhance it
        html_parts = ["<div class='news-container'>"]
        
        # Parse the news data (basic parsing for demonstration)
        lines = news_data.split('\n')
        current_item = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                if current_item:
                    # Process previous item
                    html_parts.append(f"<div class='news-item'>")
                    html_parts.append(f"<h3><a href='{current_item.get('link', '#')}'>{current_item.get('title', '')}</a></h3>")
                    html_parts.append(f"<p>{current_item.get('summary', '')}</p>")
                    html_parts.append(f"</div>")
                
                # Start new item
                current_item = {'title': line[2:].strip()}
            elif line.startswith('Link:'):
                current_item['link'] = line[5:].strip()
            elif line.startswith('Summary:'):
                current_item['summary'] = line[8:].strip()
        
        # Process last item
        if current_item:
            html_parts.append(f"<div class='news-item'>")
            html_parts.append(f"<h3><a href='{current_item.get('link', '#')}'>{current_item.get('title', '')}</a></h3>")
            html_parts.append(f"<p>{current_item.get('summary', '')}</p>")
            html_parts.append(f"</div>")
        
        html_parts.append("</div>")
        return '\n'.join(html_parts)
    
    return format_to_html

async def generate_html_with_agent(news_items):
    """Use OpenAI Agent to generate professional HTML from news items"""
    
    # Create the HTML formatting tool
    html_tool = create_html_formatter_tool()
    
    # Create the news formatter agent
    news_agent = Agent(
        name="Frontend News Formatter",
        instructions="""You are a professional frontend development news formatter. Your job is to:

1. Take formatted news data and convert it to modern, professional HTML
2. Include clean CSS styling (inline or internal styles)
3. Make titles clickable links that open in new tabs
4. Use semantic HTML elements (article, section, etc.)
5. Add subtle hover effects and modern design
6. Ensure mobile responsiveness
7. Use proper typography and spacing
8. Add accessibility features (proper alt text, semantic markup)

Style guidelines:
- Use a modern color scheme (blues, grays)
- Add subtle shadows and borders
- Use system fonts or web-safe fonts
- Include smooth transitions for interactions
- Make the layout clean and scannable

Return only the complete HTML with embedded CSS, ready to be inserted into an email body.""",
        model="gpt-4o",
        tools=[html_tool]
    )
    
    try:
        # Format the news data for the agent
        news_data = format_news_data(news_items)
        
        # Run the agent
        result = news_agent.run(
            f"Please format this frontend development news data into professional HTML with modern styling:\n\n{news_data}\n\nUse the format_to_html tool first to get the basic structure, then enhance it with professional styling, better layout, and modern CSS."
        )
        
        # Extract the HTML content from the agent's response
        html_content = result.messages[-1].content
        
        # Clean up any markdown code blocks if present
        if "```html" in html_content:
            html_content = html_content.split("```html")[1].split("```")[0].strip()
        elif "```" in html_content:
            html_content = html_content.split("```")[1].split("```")[0].strip()
        
        return html_content
        
    except Exception as e:
        logger.error(f"Error generating HTML with agent: {e}")
        # Fallback to simple HTML generation
        return generate_simple_html_fallback(news_items)

def generate_simple_html_fallback(news_items):
    """Simple HTML fallback if agent fails"""
    if not news_items:
        return "<p>No news items available at the moment.</p>"
    
    html_parts = ["""
    <style>
        .news-container { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        .news-item { margin-bottom: 30px; padding: 20px; border-left: 4px solid #2563eb; background: #f8fafc; }
        .news-item h3 { margin: 0 0 10px 0; }
        .news-item h3 a { color: #1e40af; text-decoration: none; }
        .news-item h3 a:hover { text-decoration: underline; }
        .news-item p { margin: 0; color: #4b5563; line-height: 1.6; }
    </style>
    <div class="news-container">
    """]
    
    for item in news_items:
        html_parts.append(f"""
        <div class="news-item">
            <h3><a href="{item['link']}" target="_blank">{item['title']}</a></h3>
            <p>{item['summary']}</p>
        </div>
        """)
    
    html_parts.append("</div>")
    return ''.join(html_parts)

async def send_email(subject, html_content):
    """Send email with HTML content"""
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
    """Main function to orchestrate the news generation process"""
    logger.info("Starting OpenAI Agents-powered frontend news generator...")
    
    # Fetch news items
    news_items = await fetch_frontend_news()
    
    if not news_items:
        logger.warning("No news items found")
        return
    
    logger.info(f"Found {len(news_items)} news items")
    
    # Generate HTML using OpenAI Agent
    news_html = await generate_html_with_agent(news_items)
    
    # Prepare complete email body
    subject = "Daily Frontend Development Tech Updates"
    body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Frontend Development News</title>
    </head>
    <body style="margin: 0; padding: 20px; background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <div style="max-width: 800px; margin: 0 auto;">
            <header style="text-align: center; margin-bottom: 40px;">
                <h1 style="color: #1e40af; margin: 0; font-size: 28px;">Frontend Development News</h1>
                <p style="color: #6b7280; margin: 10px 0 0 0;">Your daily dose of frontend development updates</p>
            </header>
            
            <main>
                {news_html}
            </main>
            
            <footer style="margin-top: 50px; padding-top: 30px; border-top: 2px solid #e5e7eb; text-align: center;">
                <p style="color: #9ca3af; font-size: 14px; margin: 0;">
                    Generated by OpenAI Agents | Powered by Frontend Dev News Bot
                </p>
                <p style="color: #9ca3af; font-size: 12px; margin: 10px 0 0 0;">
                    Source: <a href="{RSS_FEED_URL}" style="color: #6366f1;">Smashing Magazine</a>
                </p>
            </footer>
        </div>
    </body>
    </html>
    """
    
    # Send the email
    await send_email(subject, body)
    logger.info("Newsletter generation and sending completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())