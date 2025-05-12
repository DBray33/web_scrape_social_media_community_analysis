"""
Analyze Reddit data to identify the most relevant student and professional communities
"""
import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

def load_data(file_path):
    """Load data from CSV file"""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        return None
    
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} subreddits")
    
    # Check for subreddit column name variations and standardize
    if 'subreddit' in df.columns and 'name' not in df.columns:
        df['name'] = df['subreddit']
    
    # Fill NaN values in description (if it exists)
    if 'description' in df.columns:
        df['description'] = df['description'].fillna('')
    else:
        # Create empty description column if it doesn't exist
        df['description'] = ''
        print("Note: No description column found in data, using empty values")
    
    return df

def better_filter_for_students(df):
    """
    Apply more specific filtering to find truly student/professional focused communities
    """
    # Define keywords that are strong indicators of student/professional communities
    student_keywords = [
        'college', 'university', 'student', 'campus', 'dorm', 
        'study', 'education', 'academic', 'school', 'grad', 
        'undergrad', 'freshman', 'sophomore', 'junior', 'senior',
        'major', 'degree', 'homework', 'thesis', 'professor',
        'class', 'lecturer', 'assignments', 'exam', 'test'
    ]
    
    professional_keywords = [
        'career', 'job', 'profession', 'resume', 'interview',
        'internship', 'salary', 'workplace', 'office', 'corporate',
        'employment', 'hire', 'recruiting', 'professional', 'entry level',
        'engineer', 'programmer', 'developer', 'manager', 'hr',
        'benefits', 'promotion', 'skills', 'linkedin', 'networking'
    ]
    
    # Create a score based on keyword matches in name and description
    df['student_score'] = 0
    df['professional_score'] = 0
    
    # Check for keywords in subreddit name
    for keyword in student_keywords:
        df['student_score'] += df['name'].str.lower().str.contains(keyword, regex=False, na=False).astype(int) * 3
    
    for keyword in professional_keywords:
        df['professional_score'] += df['name'].str.lower().str.contains(keyword, regex=False, na=False).astype(int) * 3
    
    # Check for keywords in description
    for keyword in student_keywords:
        df['student_score'] += df['description'].str.lower().str.contains(keyword, regex=False, na=False).astype(int)
    
    for keyword in professional_keywords:
        df['professional_score'] += df['description'].str.lower().str.contains(keyword, regex=False, na=False).astype(int)
    
    # Calculate total relevance score
    df['relevance_score'] = df['student_score'] + df['professional_score']
    
    # Filter for at least some relevance
    relevant_df = df[df['relevance_score'] > 0].copy()
    
    # If we don't have any relevant communities found, use the original data
    if len(relevant_df) == 0:
        print("No communities matched relevance criteria. Using all communities.")
        relevant_df = df.copy()
        # Assign default scores
        relevant_df['relevance_score'] = 1
        relevant_df['student_score'] = 0
        relevant_df['professional_score'] = 0
    
    # Categorize communities
    conditions = [
        (relevant_df['student_score'] > relevant_df['professional_score']),
        (relevant_df['professional_score'] > relevant_df['student_score']),
        (relevant_df['student_score'] == relevant_df['professional_score'])
    ]
    choices = ['Student-focused', 'Professional-focused', 'Mixed']
    relevant_df['community_type'] = np.select(conditions, choices, default='Other')
    
    # Sort by relevance score and then by subscriber count
    relevant_df = relevant_df.sort_values(by=['relevance_score', 'subscribers'], ascending=[False, False])
    
    print(f"Found {len(relevant_df)} relevant communities")
    print(f"Student-focused: {len(relevant_df[relevant_df['community_type'] == 'Student-focused'])}")
    print(f"Professional-focused: {len(relevant_df[relevant_df['community_type'] == 'Professional-focused'])}")
    print(f"Mixed: {len(relevant_df[relevant_df['community_type'] == 'Mixed'])}")
    
    return relevant_df

def create_visualizations(df):
    """Create visualizations of the data with improved readability"""
    # Create output directory
    os.makedirs('visualizations/reddit', exist_ok=True)
    
    # 1. Top 15 most relevant communities by subscriber count
    plt.figure(figsize=(14, 10))  # Larger figure
    top_n = min(15, len(df))  # Make sure we don't try to plot more than we have
    top_15 = df.head(top_n)
    
    # Handle large numbers better
    if top_15['subscribers'].max() > 1000000:
        divisor = 1000000
        unit = ' million'
    else:
        divisor = 1000
        unit = 'K'
    
    # Sort by subscriber count for better visualization
    top_15 = top_15.sort_values('subscribers', ascending=True)
    
    bars = plt.barh(top_15['name'], top_15['subscribers'] / divisor, color='skyblue')
    plt.xlabel(f'Subscribers ({unit})', fontsize=12)
    plt.ylabel('Subreddit', fontsize=12)
    plt.title('Top Most Relevant Student & Professional Communities', fontsize=16)
    
    # Add subscriber count labels with better spacing
    for i, bar in enumerate(bars):
        # Format subscriber count with commas
        subscriber_count = f"{int(top_15.iloc[i]['subscribers']):,}"
        plt.text(bar.get_width() + (bar.get_width() * 0.03), 
                bar.get_y() + bar.get_height()/2, 
                subscriber_count, 
                va='center', fontsize=10)
    
    # Color-code the bars based on community type
    colors = {'Student-focused': '#3498db', 'Professional-focused': '#e74c3c', 'Mixed': '#2ecc71', 'Other': '#95a5a6'}
    for i, bar in enumerate(bars):
        community_type = top_15.iloc[i]['community_type']
        bar.set_color(colors.get(community_type, '#95a5a6'))
    
    # Add a legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=color, label=ctype)
                      for ctype, color in colors.items() if ctype in df['community_type'].values]
    plt.legend(handles=legend_elements, title='Community Type', loc='lower right')
    
    plt.tight_layout()
    plt.savefig('visualizations/reddit/top_communities.png', dpi=300)
    print("Created visualization: visualizations/reddit/top_communities.png")
    
    # 2. Community type distribution
    plt.figure(figsize=(10, 8))
    community_counts = df['community_type'].value_counts()
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#95a5a6']  # Blue, Red, Green, Grey
    
    # Check if we have data to plot
    if not community_counts.empty:
        wedges, texts, autotexts = plt.pie(
            community_counts, 
            labels=None,  # Remove labels from pie slices
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops={'fontsize': 12}
        )
        
        # Make the percentage text more readable
        for autotext in autotexts:
            autotext.set_fontsize(11)
            autotext.set_fontweight('bold')
            autotext.set_color('white')
        
        # Add a legend instead of labels on the pie
        plt.legend(wedges, community_counts.index,
                 title="Community Types",
                 loc="center left",
                 bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.title('Distribution of Community Types', fontsize=16, pad=20)
        plt.tight_layout()
        plt.savefig('visualizations/reddit/community_types.png', dpi=300)
        print("Created visualization: visualizations/reddit/community_types.png")
    else:
        print("Warning: Not enough data to create community type pie chart")
    
    # 3. Relevance vs. Size scatter plot with better handling of overlapping points
    plt.figure(figsize=(14, 10))
    colors_dict = {
        'Student-focused': '#3498db', 
        'Professional-focused': '#e74c3c', 
        'Mixed': '#2ecc71', 
        'Other': '#95a5a6'
    }
    
    # Default to 'Other' for any missing category
    color_map = [colors_dict.get(t, '#95a5a6') for t in df['community_type']]
    
    # Determine scale based on data
    if df['subscribers'].max() > 1000000:
        x_scale = 1000000
        x_label = 'Subscribers (millions)'
    else:
        x_scale = 1000
        x_label = 'Subscribers (thousands)'
    
    scatter = plt.scatter(df['subscribers'] / x_scale, df['relevance_score'], 
                         alpha=0.7, c=color_map, s=100)
    
    # Add labels for only the most significant communities to avoid overlap
    # We'll select based on both relevance and size
    top_by_relevance = df.nlargest(5, 'relevance_score')
    top_by_size = df.nlargest(5, 'subscribers')
    
    # Combine and remove duplicates
    important_communities = pd.concat([top_by_relevance, top_by_size]).drop_duplicates()
    
    for i, row in important_communities.iterrows():
        plt.annotate(row['name'], 
                    (row['subscribers'] / x_scale, row['relevance_score']),
                    xytext=(7, 7), textcoords='offset points',
                    fontsize=11, fontweight='bold',
                    arrowprops=dict(arrowstyle='-', color='black', lw=0.5))
    
    plt.xlabel(x_label, fontsize=12)
    plt.ylabel('Relevance Score', fontsize=12)
    plt.title('Community Relevance vs. Size', fontsize=16)
    
    # Add grid for better readability
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # Create a legend
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], marker='o', color='w', label=ctype,
                             markerfacecolor=color, markersize=10)
                      for ctype, color in colors_dict.items() if ctype in df['community_type'].values]
    
    plt.legend(handles=legend_elements, title='Community Type', loc='best', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('visualizations/reddit/relevance_vs_size.png', dpi=300)
    print("Created visualization: visualizations/reddit/relevance_vs_size.png")
    
    # 4. New visualization: Top 10 by relevance score (horizontal bar chart)
    plt.figure(figsize=(14, 10))
    top_10_relevant = df.nlargest(10, 'relevance_score')
    # Sort by relevance score ascending for better display
    top_10_relevant = top_10_relevant.sort_values('relevance_score')
    
    colors = [colors_dict.get(t, '#95a5a6') for t in top_10_relevant['community_type']]
    
    bars = plt.barh(top_10_relevant['name'], top_10_relevant['relevance_score'], color=colors)
    plt.xlabel('Relevance Score', fontsize=12)
    plt.ylabel('Subreddit', fontsize=12)
    plt.title('Top 10 Most Relevant Communities', fontsize=16)
    
    # Add subscriber count as text
    for i, bar in enumerate(bars):
        subscriber_count = f"{int(top_10_relevant.iloc[i]['subscribers']):,}"
        plt.text(bar.get_width() + 0.3, 
                bar.get_y() + bar.get_height()/2, 
                f"Subscribers: {subscriber_count}", 
                va='center', fontsize=10)
    
    # Add a legend
    legend_elements = [Patch(facecolor=color, label=ctype)
                      for ctype, color in colors_dict.items() if ctype in top_10_relevant['community_type'].values]
    plt.legend(handles=legend_elements, title='Community Type', loc='lower right')
    
    plt.tight_layout()
    plt.savefig('visualizations/reddit/top_by_relevance.png', dpi=300)
    print("Created visualization: visualizations/reddit/top_by_relevance.png")

def export_filtered_data(df, output_file):
    """Export filtered data to CSV"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"Exported filtered data to {output_file}")

def main():
    print("\n" + "="*50)
    print("REDDIT DATA ANALYZER")
    print("="*50)
    
    # Load the data - UPDATED FILE PATH TO CORRECT LOCATION
    input_file = 'scraped_data/reddit/analyzed_communities.csv'
    df = load_data(input_file)
    
    if df is not None:
        # Apply better filtering
        filtered_df = better_filter_for_students(df)
        
        # Create visualizations
        try:
            create_visualizations(filtered_df)
        except Exception as e:
            print(f"Error creating visualizations: {e}")
            import traceback
            traceback.print_exc()
        
        # Export filtered data
        output_file = 'scraped_data/reddit/filtered_student_communities.csv'
        export_filtered_data(filtered_df, output_file)
        
        # Display top 10 most relevant communities
        print("\nTop 10 most relevant communities:")
        top_n = min(10, len(filtered_df))
        top_10 = filtered_df.head(top_n)[['name', 'subscribers', 'community_type', 'relevance_score']]
        for i, row in top_10.iterrows():
            print(f"{i+1}. r/{row['name']} - {row['community_type']} (Score: {row['relevance_score']}, Subscribers: {row['subscribers']:,})")
    
    print("\nAnalysis completed at:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == "__main__":
    main()