#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_facebook_data.py - Analysis and visualization of Facebook Groups data

This module provides functions to analyze and visualize data collected from
Facebook Groups, focusing on community metrics, engagement patterns, and
content analysis. The analysis helps understand the dynamics of student and
emerging professional communities on Facebook.
"""

import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
import logging
from collections import Counter, defaultdict
import re
from wordcloud import WordCloud
from matplotlib.ticker import MaxNLocator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/facebook_analysis.log", mode='a'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("facebook_analysis")

class FacebookDataAnalyzer:
    """
    A class to analyze and visualize Facebook Groups data related to
    student and emerging professional communities.
    """
    
    def __init__(
        self, 
        data_dir: str = "scraped_data/facebook",
        output_dir: str = "visualizations/facebook"
    ):
        """
        Initialize the FacebookDataAnalyzer.
        
        Args:
            data_dir: Directory containing the collected Facebook data
            output_dir: Directory to save visualizations
        """
        self.data_dir = data_dir
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        # Initialize data containers
        self.groups_df = None
        self.posts_df = None
        self.members_df = None
        
        # Load data if available
        self._load_data()
        
        logger.info("FacebookDataAnalyzer initialized")
    
    def _load_data(self) -> None:
        """Load Facebook Groups data from CSV or JSON files"""
        # Try loading from CSV first (preferred for analysis)
        try:
            groups_csv = os.path.join(self.data_dir, "groups.csv")
            posts_csv = os.path.join(self.data_dir, "posts.csv")
            members_csv = os.path.join(self.data_dir, "members.csv")
            
            if os.path.exists(groups_csv):
                self.groups_df = pd.read_csv(groups_csv)
                logger.info(f"Loaded {len(self.groups_df)} groups from CSV")
            
            if os.path.exists(posts_csv):
                self.posts_df = pd.read_csv(posts_csv)
                # Convert date strings to datetime objects
                self.posts_df['date'] = pd.to_datetime(self.posts_df['date'])
                logger.info(f"Loaded {len(self.posts_df)} posts from CSV")
            
            if os.path.exists(members_csv):
                self.members_df = pd.read_csv(members_csv)
                # Convert date strings to datetime objects
                self.members_df['join_date'] = pd.to_datetime(self.members_df['join_date'])
                logger.info(f"Loaded {len(self.members_df)} members from CSV")
        
        except Exception as e:
            logger.warning(f"Error loading data from CSV: {e}")
            logger.info("Attempting to load from JSON files...")
            
            # Fallback to JSON if CSV fails
            try:
                groups_json = os.path.join(self.data_dir, "groups.json")
                posts_json = os.path.join(self.data_dir, "posts.json")
                members_json = os.path.join(self.data_dir, "members.json")
                
                if os.path.exists(groups_json):
                    with open(groups_json, 'r') as f:
                        self.groups_df = pd.DataFrame(json.load(f))
                    logger.info(f"Loaded {len(self.groups_df)} groups from JSON")
                
                if os.path.exists(posts_json):
                    with open(posts_json, 'r') as f:
                        self.posts_df = pd.DataFrame(json.load(f))
                    # Convert date strings to datetime objects
                    self.posts_df['date'] = pd.to_datetime(self.posts_df['date'])
                    logger.info(f"Loaded {len(self.posts_df)} posts from JSON")
                
                if os.path.exists(members_json):
                    with open(members_json, 'r') as f:
                        self.members_df = pd.DataFrame(json.load(f))
                    # Convert date strings to datetime objects
                    self.members_df['join_date'] = pd.to_datetime(self.members_df['join_date'])
                    logger.info(f"Loaded {len(self.members_df)} members from JSON")
            
            except Exception as e:
                logger.error(f"Error loading data from JSON: {e}")
        
        # Check if data is loaded
        if self.groups_df is None or self.posts_df is None or self.members_df is None:
            logger.warning("Some data could not be loaded. Analysis may be incomplete.")

    # [Include all the other methods from the original file here...]

    def _visualize_member_demographics(self) -> None:
        """Visualize member demographics"""
        if self.members_df is None or len(self.members_df) == 0:
            logger.warning("Member data not available for demographics visualization")
            return
        
        # Visualize profession distribution if available
        if 'reported_profession' in self.members_df.columns:
            plt.figure(figsize=(14, 10))
            
            # Get top 10 professions
            top_professions = self.members_df['reported_profession'].value_counts().head(10)
            
            # Create horizontal bar chart
            ax = sns.barplot(x=top_professions.values, y=top_professions.index, palette='viridis')
            
            # Add count and percentage labels to bars
            total_members = len(self.members_df)
            for i, count in enumerate(top_professions.values):
                percentage = 100 * count / total_members
                ax.text(count + 0.1, i, f"{count} ({percentage:.1f}%)", va='center')
            
            # Set labels and title
            plt.title('Top 10 Professions in Facebook Groups', fontsize=16, pad=20)
            plt.xlabel('Number of Members', fontsize=14)
            plt.ylabel('Profession', fontsize=14)
            plt.tight_layout()
            
            # Save if requested
            if self.output_dir:
                plt.savefig(os.path.join(self.output_dir, 'member_professions.png'), dpi=300, bbox_inches='tight')
                logger.info("Saved member professions visualization")
            
            plt.close()
        
        # Visualize location distribution if available
        if 'reported_location' in self.members_df.columns:
            plt.figure(figsize=(14, 8))
            
            # Get top 10 locations
            top_locations = self.members_df['reported_location'].value_counts().head(10)
            
            # Create pie chart
            plt.pie(top_locations.values, labels=top_locations.index, autopct='%1.1f%%', 
                   startangle=90, colors=sns.color_palette('viridis', len(top_locations)))
            
            # Set title and ensure circle shape
            plt.title('Member Location Distribution', fontsize=16, pad=20)
            plt.axis('equal')
            plt.tight_layout()
            
            # Save if requested
            if self.output_dir:
                plt.savefig(os.path.join(self.output_dir, 'member_locations.png'), dpi=300, bbox_inches='tight')
                logger.info("Saved member locations visualization")
            
            plt.close()

    def _visualize_content_word_cloud(self) -> None:
        """Visualize content themes using word cloud"""
        if self.posts_df is None or len(self.posts_df) == 0 or 'content' not in self.posts_df.columns:
            logger.warning("Post content data not available for word cloud visualization")
            return
        
        # Extract all post content
        all_content = " ".join(self.posts_df['content'].astype(str))
        
        # Define stopwords to exclude
        stopwords = set(['the', 'and', 'to', 'of', 'a', 'in', 'for', 'is', 'on', 'that', 'this', 
                        'with', 'are', 'as', 'at', 'be', 'by', 'or', 'an', 'it', 'if',
                        'has', 'have', 'had', 'was', 'were', 'will', 'would', 'should', 'could',
                        'can', 'just', 'any', 'from', 'some', 'all', 'not', 'our', 'your', 'their'])
        
        # Generate word cloud
        try:
            wordcloud = WordCloud(
                width=800, 
                height=400, 
                background_color='white',
                colormap='viridis',
                stopwords=stopwords,
                max_words=100,
                contour_width=3,
                contour_color='steelblue'
            ).generate(all_content)
            
            # Display the word cloud
            plt.figure(figsize=(12, 8))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('Common Themes in Facebook Group Discussions', fontsize=16, pad=20)
            plt.tight_layout()
            
            # Save if requested
            if self.output_dir:
                plt.savefig(os.path.join(self.output_dir, 'content_word_cloud.png'), dpi=300, bbox_inches='tight')
                logger.info("Saved content word cloud visualization")
            
            plt.close()
        except Exception as e:
            logger.error(f"Error generating word cloud: {e}")

    def _visualize_audience_focus(self) -> None:
        """Visualize audience focus based on content analysis"""
        # Get content analysis results
        content_analysis = self.analyze_content_themes()
        
        if not content_analysis or 'student_focus_percentage' not in content_analysis:
            logger.warning("Audience focus data not available for visualization")
            return
        
        # Extract focus percentages
        student_pct = content_analysis['student_focus_percentage']
        professional_pct = content_analysis['professional_focus_percentage']
        
        # Create pie chart
        plt.figure(figsize=(10, 8))
        
        # Data and labels
        sizes = [student_pct, professional_pct]
        labels = ['Student Focus', 'Professional Focus']
        colors = ['#4285F4', '#34A853']  # Blue, Green
        
        # Create pie chart with a wedge pulled out
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
               startangle=90, explode=(0.1, 0))
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        plt.axis('equal')
        
        # Add title
        plt.title('Audience Focus Based on Content Analysis', fontsize=16, pad=20)
        
        # Save if requested
        if self.output_dir:
            plt.savefig(os.path.join(self.output_dir, 'audience_focus.png'), dpi=300, bbox_inches='tight')
            logger.info("Saved audience focus visualization")
        
        plt.close()
        
        # Create bar chart showing top student vs professional keywords
        # Extract keyword counts
        student_keywords = content_analysis.get('student_keyword_count', 0)
        professional_keywords = content_analysis.get('professional_keyword_count', 0)
        
        plt.figure(figsize=(10, 6))
        
        # Create bar chart
        categories = ['Student Keywords', 'Professional Keywords']
        counts = [student_keywords, professional_keywords]
        
        ax = sns.barplot(x=categories, y=counts, palette=['#4285F4', '#34A853'])
        
        # Add count labels to bars
        for i, count in enumerate(counts):
            ax.text(i, count + (count * 0.05), str(count), ha='center')
        
        # Set labels and title
        plt.title('Student vs. Professional Keyword Frequency', fontsize=16, pad=20)
        plt.ylabel('Frequency', fontsize=14)
        plt.tight_layout()
        
        # Save if requested
        if self.output_dir:
            plt.savefig(os.path.join(self.output_dir, 'keyword_focus.png'), dpi=300, bbox_inches='tight')
            logger.info("Saved keyword focus visualization")
        
        plt.close()

    def _visualize_top_outreach_groups(self) -> None:
        """Visualize top groups for outreach based on analysis"""
        # Run cross-group analysis to get outreach scores
        cross_group = self.analyze_cross_group_patterns()
        
        # Check if outreach scores are available
        if not cross_group or ('student_outreach_scores' not in cross_group and 'professional_outreach_scores' not in cross_group):
            logger.warning("Outreach score data not available for visualization")
            return
        
        # Visualize top student outreach groups
        if 'student_outreach_scores' in cross_group and cross_group['student_outreach_scores']:
            # Convert to DataFrame for easier sorting and visualization
            student_scores = pd.DataFrame(cross_group['student_outreach_scores'].values())
            
            # Sort by outreach score and get top 10
            student_scores = student_scores.sort_values('outreach_score', ascending=False).head(10)
            
            # Create horizontal bar chart
            plt.figure(figsize=(14, 8))
            
            ax = sns.barplot(x='outreach_score', y='name', data=student_scores, palette='Blues_d')
            
            # Add educational focus labels to bars
            for i, (_, row) in enumerate(student_scores.iterrows()):
                ax.text(row['outreach_score'] + 0.1, i, f"{row['school_focus']}", va='center')
            
            # Set labels and title
            plt.title('Top 10 Groups for Student Outreach', fontsize=16, pad=20)
            plt.xlabel('Outreach Score', fontsize=14)
            plt.ylabel('Group Name', fontsize=14)
            plt.xlim(0, max(student_scores['outreach_score']) * 1.2)  # Make room for labels
            plt.tight_layout()
            
            # Save if requested
            if self.output_dir:
                plt.savefig(os.path.join(self.output_dir, 'top_student_outreach_groups.png'), dpi=300, bbox_inches='tight')
                logger.info("Saved top student outreach groups visualization")
            
            plt.close()
        
        # Visualize top professional outreach groups
        if 'professional_outreach_scores' in cross_group and cross_group['professional_outreach_scores']:
            # Convert to DataFrame for easier sorting and visualization
            prof_scores = pd.DataFrame(cross_group['professional_outreach_scores'].values())
            
            # Sort by outreach score and get top 10
            prof_scores = prof_scores.sort_values('outreach_score', ascending=False).head(10)
            
            # Create horizontal bar chart
            plt.figure(figsize=(14, 8))
            
            ax = sns.barplot(x='outreach_score', y='name', data=prof_scores, palette='Greens_d')
            
            # Add category labels to bars
            for i, (_, row) in enumerate(prof_scores.iterrows()):
                ax.text(row['outreach_score'] + 0.1, i, f"{row['category']}", va='center')
            
            # Set labels and title
            plt.title('Top 10 Groups for Professional Outreach', fontsize=16, pad=20)
            plt.xlabel('Outreach Score', fontsize=14)
            plt.ylabel('Group Name', fontsize=14)
            plt.xlim(0, max(prof_scores['outreach_score']) * 1.2)  # Make room for labels
            plt.tight_layout()
            
            # Save if requested
            if self.output_dir:
                plt.savefig(os.path.join(self.output_dir, 'top_professional_outreach_groups.png'), dpi=300, bbox_inches='tight')
                logger.info("Saved top professional outreach groups visualization")
            
            plt.close()

    def _visualize_cross_group_comparison(self) -> None:
        """Visualize comparison between Facebook Groups"""
        if self.groups_df is None or len(self.groups_df) < 2:
            logger.warning("Not enough group data for cross-group comparison visualization")
            return
        
        # Compare top groups by size
        plt.figure(figsize=(14, 8))
        
        # Sort groups by member count and get top 10
        top_groups = self.groups_df.sort_values('member_count', ascending=False).head(10)
        
        # Create horizontal bar chart
        ax = sns.barplot(x='member_count', y='name', data=top_groups, palette='viridis')
        
        # Add labels
        for i, count in enumerate(top_groups['member_count']):
            ax.text(count + 1, i, f"{count:,}", va='center')
        
        # Set labels and title
        plt.title('Top 10 Facebook Groups by Size', fontsize=16, pad=20)
        plt.xlabel('Number of Members', fontsize=14)
        plt.ylabel('Group Name', fontsize=14)
        plt.tight_layout()
        
        # Save if requested
        if self.output_dir:
            plt.savefig(os.path.join(self.output_dir, 'top_groups_by_size.png'), dpi=300, bbox_inches='tight')
            logger.info("Saved top groups by size visualization")
        
        plt.close()
        
        # Visualize categories by average members
        plt.figure(figsize=(14, 8))
        
        # Group by category and calculate stats
        category_stats = self.groups_df.groupby('category')['member_count'].agg(['mean', 'count']).reset_index()
        category_stats = category_stats.sort_values('mean', ascending=False)
        
        # Create bar chart
        ax = sns.barplot(x='mean', y='category', data=category_stats, palette='viridis')
        
        # Add count labels
        for i, row in enumerate(category_stats.itertuples()):
            ax.text(row.mean + 100, i, f"Groups: {row.count}", va='center')
        
        # Set labels and title
        plt.title('Average Group Size by Category', fontsize=16, pad=20)
        plt.xlabel('Average Members', fontsize=14)
        plt.ylabel('Category', fontsize=14)
        plt.tight_layout()
        
        # Save if requested
        if self.output_dir:
            plt.savefig(os.path.join(self.output_dir, 'avg_size_by_category.png'), dpi=300, bbox_inches='tight')
            logger.info("Saved average size by category visualization")
        
        plt.close()


def main():
    """Main function to run the Facebook data analysis."""
    print("\n" + "="*50)
    print("FACEBOOK DATA ANALYZER")
    print("="*50)
    
    # Create output directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Initialize the analyzer
    analyzer = FacebookDataAnalyzer()
    
    # Run all analyses
    print("Running Facebook Group metrics analysis...")
    group_metrics = analyzer.analyze_group_metrics()
    
    print("Running post engagement analysis...")
    post_engagement = analyzer.analyze_post_engagement()
    
    print("Running member activity analysis...")
    member_activity = analyzer.analyze_member_activity()
    
    print("Running content theme analysis...")
    content_themes = analyzer.analyze_content_themes()
    
    print("Running cross-group pattern analysis...")
    cross_group = analyzer.analyze_cross_group_patterns()
    
    # Generate visualizations
    print("Generating visualizations...")
    analyzer.generate_visualizations()
    
    # Print summary
    print("\nAnalysis Summary:")
    if group_metrics:
        print(f"Analyzed {group_metrics.get('total_groups', 0)} Facebook Groups")
    if post_engagement:
        print(f"Analyzed {post_engagement.get('total_posts', 0)} posts")
    if member_activity:
        print(f"Analyzed {member_activity.get('total_members_analyzed', 0)} members")
    print(f"\nVisualizations saved to {analyzer.output_dir}/")
    
    print("\nFacebook data analysis completed successfully!")

if __name__ == "__main__":
    main()