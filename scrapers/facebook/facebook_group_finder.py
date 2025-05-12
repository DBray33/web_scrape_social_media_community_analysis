#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
facebook_group_finder.py - Simulated Facebook Groups discovery and data collection

This module simulates the discovery and data collection from Facebook Groups
focused on students and emerging professionals. It demonstrates the methodology
and data structures that would be used in a real implementation, while
maintaining ethical development practices.
"""

import os
import json
import random
import pandas as pd
from datetime import datetime, timedelta
import time
import logging
from typing import List, Dict, Any, Optional
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/facebook_groups.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("facebook_groups")

class FacebookGroupFinder:
    """
    A class that simulates finding and collecting data from Facebook Groups
    related to students and emerging professionals.
    """
    
    def __init__(self, output_dir: str = "scraped_data/facebook"):
        """
        Initialize the FacebookGroupFinder.
        
        Args:
            output_dir: Directory to save collected data
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Expanded categories for student and emerging professional communities
        self.categories = [
            # Academic Fields
            "Computer Science", "Business", "Engineering", "Liberal Arts", 
            "Medicine", "Law", "Education", "Social Sciences", "Fine Arts",
            "Natural Sciences", "Mathematics", "Communications", "Psychology",
            
            # Career-Related
            "Job Hunting", "Internships", "Entry-Level", "Career Transitions",
            "Professional Development", "Networking", "Interview Prep", "Resume Building",
            
            # Student Life
            "College Life", "Graduate School", "Student Organizations", "Study Abroad",
            "Financial Aid", "Scholarships", "Campus Housing", "Student Activities"
        ]
        
        # School focus levels
        self.school_focus_levels = [
            "High School", "Community College", "Undergraduate", "Graduate",
            "PhD", "Professional School", "All Levels", "Not School Specific"
        ]
        
        # Geographic scopes
        self.geographic_scopes = [
            "Local", "State/Provincial", "Regional", "National", "International", "Global"
        ]
        
        logger.info("FacebookGroupFinder initialized")
    
    def simulate_group_discovery(self, query: str, limit: int = 15) -> List[Dict[str, Any]]:
        """
        Simulate the discovery of Facebook Groups based on a search query.
        
        Args:
            query: Search term for finding groups
            limit: Maximum number of groups to return
            
        Returns:
            List of dictionaries containing group information
        """
        logger.info(f"Simulating group discovery for query: {query}")
        
        # Clean the query for use in group naming
        clean_query = re.sub(r'[^\w\s]', '', query).strip()
        
        # Simulate rate limiting
        time.sleep(random.uniform(1.0, 2.5))
        
        discovered_groups = []
        
        # Generate a realistic number of groups (fewer than the limit)
        actual_count = random.randint(max(5, limit - 10), limit)
        
        for i in range(actual_count):
            # Select random category that might be related to the query
            category = random.choice(self.categories)
            
            # Create group with realistic attributes
            group_id = f"fb_group_{100000000 + random.randint(1, 999999999)}"
            
            # Create varied group naming patterns
            name_patterns = [
                f"{clean_query} {category} Group",
                f"{category} {clean_query} Network",
                f"{clean_query} Students & {category} Professionals",
                f"{category} Learning & Support",
                f"Future {category} Leaders",
                f"{clean_query} Community",
                f"Connect: {category} {clean_query}",
                f"{clean_query} Success in {category}",
                f"{category} Opportunities for {clean_query}",
                f"{clean_query} Help & Advice"
            ]
            
            group_name = random.choice(name_patterns)
            
            # Simulate member counts (adjusted based on category popularity)
            base_members = random.randint(200, 8000)
            
            # More popular categories have larger groups
            popular_categories = ["Business", "Job Hunting", "College Life", "Internships", "Computer Science"]
            if category in popular_categories:
                base_members *= random.randint(2, 4)
            
            # Simulate group creation dates (between 1-7 years ago)
            days_ago = random.randint(365, 365 * 7)
            creation_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            
            # Simulate posting frequency (posts per day)
            if base_members > 10000:
                post_frequency = random.uniform(10.0, 50.0)
            elif base_members > 5000:
                post_frequency = random.uniform(5.0, 15.0)
            else:
                post_frequency = random.uniform(1.0, 7.0)
            
            # Random privacy setting (more likely to be closed for professional groups)
            privacy = random.choices(
                ["Public", "Closed"], 
                weights=[0.25, 0.75]
            )[0]
            
            # School focus - weight toward education-related queries
            if any(term in query.lower() for term in ["student", "college", "university", "school", "education", "academic"]):
                school_focus_weights = [0.15, 0.15, 0.25, 0.15, 0.05, 0.05, 0.15, 0.05]
            else:
                school_focus_weights = [0.05, 0.05, 0.15, 0.10, 0.05, 0.05, 0.05, 0.50]
            
            school_focus = random.choices(
                self.school_focus_levels,
                weights=school_focus_weights
            )[0]
            
            # Geographic focus
            geographic_scope = random.choice(self.geographic_scopes)
            
            # Target age range
            if "high school" in query.lower() or school_focus == "High School":
                min_age, max_age = 14, 19
            elif "college" in query.lower() or "undergraduate" in school_focus:
                min_age, max_age = 18, 23
            elif "graduate" in query.lower() or "Graduate" in school_focus:
                min_age, max_age = 22, 30
            elif "professional" in query.lower() or "career" in query.lower():
                min_age, max_age = 22, 40
            else:
                min_age, max_age = 18, 35
            
            # Adjust ranges slightly for realism
            min_age += random.randint(-2, 2)
            max_age += random.randint(-3, 3)
            min_age = max(13, min_age)  # Facebook minimum age
            max_age = max(min_age + 5, max_age)  # Ensure sensible range
            
            # Outreach potential (1-10 scale)
            # Higher for groups with specific focus, active moderation, etc.
            outreach_factors = {
                "size": min(10, base_members / 10000 * 10),  # Size factor (max 10)
                "activity": min(10, post_frequency / 5),     # Activity factor
                "specificity": 8 if school_focus != "Not School Specific" else 5,  # Specificity bonus
                "accessibility": 7 if privacy == "Public" else 4  # Public groups easier to reach
            }
            outreach_potential = sum(outreach_factors.values()) / len(outreach_factors)
            outreach_potential = round(min(10, outreach_potential), 1)  # Cap at 10
            
            # Best contact methods
            contact_methods = []
            if random.random() < 0.7:
                contact_methods.append("Group Admin Message")
            if random.random() < 0.5:
                contact_methods.append("Post in Group")
            if random.random() < 0.3 and privacy == "Public":
                contact_methods.append("Comment on Active Threads")
            if random.random() < 0.2:
                contact_methods.append("Member Direct Messages")
            if len(contact_methods) == 0:
                contact_methods = ["Group Admin Message"]
            
            group = {
                "group_id": group_id,
                "name": group_name,
                "category": category,
                "privacy": privacy,
                "member_count": base_members,
                "creation_date": creation_date,
                "post_frequency": round(post_frequency, 2),
                "description": self._generate_group_description(group_name, category),
                "location": random.choice(["Global", "United States", "Europe", "Asia", "Online"]),
                "related_keywords": self._generate_related_keywords(category, clean_query),
                "discovery_date": datetime.now().strftime("%Y-%m-%d"),
                "school_focus": school_focus,
                "geographic_scope": geographic_scope,
                "target_age_range": f"{min_age}-{max_age}",
                "outreach_potential": outreach_potential,
                "best_contact_methods": contact_methods,
                "admin_responsiveness": random.choice(["High", "Medium", "Low", "Unknown"]),
                "group_rules_strictness": random.choice(["Strict", "Moderate", "Relaxed", "Unknown"])
            }
            
            discovered_groups.append(group)
            
        logger.info(f"Discovered {len(discovered_groups)} groups for query: {query}")
        return discovered_groups
    
    def _generate_group_description(self, name: str, category: str) -> str:
        """Generate a realistic group description based on group category"""
        academic_descriptions = [
            f"A community for {category} students and scholars to network, share resources, and discuss academic topics.",
            f"Supporting students and professionals in {category}. Share research, ask questions, and find collaborators.",
            f"A space for {category} students to connect with peers, ask questions, and share advice on coursework and research.",
            f"This group brings together {category} students, faculty, and professionals for academic discourse and support."
        ]
        
        career_descriptions = [
            f"Connect with fellow {category} professionals, share job opportunities, and discuss industry trends.",
            f"A community dedicated to helping students transition into professional roles in {category}.",
            f"Job postings, career advice, and networking opportunities for those in {category}.",
            f"Support group for early-career professionals in {category}. Resume reviews, interview tips, and mentorship."
        ]
        
        student_life_descriptions = [
            f"For students interested in {category} to find roommates, study partners, and campus event information.",
            f"Discuss {category} events, student activities, and campus life. Share tips on balancing academics and social life.",
            f"A supportive community for students navigating {category} challenges and celebrating successes.",
            f"Connect with peers in {category}, organize study sessions, and share campus resources."
        ]
        
        # Choose appropriate description type based on category
        if category in ["Computer Science", "Business", "Engineering", "Liberal Arts", "Medicine", "Law", 
                        "Education", "Social Sciences", "Fine Arts", "Natural Sciences", "Mathematics", 
                        "Communications", "Psychology"]:
            descriptions = academic_descriptions
        elif category in ["Job Hunting", "Internships", "Entry-Level", "Career Transitions", 
                         "Professional Development", "Networking", "Interview Prep", "Resume Building"]:
            descriptions = career_descriptions
        else:
            descriptions = student_life_descriptions
        
        return random.choice(descriptions)
    
    def _generate_related_keywords(self, category: str, query: str) -> List[str]:
        """Generate realistic related keywords based on category and query"""
        # Academic field keywords
        academic_keywords = {
            "Computer Science": ["programming", "algorithms", "software", "coding", "CS major", "tech", "developer"],
            "Business": ["marketing", "entrepreneurship", "management", "finance", "MBA", "startups", "economics"],
            "Engineering": ["mechanical", "electrical", "civil", "systems", "engineering major", "technical", "design"],
            "Liberal Arts": ["humanities", "philosophy", "literature", "history", "arts", "writing", "culture"],
            "Medicine": ["medical school", "pre-med", "healthcare", "MCAT", "clinical", "doctor", "physician"],
            "Law": ["law school", "legal studies", "LSAT", "attorney", "paralegal", "JD", "legal profession"],
            "Education": ["teaching", "pedagogy", "childhood education", "curriculum", "educational studies", "learning"],
            "Social Sciences": ["sociology", "psychology", "anthropology", "political science", "research", "behavioral"],
            "Fine Arts": ["studio art", "design", "music", "theater", "film", "creative", "artistic", "performance"],
            "Natural Sciences": ["biology", "chemistry", "physics", "lab work", "research", "scientific", "experiments"],
            "Mathematics": ["statistics", "calculus", "algebra", "math major", "quantitative", "analytical", "numerical"],
            "Communications": ["journalism", "media", "public relations", "broadcasting", "speech", "digital media"],
            "Psychology": ["clinical", "cognitive", "behavioral", "counseling", "mental health", "psychological research"]
        }
        
        # Career-related keywords
        career_keywords = {
            "Job Hunting": ["job search", "applications", "career fair", "hiring", "opportunities", "job market", "employment"],
            "Internships": ["summer internship", "paid internship", "practicum", "work experience", "intern", "trainee"],
            "Entry-Level": ["entry jobs", "new grad", "recent graduate", "first job", "junior position", "starter role"],
            "Career Transitions": ["career change", "pivot", "reskilling", "new industry", "transition", "changing fields"],
            "Professional Development": ["skills", "certification", "training", "workshops", "continuing education", "learning"],
            "Networking": ["connections", "professional network", "meetups", "industry events", "contacts", "referrals"],
            "Interview Prep": ["mock interviews", "interview questions", "behavioral interview", "technical interview", "preparation"],
            "Resume Building": ["CV", "cover letter", "resume tips", "portfolio", "application materials", "credentials"]
        }
        
        # Student life keywords
        student_life_keywords = {
            "College Life": ["dorm", "campus", "university life", "college experience", "freshmen", "sophomore", "college students"],
            "Graduate School": ["grad school", "masters", "PhD", "doctoral", "thesis", "dissertation", "graduate studies"],
            "Student Organizations": ["clubs", "societies", "student groups", "extracurricular", "campus activities", "leadership"],
            "Study Abroad": ["international study", "exchange program", "foreign university", "global experience", "abroad semester"],
            "Financial Aid": ["scholarships", "FAFSA", "student loans", "grants", "tuition assistance", "college funding"],
            "Scholarships": ["merit scholarships", "fellowship", "financial awards", "academic scholarships", "funding opportunities"],
            "Campus Housing": ["dorms", "residence halls", "roommates", "on-campus living", "housing options", "university housing"],
            "Student Activities": ["events", "recreation", "student life", "campus engagement", "university programs", "activities"]
        }
        
        # Select appropriate keyword set based on category
        if category in academic_keywords:
            base_keywords = academic_keywords[category]
        elif category in career_keywords:
            base_keywords = career_keywords[category]
        elif category in student_life_keywords:
            base_keywords = student_life_keywords[category]
        else:
            base_keywords = ["students", "education", "learning", "career", "professional", "academic"]
        
        # Add some general keywords related to students and emerging professionals
        general_keywords = ["advice", "community", "resources", "support", "discussion", "collaboration", "opportunities"]
        
        # Add keywords from the query
        query_words = [word.lower() for word in query.split() if len(word) > 3]
        
        # Combine and select random subset
        all_keywords = base_keywords + general_keywords + query_words
        return random.sample(all_keywords, k=min(len(all_keywords), random.randint(5, 8)))
    
    def simulate_group_posts(self, group_id: str, days: int = 30, max_posts: int = 100) -> List[Dict[str, Any]]:
        """
        Simulate posts from a Facebook Group over a specified time period.
        
        Args:
            group_id: ID of the Facebook Group
            days: Number of days of posts to simulate
            max_posts: Maximum number of posts to generate
            
        Returns:
            List of dictionaries containing post information
        """
        logger.info(f"Simulating posts for group {group_id} over {days} days")
        
        # Load group info if available
        group_file = os.path.join(self.output_dir, "groups.json")
        group_info = None
        
        if os.path.exists(group_file):
            with open(group_file, "r") as f:
                groups = json.load(f)
                for group in groups:
                    if group["group_id"] == group_id:
                        group_info = group
                        break
        
        if not group_info:
            logger.warning(f"Group {group_id} not found in saved data")
            # Create a generic group info
            group_info = {
                "group_id": group_id,
                "name": f"Group {group_id}",
                "category": random.choice(self.categories),
                "post_frequency": random.uniform(1.0, 10.0)
            }
        
        # Determine number of posts based on post frequency and days
        expected_posts = int(group_info["post_frequency"] * days)
        num_posts = min(expected_posts, max_posts)
        
        posts = []
        for i in range(num_posts):
            # Generate post date within the specified range
            post_date = datetime.now() - timedelta(days=random.randint(0, days))
            
            # Determine post type based on category
            post_type = self._determine_post_type(group_info["category"])
            
            # Generate appropriate content based on post_type and category
            content = self._generate_post_content(post_type, group_info["category"])
            
            # Generate post with realistic attributes
            post = {
                "post_id": f"post_{group_id}_{i}",
                "group_id": group_id,
                "date": post_date.strftime("%Y-%m-%d %H:%M:%S"),
                "content": content,
                "likes": self._generate_engagement_count(group_info.get("member_count", 1000)),
                "comments": self._generate_engagement_count(group_info.get("member_count", 1000), is_comments=True),
                "has_image": random.random() < 0.4,  # 40% chance of having an image
                "has_link": random.random() < 0.3,   # 30% chance of having a link
                "post_type": post_type,
                "author_type": random.choices(
                    ["Student", "Professional", "Faculty", "Admin", "Organization"], 
                    weights=[0.5, 0.3, 0.1, 0.05, 0.05]
                )[0]
            }
            posts.append(post)
        
        # Sort posts by date (newest first)
        posts.sort(key=lambda x: x["date"], reverse=True)
        
        logger.info(f"Generated {len(posts)} posts for group {group_id}")
        return posts
    
    def _generate_post_content(self, post_type: str, category: str) -> str:
        """Generate realistic post content based on post type and group category"""
        # Question posts
        question_templates = [
            f"Has anyone taken [course/program] in {category}? What was your experience?",
            f"What certifications would you recommend for someone starting in {category}?",
            f"Best resources to learn advanced {category} concepts?",
            f"How did you transition into {category} from another field?",
            f"Tips for finding {category} internships for next summer?",
            f"What's the job market like for {category} right now?",
            f"Anyone know of any good {category} scholarships still accepting applications?",
            f"How do you balance coursework with extracurriculars in {category}?"
        ]
        
        # Job posting posts
        job_posts = [
            f"[Company] is hiring a {category} Specialist! DM for details.",
            f"Job opportunity: Junior {category} position at [Company]. Apply by [date]!",
            f"Looking for a talented {category} intern to join our team this [season].",
            f"Remote {category} opportunity for recent graduates. $[salary] range.",
            f"[University] seeking part-time student assistants in {category} department.",
            f"Paid summer internship opportunity in {category}. Application deadline approaching!",
            f"Entry-level {category} position available - great for new grads!",
            f"Anyone interested in a {category} role at [Company]? I can refer!"
        ]
        
        # Resource sharing posts
        resource_posts = [
            f"Just found this amazing resource for {category}: [link]",
            f"Free workshop on {category} fundamentals this weekend!",
            f"Sharing my notes from the recent {category} conference.",
            f"Great podcast about {category} career paths: [link]",
            f"Helpful YouTube channel for {category} students: [link]",
            f"I created a study guide for the {category} certification exam. Happy to share!",
            f"New scholarship opportunity for {category} students: [link]",
            f"Found a great template for {category} portfolios/resumes: [link]"
        ]
        
        # Discussion posts
        discussion_posts = [
            f"What do you think about the future of {category} with AI advancements?",
            f"How has remote work/learning changed your approach to {category}?",
            f"Let's discuss the latest trends in {category} for 2025.",
            f"What's your biggest challenge as a {category} student/professional?",
            f"Anyone else feeling overwhelmed by the {category} curriculum this semester?",
            f"What's the most valuable skill you've developed in your {category} journey?",
            f"How did you choose to specialize in {category}?",
            f"Is a master's degree worth it for {category} careers?"
        ]
        
        # Event posts
        event_posts = [
            f"{category} Networking Event on [date] - Who's going?",
            f"Virtual {category} Workshop next week - registration link in comments!",
            f"Join us for a {category} Study Group this Saturday at [location/platform].",
            f"Upcoming Career Fair specializing in {category} - [date/details]",
            f"{category} Department hosting guest speaker on [topic] - open to all students!",
            f"Annual {category} Symposium looking for student volunteers",
            f"Registration open for {category} Hackathon/Competition!",
            f"Join our {category} Book Club meeting this month - discussing [book title]"
        ]
        
        # Other/miscellaneous posts
        other_posts = [
            f"Just passed my {category} certification exam! Happy to answer questions.",
            f"Looking for study partners for {category} courses this semester.",
            f"Proud to announce I've accepted a {category} position at [Company]!",
            f"Anyone else applying to {category} graduate programs for next year?",
            f"New to this group! I'm studying {category} at [University].",
            f"Created a Discord server for {category} students - link in comments.",
            f"Poll: What's your favorite {category} class/subject?",
            f"Just submitted my {category} thesis/project! Feeling relieved!"
        ]
        
        # Select appropriate content based on post type
        if post_type == "question":
            content = random.choice(question_templates)
        elif post_type == "job_posting":
            content = random.choice(job_posts)
        elif post_type == "resource_sharing":
            content = random.choice(resource_posts)
        elif post_type == "discussion":
            content = random.choice(discussion_posts)
        elif post_type == "event":
            content = random.choice(event_posts)
        else:
            content = random.choice(other_posts)
        
        return content
    
    def _generate_engagement_count(self, member_count: int, is_comments: bool = False) -> int:
        """Generate realistic engagement numbers based on group size"""
        # Comments typically fewer than likes
        base_rate = 0.02 if not is_comments else 0.005
        
        # Adjust for virality factor (some posts get more engagement)
        virality = random.choices(
            [1, 2, 5, 10], 
            weights=[0.7, 0.2, 0.08, 0.02]
        )[0]
        
        engagement = int(member_count * base_rate * virality)
        
        # Add some randomness
        engagement = int(engagement * random.uniform(0.5, 1.5))
        
        return max(0, engagement)
    
    def _determine_post_type(self, category: str) -> str:
        """Determine post type with realistic distribution based on group category"""
        post_types = ["question", "job_posting", "resource_sharing", "discussion", "event", "other"]
        
        # Adjust weights based on category
        if category in ["Job Hunting", "Internships", "Entry-Level", "Career Transitions"]:
            # Career-focused categories have more job postings
            weights = [0.2, 0.4, 0.15, 0.15, 0.05, 0.05]
        elif category in ["Computer Science", "Business", "Engineering", "Medicine", "Law"]:
            # Professional fields have balanced content
            weights = [0.25, 0.25, 0.2, 0.15, 0.1, 0.05]
        elif category in ["College Life", "Student Organizations", "Campus Housing"]:
            # Student life categories have more discussion and events
            weights = [0.2, 0.05, 0.15, 0.3, 0.25, 0.05]
        elif category in ["Professional Development", "Networking", "Interview Prep"]:
            # Professional development has more resources and questions
            weights = [0.3, 0.15, 0.3, 0.15, 0.05, 0.05]
        else:
            # Balanced for other categories
            weights = [0.25, 0.15, 0.2, 0.2, 0.15, 0.05]
            
        return random.choices(post_types, weights=weights)[0]
    
    def simulate_member_data(self, group_id: str, sample_size: int = 100) -> List[Dict[str, Any]]:
        """
        Simulate member data for a Facebook Group.
        
        Args:
            group_id: ID of the Facebook Group
            sample_size: Number of members to simulate
            
        Returns:
            List of dictionaries containing member information
        """
        logger.info(f"Simulating {sample_size} members for group {group_id}")
        
        # Load group info if available
        group_file = os.path.join(self.output_dir, "groups.json")
        group_info = None
        
        if os.path.exists(group_file):
            with open(group_file, "r") as f:
                groups = json.load(f)
                for group in groups:
                    if group["group_id"] == group_id:
                        group_info = group
                        break
        
        if not group_info:
            logger.warning(f"Group {group_id} not found in saved data")
            # Create a generic group info
            group_info = {
                "group_id": group_id,
                "category": random.choice(self.categories),
                "school_focus": random.choice(self.school_focus_levels)
            }
        
        # Get category and school focus for demographic distribution
        category = group_info.get("category", "General")
        school_focus = group_info.get("school_focus", "All Levels")
        
        members = []
        for i in range(sample_size):
            # Simulate member join date (more recent members for newer groups)
            group_age_days = 365 * random.randint(1, 7)  # 1-7 years
            join_days_ago = random.randint(1, group_age_days)
            join_date = (datetime.now() - timedelta(days=join_days_ago)).strftime("%Y-%m-%d")
            
            # Simulate member activity level
            activity_level = random.choices(
                ["high", "medium", "low", "inactive"],
                weights=[0.1, 0.3, 0.4, 0.2]
            )[0]
            
            # Determine member type based on group category and school focus
            member_type = self._determine_member_type(category, school_focus)
            
            # Determine location - higher chance of matching group geographic scope
            if "group_geographic_scope" in group_info:
                if group_info["geographic_scope"] == "Local":
                    location_weights = [0.7, 0.2, 0.05, 0.05]
                elif group_info["geographic_scope"] == "National":
                    location_weights = [0.2, 0.6, 0.1, 0.1]
                elif group_info["geographic_scope"] == "International":
                    location_weights = [0.1, 0.2, 0.6, 0.1]
                else:
                    location_weights = [0.25, 0.25, 0.25, 0.25]
                
                location = random.choices(
                    ["United States", "Canada/Europe", "Asia/Other", "Not Specified"],
                    weights=location_weights
                )[0]
            else:
                location = random.choice(["United States", "Canada/Europe", "Asia/Other", "Not Specified"])
            
            # Generate member attributes
            member = {
                "member_id": f"fb_user_{100000000 + random.randint(1, 999999999)}",
                "group_id": group_id,
                "join_date": join_date,
                "activity_level": activity_level,
                "post_count": self._generate_activity_count(activity_level),
                "comment_count": self._generate_activity_count(activity_level, is_comments=True),
                "reported_location": location,
                "reported_profession": self._generate_profession(category, member_type),
                "member_type": member_type,
                "education_level": self._generate_education_level(member_type, school_focus),
                "engagement_topics": self._generate_engagement_topics(category),
                "is_admin": random.random() < 0.02,  # 2% chance of being admin
                "is_moderator": random.random() < 0.05  # 5% chance of being moderator
            }
            members.append(member)
        
        logger.info(f"Generated {len(members)} member profiles for group {group_id}")
        return members
    
    def _determine_member_type(self, category: str, school_focus: str) -> str:
        """Determine realistic member type based on group category and school focus"""
        
        if school_focus == "High School":
            types = ["High School Student", "Teacher", "Parent", "Counselor", "Education Professional"]
            weights = [0.7, 0.15, 0.1, 0.03, 0.02]
        
        elif school_focus == "Undergraduate":
            types = ["Undergraduate Student", "Recent Graduate", "Professor/Faculty", "Academic Staff", "Working Professional"]
            weights = [0.7, 0.15, 0.08, 0.05, 0.02]
        
        elif school_focus == "Graduate":
            types = ["Graduate Student", "PhD Student", "Faculty", "Research Professional", "Industry Professional"]
            weights = [0.5, 0.2, 0.15, 0.05, 0.1]
        
        elif school_focus == "Professional School":
            types = ["Professional Student", "Recent Graduate", "Practitioner", "Faculty", "Industry Professional"]
            weights = [0.4, 0.2, 0.2, 0.1, 0.1]
            
        elif category in ["Job Hunting", "Entry-Level", "Internships"]:
            types = ["Student", "Recent Graduate", "Job Seeker", "Career Changer", "Hiring Manager"]
            weights = [0.35, 0.3, 0.2, 0.1, 0.05]
            
        elif "Career" in category or "Professional" in category:
            types = ["Working Professional", "Manager", "Student", "Recent Graduate", "Educator"]
            weights = [0.5, 0.2, 0.15, 0.1, 0.05]
            
        else:
            types = ["Student", "Recent Graduate", "Young Professional", "Educator", "Industry Expert"]
            weights = [0.4, 0.25, 0.2, 0.1, 0.05]
        
        return random.choices(types, weights=weights)[0]
    
    def _generate_education_level(self, member_type: str, school_focus: str) -> str:
        """Generate appropriate education level based on member type and school focus"""
        
        if "High School" in member_type:
            return random.choice(["High School", "Some High School"])
            
        elif "Undergraduate" in member_type or "Student" in member_type:
            if "School" in school_focus:
                return random.choice(["High School Graduate", "Some College", "Associate's Degree", "Bachelor's Degree"])
            else:
                return random.choice(["Some College", "Associate's Degree", "Bachelor's Degree"])
                
        elif "Graduate" in member_type or "PhD" in member_type:
            return random.choice(["Bachelor's Degree", "Master's Degree", "In Progress: Master's", "In Progress: PhD"])
            
        elif "Faculty" in member_type or "Professor" in member_type:
            return random.choice(["Master's Degree", "PhD", "Professional Doctorate"])
            
        elif "Professional" in member_type or "Manager" in member_type:
            return random.choice(["Bachelor's Degree", "Master's Degree", "MBA", "PhD", "Professional Certification"])
            
        else:
            return random.choice(["High School", "Some College", "Associate's Degree", "Bachelor's Degree", "Master's Degree", "PhD", "Other"])
    
    def _generate_activity_count(self, activity_level: str, is_comments: bool = False) -> int:
        """Generate realistic activity counts based on member activity level"""
        base_counts = {
            "high": 20 if not is_comments else 50,
            "medium": 8 if not is_comments else 20,
            "low": 2 if not is_comments else 5,
            "inactive": 0 if not is_comments else 1
        }
        
        base = base_counts.get(activity_level, 0)
        
        # Add randomness
        return int(base * random.uniform(0.5, 1.5))
    
    def _generate_profession(self, category: str, member_type: str) -> str:
        """Generate realistic profession based on group category and member type"""
        
        if "Student" in member_type:
            return f"{category} Student"
            
        elif "Faculty" in member_type or "Professor" in member_type or "Teacher" in member_type:
            return f"{category} Educator"
            
        elif "Recent Graduate" in member_type:
            return f"Entry-Level {category} Professional"
            
        elif "Professional" in member_type:
            seniority = random.choice(["Junior", "Mid-Level", "Senior", "Lead", "Principal"])
            return f"{seniority} {category} Professional"
            
        elif "Manager" in member_type:
            return f"{category} Manager"
            
        else:
            roles = [
                f"{category} Specialist", 
                f"{category} Consultant", 
                f"{category} Freelancer", 
                f"{category} Coordinator", 
                "Self-Employed", 
                "Entrepreneur"
            ]
            return random.choice(roles)
    
    def _generate_engagement_topics(self, category: str) -> List[str]:
        """Generate topics the member engages with based on group category"""
        
        # Base topics related to the category
        base_topics = [f"{category} Basics", f"{category} Advanced Topics", f"{category} Resources"]
        
        # Additional topics based on category type
        if category in ["Computer Science", "Business", "Engineering", "Medicine", "Law", "Education"]:
            additional_topics = [
                "Industry News", "Career Development", "Academic Research", 
                "Technical Questions", "Best Practices", "Tools & Technologies"
            ]
        elif category in ["Job Hunting", "Internships", "Entry-Level", "Career Transitions"]:
            additional_topics = [
                "Resume Tips", "Interview Preparation", "Networking", 
                "Job Postings", "Career Advice", "Industry Insights"
            ]
        elif category in ["College Life", "Graduate School", "Student Organizations"]:
            additional_topics = [
                "Campus Events", "Study Groups", "Coursework Help", 
                "Extracurricular Activities", "Housing Advice", "Student Support"
            ]
        else:
            additional_topics = [
                "General Discussions", "Community Questions", "Resource Sharing", 
                "Networking", "Career Development", "Learning Opportunities"
            ]
        
        # Select 2-4 base topics and 1-3 additional topics
        selected_base = random.sample(base_topics, k=min(len(base_topics), random.randint(1, 3)))
        selected_additional = random.sample(additional_topics, k=min(len(additional_topics), random.randint(1, 3)))
        
        return selected_base + selected_additional
    
    def collect_and_save_data(self, queries: List[str], save: bool = True) -> Dict[str, Any]:
        """
        Collect and optionally save Facebook Group data based on search queries.
        
        Args:
            queries: List of search queries
            save: Whether to save the collected data to files
            
        Returns:
            Dictionary containing collected data
        """
        all_groups = []
        all_posts = []
        all_members = []
        
        # Process each query
        for query in queries:
            logger.info(f"Processing query: {query}")
            
            # Discover groups
            groups = self.simulate_group_discovery(query)
            all_groups.extend(groups)
            
            # For each group, collect posts and members
            for group in groups:
                group_id = group["group_id"]
                
                # Collect posts (last 30 days, up to 100 posts)
                posts = self.simulate_group_posts(group_id, days=30, max_posts=100)
                all_posts.extend(posts)
                
                # Collect member data (sample of 100 members)
                members = self.simulate_member_data(group_id, sample_size=100)
                all_members.extend(members)
                
                # Simulate rate limiting
                time.sleep(random.uniform(1.0, 3.0))
        
        # Remove duplicates based on IDs
        unique_groups = {group["group_id"]: group for group in all_groups}
        unique_posts = {post["post_id"]: post for post in all_posts}
        unique_members = {member["member_id"]: member for member in all_members}
        
        collected_data = {
            "groups": list(unique_groups.values()),
            "posts": list(unique_posts.values()),
            "members": list(unique_members.values())
        }
        
        # Save data to files if requested
        if save:
            self._save_data(collected_data)
        
        return collected_data
    
    def _save_data(self, data: Dict[str, List[Dict[str, Any]]]) -> None:
        """Save collected data to JSON and CSV files"""
        # Save JSON files
        for key, items in data.items():
            file_path = os.path.join(self.output_dir, f"{key}.json")
            with open(file_path, "w") as f:
                json.dump(items, f, indent=2)
            logger.info(f"Saved {len(items)} {key} to {file_path}")
        
        # Save CSV files (more practical for data analysis)
        for key, items in data.items():
            if items:
                df = pd.DataFrame(items)
                file_path = os.path.join(self.output_dir, f"{key}.csv")
                df.to_csv(file_path, index=False)
                logger.info(f"Saved {len(items)} {key} to {file_path}")

def main():
    """Main function to demonstrate the FacebookGroupFinder functionality"""
    # Create output directories if they don't exist
    os.makedirs("logs", exist_ok=True)
    os.makedirs("scraped_data/facebook", exist_ok=True)
    
    # Initialize the FacebookGroupFinder
    finder = FacebookGroupFinder()
    
    # Define search queries related to students and emerging professionals
    # Using a diverse set of queries covering different academic fields and career stages
    queries = [
        # General Student Communities
        "university students",
        "college freshmen",
        "graduate students",
        "international students",
        "transfer students",
        "first generation college",
        "student organizations",
        
        # Academic Support
        "study groups",
        "academic support",
        "thesis writing",
        "dissertation help",
        "research students",
        
        # Career Development
        "entry level jobs",
        "new graduates",
        "internship opportunities",
        "student career network",
        "campus recruiting",
        "young professionals",
        "early career",
        
        # School Specific
        "university clubs",
        "campus organizations",
        "alumni network",
        "fraternity sorority",
        "student government",
        
        # Specialized Student Groups
        "medical students",
        "law school students",
        "MBA students",
        "engineering students",
        "arts students",
        "humanities majors",
        "science majors"
    ]
    
    # Collect and save data
    collected_data = finder.collect_and_save_data(queries)
    
    # Print summary
    print("\nData Collection Summary:")
    print(f"Collected {len(collected_data['groups'])} unique Facebook Groups")
    print(f"Collected {len(collected_data['posts'])} posts")
    print(f"Collected {len(collected_data['members'])} member profiles")
    print(f"\nData saved to {finder.output_dir}/")

if __name__ == "__main__":
    main()