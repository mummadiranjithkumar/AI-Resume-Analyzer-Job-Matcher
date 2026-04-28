import re
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class SkillMatcher:
    """Service for matching skills between resume and job description"""
    
    def __init__(self):
        # Load pre-trained sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Common technical skills to look for
        self.tech_skills = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'nosql',
            'mongodb', 'postgresql', 'mysql', 'aws', 'azure', 'gcp', 'docker',
            'kubernetes', 'git', 'linux', 'html', 'css', 'typescript', 'angular',
            'vue.js', 'django', 'flask', 'fastapi', 'tensorflow', 'pytorch',
            'machine learning', 'deep learning', 'data science', 'analytics',
            'tableau', 'power bi', 'excel', 'spark', 'hadoop', 'rest api',
            'graphql', 'microservices', 'devops', 'ci/cd', 'jenkins', 'terraform'
        ]
        
        # Common soft skills
        self.soft_skills = [
            'communication', 'leadership', 'teamwork', 'problem solving',
            'critical thinking', 'project management', 'time management',
            'collaboration', 'adaptability', 'creativity', 'analytical'
        ]
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from text using keyword matching
        
        Args:
            text: Input text (resume or job description)
            
        Returns:
            List of found skills
        """
        text_lower = text.lower()
        found_skills = set()
        
        # Check for technical skills
        for skill in self.tech_skills:
            if skill in text_lower:
                found_skills.add(skill)
        
        # Check for soft skills
        for skill in self.soft_skills:
            if skill in text_lower:
                found_skills.add(skill)
        
        # Extract additional skills using regex patterns
        # Look for common patterns like "X years of experience with Y"
        experience_pattern = r'(?:experience|exp|skilled|proficient|knowledge|familiar)\s+(?:in|with|of)\s+([a-zA-Z\s]{2,30})'
        matches = re.findall(experience_pattern, text_lower)
        for match in matches:
            # Clean and add if it looks like a skill
            skill = match.strip()
            if len(skill) > 2 and skill not in found_skills:
                found_skills.add(skill)
        
        return list(found_skills)
    
    def compute_similarity(self, resume_text: str, job_text: str) -> float:
        """
        Compute semantic similarity between resume and job description
        
        Args:
            resume_text: Resume text
            job_text: Job description text
            
        Returns:
            Similarity score between 0 and 1
        """
        # Generate embeddings
        resume_embedding = self.model.encode([resume_text])
        job_embedding = self.model.encode([job_text])
        
        # Compute cosine similarity
        similarity = cosine_similarity(resume_embedding, job_embedding)[0][0]
        
        return float(similarity)
    
    def analyze_match(self, resume_text: str, job_text: str) -> Dict:
        """
        Analyze match between resume and job description
        
        Args:
            resume_text: Resume text
            job_text: Job description text
            
        Returns:
            Dictionary with match analysis
        """
        # Extract skills from both texts
        resume_skills = set(self.extract_skills(resume_text))
        job_skills = set(self.extract_skills(job_text))
        
        # Find matching and missing skills
        matching_skills = list(resume_skills & job_skills)
        missing_skills = list(job_skills - resume_skills)
        
        # Compute semantic similarity
        similarity_score = self.compute_similarity(resume_text, job_text)
        
        # Calculate match score (0-100)
        # Combine semantic similarity and skill overlap
        skill_overlap_score = len(matching_skills) / max(len(job_skills), 1)
        match_score = int((similarity_score * 0.7 + skill_overlap_score * 0.3) * 100)
        
        # Generate suggestions based on missing skills
        suggestions = self._generate_suggestions(missing_skills)
        
        return {
            "match_score": min(match_score, 100),  # Cap at 100
            "matching_skills": sorted(matching_skills),
            "missing_skills": sorted(missing_skills),
            "suggestions": suggestions
        }
    
    def _generate_suggestions(self, missing_skills: List[str]) -> List[str]:
        """
        Generate improvement suggestions based on missing skills
        
        Args:
            missing_skills: List of skills missing from resume
            
        Returns:
            List of suggestions
        """
        suggestions = []
        
        for skill in missing_skills[:5]:  # Limit to top 5 missing skills
            if any(tech in skill.lower() for tech in ['python', 'java', 'javascript', 'sql']):
                suggestions.append(f"Add experience with {skill.title()} to your technical skills section")
            elif any(soft in skill.lower() for soft in ['communication', 'leadership', 'teamwork']):
                suggestions.append(f"Include examples of your {skill} abilities in your work experience")
            else:
                suggestions.append(f"Consider adding projects or experience involving {skill.title()}")
        
        if not suggestions:
            suggestions.append("Your resume aligns well with the job requirements!")
        
        return suggestions
