import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

def create_skill_match_chart(matched_skills, missing_skills, extra_skills):
    """Create a donut chart showing skill distribution"""
    
    # Prepare data
    labels = ['Matched Skills', 'Missing Skills', 'Extra Skills']
    values = [len(matched_skills), len(missing_skills), len(extra_skills)]
    colors = ['#48bb78', '#f56565', '#4299e1']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values,
        hole=0.4,
        marker=dict(colors=colors),
        textinfo='label+percent+value',
        textfont=dict(size=14, color='white'),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title={
            'text': "🎯 Skill Distribution Overview",
            'x': 0.5,
            'font': {'size': 20, 'color': '#2d3748'}
        },
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        height=400,
        margin=dict(t=80, b=80, l=50, r=50)
    )
    
    return fig

def create_skill_category_analysis(resume_skills, jd_skills):
    """Analyze and visualize skills by categories"""
    
    # Define skill categories
    categories = {
        'Programming Languages': ['python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'kotlin', 'swift'],
        'Web Technologies': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask'],
        'Databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite'],
        'Cloud & DevOps': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'ci/cd', 'terraform'],
        'Data Science': ['machine learning', 'data science', 'pandas', 'numpy', 'tensorflow', 'pytorch', 'tableau'],
        'Mobile Development': ['android', 'ios', 'react native', 'flutter', 'xamarin'],
        'Tools & Others': ['git', 'github', 'jira', 'figma', 'photoshop', 'excel']
    }
    
    # Categorize skills
    resume_categories = {cat: 0 for cat in categories}
    jd_categories = {cat: 0 for cat in categories}
    
    for skill in resume_skills:
        for category, skills_list in categories.items():
            if any(s in skill.lower() for s in skills_list):
                resume_categories[category] += 1
                break
    
    for skill in jd_skills:
        for category, skills_list in categories.items():
            if any(s in skill.lower() for s in skills_list):
                jd_categories[category] += 1
                break
    
    # Create comparison chart
    categories_list = list(categories.keys())
    resume_counts = [resume_categories[cat] for cat in categories_list]
    jd_counts = [jd_categories[cat] for cat in categories_list]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Your Skills',
        x=categories_list,
        y=resume_counts,
        marker_color='#48bb78',
        text=resume_counts,
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        name='Job Requirements',
        x=categories_list,
        y=jd_counts,
        marker_color='#667eea',
        text=jd_counts,
        textposition='auto'
    ))
    
    fig.update_layout(
        title={
            'text': "📊 Skills by Category Comparison",
            'x': 0.5,
            'font': {'size': 20, 'color': '#2d3748'}
        },
        xaxis_title="Skill Categories",
        yaxis_title="Number of Skills",
        barmode='group',
        height=500,
        xaxis_tickangle=-45,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    
    return fig

def create_skill_proficiency_radar(matched_skills, missing_skills, skill_weights=None):
    """Create a radar chart showing skill proficiency areas"""
    
    if skill_weights is None:
        skill_weights = {
            'Technical Skills': 0.8,
            'Programming': 0.9,
            'Cloud/DevOps': 0.6,
            'Data Science': 0.7,
            'Web Development': 0.8,
            'Mobile Development': 0.5,
            'Database': 0.7,
            'Soft Skills': 0.9
        }
    
    # Calculate proficiency scores based on matched vs required
    categories = list(skill_weights.keys())
    
    # Simulate proficiency calculation (in real scenario, this would be more sophisticated)
    proficiency_scores = []
    for category in categories:
        # Base proficiency on having relevant skills
        base_score = len([s for s in matched_skills if any(cat_word in s.lower() 
                         for cat_word in category.lower().split())]) * 20
        proficiency_scores.append(min(100, base_score + 40))  # Add base competency
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=proficiency_scores,
        theta=categories,
        fill='toself',
        name='Current Proficiency',
        line_color='#667eea',
        fillcolor='rgba(102, 126, 234, 0.3)'
    ))
    
    # Add ideal proficiency line
    ideal_scores = [85] * len(categories)  # Target proficiency
    fig.add_trace(go.Scatterpolar(
        r=ideal_scores,
        theta=categories,
        fill='toself',
        name='Target Level',
        line_color='#48bb78',
        fillcolor='rgba(72, 187, 120, 0.1)',
        line_dash='dash'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[20, 40, 60, 80, 100],
                ticktext=['20%', '40%', '60%', '80%', '100%']
            )
        ),
        title={
            'text': "🎪 Skill Proficiency Radar",
            'x': 0.5,
            'font': {'size': 20, 'color': '#2d3748'}
        },
        height=500,
        showlegend=True
    )
    
    return fig

def create_career_progression_timeline(current_skills, target_skills, experience_level):
    """Create a timeline showing career progression path"""
    
    # Define career levels and typical skill counts
    career_levels = {
        'Entry Level': {'min_skills': 8, 'max_skills': 15, 'level': 1},
        'Mid Level': {'min_skills': 15, 'max_skills': 25, 'level': 2},
        'Senior Level': {'min_skills': 25, 'max_skills': 40, 'level': 3},
        'Lead/Principal': {'min_skills': 35, 'max_skills': 50, 'level': 4},
        'Expert/Architect': {'min_skills': 45, 'max_skills': 60, 'level': 5}
    }
    
    current_level = career_levels.get(experience_level, career_levels['Mid Level'])
    current_skill_count = len(current_skills)
    target_skill_count = len(target_skills)
    
    # Create timeline data
    levels = list(career_levels.keys())
    skill_ranges = [career_levels[level]['max_skills'] for level in levels]
    current_position = current_level['level'] - 1
    
    fig = go.Figure()
    
    # Add career progression line
    fig.add_trace(go.Scatter(
        x=levels,
        y=skill_ranges,
        mode='lines+markers',
        name='Career Path',
        line=dict(color='#667eea', width=3),
        marker=dict(size=12, color='#667eea')
    ))
    
    # Mark current position
    fig.add_trace(go.Scatter(
        x=[experience_level],
        y=[current_skill_count],
        mode='markers',
        name='Current Position',
        marker=dict(size=20, color='#f56565', symbol='star')
    ))
    
    # Mark target position
    if target_skill_count > current_skill_count:
        next_level_index = min(current_position + 1, len(levels) - 1)
        fig.add_trace(go.Scatter(
            x=[levels[next_level_index]],
            y=[target_skill_count],
            mode='markers',
            name='Target Position',
            marker=dict(size=15, color='#48bb78', symbol='diamond')
        ))
    
    fig.update_layout(
        title={
            'text': "📈 Career Progression Timeline",
            'x': 0.5,
            'font': {'size': 20, 'color': '#2d3748'}
        },
        xaxis_title="Career Level",
        yaxis_title="Total Skills",
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    
    return fig

def create_skill_gap_priority_chart(missing_skills):
    """Create a priority chart for missing skills"""
    
    # Define skill priorities (in real scenario, this would be AI-determined)
    skill_priorities = {
        'python': 95, 'javascript': 90, 'react': 85, 'sql': 88, 'aws': 82,
        'docker': 78, 'git': 92, 'machine learning': 75, 'node.js': 80,
        'mongodb': 72, 'kubernetes': 70, 'angular': 75, 'vue': 70
    }
    
    # Calculate priorities for missing skills
    skill_data = []
    for skill in missing_skills[:10]:  # Top 10 missing skills
        priority = skill_priorities.get(skill.lower(), 60 + len(skill) * 2)  # Default priority
        skill_data.append({'Skill': skill.title(), 'Priority': priority})
    
    if not skill_data:
        return None
    
    df = pd.DataFrame(skill_data)
    df = df.sort_values('Priority', ascending=True)
    
    # Color mapping based on priority
    colors = ['#f56565' if p >= 85 else '#ed8936' if p >= 70 else '#4299e1' for p in df['Priority']]
    
    fig = go.Figure(go.Bar(
        x=df['Priority'],
        y=df['Skill'],
        orientation='h',
        marker=dict(color=colors),
        text=df['Priority'],
        textposition='auto'
    ))
    
    fig.update_layout(
        title={
            'text': "🚨 Skill Gap Priority Matrix",
            'x': 0.5,
            'font': {'size': 20, 'color': '#2d3748'}
        },
        xaxis_title="Priority Score",
        yaxis_title="Missing Skills",
        height=400,
        margin=dict(l=100, r=50, t=80, b=50)
    )
    
    return fig

def render_advanced_visualizations(comparison, resume_skills, jd_skills, experience_level):
    """Render all advanced visualizations"""
    
    st.markdown('<div class="viz-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="viz-header">📊 Advanced Skill Analytics Dashboard</h2>', unsafe_allow_html=True)
    
    # Create three columns for different charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Skill distribution chart
        fig1 = create_skill_match_chart(
            comparison['matched'], 
            comparison['missing'], 
            comparison['extra']
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Career progression timeline
        fig3 = create_career_progression_timeline(
            resume_skills, 
            jd_skills, 
            experience_level
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Skill proficiency radar
        fig2 = create_skill_proficiency_radar(
            comparison['matched'], 
            comparison['missing']
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Skill gap priority chart
        if comparison['missing']:
            fig4 = create_skill_gap_priority_chart(comparison['missing'])
            if fig4:
                st.plotly_chart(fig4, use_container_width=True)
    
    # Full width chart for category analysis
    st.markdown("### 🏗️ Skill Category Breakdown")
    fig5 = create_skill_category_analysis(resume_skills, jd_skills)
    st.plotly_chart(fig5, use_container_width=True)
    
    # Key insights
    st.markdown("### 💡 Key Visual Insights")
    
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        match_rate = len(comparison['matched']) / len(jd_skills) * 100 if jd_skills else 0
        st.markdown(f"""
        <div class="metric-viz">
            <h3 style="color: #667eea; margin: 0;">Match Rate</h3>
            <h2 style="color: #2d3748; margin: 0.5rem 0;">{match_rate:.1f}%</h2>
            <p style="margin: 0; color: #6c757d;">Skills Alignment</p>
        </div>
        """, unsafe_allow_html=True)
    
    with insight_col2:
        gap_count = len(comparison['missing'])
        st.markdown(f"""
        <div class="metric-viz">
            <h3 style="color: #f56565; margin: 0;">Skill Gaps</h3>
            <h2 style="color: #2d3748; margin: 0.5rem 0;">{gap_count}</h2>
            <p style="margin: 0; color: #6c757d;">Skills to Learn</p>
        </div>
        """, unsafe_allow_html=True)
    
    with insight_col3:
        strength_count = len(comparison['extra'])
        st.markdown(f"""
        <div class="metric-viz">
            <h3 style="color: #48bb78; margin: 0;">Extra Skills</h3>
            <h2 style="color: #2d3748; margin: 0.5rem 0;">{strength_count}</h2>
            <p style="margin: 0; color: #6c757d;">Bonus Assets</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)