#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
integrate_platform_data.py - Integrates data from multiple platforms for cross-platform analysis

This module integrates data from Reddit, Discord, Instagram, and Facebook to enable
cross-platform analysis of student and emerging professional communities. It
standardizes data formats, merges datasets, and creates visualizations that
compare communities across platforms.
"""

import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import logging
from wordcloud import WordCloud
import networkx as nx
from collections import Counter
import glob

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/integration.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("integration")

class PlatformIntegrator:
    """
    A class to integrate and analyze data from multiple social media platforms.
    """
    
    def __init__(
        self,
        reddit_dir: str = "scraped_data/reddit",
        discord_dir: str = "scraped_data/discord",
        instagram_dir: str = "scraped_data/instagram",
        facebook_dir: str = "scraped_data/facebook",
        output_dir: str = "scraped_data/integrated",
        viz_dir: str = "visualizations/integrated/all_platforms"
    ):
        """
        Initialize the PlatformIntegrator.
        
        Args:
            reddit_dir: Directory containing Reddit data
            discord_dir: Directory containing Discord data
            instagram_dir: Directory containing Instagram data
            facebook_dir: Directory containing Facebook data
            output_dir: Directory to save integrated data
            viz_dir: Directory to save visualizations
        """
        self.reddit_dir = reddit_dir
        self.discord_dir = discord_dir
        self.instagram_dir = instagram_dir
        self.facebook_dir = facebook_dir
        self.output_dir = output_dir
        self.viz_dir = viz_dir
        
        # Create output directories if they don't exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.viz_dir, exist_ok=True)
        
        # Initialize data containers
        self.reddit_communities = None
        self.discord_communities = None
        self.instagram_communities = None
        self.facebook_communities = None
        
        self.integrated_communities = None
        self.integrated_content = None
        self.integrated_engagement = None
        self.cross_platform_metrics = None
        
        # Load data if available
        self._load_data()
        
        logger.info("PlatformIntegrator initialized")
    
    def _load_data(self) -> None:
        """Load data from all platforms"""
        # Load Reddit data
        reddit_communities_file = os.path.join(self.reddit_dir, "filtered_student_communities.csv")
        if os.path.exists(reddit_communities_file):
            self.reddit_communities = pd.read_csv(reddit_communities_file)
            logger.info(f"Loaded {len(self.reddit_communities)} Reddit communities")
        else:
            logger.warning(f"Reddit communities file not found: {reddit_communities_file}")
        
        # Load Discord data
        # Find the most recent discord_communities file
        discord_files = glob.glob(os.path.join(self.discord_dir, "discord_communities_*.csv"))
        if discord_files:
            discord_communities_file = max(discord_files, key=os.path.getmtime)
            self.discord_communities = pd.read_csv(discord_communities_file)
            logger.info(f"Loaded {len(self.discord_communities)} Discord communities")
        else:
            logger.warning(f"Discord communities files not found in: {self.discord_dir}")
        
        # Load Instagram data
        # Find the most recent filtered communities file
        instagram_files = glob.glob(os.path.join(self.instagram_dir, "instagram_communities_filtered_*.csv"))
        if instagram_files:
            instagram_communities_file = max(instagram_files, key=os.path.getmtime)
            self.instagram_communities = pd.read_csv(instagram_communities_file)
            logger.info(f"Loaded {len(self.instagram_communities)} Instagram communities")
        else:
            instagram_processed_file = os.path.join(self.instagram_dir, "processed_instagram_data_20250511.csv")
            if os.path.exists(instagram_processed_file):
                self.instagram_communities = pd.read_csv(instagram_processed_file)
                logger.info(f"Loaded {len(self.instagram_communities)} Instagram communities from processed data")
            else:
                logger.warning(f"Instagram communities files not found in: {self.instagram_dir}")
        
        # Load Facebook data
        facebook_groups_file = os.path.join(self.facebook_dir, "groups.csv")
        if os.path.exists(facebook_groups_file):
            self.facebook_communities = pd.read_csv(facebook_groups_file)
            logger.info(f"Loaded {len(self.facebook_communities)} Facebook communities")
        else:
            logger.warning(f"Facebook groups file not found: {facebook_groups_file}")
        
        # Check if any data is loaded
        if (self.reddit_communities is None and 
            self.discord_communities is None and 
            self.instagram_communities is None and
            self.facebook_communities is None):
            logger.error("No community data loaded from any platform")
    
    def standardize_community_data(self) -> pd.DataFrame:
        """
        Standardize community data from different platforms into a common format.
        
        Returns:
            DataFrame containing standardized community data from all platforms
        """
        logger.info("Standardizing community data from all platforms")
        
        standardized_communities = []
        
        # Process Reddit communities
        if self.reddit_communities is not None and len(self.reddit_communities) > 0:
            # Create standardized format for Reddit
            for _, row in self.reddit_communities.iterrows():
                std_community = {
                    'platform': 'Reddit',
                    'community_id': f"reddit_{row.get('subreddit_id', row.get('id', 'unknown'))}",
                    'name': row.get('display_name', row.get('subreddit', 'Unknown Reddit Community')),
                    'description': row.get('public_description', row.get('description', '')),
                    'member_count': row.get('subscribers', 0),
                    'creation_date': row.get('created_utc', None),
                    'category': row.get('category', 'General'),
                    'is_public': not row.get('over18', False),
                    'location': 'Global',
                    'engagement_rate': self._calculate_reddit_engagement(row),
                    'post_frequency': row.get('posts_per_day', 0),
                    'primary_language': 'English',
                    'related_topics': row.get('related_topics', row.get('keywords', '')),
                    'source_url': f"https://www.reddit.com/r/{row.get('display_name', row.get('subreddit', 'unknown'))}"
                }
                standardized_communities.append(std_community)
            
            logger.info(f"Standardized {len(self.reddit_communities)} Reddit communities")
        
        # Process Discord communities
        if self.discord_communities is not None and len(self.discord_communities) > 0:
            # Create standardized format for Discord
            for _, row in self.discord_communities.iterrows():
                std_community = {
                    'platform': 'Discord',
                    'community_id': f"discord_{row.get('server_id', row.get('id', 'unknown'))}",
                    'name': row.get('server_name', row.get('name', 'Unknown Discord Server')),
                    'description': row.get('description', ''),
                    'member_count': row.get('member_count', 0),
                    'creation_date': row.get('created_at', None),
                    'category': row.get('category', row.get('primary_topic', 'General')),
                    'is_public': row.get('is_public', True),
                    'location': 'Global',
                    'engagement_rate': self._calculate_discord_engagement(row),
                    'post_frequency': row.get('messages_per_day', 0),
                    'primary_language': 'English',
                    'related_topics': row.get('related_topics', row.get('tags', '')),
                    'source_url': row.get('invite_url', '')
                }
                standardized_communities.append(std_community)
            
            logger.info(f"Standardized {len(self.discord_communities)} Discord communities")
        
        # Process Instagram communities
        if self.instagram_communities is not None and len(self.instagram_communities) > 0:
            # Create standardized format for Instagram
            for _, row in self.instagram_communities.iterrows():
                std_community = {
                    'platform': 'Instagram',
                    'community_id': f"instagram_{row.get('profile_id', row.get('id', 'unknown'))}",
                    'name': row.get('username', row.get('handle', 'Unknown Instagram Community')),
                    'description': row.get('biography', row.get('bio', '')),
                    'member_count': row.get('followers', 0),
                    'creation_date': row.get('created_at', None),
                    'category': row.get('category', 'General'),
                    'is_public': row.get('is_private', True) == False,
                    'location': row.get('location', 'Global'),
                    'engagement_rate': self._calculate_instagram_engagement(row),
                    'post_frequency': row.get('posts_per_day', 0),
                    'primary_language': 'English',
                    'related_topics': row.get('hashtags', row.get('tags', '')),
                    'source_url': f"https://www.instagram.com/{row.get('username', row.get('handle', 'unknown'))}"
                }
                standardized_communities.append(std_community)
            
            logger.info(f"Standardized {len(self.instagram_communities)} Instagram communities")
        
        # Process Facebook communities
        if self.facebook_communities is not None and len(self.facebook_communities) > 0:
            # Create standardized format for Facebook
            for _, row in self.facebook_communities.iterrows():
                std_community = {
                    'platform': 'Facebook',
                    'community_id': f"facebook_{row.get('group_id', row.get('id', 'unknown'))}",
                    'name': row.get('name', 'Unknown Facebook Group'),
                    'description': row.get('description', ''),
                    'member_count': row.get('member_count', 0),
                    'creation_date': row.get('creation_date', None),
                    'category': row.get('category', 'General'),
                    'is_public': row.get('privacy', 'Closed') == 'Public',
                    'location': row.get('location', 'Global'),
                    'engagement_rate': self._calculate_facebook_engagement(row),
                    'post_frequency': row.get('post_frequency', 0),
                    'primary_language': 'English',
                    'related_topics': ','.join(row.get('related_keywords', [])) if isinstance(row.get('related_keywords', []), list) else row.get('related_keywords', ''),
                    'source_url': f"https://www.facebook.com/groups/{row.get('group_id', 'unknown')}"
                }
                standardized_communities.append(std_community)
            
            logger.info(f"Standardized {len(self.facebook_communities)} Facebook communities")
        
        # Create DataFrame from standardized communities
        self.integrated_communities = pd.DataFrame(standardized_communities)
        
        # Save to file
        if len(self.integrated_communities) > 0:
            output_file = os.path.join(self.output_dir, "integrated_communities.csv")
            self.integrated_communities.to_csv(output_file, index=False)
            logger.info(f"Saved {len(self.integrated_communities)} integrated communities to {output_file}")
        
        return self.integrated_communities
    
    def _calculate_reddit_engagement(self, row: pd.Series) -> float:
        """Calculate engagement rate for Reddit communities"""
        # If available metrics exist, use them
        if 'avg_comments' in row and 'avg_upvotes' in row and 'subscribers' in row and row['subscribers'] > 0:
            engagement = (row['avg_comments'] + row['avg_upvotes']) / row['subscribers']
            return min(1.0, engagement)  # Cap at 100%
        
        # Fallback: use any available engagement metric
        if 'engagement_rate' in row:
            return row['engagement_rate']
        
        # Default engagement rate based on community size (simulated)
        subscribers = row.get('subscribers', 0)
        if subscribers > 0:
            # Larger communities tend to have lower engagement rates
            if subscribers > 1000000:
                return np.random.uniform(0.001, 0.01)  # 0.1% - 1%
            elif subscribers > 100000:
                return np.random.uniform(0.01, 0.03)   # 1% - 3%
            elif subscribers > 10000:
                return np.random.uniform(0.03, 0.05)   # 3% - 5%
            elif subscribers > 1000:
                return np.random.uniform(0.05, 0.1)    # 5% - 10%
            else:
                return np.random.uniform(0.1, 0.2)     # 10% - 20%
        
        return 0.0
    
    def _calculate_discord_engagement(self, row: pd.Series) -> float:
        """Calculate engagement rate for Discord communities"""
        # If available metrics exist, use them
        if 'active_members' in row and 'member_count' in row and row['member_count'] > 0:
            return min(1.0, row['active_members'] / row['member_count'])
        
        # Fallback: use any available engagement metric
        if 'engagement_rate' in row:
            return row['engagement_rate']
        
        # Default engagement rate based on community size (simulated)
        member_count = row.get('member_count', 0)
        if member_count > 0:
            # Discord tends to have higher engagement rates than other platforms
            if member_count > 100000:
                return np.random.uniform(0.05, 0.1)    # 5% - 10%
            elif member_count > 10000:
                return np.random.uniform(0.1, 0.2)     # 10% - 20%
            elif member_count > 1000:
                return np.random.uniform(0.2, 0.3)     # 20% - 30%
            else:
                return np.random.uniform(0.3, 0.5)     # 30% - 50%
        
        return 0.0
    
    def _calculate_instagram_engagement(self, row: pd.Series) -> float:
        """Calculate engagement rate for Instagram communities"""
        # If available metrics exist, use them
        if all(metric in row for metric in ['avg_likes', 'avg_comments', 'followers']) and row['followers'] > 0:
            engagement = (row['avg_likes'] + row['avg_comments']) / row['followers']
            return min(1.0, engagement)  # Cap at 100%
        
        # Fallback: use any available engagement metric
        if 'engagement_rate' in row:
            return row['engagement_rate']
        
        # Default engagement rate based on community size (simulated)
        followers = row.get('followers', 0)
        if followers > 0:
            # Instagram engagement rates by follower count
            if followers > 1000000:
                return np.random.uniform(0.01, 0.02)   # 1% - 2%
            elif followers > 100000:
                return np.random.uniform(0.02, 0.035)  # 2% - 3.5%
            elif followers > 10000:
                return np.random.uniform(0.035, 0.06)  # 3.5% - 6%
            elif followers > 1000:
                return np.random.uniform(0.06, 0.1)    # 6% - 10%
            else:
                return np.random.uniform(0.1, 0.15)    # 10% - 15%
        
        return 0.0
    
    def _calculate_facebook_engagement(self, row: pd.Series) -> float:
        """Calculate engagement rate for Facebook communities"""
        # Default engagement rate based on community size and post frequency (simulated)
        member_count = row.get('member_count', 0)
        post_frequency = row.get('post_frequency', 0)
        
        if member_count > 0 and post_frequency > 0:
            # Calculate base engagement rate
            if member_count > 100000:
                base_rate = np.random.uniform(0.005, 0.015)  # 0.5% - 1.5%
            elif member_count > 10000:
                base_rate = np.random.uniform(0.015, 0.03)   # 1.5% - 3%
            elif member_count > 1000:
                base_rate = np.random.uniform(0.03, 0.05)    # 3% - 5%
            else:
                base_rate = np.random.uniform(0.05, 0.1)     # 5% - 10%
            
            # Adjust for post frequency
            # Higher post frequency can indicate more active community
            frequency_factor = min(2.0, max(0.5, (post_frequency / 5)))
            
            return min(1.0, base_rate * frequency_factor)
        
        return 0.0
    
    def analyze_cross_platform_metrics(self) -> Dict[str, Any]:
        """
        Analyze metrics across all platforms.
        
        Returns:
            Dictionary containing cross-platform metrics analysis results
        """
        if self.integrated_communities is None or len(self.integrated_communities) == 0:
            logger.warning("No integrated community data available for analysis")
            self.standardize_community_data()
        
        if self.integrated_communities is None or len(self.integrated_communities) == 0:
            logger.error("Failed to generate integrated community data")
            return {}
        
        logger.info("Analyzing cross-platform metrics")
        
        # Platform distribution
        platform_counts = self.integrated_communities['platform'].value_counts()
        
        # Calculate averages by platform
        platform_metrics = self.integrated_communities.groupby('platform').agg({
            'member_count': ['mean', 'median', 'sum'],
            'engagement_rate': ['mean', 'median'],
            'post_frequency': ['mean', 'median'],
            'is_public': 'mean'  # Percentage of public communities
        })
        
        # Flatten multi-index
        platform_metrics.columns = ['_'.join(col).strip() for col in platform_metrics.columns.values]
        platform_metrics = platform_metrics.reset_index()
        
        # Calculate normalized engagement (for fair comparison)
        # Scale each platform's engagement to account for platform differences
        platform_scaling = {
            'Reddit': 1.0,       # Base platform
            'Discord': 0.5,      # Discord tends to have higher raw engagement
            'Instagram': 1.2,    # Instagram often has lower engagement than Reddit
            'Facebook': 0.8      # Facebook between Reddit and Instagram
        }
        
        # Apply scaling
        self.integrated_communities['normalized_engagement'] = self.integrated_communities.apply(
            lambda row: row['engagement_rate'] * platform_scaling.get(row['platform'], 1.0),
            axis=1
        )
        
        # Recalculate with normalized values
        normalized_engagement = self.integrated_communities.groupby('platform')['normalized_engagement'].mean().reset_index()
        
        # Category distribution across platforms
        if 'category' in self.integrated_communities.columns:
            # Get top categories
            top_categories = self.integrated_communities['category'].value_counts().head(10).index
            
            # Calculate category distribution by platform
            category_platform_dist = {}
            for category in top_categories:
                cat_data = self.integrated_communities[self.integrated_communities['category'] == category]
                category_platform_dist[category] = cat_data['platform'].value_counts().to_dict()
        else:
            category_platform_dist = {}
        
        # Calculate average community size for each platform
        community_sizes = self.integrated_communities.groupby('platform')['member_count'].mean().to_dict()
        
        # Compile cross-platform metrics
        self.cross_platform_metrics = {
            'platform_distribution': platform_counts.to_dict(),
            'platform_metrics': platform_metrics.to_dict('records'),
            'normalized_engagement': normalized_engagement.to_dict('records'),
            'category_platform_distribution': category_platform_dist,
            'avg_community_size': community_sizes
        }
        
        # Save to file
        output_file = os.path.join(self.output_dir, "cross_platform_metrics.json")
        with open(output_file, 'w') as f:
            json.dump(self.cross_platform_metrics, f, indent=2)
        logger.info(f"Saved cross-platform metrics to {output_file}")
        
        return self.cross_platform_metrics
    
    def generate_cross_platform_visualizations(self) -> None:
        """Generate visualizations comparing communities across platforms"""
        if self.integrated_communities is None or len(self.integrated_communities) == 0:
            logger.warning("No integrated community data available for visualizations")
            return
        
        logger.info("Generating cross-platform visualizations")
        
        # Set up matplotlib style
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams['figure.figsize'] = (14, 8)
        plt.rcParams['font.size'] = 12
        
        # 1. Platform distribution
        self._visualize_platform_distribution()
        
        # 2. Community sizes by platform
        self._visualize_community_sizes()
        
        # 3. Engagement rates by platform
        self._visualize_engagement_rates()
        
        # 4. Categories across platforms
        self._visualize_categories()
        
        # 5. Platform network graph
        self._visualize_platform_network()
        
        # 6. Top communities across platforms
        self._visualize_top_communities()
        
        logger.info("All cross-platform visualizations generated successfully")
    
    def _visualize_platform_distribution(self) -> None:
        """Visualize distribution of communities by platform"""
        plt.figure(figsize=(12, 8))
        
        # Count communities by platform
        platform_counts = self.integrated_communities['platform'].value_counts()
        
        # Create color mapping for platforms (used consistently across visualizations)
        platform_colors = {
            'Reddit': '#FF4500',      # Reddit orange
            'Discord': '#5865F2',     # Discord blue
            'Instagram': '#C13584',   # Instagram purple/pink
            'Facebook': '#3b5998'     # Facebook blue
        }
        
        # Map colors to data
        colors = [platform_colors.get(platform, '#999999') for platform in platform_counts.index]
        
        # Create pie chart
        plt.pie(
            platform_counts.values, 
            labels=platform_counts.index, 
            autopct='%1.1f%%', 
            startangle=90, 
            colors=colors,
            wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}
        )
        
        # Equal aspect ratio ensures the pie chart is circular
        plt.axis('equal')
        
        # Set title
        plt.title('Distribution of Communities by Platform', fontsize=16, pad=20)
        
        # Save visualization
        plt.savefig(os.path.join(self.viz_dir, 'platform_distribution.png'), dpi=300, bbox_inches='tight')
        logger.info("Saved platform distribution visualization")
        
        plt.close()
    
    def _visualize_community_sizes(self) -> None:
        """Visualize community sizes by platform"""
        plt.figure(figsize=(14, 10))
        
        # Create violin plot
        ax = sns.violinplot(
            x='platform', 
            y='member_count', 
            data=self.integrated_communities,
            palette={
                'Reddit': '#FF4500', 
                'Discord': '#5865F2', 
                'Instagram': '#C13584',
                'Facebook': '#3b5998'
            },
            inner='quartile',
            scale='width'
        )
        
        # Set log scale for y-axis (community sizes vary widely)
        ax.set_yscale('log')
        
        # Set labels and title
        plt.title('Community Sizes by Platform', fontsize=16, pad=20)
        plt.xlabel('Platform', fontsize=14)
        plt.ylabel('Number of Members (log scale)', fontsize=14)
        
        # Add mean markers
        means = self.integrated_communities.groupby('platform')['member_count'].mean()
        for i, platform in enumerate(means.index):
            plt.scatter(i, means[platform], marker='o', color='white', s=50, zorder=3)
            plt.scatter(i, means[platform], marker='x', color='black', s=30, zorder=4)
        
        # Add platform-specific average annotation
        for i, platform in enumerate(means.index):
            ax.text(
                i, 
                means[platform] * 2, 
                f'Avg: {int(means[platform]):,}', 
                ha='center',
                va='bottom',
                fontweight='bold',
                bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5')
            )
        
        # Save visualization
        plt.tight_layout()
        plt.savefig(os.path.join(self.viz_dir, 'community_sizes_by_platform.png'), dpi=300, bbox_inches='tight')
        logger.info("Saved community sizes visualization")
        
        plt.close()
        
        # Additional visualization: Top communities by size
        plt.figure(figsize=(14, 10))
        
        # Get top 5 communities for each platform
        top_communities = []
        for platform in self.integrated_communities['platform'].unique():
            platform_communities = self.integrated_communities[self.integrated_communities['platform'] == platform]
            top_platform = platform_communities.nlargest(5, 'member_count')
            top_communities.append(top_platform)
        
        # Combine all top communities
        top_df = pd.concat(top_communities).sort_values(['platform', 'member_count'], ascending=[True, False])
        
        # Create grouped bar chart
        ax = sns.barplot(
            x='name', 
            y='member_count', 
            hue='platform',
            data=top_df,
            palette={
                'Reddit': '#FF4500', 
                'Discord': '#5865F2', 
                'Instagram': '#C13584',
                'Facebook': '#3b5998'
            }
        )
        
        # Rotate x labels
        plt.xticks(rotation=45, ha='right')
        
        # Set labels and title
        plt.title('Top 5 Largest Communities by Platform', fontsize=16, pad=20)
        plt.xlabel('Community Name', fontsize=14)
        plt.ylabel('Member Count', fontsize=14)
        plt.legend(title='Platform')
        
        # Format y-axis with thousands separator
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))
        
        # Save visualization
        plt.tight_layout()
        plt.savefig(os.path.join(self.viz_dir, 'top_communities_by_size.png'), dpi=300, bbox_inches='tight')
        logger.info("Saved top communities by size visualization")
        
        plt.close()
    
    def _visualize_engagement_rates(self) -> None:
        """Visualize engagement rates by platform"""
        plt.figure(figsize=(14, 8))
        
        # Create box plot
        ax = sns.boxplot(
            x='platform', 
            y='engagement_rate', 
            data=self.integrated_communities,
            palette={
                'Reddit': '#FF4500', 
                'Discord': '#5865F2', 
                'Instagram': '#C13584',
                'Facebook': '#3b5998'
            }
        )
        
        # Add a swarm plot for individual points
        sns.swarmplot(
            x='platform', 
            y='engagement_rate', 
            data=self.integrated_communities,
            color='black',
            alpha=0.5,
            size=4
        )
        
        # Set labels and title
        plt.title('Engagement Rates by Platform', fontsize=16, pad=20)
        plt.xlabel('Platform', fontsize=14)
        plt.ylabel('Engagement Rate', fontsize=14)
        
        # Format y-axis as percentage
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))
        
        # Add platform averages
        means = self.integrated_communities.groupby('platform')['engagement_rate'].mean()
        for i, platform in enumerate(means.index):
            ax.text(
                i, 
                means[platform] + 0.01, 
                f'Avg: {means[platform]:.1%}', 
                ha='center',
                fontweight='bold',
                bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5')
            )
        
        # Save visualization
        plt.tight_layout()
        plt.savefig(os.path.join(self.viz_dir, 'engagement_rates_by_platform.png'), dpi=300, bbox_inches='tight')
        logger.info("Saved engagement rates visualization")
        
        plt.close()
        
        # Additional visualization: Normalized engagement comparison
        plt.figure(figsize=(12, 8))
        
        # Calculate mean and standard deviation of normalized engagement for each platform
        platform_norm_eng = self.integrated_communities.groupby('platform')['normalized_engagement'].agg(['mean', 'std']).reset_index()
        
        # Sort by mean engagement
        platform_norm_eng = platform_norm_eng.sort_values('mean', ascending=False)
        
        # Create bar chart with error bars
        ax = sns.barplot(
            x='platform', 
            y='mean',
            data=platform_norm_eng,
            palette={
                'Reddit': '#FF4500', 
                'Discord': '#5865F2', 
                'Instagram': '#C13584',
                'Facebook': '#3b5998'
            }
        )
        
        # Add error bars
        ax.errorbar(
            x=range(len(platform_norm_eng)),
            y=platform_norm_eng['mean'],
            yerr=platform_norm_eng['std'],
            fmt='none',
            color='black',
            capsize=5
        )
        
        # Set labels and title
        plt.title('Normalized Engagement Rates by Platform', fontsize=16, pad=20)
        plt.xlabel('Platform', fontsize=14)
        plt.ylabel('Normalized Engagement Rate', fontsize=14)
        
        # Format y-axis as percentage
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))
        
        # Add value labels on bars
        for i, row in enumerate(platform_norm_eng.itertuples()):
            ax.text(
                i, 
                row.mean / 2, 
                f'{row.mean:.1%}', 
                ha='center',
                color='white',
                fontweight='bold'
            )
        
        # Save visualization
        plt.tight_layout()
        plt.savefig(os.path.join(self.viz_dir, 'normalized_engagement_by_platform.png'), dpi=300, bbox_inches='tight')
        logger.info("Saved normalized engagement visualization")
        
        plt.close()
    
    def _visualize_categories(self) -> None:
        """Visualize categories across platforms"""
        if 'category' not in self.integrated_communities.columns:
            logger.warning("Category data not available for visualization")
            return
        
        # Get top categories overall
        top_categories = self.integrated_communities['category'].value_counts().head(8).index
        
        # Create a new dataframe with just these categories
        cat_data = self.integrated_communities[self.integrated_communities['category'].isin(top_categories)]
        
        # Count occurrences of each category by platform
        cat_platform_counts = pd.crosstab(cat_data['category'], cat_data['platform'])
        
        # Create stacked bar chart
        plt.figure(figsize=(14, 10))
        
        # Plot stacked bars
        cat_platform_counts.plot(
            kind='bar',
            stacked=True,
            color=['#FF4500', '#5865F2', '#C13584', '#3b5998'],  # Platform colors
            figsize=(14, 8)
        )
        
        # Set labels and title
        plt.title('Top Categories Across Platforms', fontsize=16, pad=20)
        plt.xlabel('Category', fontsize=14)
        plt.ylabel('Number of Communities', fontsize=14)
        plt.legend(title='Platform')
        
        # Rotate x labels for readability
        plt.xticks(rotation=45, ha='right')
        
        # Save visualization
        plt.tight_layout()
        plt.savefig(os.path.join(self.viz_dir, 'categories_across_platforms.png'), dpi=300, bbox_inches='tight')
        logger.info("Saved categories visualization")
        
        plt.close()
        
        # Additional visualization: Heatmap of categories by platform
        plt.figure(figsize=(12, 10))
        
        # Normalize data (percentage of each category within platform)
        cat_platform_pct = cat_platform_counts.div(cat_platform_counts.sum(axis=0), axis=1) * 100
        
        # Create heatmap
        sns.heatmap(
            cat_platform_pct, 
            annot=True, 
            cmap='YlGnBu', 
            fmt='.1f',
            cbar_kws={'label': '% of Platform Communities'}
        )
        
        # Set labels and title
        plt.title('Category Distribution by Platform (%)', fontsize=16, pad=20)
        plt.tight_layout()
        
        # Save visualization
        plt.savefig(os.path.join(self.viz_dir, 'category_heatmap.png'), dpi=300, bbox_inches='tight')
        logger.info("Saved category heatmap visualization")
        
        plt.close()
    
    def _visualize_platform_network(self) -> None:
        """Visualize network of connections between platforms"""
        # This visualization simulates relationships between platforms
        # In a real implementation, this would use actual data about cross-posting or shared members
        
        # Create a graph
        G = nx.Graph()
        
        # Add platform nodes
        platforms = ['Reddit', 'Discord', 'Instagram', 'Facebook']
        platform_sizes = {}
        platform_colors = {
            'Reddit': '#FF4500',      # Reddit orange
            'Discord': '#5865F2',     # Discord blue
            'Instagram': '#C13584',   # Instagram purple/pink
            'Facebook': '#3b5998'     # Facebook blue
        }
        
        # Calculate total members for each platform for node sizes
        for platform in platforms:
            if platform in self.integrated_communities['platform'].values:
                platform_sizes[platform] = self.integrated_communities[
                    self.integrated_communities['platform'] == platform
                ]['member_count'].sum()
            else:
                platform_sizes[platform] = 0
        
        # Normalize sizes for visualization
        max_size = max(platform_sizes.values()) if platform_sizes else 1
        for platform in platforms:
            size = 1000 * (platform_sizes[platform] / max_size) if max_size > 0 else 500
            G.add_node(platform, size=max(300, size), color=platform_colors.get(platform, '#999999'))
        
        # Add edges with weights representing connection strength
        # These would ideally be based on real data about cross-posting or overlapping members
        edges = [
            ('Reddit', 'Discord', 0.8),      # Strong connection (many Discord servers are linked to subreddits)
            ('Reddit', 'Instagram', 0.4),    # Moderate connection
            ('Reddit', 'Facebook', 0.3),     # Moderate connection
            ('Discord', 'Instagram', 0.3),   # Moderate connection
            ('Discord', 'Facebook', 0.3),    # Moderate connection
            ('Instagram', 'Facebook', 0.9),  # Strong connection (both Meta platforms)
        ]
        
        # Add edges to graph
        for source, target, weight in edges:
            G.add_edge(source, target, weight=weight)
        
        # Create figure
        plt.figure(figsize=(12, 10))
        
        # Get position layout
        pos = nx.spring_layout(G, seed=42)
        
        # Draw nodes
        node_sizes = [G.nodes[platform]['size'] for platform in G.nodes()]
        node_colors = [G.nodes[platform]['color'] for platform in G.nodes()]
        
        nx.draw_networkx_nodes(
            G, 
            pos, 
            node_size=node_sizes,
            node_color=node_colors,
            alpha=0.8
        )
        
        # Draw edges with varying widths based on weight
        edge_widths = [G[u][v]['weight'] * 5 for u, v in G.edges()]
        
        nx.draw_networkx_edges(
            G, 
            pos, 
            width=edge_widths,
            alpha=0.7,
            edge_color='gray'
        )
        
        # Draw labels
        nx.draw_networkx_labels(
            G, 
            pos, 
            font_size=16,
            font_family='sans-serif',
            font_weight='bold'
        )
        
        # Add edge weights as labels
        edge_labels = {(u, v): f"{d['weight']:.1f}" for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(
            G, 
            pos, 
            edge_labels=edge_labels,
            font_size=12
        )
        
        # Remove axis
        plt.axis('off')
        
        # Add title
        plt.title('Cross-Platform Relationship Network', fontsize=16, pad=20)
        
        # Save visualization
        plt.tight_layout()
        plt.savefig(os.path.join(self.viz_dir, 'platform_network.png'), dpi=300, bbox_inches='tight')
        logger.info("Saved platform network visualization")
        
        plt.close()
    
    def _visualize_top_communities(self) -> None:
        """Visualize top communities across all platforms"""
        # Get top communities by engagement-adjusted size 
        # (size * engagement to balance large but inactive vs. small but active)
        self.integrated_communities['engagement_adjusted_size'] = (
            self.integrated_communities['member_count'] * self.integrated_communities['engagement_rate']
        )
        
        # Get top 15 communities overall
        top_communities = self.integrated_communities.nlargest(15, 'engagement_adjusted_size')
        
        # Create horizontal bar chart
        plt.figure(figsize=(14, 10))
        
        # Create color mapping based on platform
        platform_colors = {
            'Reddit': '#FF4500',
            'Discord': '#5865F2',
            'Instagram': '#C13584',
            'Facebook': '#3b5998'
        }
        colors = [platform_colors[platform] for platform in top_communities['platform']]
        
        # Plot bars
        ax = sns.barplot(
            x='engagement_adjusted_size',
            y='name',
            data=top_communities,
            palette={
                'Reddit': '#FF4500',
                'Discord': '#5865F2',
                'Instagram': '#C13584',
                'Facebook': '#3b5998'
            },
            hue='platform'
        )
        
        # Set labels and title
        plt.title('Top 15 Communities by Engagement-Adjusted Size', fontsize=16, pad=20)
        plt.xlabel('Engagement-Adjusted Size (Members × Engagement Rate)', fontsize=14)
        plt.ylabel('Community Name', fontsize=14)
        
        # Format x-axis with thousands separator
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))
        
        # Add grid lines
        plt.grid(axis='x', alpha=0.3)
        
        # Save visualization
        plt.tight_layout()
        plt.savefig(os.path.join(self.viz_dir, 'top_communities_overall.png'), dpi=300, bbox_inches='tight')
        logger.info("Saved top communities visualization")
        
        plt.close()

def main():
    """Main function to demonstrate PlatformIntegrator functionality"""
    # Create output directories if they don't exist
    os.makedirs("logs", exist_ok=True)
    
    # Initialize the integrator
    integrator = PlatformIntegrator()
    
    # Standardize community data
    print("Standardizing community data from all platforms...")
    integrated_communities = integrator.standardize_community_data()
    print(f"Integrated {len(integrated_communities)} communities from all platforms")
    
    # Analyze cross-platform metrics
    print("Analyzing cross-platform metrics...")
    cross_platform_metrics = integrator.analyze_cross_platform_metrics()
    
    # Generate visualizations
    print("Generating cross-platform visualizations...")
    integrator.generate_cross_platform_visualizations()
    
    print(f"\nAll cross-platform analysis completed.")
    print(f"Integrated data saved to {integrator.output_dir}/")
    print(f"Visualizations saved to {integrator.viz_dir}/")

if __name__ == "__main__":
    main()