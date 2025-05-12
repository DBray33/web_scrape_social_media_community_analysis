"""
Reddit Subreddit Finder - Discovers relevant subreddits based on keywords
and collects metadata for outreach purposes.
"""
import praw
import pandas as pd
import os
from dotenv import load_dotenv
import time
from datetime import datetime

# Load environment variables
load_dotenv()

# Debug prints for environment variables
print("Checking environment variables:")
print(f"Client ID exists: {'Yes' if os.getenv('REDDIT_CLIENT_ID') else 'No'}")
print(f"Client Secret exists: {'Yes' if os.getenv('REDDIT_CLIENT_SECRET') else 'No'}")
print(f"User Agent exists: {'Yes' if os.getenv('REDDIT_USER_AGENT') else 'No'}")

# Set up Reddit API credentials
try:
    # Store these in a .env file for security
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT', 'SubredditFinder v1.0 by YourUsername'),
        username=os.getenv('REDDIT_USERNAME', ''),
        password=os.getenv('REDDIT_PASSWORD', '')
    )
    print("Reddit instance created successfully")
except Exception as e:
    print(f"Error creating Reddit instance: {e}")
    raise

def find_relevant_subreddits(keywords, limit=50):
    """
    Find subreddits related to given keywords
    """
    all_subreddits = []
    
    for keyword in keywords:
        print(f"Searching for subreddits related to: {keyword}")
        
        try:
            # Search for subreddits
            subreddits = reddit.subreddits.search(keyword, limit=limit)
            
            for subreddit in subreddits:
                try:
                    # Get subreddit details
                    sub_data = {
                        'name': subreddit.display_name,
                        'url': f"https://www.reddit.com/r/{subreddit.display_name}/",
                        'subscribers': subreddit.subscribers,
                        'description': subreddit.public_description,
                        'created_utc': datetime.fromtimestamp(subreddit.created_utc).strftime('%Y-%m-%d'),
                        'is_active': is_subreddit_active(subreddit),
                        'keyword': keyword,
                        'last_updated': datetime.now().strftime('%Y-%m-%d')
                    }
                    
                    all_subreddits.append(sub_data)
                    print(f"Found: r/{subreddit.display_name} - {subreddit.subscribers} subscribers")
                
                except Exception as e:
                    print(f"Error processing r/{subreddit.display_name}: {e}")
            
            # Respect Reddit's rate limits
            time.sleep(2)
        
        except Exception as e:
            print(f"Error searching for '{keyword}': {e}")
    
    # Convert to DataFrame and remove duplicates
    if all_subreddits:
        df = pd.DataFrame(all_subreddits)
        df = df.drop_duplicates(subset=['name'])
        return df
    else:
        print("No subreddits found!")
        return pd.DataFrame()

def is_subreddit_active(subreddit):
    """
    Check if a subreddit is active based on recent posts
    """
    try:
        # Get newest posts
        newest_posts = list(subreddit.new(limit=5))
        
        if not newest_posts:
            return False
        
        # Check if the newest post is within the last month
        newest_post_time = newest_posts[0].created_utc
        current_time = time.time()
        
        # If newest post is within 30 days, consider active
        return (current_time - newest_post_time) < (30 * 24 * 60 * 60)
    
    except Exception as e:
        print(f"Error checking if r/{subreddit.display_name} is active: {e}")
        return False

def export_to_csv(df, filename='reddit_outreach_targets.csv'):
    """
    Export subreddit data to CSV
    """
    # Make sure the scraped_data directory exists
    os.makedirs('scraped_data', exist_ok=True)
    
    if df.empty:
        print("No data to export!")
        return None
    
    filepath = os.path.join('scraped_data', filename)
    df.to_csv(filepath, index=False)
    print(f"Data exported to {filepath}")
    
    return filepath

def main():
    print("\n" + "="*50)
    print("REDDIT SUBREDDIT FINDER")
    print("="*50)
    
    # Debug prints
    print("Script started at:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print(f"Client ID: {os.getenv('REDDIT_CLIENT_ID')}")
    print(f"Client Secret: {os.getenv('REDDIT_CLIENT_SECRET')[:5]}..." if os.getenv('REDDIT_CLIENT_SECRET') else "Client Secret: Not found")
    print(f"User Agent: {os.getenv('REDDIT_USER_AGENT')}")
    
    try:
        # Test Reddit connection
        print("Testing Reddit connection...")
        me = reddit.user.me()
        print(f"Connected as: {me if me else 'Read-only mode'}")
    except Exception as e:
        print(f"Reddit connection error: {str(e)}")
    
    # Define relevant keywords for student and emerging professional communities
    keywords = [
        'college students', 
        'university', 
        'grad school',
        'students', 
        'career advice',
        'internships',
        'job hunting',
        'professional development',
        'coding bootcamp',
        'new grads',
        'entry level jobs'
    ]
    
    # Find relevant subreddits
    print("\nStarting subreddit search...")
    subreddits_df = find_relevant_subreddits(keywords)
    
    if not subreddits_df.empty:
        print(f"\nFound {len(subreddits_df)} total subreddits before filtering")
        
        # Filter for more relevant communities (e.g., minimum subscriber count)
        filtered_df = subreddits_df[subreddits_df['subscribers'] > 1000]
        print(f"After subscriber filter: {len(filtered_df)} subreddits")
        
        filtered_df = filtered_df[filtered_df['is_active'] == True]
        print(f"After activity filter: {len(filtered_df)} subreddits")
        
        # Sort by subscriber count
        filtered_df = filtered_df.sort_values(by='subscribers', ascending=False)
        
        # Export the data
        export_filepath = export_to_csv(filtered_df)
        
        if export_filepath:
            print(f"\nSuccessfully found {len(filtered_df)} relevant subreddits for outreach")
            print(f"Data saved to {export_filepath}")
    else:
        print("No subreddits found. Check your Reddit API credentials.")
    
    print("\nScript completed at:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == "__main__":
    main()