#!/usr/bin/env python3
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def main():
    print("Running expanded Facebook visualizer...")
    
    # Create output directory
    os.makedirs("visualizations/facebook", exist_ok=True)
    
    # Load data
    try:
        groups_df = pd.read_csv("scraped_data/facebook/groups.csv")
        posts_df = pd.read_csv("scraped_data/facebook/posts.csv")
        members_df = pd.read_csv("scraped_data/facebook/members.csv")
        
        print(f"Loaded {len(groups_df)} groups, {len(posts_df)} posts, and {len(members_df)} members")
        
        # Visualization 1: Group Categories
        plt.figure(figsize=(12, 8))
        category_counts = groups_df['category'].value_counts().head(15)  # Top 15 categories
        sns.barplot(x=category_counts.values, y=category_counts.index, palette='viridis')
        plt.title('Top 15 Facebook Group Categories')
        plt.xlabel('Number of Groups')
        plt.tight_layout()
        plt.savefig("visualizations/facebook/group_categories.png")
        print("Created group categories visualization")
        plt.close()
        
        # Visualization 2: Group Sizes
        plt.figure(figsize=(12, 8))
        sns.histplot(groups_df['member_count'], bins=20, kde=True)
        plt.title('Distribution of Facebook Group Sizes')
        plt.xlabel('Number of Members')
        plt.ylabel('Count')
        plt.tight_layout()
        plt.savefig("visualizations/facebook/group_sizes.png")
        print("Created group sizes visualization")
        plt.close()
        
        # Visualization 3: Top 10 Largest Groups
        plt.figure(figsize=(12, 8))
        top_groups = groups_df.nlargest(10, 'member_count')
        sns.barplot(x='member_count', y='name', data=top_groups, palette='viridis')
        plt.title('Top 10 Largest Facebook Groups')
        plt.xlabel('Member Count')
        plt.tight_layout()
        plt.savefig("visualizations/facebook/top_groups.png")
        print("Created top groups visualization")
        plt.close()
        
        # Visualization 4: Post Types
        if 'post_type' in posts_df.columns:
            plt.figure(figsize=(10, 10))
            post_types = posts_df['post_type'].value_counts()
            plt.pie(post_types.values, labels=post_types.index, autopct='%1.1f%%', startangle=90, 
                   colors=sns.color_palette('viridis', len(post_types)))
            plt.axis('equal')
            plt.title('Distribution of Post Types')
            plt.tight_layout()
            plt.savefig("visualizations/facebook/post_types.png")
            print("Created post types visualization")
            plt.close()
        
        # Visualization 5: Member Types
        if 'member_type' in members_df.columns:
            plt.figure(figsize=(12, 8))
            member_types = members_df['member_type'].value_counts()
            sns.barplot(x=member_types.values, y=member_types.index, palette='viridis')
            plt.title('Facebook Group Member Types')
            plt.xlabel('Number of Members')
            plt.tight_layout()
            plt.savefig("visualizations/facebook/member_types.png")
            print("Created member types visualization")
            plt.close()
        
        # Visualization 6: School Focus Distribution (if available)
        if 'school_focus' in groups_df.columns:
            plt.figure(figsize=(10, 10))
            focus_counts = groups_df['school_focus'].value_counts()
            plt.pie(focus_counts.values, labels=focus_counts.index, autopct='%1.1f%%',
                  startangle=90, colors=sns.color_palette('viridis', len(focus_counts)))
            plt.axis('equal')
            plt.title('Distribution of Facebook Groups by Educational Focus')
            plt.tight_layout()
            plt.savefig("visualizations/facebook/school_focus_distribution.png")
            print("Created school focus distribution visualization")
            plt.close()
        
        # Visualization 7: Engagement by Post Type (if available)
        if 'post_type' in posts_df.columns and 'likes' in posts_df.columns and 'comments' in posts_df.columns:
            plt.figure(figsize=(14, 8))
            
            # Calculate average engagement for each post type
            engagement_by_type = posts_df.groupby('post_type').agg({
                'likes': 'mean',
                'comments': 'mean'
            }).reset_index()
            
            # Sort by total engagement
            engagement_by_type['total_engagement'] = engagement_by_type['likes'] + engagement_by_type['comments']
            engagement_by_type = engagement_by_type.sort_values('total_engagement', ascending=False)
            
            # Create grouped bar chart
            x = np.arange(len(engagement_by_type))
            width = 0.35
            
            fig, ax = plt.subplots(figsize=(14, 8))
            ax.bar(x - width/2, engagement_by_type['likes'], width, label='Likes', color='#3b5998')
            ax.bar(x + width/2, engagement_by_type['comments'], width, label='Comments', color='#6eb5ff')
            
            # Add labels and title
            ax.set_title('Average Engagement by Post Type', fontsize=16)
            ax.set_xticks(x)
            ax.set_xticklabels(engagement_by_type['post_type'])
            ax.set_ylabel('Average Count')
            ax.legend()
            
            plt.tight_layout()
            plt.savefig("visualizations/facebook/post_type_engagement.png")
            print("Created post type engagement visualization")
            plt.close()
        
        # Visualization 8: Activity Levels (if available)
        if 'activity_level' in members_df.columns:
            plt.figure(figsize=(12, 7))
            
            # Define activity level order if possible
            try:
                activity_order = ['high', 'medium', 'low', 'inactive']
                activity_counts = members_df['activity_level'].value_counts().reindex(activity_order)
            except:
                activity_counts = members_df['activity_level'].value_counts()
            
            # Plot bar chart
            colors = ['#4CAF50', '#2196F3', '#FFC107', '#F44336']  # Green, Blue, Yellow, Red
            ax = sns.barplot(x=activity_counts.index, y=activity_counts.values, palette=colors)
            
            # Add percentage labels
            total = activity_counts.sum()
            for i, count in enumerate(activity_counts.values):
                percentage = 100 * count / total
                ax.text(i, count + 0.1, f"{percentage:.1f}%", ha='center')
            
            # Set labels and title
            plt.title('Member Activity Level Distribution', fontsize=16)
            plt.xlabel('Activity Level')
            plt.ylabel('Number of Members')
            plt.tight_layout()
            
            plt.savefig("visualizations/facebook/member_activity_distribution.png")
            print("Created member activity distribution visualization")
            plt.close()
        
        # Visualization 9: Outreach Potential (if available)
        if 'outreach_potential' in groups_df.columns:
            plt.figure(figsize=(14, 8))
            
            # Create scatter plot
            sns.scatterplot(
                x='member_count', 
                y='outreach_potential', 
                data=groups_df,
                hue='category',
                size='post_frequency' if 'post_frequency' in groups_df.columns else None,
                sizes=(50, 300),
                alpha=0.7
            )
            
            # Set labels and title
            plt.title('Outreach Potential vs. Group Size', fontsize=16)
            plt.xlabel('Number of Members')
            plt.ylabel('Outreach Potential (0-10)')
            plt.xscale('log')  # Log scale for member count
            plt.grid(True, alpha=0.3)
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            
            plt.savefig("visualizations/facebook/outreach_vs_size.png")
            print("Created outreach potential vs. size visualization")
            plt.close()
        
        # Visualization 10: Top 10 by Outreach Potential (if available)
        if 'outreach_potential' in groups_df.columns:
            plt.figure(figsize=(14, 8))
            
            # Get top 10 groups by outreach potential
            top_outreach = groups_df.nlargest(10, 'outreach_potential')
            
            # Create horizontal bar chart
            ax = sns.barplot(x='outreach_potential', y='name', data=top_outreach, palette='viridis')
            
            # Add category labels to bars
            for i, (_, row) in enumerate(top_outreach.iterrows()):
                ax.text(row['outreach_potential'] + 0.1, i, row['category'], va='center')
            
            # Set labels and title
            plt.title('Top 10 Groups by Outreach Potential', fontsize=16)
            plt.xlabel('Outreach Potential Score')
            plt.ylabel('Group Name')
            plt.tight_layout()
            
            plt.savefig("visualizations/facebook/top_outreach_groups.png")
            print("Created top outreach groups visualization")
            plt.close()
            
        print("Expanded visualization complete! Created visualizations in visualizations/facebook/")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()