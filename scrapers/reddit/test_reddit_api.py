import praw
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Print loaded variables for debugging
print("API Credentials:")
print(f"Client ID: {os.getenv('REDDIT_CLIENT_ID')}")
print(f"Client Secret: {os.getenv('REDDIT_CLIENT_SECRET')[:5]}..." if os.getenv('REDDIT_CLIENT_SECRET') else "Client Secret: Not found")
print(f"User Agent: {os.getenv('REDDIT_USER_AGENT')}")

# Initialize the Reddit API
reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent=os.getenv('REDDIT_USER_AGENT', 'TestScript v1.0'),
)

# Test a simple API call
print("\nTesting Reddit API...")
try:
    # Try to get a popular subreddit
    subreddit = reddit.subreddit("AskReddit")
    print(f"Successfully connected to r/{subreddit.display_name}")
    print(f"Subscribers: {subreddit.subscribers}")
    print(f"Description: {subreddit.public_description[:100]}...")
    
    # Try to get a few posts
    print("\nRecent posts:")
    for i, post in enumerate(subreddit.hot(limit=3)):
        print(f"{i+1}. {post.title[:50]}...")
    
    print("\nAPI test successful!")
except Exception as e:
    print(f"Error: {e}")