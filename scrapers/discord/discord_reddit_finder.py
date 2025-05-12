#!/usr/bin/env python3
"""
discord_reddit_finder.py - Script to search Reddit for Discord communities and extract invite links.
Part of Web Scraping Portfolio project for job interview preparation.
"""

import re
import os
import csv
import json
import time
import logging
import pandas as pd
import praw
import requests
from datetime import datetime
from urllib.parse import urlparse
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("discord_finder.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('discord_reddit_finder')

# Load environment variables
load_dotenv()

class DiscordRedditFinder:
    def __init__(self):
        """Initialize the Discord Reddit Finder with Reddit API credentials."""
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent=os.getenv('REDDIT_USER_AGENT', 'discord_finder_script v0.1')
            )
            logger.info("Successfully authenticated with Reddit API")
            
            # Create necessary directories
            os.makedirs('scraped_data/discord', exist_ok=True)
            
            # Discord invite pattern - matches discord.gg/xyz and discord.com/invite/xyz formats
            self.discord_pattern = re.compile(
                r'(https?://)?(discord\.(?:gg|com/invite))/([a-zA-Z0-9-]+)'
            )
            
            # Tracked data
            self.found_invites = set()
            self.discord_communities = []
            
        except Exception as e:
            logger.error(f"Failed to initialize: {str(e)}")
            raise
    
    def search_reddit_for_discord(self, subreddits, query="discord", limit=100):
        """
        Search specified subreddits for posts mentioning Discord.
        
        Args:
            subreddits: List of subreddit names to search
            query: Search term (default: "discord")
            limit: Maximum number of posts to fetch per subreddit
            
        Returns:
            List of posts containing potential Discord links
        """
        all_posts = []
        
        for subreddit_name in subreddits:
            logger.info(f"Searching r/{subreddit_name} for '{query}'")
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Search in posts
                for post in subreddit.search(query, limit=limit):
                    # Check title and selftext for Discord links
                    if self._contains_discord_link(post.title) or \
                       (hasattr(post, 'selftext') and self._contains_discord_link(post.selftext)):
                        all_posts.append(post)
                        
                # Also check comments if post count is low
                if len(all_posts) < 10:
                    logger.info(f"Checking comments in r/{subreddit_name} hot posts")
                    for post in subreddit.hot(limit=25):
                        post.comments.replace_more(limit=0)  # Only fetch top-level comments
                        for comment in post.comments:
                            if hasattr(comment, 'body') and self._contains_discord_link(comment.body):
                                all_posts.append(post)
                                break  # Only need to add the post once
            
            except Exception as e:
                logger.error(f"Error searching r/{subreddit_name}: {str(e)}")
                continue
                
            # Respect rate limits
            time.sleep(2)
            
        logger.info(f"Found {len(all_posts)} posts potentially containing Discord links")
        return all_posts
    
    def _contains_discord_link(self, text):
        """Check if text contains a Discord invite link."""
        if not text:
            return False
        return bool(self.discord_pattern.search(text))
    
    def extract_discord_invites(self, posts):
        """
        Extract all Discord invite links from a list of Reddit posts.
        
        Args:
            posts: List of praw post objects
            
        Returns:
            Set of unique Discord invite codes
        """
        for post in posts:
            # Check post title
            self._extract_invites_from_text(post.title)
            
            # Check post content
            if hasattr(post, 'selftext'):
                self._extract_invites_from_text(post.selftext)
            
            # Check comments
            try:
                post.comments.replace_more(limit=0)
                for comment in post.comments.list():
                    if hasattr(comment, 'body'):
                        self._extract_invites_from_text(comment.body)
            except Exception as e:
                logger.error(f"Error processing comments for post {post.id}: {str(e)}")
            
            # Respect rate limits
            time.sleep(1)
        
        logger.info(f"Extracted {len(self.found_invites)} unique Discord invite codes")
        return self.found_invites
    
    def _extract_invites_from_text(self, text):
        """Extract Discord invite links from text and add to found_invites."""
        if not text:
            return
            
        matches = self.discord_pattern.finditer(text)
        for match in matches:
            invite_code = match.group(3)
            self.found_invites.add(invite_code)
    
    def collect_discord_info(self, max_invites=50):
        """
        Collect information about Discord communities using invite links.
        
        Args:
            max_invites: Maximum number of invites to process
            
        Returns:
            List of Discord community information dictionaries
        """
        processed = 0
        
        for invite_code in list(self.found_invites)[:max_invites]:
            try:
                info = self._get_discord_invite_info(invite_code)
                if info:
                    self.discord_communities.append(info)
                    processed += 1
                    logger.info(f"Processed invite {processed}/{max_invites}: {invite_code}")
                
                # Respect Discord API rate limits
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"Error processing invite {invite_code}: {str(e)}")
        
        logger.info(f"Successfully collected info for {len(self.discord_communities)} Discord communities")
        return self.discord_communities
    
    def _get_discord_invite_info(self, invite_code):
        """
        Get information about a Discord server from its invite code.
        Uses Discord's public invite endpoint.
        
        Args:
            invite_code: The Discord invite code (without discord.gg/)
            
        Returns:
            Dictionary with server information or None if failed
        """
        url = f"https://discord.com/api/v9/invites/{invite_code}?with_counts=true"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract relevant information
                server_info = {
                    'invite_code': invite_code,
                    'server_name': data.get('guild', {}).get('name', 'Unknown'),
                    'description': data.get('guild', {}).get('description'),
                    'member_count': data.get('approximate_member_count'),
                    'online_count': data.get('approximate_presence_count'),
                    'verified': data.get('guild', {}).get('verified', False),
                    'channel_name': data.get('channel', {}).get('name'),
                    'inviter_username': data.get('inviter', {}).get('username'),
                    'expires_at': data.get('expires_at'),
                    'collected_at': datetime.now().isoformat(),
                }
                return server_info
                
            else:
                logger.warning(f"Failed to get info for invite {invite_code}: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching Discord invite {invite_code}: {str(e)}")
            return None
    
    def save_results(self):
        """Save the collected Discord community information to CSV and JSON files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save to CSV
        csv_path = f"scraped_data/discord/discord_communities_{timestamp}.csv"
        try:
            df = pd.DataFrame(self.discord_communities)
            df.to_csv(csv_path, index=False)
            logger.info(f"Saved CSV results to {csv_path}")
        except Exception as e:
            logger.error(f"Error saving CSV: {str(e)}")
        
        # Save to JSON
        json_path = f"scraped_data/discord/discord_communities_{timestamp}.json"
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.discord_communities, f, indent=2)
            logger.info(f"Saved JSON results to {json_path}")
        except Exception as e:
            logger.error(f"Error saving JSON: {str(e)}")
            
        # Save invite codes
        invites_path = f"scraped_data/discord/discord_invites_{timestamp}.txt"
        try:
            with open(invites_path, 'w', encoding='utf-8') as f:
                for invite in self.found_invites:
                    f.write(f"{invite}\n")
            logger.info(f"Saved invite codes to {invites_path}")
        except Exception as e:
            logger.error(f"Error saving invite codes: {str(e)}")
    
    def analyze_communities(self):
        """Analyze the collected Discord communities and print summary statistics."""
        if not self.discord_communities:
            logger.warning("No communities to analyze")
            return
            
        df = pd.DataFrame(self.discord_communities)
        
        # Calculate statistics
        stats = {
            'total_communities': len(df),
            'valid_communities': df['server_name'].count(),
            'average_members': df['member_count'].mean(),
            'median_members': df['member_count'].median(),
            'verified_count': df['verified'].sum(),
            'largest_community': df.loc[df['member_count'].idxmax()]['server_name'] if not df.empty else 'None',
            'max_members': df['member_count'].max(),
        }
        
        logger.info("Discord Communities Analysis:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
            
        return stats

def main():
    """Main function to run the Discord Reddit Finder."""
    finder = DiscordRedditFinder()
    
    # Use the communities from your existing Reddit data
    try:
        reddit_df = pd.read_csv('scraped_data/reddit/analyzed_communities.csv')
        subreddits = reddit_df['subreddit'].tolist()
        logger.info(f"Loaded {len(subreddits)} subreddits from analyzed_communities.csv")
    except Exception as e:
        logger.error(f"Error loading existing Reddit data: {str(e)}")
        logger.info("Using default subreddits list")
        # Updated list focusing on student and professional communities
        subreddits = [
            'college', 'gradschool', 'StudentLoans', 'StudentLife', 'ApplyingToCollege',
            'careerguidance', 'jobs', 'internships', 'careeradvice', 'resumes',
            'GetEmployed', 'youngprofessionals', 'EngineeringStudents', 'premed',
            'lawschool', 'MBA', 'teachingresources', 'UniversityOfReddit',
            'highschool', 'teenagers', 'cscareerquestions', 'AskAcademia',
            'GradAdmissions', 'PhDAdvice', 'professors', 'HomeWorkHelp',
            'study', 'campuslife', 'FinancialAid', 'OnlineLearning'
        ]
    
    # Limit to top 30 subreddits to avoid rate limiting issues but get better coverage
    subreddits = subreddits[:30]
    
    # Search for Discord mentions
    posts = finder.search_reddit_for_discord(subreddits)
    
    # Extract invite links
    finder.extract_discord_invites(posts)
    
    # Collect information about Discord communities
    finder.collect_discord_info(max_invites=100)  # Increased to get more communities
    
    # Save results
    finder.save_results()
    
    # Analyze communities
    finder.analyze_communities()
    
    logger.info("Discord Reddit Finder completed successfully")

if __name__ == "__main__":
    main()