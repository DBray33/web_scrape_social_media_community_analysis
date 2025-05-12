#!/usr/bin/env python3
"""
analyze_instagram_data.py - Script to analyze and visualize Instagram community data.
Part of Web Scraping Portfolio project for job interview preparation.
"""

import os
import glob
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# Set up visualization style
sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

def load_instagram_data():
    """
    Load the most recent Instagram community data.
    
    Returns:
        Pandas DataFrame with Instagram community information
    """
    # Find the most recent filtered communities CSV file
    csv_files = glob.glob('scraped_data/instagram/instagram_communities_filtered_*.csv')
    
    if not csv_files:
        print("No filtered Instagram community data files found!")
        
        # Check if raw data exists
        raw_files = glob.glob('scraped_data/instagram/instagram_communities_raw_*.csv')
        if not raw_files:
            print("No Instagram data files found at all!")
            return None
            
        latest_file = max(raw_files, key=os.path.getmtime)
        print(f"Loading raw Instagram data from {latest_file}")
    else:
        latest_file = max(csv_files, key=os.path.getmtime)
        print(f"Loading filtered Instagram data from {latest_file}")
    
    # Load the data
    df = pd.read_csv(latest_file)
    print(f"Loaded {len(df)} Instagram communities")
    
    return df

def clean_and_prepare_data(df):
    """
    Clean and prepare the Instagram community data for analysis.
    
    Args:
        df: Pandas DataFrame with raw Instagram community data
        
    Returns:
        Cleaned and prepared DataFrame
    """
    if df is None or df.empty:
        print("No data to prepare")
        return None
        
    # Make a copy to avoid modifying the original
    cleaned_df = df.copy()
    
    # Ensure numeric columns are numeric
    numeric_cols = ['followers', 'posts', 'engagement_rate', 'relevance_score']
    for col in numeric_cols:
        if col in cleaned_df.columns:
            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
    
    # Fill missing values with 0
    cleaned_df = cleaned_df.fillna(0)
    
    # Create bins for follower counts
    bins = [0, 5000, 10000, 50000, 100000, float('inf')]
    labels = ['Micro (<5K)', 'Small (5K-10K)', 'Medium (10K-50K)', 'Large (50K-100K)', 'Massive (>100K)']
    cleaned_df['size_category'] = pd.cut(cleaned_df['followers'], bins=bins, labels=labels)
    
    # Calculate engagement score
    if 'engagement_rate' in cleaned_df.columns and 'followers' in cleaned_df.columns:
        cleaned_df['engagement_score'] = cleaned_df['engagement_rate'] * np.log(cleaned_df['followers'])
    
    # Convert datetime strings to datetime objects if they exist
    if 'collected_at' in cleaned_df.columns:
        cleaned_df['collected_at'] = pd.to_datetime(cleaned_df['collected_at'], errors='coerce')
    
    return cleaned_df

def create_visualizations(df):
    """
    Create visualizations for Instagram community data.
    
    Args:
        df: Pandas DataFrame with cleaned Instagram community data
    """
    if df is None or df.empty:
        print("No data to visualize")
        return
        
    # Create output directory
    os.makedirs('visualizations/instagram', exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d")
    
    # 1. Distribution of community sizes
    plt.figure(figsize=(12, 8))
    sns.histplot(data=df, x='followers', hue='community_type', bins=30, log_scale=True)
    plt.title('Distribution of Instagram Community Sizes (Log Scale)')
    plt.xlabel('Follower Count (log scale)')
    plt.ylabel('Number of Communities')
    plt.tight_layout()
    plt.savefig(f'visualizations/instagram/community_size_dist_{timestamp}.png', dpi=300)
    plt.close()
    print("Created visualization: community_size_dist.png")
    
    # 2. Community type distribution
    plt.figure(figsize=(10, 8))
    community_counts = df['community_type'].value_counts()
    
    # Plot as a pie chart
    plt.pie(
        community_counts, 
        labels=None,
        autopct='%1.1f%%', 
        startangle=90,
        colors=['#3498db', '#e74c3c', '#2ecc71']
    )
    plt.legend(
        community_counts.index,
        title="Community Types",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1)
    )
    plt.axis('equal')
    plt.title('Distribution of Instagram Community Types')
    plt.tight_layout()
    plt.savefig(f'visualizations/instagram/community_types_{timestamp}.png', dpi=300)
    plt.close()
    print("Created visualization: community_types.png")
    
    # 3. Engagement rate vs. follower count
    plt.figure(figsize=(12, 8))
    sns.scatterplot(
        data=df, 
        x='followers', 
        y='engagement_rate',
        hue='community_type',
        size='posts', 
        sizes=(50, 300),
        alpha=0.7
    )
    plt.xscale('log')
    plt.title('Engagement Rate vs. Community Size')
    plt.xlabel('Followers (log scale)')
    plt.ylabel('Engagement Rate')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'visualizations/instagram/engagement_vs_size_{timestamp}.png', dpi=300)
    plt.close()
    print("Created visualization: engagement_vs_size.png")
    
    # 4. Top 15 most relevant communities
    plt.figure(figsize=(14, 10))
    top_communities = df.nlargest(15, 'relevance_score')
    top_communities = top_communities.sort_values('relevance_score')
    
    colors = {
        'Student-focused': '#3498db',
        'Professional-focused': '#e74c3c'
    }
    
    bar_colors = [colors.get(t, '#95a5a6') for t in top_communities['community_type']]
    
    bars = plt.barh(top_communities['username'], top_communities['relevance_score'], color=bar_colors)
    plt.xlabel('Relevance Score')
    plt.ylabel('Username')
    plt.title('Top 15 Most Relevant Instagram Communities')
    
    # Add follower count annotations
    for i, bar in enumerate(bars):
        followers = f"{int(top_communities.iloc[i]['followers']):,}"
        plt.text(
            bar.get_width() + 0.3,
            bar.get_y() + bar.get_height()/2,
            f"Followers: {followers}",
            va='center'
        )
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=colors['Student-focused'], label='Student-focused'),
        Patch(facecolor=colors['Professional-focused'], label='Professional-focused')
    ]
    plt.legend(handles=legend_elements, loc='lower right')
    
    plt.tight_layout()
    plt.savefig(f'visualizations/instagram/top_communities_{timestamp}.png', dpi=300)
    plt.close()
    print("Created visualization: top_communities.png")
    
    # 5. Posts vs. engagement score by community type
    plt.figure(figsize=(12, 8))
    
    # Only include this visualization if engagement_score exists
    if 'engagement_score' in df.columns:
        sns.scatterplot(
            data=df,
            x='posts',
            y='engagement_score',
            hue='community_type',
            size='followers',
            sizes=(50, 300),
            alpha=0.7
        )
        plt.title('Content Volume vs. Engagement Impact by Community Type')
        plt.xlabel('Number of Posts')
        plt.ylabel('Engagement Impact (Rate × log(Followers))')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'visualizations/instagram/posts_vs_engagement_{timestamp}.png', dpi=300)
        plt.close()
        print("Created visualization: posts_vs_engagement.png")
    
    print(f"Created visualizations in the visualizations/instagram directory")

def generate_summary_report(df):
    """
    Generate a summary report of the Instagram community data.
    
    Args:
        df: Pandas DataFrame with cleaned Instagram community data
        
    Returns:
        Summary report as a string
    """
    if df is None or df.empty:
        return "No data available for summary report."
    
    # Calculate summary statistics
    total_communities = len(df)
    student_focused = len(df[df['community_type'] == 'Student-focused'])
    professional_focused = len(df[df['community_type'] == 'Professional-focused'])
    
    total_followers = df['followers'].sum()
    avg_followers = df['followers'].mean()
    median_followers = df['followers'].median()
    max_followers = df['followers'].max()
    min_followers = df['followers'].min()
    
    largest_community = df.loc[df['followers'].idxmax()]['username']
    most_engaged = df.loc[df['engagement_rate'].idxmax()]['username']
    avg_engagement = df['engagement_rate'].mean() * 100  # Convert to percentage
    
    # Format the report
    report = f"""
Instagram Communities Analysis Report
====================================
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Summary Statistics:
------------------
Total Instagram communities analyzed: {total_communities}
Student-focused communities: {student_focused} ({student_focused/total_communities*100:.1f}%)
Professional-focused communities: {professional_focused} ({professional_focused/total_communities*100:.1f}%)

Total followers across all communities: {int(total_followers):,}
Average followers per community: {int(avg_followers):,}
Median followers per community: {int(median_followers):,}
Largest community: {largest_community} with {int(max_followers):,} followers
Smallest community: {int(min_followers):,} followers

Engagement Metrics:
-----------------
Average engagement rate: {avg_engagement:.2f}%
Most engaging community: {most_engaged} with {df.loc[df['engagement_rate'].idxmax()]['engagement_rate']*100:.2f}% engagement

Size Distribution:
----------------
"""
    
    # Add size distribution breakdown
    size_distribution = df['size_category'].value_counts().sort_index()
    for category, count in size_distribution.items():
        percentage = (count / total_communities) * 100
        report += f"{category}: {count} communities ({percentage:.1f}%)\n"
    
    # Add top communities section
    report += "\nTop 5 Most Relevant Communities:\n"
    report += "-----------------------------\n"
    
    top_5 = df.nlargest(5, 'relevance_score')
    for i, (_, row) in enumerate(top_5.iterrows()):
        report += f"{i+1}. {row['username']} ({row['community_type']})\n"
        report += f"   Followers: {int(row['followers']):,}, Posts: {int(row['posts'])}\n"
        report += f"   Engagement Rate: {row['engagement_rate']*100:.2f}%\n"
        if 'description' in row and row['description']:
            report += f"   Description: {row['description'][:100]}...\n"
        report += "\n"
    
    # Save report to file
    timestamp = datetime.now().strftime("%Y%m%d")
    report_path = f'scraped_data/instagram/instagram_analysis_report_{timestamp}.txt'
    
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"Saved analysis report to {report_path}")
    return report

def main():
    """Main function to run the Instagram data analysis."""
    print("Starting Instagram data analysis...")
    
    # Load the data
    df = load_instagram_data()
    
    if df is None or df.empty:
        print("No Instagram data available to analyze.")
        return
    
    # Clean and prepare the data
    cleaned_df = clean_and_prepare_data(df)
    
    if cleaned_df is None or cleaned_df.empty:
        print("Error cleaning data.")
        return
    
    # Create visualizations
    create_visualizations(cleaned_df)
    
    # Generate summary report
    report = generate_summary_report(cleaned_df)
    print("\nAnalysis Summary:")
    print(report)
    
    # Save processed data
    timestamp = datetime.now().strftime("%Y%m%d")
    processed_path = f'scraped_data/instagram/processed_instagram_data_{timestamp}.csv'
    cleaned_df.to_csv(processed_path, index=False)
    print(f"Saved processed data to {processed_path}")
    
    print("\nInstagram data analysis completed successfully!")

if __name__ == "__main__":
    main()