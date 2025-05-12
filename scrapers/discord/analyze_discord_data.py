#!/usr/bin/env python3
"""
analyze_discord_data.py - Script to analyze and visualize Discord community data.
Part of Web Scraping Portfolio project for job interview preparation.
"""

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# Set up visualization style
sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

def load_discord_data():
    """
    Load the most recent Discord community data.
    
    Returns:
        Pandas DataFrame with Discord community information
    """
    # Find the most recent CSV file
    csv_files = glob.glob('scraped_data/discord/discord_communities_*.csv')
    if not csv_files:
        print("No Discord community data files found!")
        return None
    
    latest_file = max(csv_files, key=os.path.getmtime)
    print(f"Loading Discord data from {latest_file}")
    
    # Load the data
    df = pd.read_csv(latest_file)
    print(f"Loaded {len(df)} Discord communities")
    
    return df

def clean_and_prepare_data(df):
    """
    Clean and prepare the Discord community data for analysis.
    
    Args:
        df: Pandas DataFrame with raw Discord community data
        
    Returns:
        Cleaned and prepared DataFrame
    """
    if df is None or df.empty:
        print("No data to prepare")
        return None
        
    # Make a copy to avoid modifying the original
    cleaned_df = df.copy()
    
    # Convert member counts to numeric, handling NaN values
    cleaned_df['member_count'] = pd.to_numeric(cleaned_df['member_count'], errors='coerce')
    cleaned_df['online_count'] = pd.to_numeric(cleaned_df['online_count'], errors='coerce')
    
    # Fill missing values with 0
    cleaned_df['member_count'] = cleaned_df['member_count'].fillna(0)
    cleaned_df['online_count'] = cleaned_df['online_count'].fillna(0)
    
    # Create a activity ratio column (online/total members)
    cleaned_df['activity_ratio'] = cleaned_df.apply(
        lambda row: row['online_count'] / row['member_count'] if row['member_count'] > 0 else 0, 
        axis=1
    )
    
    # Create a size category column
    bins = [0, 100, 1000, 10000, 100000, float('inf')]
    labels = ['Tiny (<100)', 'Small (100-1K)', 'Medium (1K-10K)', 'Large (10K-100K)', 'Massive (>100K)']
    cleaned_df['size_category'] = pd.cut(cleaned_df['member_count'], bins=bins, labels=labels)
    
    # Convert datetime strings to datetime objects
    cleaned_df['collected_at'] = pd.to_datetime(cleaned_df['collected_at'], errors='coerce')
    
    return cleaned_df

def create_visualizations(df):
    """
    Create visualizations for Discord community data.
    
    Args:
        df: Pandas DataFrame with cleaned Discord community data
    """
    if df is None or df.empty:
        print("No data to visualize")
        return
        
    os.makedirs('visualizations', exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d")
    
    # 1. Distribution of server sizes
    plt.figure(figsize=(12, 8))
    sns.histplot(data=df, x='member_count', bins=30, log_scale=True)
    plt.title('Distribution of Discord Server Sizes (Log Scale)')
    plt.xlabel('Member Count (log scale)')
    plt.ylabel('Number of Servers')
    plt.tight_layout()
    plt.savefig(f'visualizations/discord_server_size_dist_{timestamp}.png')
    plt.close()
    
    # 2. Server size categories
    plt.figure(figsize=(12, 8))
    size_counts = df['size_category'].value_counts().sort_index()
    ax = size_counts.plot(kind='bar', color='skyblue')
    plt.title('Discord Server Size Categories')
    plt.xlabel('Size Category')
    plt.ylabel('Number of Servers')
    for i, v in enumerate(size_counts):
        ax.text(i, v + 0.1, str(v), ha='center')
    plt.tight_layout()
    plt.savefig(f'visualizations/discord_size_categories_{timestamp}.png')
    plt.close()
    
    # 3. Online ratio vs. server size
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=df, x='member_count', y='activity_ratio', hue='size_category', 
                   alpha=0.7, s=100)
    plt.title('Activity Ratio vs. Server Size')
    plt.xlabel('Member Count (log scale)')
    plt.ylabel('Activity Ratio (Online/Total)')
    plt.xscale('log')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'visualizations/discord_activity_vs_size_{timestamp}.png')
    plt.close()
    
    # 4. Top 10 largest communities
    plt.figure(figsize=(14, 10))
    top_servers = df.nlargest(10, 'member_count')
    bars = sns.barplot(data=top_servers, y='server_name', x='member_count', 
                     palette='viridis', orient='h')
    plt.title('Top 10 Largest Discord Communities')
    plt.xlabel('Member Count')
    plt.ylabel('Server Name')
    # Add member count labels to the bars
    for i, v in enumerate(top_servers['member_count']):
        bars.text(v + 100, i, f"{int(v):,}", va='center')
    plt.tight_layout()
    plt.savefig(f'visualizations/discord_top10_largest_{timestamp}.png')
    plt.close()
    
    # 5. Correlation between online and total members
    plt.figure(figsize=(12, 8))
    sns.regplot(data=df, x='member_count', y='online_count', 
               scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
    plt.title('Correlation Between Total Members and Online Members')
    plt.xlabel('Total Member Count')
    plt.ylabel('Online Member Count')
    plt.tight_layout()
    plt.savefig(f'visualizations/discord_online_correlation_{timestamp}.png')
    plt.close()
    
    print(f"Created 5 visualizations in the visualizations directory")

def generate_summary_report(df):
    """
    Generate a summary report of the Discord community data.
    
    Args:
        df: Pandas DataFrame with cleaned Discord community data
        
    Returns:
        Summary report as a string
    """
    if df is None or df.empty:
        return "No data available for summary report."
    
    # Calculate summary statistics
    total_servers = len(df)
    total_members = df['member_count'].sum()
    avg_members = df['member_count'].mean()
    median_members = df['member_count'].median()
    max_members = df['member_count'].max()
    min_members = df['member_count'].min()
    
    largest_server = df.loc[df['member_count'].idxmax()]['server_name']
    avg_online_ratio = df['activity_ratio'].mean() * 100  # Convert to percentage
    
    size_distribution = df['size_category'].value_counts().sort_index()
    
    # Format the report
    report = f"""
Discord Communities Analysis Report
==================================
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Summary Statistics:
------------------
Total Discord servers analyzed: {total_servers}
Total members across all servers: {int(total_members):,}
Average members per server: {avg_members:.1f}
Median members per server: {median_members:.1f}
Largest server: {largest_server} with {int(max_members):,} members
Smallest server: {int(min_members):,} members
Average online activity ratio: {avg_online_ratio:.1f}%

Server Size Distribution:
-----------------------
"""
    
    for category, count in size_distribution.items():
        percentage = (count / total_servers) * 100
        report += f"{category}: {count} servers ({percentage:.1f}%)\n"
    
    # Add correlation information
    corr = df[['member_count', 'online_count']].corr().iloc[0, 1]
    report += f"\nCorrelation between total members and online members: {corr:.3f}\n"
    
    # Save report to file
    timestamp = datetime.now().strftime("%Y%m%d")
    report_path = f'scraped_data/discord/discord_analysis_report_{timestamp}.txt'
    
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"Saved analysis report to {report_path}")
    return report

def main():
    """Main function to run the Discord data analysis."""
    print("Starting Discord data analysis...")
    
    # Load the data
    df = load_discord_data()
    
    if df is None or df.empty:
        print("No Discord data available to analyze.")
        return
    
    # Clean and prepare the data
    cleaned_df = clean_and_prepare_data(df)
    
    # Create visualizations
    create_visualizations(cleaned_df)
    
    # Generate summary report
    report = generate_summary_report(cleaned_df)
    print("\nAnalysis Summary:")
    print(report)
    
    # Save processed data
    timestamp = datetime.now().strftime("%Y%m%d")
    cleaned_df.to_csv(f'scraped_data/discord/processed_discord_data_{timestamp}.csv', index=False)
    
    print("\nDiscord data analysis completed successfully!")

if __name__ == "__main__":
    main()