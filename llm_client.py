import os
import google.generativeai as genai
import json
import re
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self, provider="Gemini", api_key=None):
        self.provider = provider
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if self.provider == "Gemini":
            if not self.api_key:
                raise ValueError("Gemini API Key is missing. Please set GEMINI_API_KEY in .env or provide it in the sidebar.")
            genai.configure(api_key=self.api_key)
            self.model = self._initialize_gemini_model()

    def _initialize_gemini_model(self):
        """Initialize Gemini model with fallback options"""
        # Try different model names in order of preference (based on available models)
        models_to_try = [
            'gemini-2.5-flash',           # Latest fast model
            'gemini-2.5-pro',             # Latest pro model  
            'gemini-2.0-flash',           # Stable 2.0 fast
            'gemini-flash-latest',        # Generic latest flash
            'gemini-pro-latest',          # Generic latest pro
            'gemini-1.5-flash',           # Fallback to 1.5
            'gemini-1.5-pro'              # Final fallback
        ]
        
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                print(f"Successfully initialized model: {model_name}")
                return model
            except Exception as e:
                print(f"Model {model_name} failed to initialize: {e}")
                continue
        
        # Final fallback - use the most common available model
        print("Using fallback model: gemini-2.5-flash")
        return genai.GenerativeModel('gemini-2.5-flash')

    def extract_skills(self, text):
        """
        Uses LLM to extract skills from text comprehensively.
        Returns a list of skills.
        """
        if not text or len(text.strip()) < 10:
            return []
            
        prompt = f"""
        You are an expert HR professional and technical recruiter. Analyze the following text and extract ALL skills, technologies, tools, qualifications, and competencies mentioned.
        
        Be extremely thorough and extract:
        
        TECHNICAL SKILLS:
        - Programming languages (Python, JavaScript, Java, C++, C#, Go, Rust, etc.)
        - Web technologies (HTML, CSS, React, Angular, Vue, Node.js, Express, etc.)
        - Frameworks & Libraries (Django, Flask, Spring, Laravel, TensorFlow, PyTorch, etc.)
        - Databases (MySQL, PostgreSQL, MongoDB, Redis, Oracle, SQL Server, etc.)
        - Cloud platforms (AWS, Azure, GCP, Heroku, DigitalOcean, etc.)
        - DevOps tools (Docker, Kubernetes, Jenkins, CI/CD, Terraform, etc.)
        - Version control (Git, GitHub, GitLab, SVN, etc.)
        - Operating systems (Linux, Windows, macOS, Ubuntu, etc.)
        - Mobile development (iOS, Android, React Native, Flutter, etc.)
        - Data tools (Pandas, NumPy, Tableau, Power BI, Excel, etc.)
        - Design tools (Photoshop, Figma, Sketch, Adobe Creative Suite, etc.)
        
        SOFT SKILLS:
        - Leadership, Management, Team Leadership
        - Communication, Presentation, Public Speaking
        - Problem Solving, Critical Thinking, Analytical Skills
        - Project Management, Agile, Scrum, Kanban
        - Collaboration, Teamwork, Cross-functional teams
        - Time Management, Organization, Multitasking
        - Adaptability, Learning Agility, Flexibility
        
        CERTIFICATIONS & QUALIFICATIONS:
        - Degree requirements (Bachelor's, Master's, PhD)
        - Professional certifications (AWS Certified, Google Cloud, Microsoft, etc.)
        - Industry certifications (PMP, Scrum Master, etc.)
        
        DOMAIN EXPERTISE:
        - Industry knowledge (Healthcare, Finance, E-commerce, etc.)
        - Methodologies (Machine Learning, Data Science, AI, etc.)
        - Business skills (Sales, Marketing, Business Analysis, etc.)
        
        Extract every single skill mentioned or implied. Don't miss anything!
        Return each skill on a new line, be very comprehensive.
        
        Text to analyze:
        {text}
        
        Extracted Skills:
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            if not response_text:
                print("Empty response from AI model, using fallback")
                return self._fallback_skill_extraction(text)
            
            # Split by lines and clean up
            skills = []
            for line in response_text.split('\n'):
                skill = line.strip()
                # Remove common prefixes and clean up
                skill = re.sub(r'^[-•*\d+\.)\s]+', '', skill)  # Remove bullets, numbers
                skill = re.sub(r'^(skills?|abilities?|experience|knowledge|extracted|skills?)[\s:]+', '', skill, flags=re.IGNORECASE)
                skill = re.sub(r'^(technical|soft)[\s]+', '', skill, flags=re.IGNORECASE)
                
                if skill and len(skill) > 1 and len(skill) < 100 and not skill.lower().startswith('text to analyze'):
                    skills.append(skill.lower().strip())
            
            # Remove duplicates while preserving order
            unique_skills = []
            seen = set()
            for skill in skills:
                if skill not in seen and skill and len(skill) > 1:
                    seen.add(skill)
                    unique_skills.append(skill)
            
            # If we got very few skills, try fallback as well
            if len(unique_skills) < 5:
                fallback_skills = self._fallback_skill_extraction(text)
                for skill in fallback_skills:
                    if skill not in seen:
                        unique_skills.append(skill)
                        seen.add(skill)
            
            return unique_skills[:50]  # Increased limit for more comprehensive extraction
            
        except Exception as e:
            print(f"Error extracting skills: {e}")
            # Fallback: Basic keyword extraction
            return self._fallback_skill_extraction(text)

    def _fallback_skill_extraction(self, text):
        """
        Comprehensive fallback method for skill extraction using extensive keyword matching.
        """
        # Extensive skill keywords database
        skill_keywords = {
            'programming': ['python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'kotlin', 'swift', 'scala', 'r', 'matlab', 'perl'],
            'web': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'laravel', 'spring', 'asp.net', 'bootstrap', 'jquery'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite', 'cassandra', 'elasticsearch', 'dynamodb'],
            'cloud': ['aws', 'azure', 'gcp', 'google cloud', 'heroku', 'digitalocean', 'cloud computing', 'serverless'],
            'devops': ['docker', 'kubernetes', 'jenkins', 'ci/cd', 'terraform', 'ansible', 'chef', 'puppet', 'git', 'github', 'gitlab'],
            'data': ['machine learning', 'data science', 'artificial intelligence', 'deep learning', 'pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit-learn', 'tableau', 'power bi', 'excel'],
            'mobile': ['android', 'ios', 'react native', 'flutter', 'xamarin', 'mobile development'],
            'design': ['photoshop', 'illustrator', 'figma', 'sketch', 'adobe creative suite', 'ui/ux', 'graphic design'],
            'soft_skills': ['leadership', 'communication', 'teamwork', 'project management', 'problem solving', 'critical thinking', 'analytical thinking', 'time management', 'collaboration', 'adaptability'],
            'methodologies': ['agile', 'scrum', 'kanban', 'waterfall', 'lean', 'six sigma', 'devops', 'microservices'],
            'os': ['linux', 'windows', 'macos', 'ubuntu', 'centos', 'unix'],
            'tools': ['jira', 'confluence', 'slack', 'trello', 'asana', 'notion', 'microsoft office', 'google workspace']
        }
        
        found_skills = []
        text_lower = text.lower()
        
        # Check for skills in text
        for category, skills in skill_keywords.items():
            for skill in skills:
                if skill in text_lower:
                    found_skills.append(skill)
        
        # Also look for common patterns
        patterns = [
            r'\b\w+\.js\b',  # JavaScript frameworks
            r'\b\w+\.py\b',  # Python files
            r'\bAPI\b',
            r'\bREST\b',
            r'\bGraphQL\b',
            r'\bJSON\b',
            r'\bXML\b',
            r'\bHTTP\b',
            r'\bSSL\b',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            found_skills.extend([match.lower() for match in matches])
        
        # Remove duplicates
        return list(set(found_skills))

    def get_suggestions(self, resume_skills, jd_skills, missing_skills, experience_level="Mid Level"):
        """
        Generates comprehensive AI-powered career advice and suggestions with beautiful HTML formatting.
        """
        match_percentage = len([skill for skill in resume_skills if skill in jd_skills]) / len(jd_skills) * 100 if jd_skills else 0
        
        prompt = f"""
        You are an expert AI career coach and technical recruiter. Generate a comprehensive career analysis report in HTML format with beautiful styling.
        
        **CANDIDATE PROFILE:**
        - Experience Level: {experience_level}
        - Resume Skills: {', '.join(resume_skills[:25])}
        - Job Requirements: {', '.join(jd_skills[:25])}
        - Missing Skills: {', '.join(missing_skills[:20])}
        - Match Rate: {match_percentage:.1f}%
        
        Generate HTML content using these EXACT CSS classes (they are already defined):
        - .analysis-section for each major section
        - .analysis-header for section titles
        - .skill-gap-item for critical skill gaps
        - .learning-item for learning recommendations
        - .project-item for project suggestions
        - .platform-link for clickable learning platform links
        
        **STRUCTURE YOUR RESPONSE AS HTML:**
        
        <div class="analysis-section">
        <div class="analysis-header">🎯 Skill Match Assessment</div>
        [Provide detailed assessment of competency level, strengths, and concerns]
        </div>
        
        <div class="analysis-section">
        <div class="analysis-header">🚨 Critical Skill Gaps</div>
        [For each of TOP 5 missing skills, create:]
        <div class="skill-gap-item">
        <strong>[Skill Name]</strong><br>
        <em>Why crucial:</em> [Explanation]<br>
        <em>Learning time:</em> [Time estimate]
        </div>
        </div>
        
        <div class="analysis-section">
        <div class="analysis-header">📚 Learning Roadmap</div>
        <div class="learning-item">
        <strong>Week 1-2: Quick Wins</strong><br>
        [List 2-3 skills that can be learned quickly]
        </div>
        <div class="learning-item">
        <strong>Week 3-6: Core Competencies</strong><br>
        [List 3-4 essential skills]
        </div>
        <div class="learning-item">
        <strong>Week 7-12: Advanced Skills</strong><br>
        [List 2-3 advanced skills]
        </div>
        </div>
        
        <div class="analysis-section">
        <div class="analysis-header">💡 Hands-on Projects</div>
        [For each project, create:]
        <div class="project-item">
        <strong>[Project Name]</strong><br>
        <em>Description:</em> [Brief description]<br>
        <em>Skills demonstrated:</em> [List skills]<br>
        <em>Timeline:</em> [Duration]
        </div>
        </div>
        
        <div class="analysis-section">
        <div class="analysis-header">🎪 Interview Preparation Resources</div>
        <p>Master these skills with top learning platforms:</p>
        
        **For Programming/Technical Skills:**
        <a href="https://leetcode.com/" target="_blank" class="platform-link">LeetCode</a>
        <a href="https://www.hackerrank.com/" target="_blank" class="platform-link">HackerRank</a>
        <a href="https://www.codewars.com/" target="_blank" class="platform-link">Codewars</a>
        <a href="https://www.freecodecamp.org/" target="_blank" class="platform-link">freeCodeCamp</a>
        
        **For System Design:**
        <a href="https://www.educative.io/courses/grokking-the-system-design-interview" target="_blank" class="platform-link">Grokking System Design</a>
        <a href="https://github.com/donnemartin/system-design-primer" target="_blank" class="platform-link">System Design Primer</a>
        
        **For Data Science/ML:**
        <a href="https://www.kaggle.com/learn" target="_blank" class="platform-link">Kaggle Learn</a>
        <a href="https://www.coursera.org/learn/machine-learning" target="_blank" class="platform-link">Andrew Ng ML Course</a>
        
        **For Cloud Platforms:**
        <a href="https://aws.amazon.com/training/" target="_blank" class="platform-link">AWS Training</a>
        <a href="https://docs.microsoft.com/en-us/learn/azure/" target="_blank" class="platform-link">Azure Learning</a>
        <a href="https://cloud.google.com/training" target="_blank" class="platform-link">Google Cloud Training</a>
        
        **For Web Development:**
        <a href="https://developer.mozilla.org/en-US/" target="_blank" class="platform-link">MDN Web Docs</a>
        <a href="https://www.w3schools.com/" target="_blank" class="platform-link">W3Schools</a>
        <a href="https://javascript.info/" target="_blank" class="platform-link">JavaScript.info</a>
        
        **For Practice Interviews:**
        <a href="https://www.pramp.com/" target="_blank" class="platform-link">Pramp</a>
        <a href="https://interviewing.io/" target="_blank" class="platform-link">Interviewing.io</a>
        <a href="https://www.youtube.com/c/TechInterviewPro" target="_blank" class="platform-link">Tech Interview Pro</a>
        </div>
        
        <div class="analysis-section">
        <div class="analysis-header">📈 Career Growth Strategy</div>
        [Provide long-term development path, industry trends, networking advice, and certification priorities]
        </div>
        
        IMPORTANT: Return ONLY the HTML content without markdown code blocks or explanations.
        """
        
        try:
            response = self.model.generate_content(prompt)
            if hasattr(response, 'text') and response.text:
                return response.text
            else:
                raise Exception("Empty response from AI model")
        except Exception as e:
            error_msg = str(e)
            print(f"AI Analysis Error: {error_msg}")
            
            # Provide a comprehensive manual analysis as fallback
            match_rate = len([skill for skill in resume_skills if skill in jd_skills]) / len(jd_skills) * 100 if jd_skills else 0
            return f"""
            <div class="analysis-section">
                <div class="analysis-header">🎯 Skill Match Assessment</div>
                <p><strong>Current Match Rate:</strong> {match_rate:.1f}%</p>
                <p><strong>Resume Skills Found:</strong> {len(resume_skills)} skills detected</p>
                <p><strong>Job Requirements:</strong> {len(jd_skills)} skills required</p>
                <p><strong>Missing Skills:</strong> {len(missing_skills)} skills to develop</p>
            </div>
            
            <div class="analysis-section">
                <div class="analysis-header">🚨 Critical Skill Gaps</div>
                {chr(10).join([f'<div class="skill-gap-item"><strong>{skill.title()}</strong><br><em>Priority:</em> Essential for this role</div>' for skill in missing_skills[:5]])}
            </div>
            
            <div class="analysis-section">
                <div class="analysis-header">📚 Learning Roadmap</div>
                <div class="learning-item">
                    <strong>Week 1-2: Immediate Priority</strong><br>
                    {', '.join([skill.title() for skill in missing_skills[:3]])}
                </div>
                <div class="learning-item">
                    <strong>Week 3-8: Medium-term Focus</strong><br>
                    {', '.join([skill.title() for skill in missing_skills[3:7]])}
                </div>
            </div>
            
            <div class="analysis-section">
                <div class="analysis-header">💡 Action Steps</div>
                <div class="project-item">
                    <strong>Online Learning</strong><br>
                    Enroll in courses for top 3 missing skills
                </div>
                <div class="project-item">
                    <strong>Practice Projects</strong><br>
                    Build portfolio projects showcasing new skills
                </div>
                <div class="project-item">
                    <strong>Resume Enhancement</strong><br>
                    Add newly learned skills with specific examples
                </div>
            </div>
            
            <div class="analysis-section">
                <div class="analysis-header">🎪 Interview Preparation Resources</div>
                <p>Master these skills with top learning platforms:</p>
                <a href="https://leetcode.com/" target="_blank" class="platform-link">LeetCode</a>
                <a href="https://www.hackerrank.com/" target="_blank" class="platform-link">HackerRank</a>
                <a href="https://www.freecodecamp.org/" target="_blank" class="platform-link">freeCodeCamp</a>
                <a href="https://www.coursera.org/" target="_blank" class="platform-link">Coursera</a>
                <a href="https://www.udemy.com/" target="_blank" class="platform-link">Udemy</a>
                <a href="https://www.pluralsight.com/" target="_blank" class="platform-link">Pluralsight</a>
            </div>
            
            <div class="analysis-section">
                <div class="analysis-header">📈 Career Growth Strategy</div>
                <p><em>Note: AI analysis temporarily unavailable. This fallback provides essential guidance for your career development.</em></p>
                <div class="learning-item">
                    <strong>Focus Areas:</strong> Study technical concepts for missing skills, prepare examples of transferable skills, practice explaining your learning approach.
                </div>
            </div>
            """
