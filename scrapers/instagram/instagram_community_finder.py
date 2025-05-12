#!/usr/bin/env python3
"""
instagram_community_finder.py - Script to discover and collect data on Instagram communities
focused on students and emerging professionals.

Part of Web Scraping Portfolio project for job interview preparation.
"""

import os
import time
import json
import random
import logging
import pandas as pd
import requests
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/instagram_finder.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('instagram_finder')

# Load environment variables
load_dotenv()

class InstagramCommunityFinder:
    """Class to find and collect data on Instagram communities."""
    
    def __init__(self):
        """Initialize the Instagram Community Finder."""
        # Create necessary directories
        os.makedirs('scraped_data/instagram', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Base URL
        self.base_url = "https://www.instagram.com"
        
        # User agent to simulate a browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        
        # Storage for found communities
        self.communities = []
        
        # Keywords to identify student and professional communities
        self.student_keywords = [
            'student', 'college', 'university', 'campus', 'dorm', 
            'study', 'education', 'academic', 'school', 'grad', 
            'undergrad', 'freshman', 'sophomore', 'junior', 'senior',
            'major', 'degree', 'class', 'lecturer', 'professor'
        ]
        
        self.professional_keywords = [
            'career', 'job', 'profession', 'resume', 'interview',
            'internship', 'salary', 'workplace', 'office', 'corporate',
            'employment', 'hire', 'recruiting', 'professional', 'entry level',
            'networking', 'linkedin', 'business', 'entrepreneur', 'startup'
        ]
        
        logger.info("Instagram Community Finder initialized")
    
    def discover_communities_via_hashtags(self, base_hashtags=None, max_hashtags=30):
        """
        Discover Instagram communities via relevant hashtags.
        
        Args:
            base_hashtags: Initial hashtags to start discovery process
            max_hashtags: Maximum number of hashtags to process
        """
        if base_hashtags is None:
            base_hashtags = [
                'studentlife', 'collegelife', 'universitylife', 'gradschool',
                'careeradvice', 'jobsearch', 'internships', 'resumetips'
            ]
        
        all_hashtags = set(base_hashtags)
        processed_hashtags = set()
        
        logger.info(f"Starting discovery with {len(base_hashtags)} base hashtags")
        
        # Fix: add a check to ensure all_hashtags - processed_hashtags is not empty
        while len(processed_hashtags) < max_hashtags and all_hashtags - processed_hashtags:
            # Get next hashtag to process
            hashtag = (all_hashtags - processed_hashtags).pop()
            processed_hashtags.add(hashtag)
            
            logger.info(f"Processing hashtag: #{hashtag}")
            
            try:
                # Simulate web request to get hashtag page
                url = f"{self.base_url}/explore/tags/{hashtag}/"
                
                # In a real implementation, we'd make an actual request and parse data
                # This is a simulation for portfolio purposes to show the structure
                self._simulate_hashtag_processing(hashtag)
                
                # Add delay to respect rate limits
                time.sleep(random.uniform(2.0, 4.0))
                
            except Exception as e:
                logger.error(f"Error processing hashtag #{hashtag}: {str(e)}")
            
        logger.info(f"Processed {len(processed_hashtags)} hashtags")
        logger.info(f"Found {len(self.communities)} potential communities")
        
        return self.communities
    
    def _simulate_hashtag_processing(self, hashtag):
        """
        Simulate processing a hashtag page.
        
        In a real implementation, this would:
        1. Make an actual request to Instagram's hashtag page
        2. Parse the HTML to extract related accounts
        3. Analyze each account to see if it's a community
        
        This simulation generates realistic-looking dummy data.
        
        Args:
            hashtag: The hashtag to process
        """
        # Create a relevance score based on how well the hashtag matches our keywords
        student_score = sum(1 for kw in self.student_keywords if kw in hashtag.lower())
        professional_score = sum(1 for kw in self.professional_keywords if kw in hashtag.lower())
        
        # Generate dummy communities with realistic data
        num_communities = random.randint(1, 3)  # Each hashtag leads to 1-3 communities
        
        for i in range(num_communities):
            # Generate sensible dummy data based on hashtag
            if student_score > professional_score:
                community_type = "Student-focused"
                prefix = random.choice(['student', 'college', 'campus', 'edu', 'university', 'academic'])
            else:
                community_type = "Professional-focused"
                prefix = random.choice(['career', 'pro', 'job', 'work', 'business', 'corp'])
            
            # Make username related to hashtag
            suffix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(0, 5)))
            username = f"{prefix}_{hashtag}{suffix}"
            
            # Generate follower count - student accounts tend to have fewer followers 
            if community_type == "Student-focused":
                followers = random.randint(1000, 50000)
            else:
                followers = random.randint(5000, 100000)
            
            # Create a community description that matches our focus
            if community_type == "Student-focused":
                words = random.sample([
                    "students", "campus", "university", "college", "education", "academic",
                    "study", "learning", "school", "scholarship", "student life", "dorm",
                    "classes", "exams", "lectures", "professors", "major", "degree", "campus"
                ], k=random.randint(3, 6))
            else:
                words = random.sample([
                    "career", "professional", "jobs", "workplace", "business", "corporate",
                    "employment", "hiring", "resume", "interview", "internship", "networking",
                    "skills", "development", "leadership", "mentoring", "success", "startup" 
                ], k=random.randint(3, 6))
                
            description = f"Community for {' '.join(words)}. Follow for daily content!"
            
            # Posts and engagement metrics
            posts = random.randint(50, 1000)
            engagement_rate = random.uniform(0.01, 0.05)  # 1-5% engagement rate
            
            # Calculate relevance score
            if community_type == "Student-focused":
                relevance_score = student_score + random.randint(1, 5)
            else:
                relevance_score = professional_score + random.randint(1, 5)
                
            # Add some community accounts
            community = {
                'username': username,
                'full_name': username.replace('_', ' ').title(),
                'followers': followers,
                'posts': posts,
                'engagement_rate': engagement_rate,
                'description': description,
                'community_type': community_type,
                'source_hashtag': hashtag,
                'is_verified': random.random() < 0.1,  # 10% chance of being verified
                'relevance_score': relevance_score,
                'collected_at': datetime.now().isoformat()
            }
            
            self.communities.append(community)
            
        logger.info(f"Found {num_communities} potential communities from #{hashtag}")
    
    def filter_communities(self, min_followers=1000):
        """
        Filter the collected communities based on relevance and size.
        
        Args:
            min_followers: Minimum follower count for a relevant community
            
        Returns:
            Filtered list of communities
        """
        if not self.communities:
            logger.warning("No communities to filter")
            return []
        
        # Convert to DataFrame for easier filtering
        df = pd.DataFrame(self.communities)
        
        # Apply size filter
        filtered_df = df[df['followers'] >= min_followers].copy()
        
        # Sort by relevance score and then by follower count
        filtered_df = filtered_df.sort_values(
            by=['relevance_score', 'followers'], 
            ascending=[False, False]
        )
        
        logger.info(f"Filtered to {len(filtered_df)} communities with at least {min_followers} followers")
        
        # Convert back to list of dictionaries
        filtered_communities = filtered_df.to_dict('records')
        
        return filtered_communities
    
    def save_results(self, filtered_communities=None):
        """
        Save the collected and filtered community data.
        
        Args:
            filtered_communities: Optional filtered list of communities to save
        """
        if filtered_communities is None:
            filtered_communities = self.filter_communities()
            
        if not filtered_communities:
            logger.warning("No communities to save")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save all raw communities
        all_communities_path = f"scraped_data/instagram/instagram_communities_raw_{timestamp}.json"
        with open(all_communities_path, 'w', encoding='utf-8') as f:
            json.dump(self.communities, f, indent=2)
        logger.info(f"Saved {len(self.communities)} raw communities to {all_communities_path}")
        
        # Save all raw communities as CSV
        df_all = pd.DataFrame(self.communities)
        csv_all_path = f"scraped_data/instagram/instagram_communities_raw_{timestamp}.csv"
        df_all.to_csv(csv_all_path, index=False)
        logger.info(f"Saved raw communities to CSV: {csv_all_path}")
        
        # Save filtered communities
        filtered_path = f"scraped_data/instagram/instagram_communities_filtered_{timestamp}.json"
        with open(filtered_path, 'w', encoding='utf-8') as f:
            json.dump(filtered_communities, f, indent=2)
        logger.info(f"Saved {len(filtered_communities)} filtered communities to {filtered_path}")
        
        # Save filtered communities as CSV
        df_filtered = pd.DataFrame(filtered_communities)
        csv_filtered_path = f"scraped_data/instagram/instagram_communities_filtered_{timestamp}.csv"
        df_filtered.to_csv(csv_filtered_path, index=False)
        logger.info(f"Saved filtered communities to CSV: {csv_filtered_path}")
        
        # Generate basic stats
        student_focused = len([c for c in filtered_communities if c['community_type'] == 'Student-focused'])
        professional_focused = len([c for c in filtered_communities if c['community_type'] == 'Professional-focused'])
        total_followers = sum(c['followers'] for c in filtered_communities)
        
        stats = {
            'total_communities': len(filtered_communities),
            'student_focused': student_focused,
            'professional_focused': professional_focused,
            'total_followers': total_followers,
            'avg_followers': total_followers / len(filtered_communities) if filtered_communities else 0,
            'timestamp': timestamp
        }
        
        # Save stats
        stats_path = f"scraped_data/instagram/instagram_stats_{timestamp}.json"
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        logger.info(f"Saved stats to {stats_path}")
        
        return stats

def main():
    """Main function to run the Instagram Community Finder."""
    print("\n" + "="*50)
    print("INSTAGRAM COMMUNITY FINDER")
    print("="*50)
    
    finder = InstagramCommunityFinder()
    
    print("Discovering Instagram communities via hashtags...")
    finder.discover_communities_via_hashtags()
    
    print("Filtering communities by relevance and size...")
    filtered_communities = finder.filter_communities()
    
    print("Saving results...")
    stats = finder.save_results(filtered_communities)
    
    print("\nDiscovery Results:")
    print(f"- Total communities found: {len(finder.communities)}")
    print(f"- Communities after filtering: {stats['total_communities']}")
    print(f"- Student-focused communities: {stats['student_focused']}")
    print(f"- Professional-focused communities: {stats['professional_focused']}")
    print(f"- Total followers reached: {stats['total_followers']:,}")
    print(f"- Average followers per community: {int(stats['avg_followers']):,}")
    
    print("\nDiscovery process completed successfully!")
    print("Data saved in scraped_data/instagram/ directory")
    
    print("\nNOTE: This implementation simulates Instagram API data collection")
    print("for ethical development purposes. In a real-world scenario, proper")
    print("authentication and API access would be required.")

if __name__ == "__main__":
    main()