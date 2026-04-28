import streamlit as st
import requests
import json
from typing import Dict, Any
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


# Configure page
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_BASE_URL = "http://localhost:8000"


def main():
    """Main Streamlit application"""
    st.title("🤖 AI Resume Analyzer + Job Matcher")
    st.markdown("---")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_url = st.text_input(
            "API URL",
            value=API_BASE_URL,
            help="Backend API URL"
        )
        
        # Test API connection
        if st.button("🔗 Test Connection"):
            test_api_connection(api_url)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📄 Resume Upload")
        uploaded_file = st.file_uploader(
            "Upload your resume (PDF only)",
            type=['pdf'],
            help="Upload your resume in PDF format"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Display file info
            file_size = uploaded_file.size / (1024 * 1024)  # Convert to MB
            st.info(f"📊 File size: {file_size:.2f} MB")
    
    with col2:
        st.header("📝 Job Description")
        job_description = st.text_area(
            "Paste the job description here",
            height=300,
            placeholder="Paste the complete job description here...",
            help="Copy and paste the full job description for accurate analysis"
        )
        
        if job_description:
            char_count = len(job_description)
            st.info(f"📊 Character count: {char_count}")
    
    # Analyze button
    st.markdown("---")
    
    col_analyze, col_clear = st.columns([1, 1])
    
    with col_analyze:
        analyze_button = st.button(
            "🔍 Analyze Resume",
            type="primary",
            use_container_width=True,
            disabled=uploaded_file is None or not job_description
        )
    
    with col_clear:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.rerun()
    
    # Analysis section
    if analyze_button and uploaded_file and job_description:
        analyze_resume(uploaded_file, job_description, api_url)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>🚀 AI Resume Analyzer | Powered by FastAPI & Streamlit</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def test_api_connection(api_url: str):
    """Test connection to the backend API"""
    try:
        response = requests.get(f"{api_url}/api/health", timeout=5)
        if response.status_code == 200:
            st.success("✅ API connection successful!")
        else:
            st.error(f"❌ API returned status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to connect to API: {str(e)}")


def analyze_resume(uploaded_file, job_description: str, api_url: str):
    """Analyze resume against job description"""
    
    # Show loading spinner
    with st.spinner("🔄 Analyzing your resume... This may take a moment."):
        try:
            # Prepare files and data for API request
            files = {"resume": uploaded_file}
            data = {"job_description": job_description}
            
            # Make API request
            response = requests.post(
                f"{api_url}/api/match",
                files=files,
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                display_results(result)
            else:
                error_message = response.json().get("detail", "Unknown error occurred")
                st.error(f"❌ Analysis failed: {error_message}")
                
        except requests.exceptions.Timeout:
            st.error("❌ Request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Network error: {str(e)}")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")


def display_results(result: Dict[str, Any]):
    """Display analysis results"""
    
    st.markdown("---")
    st.header("📊 Analysis Results")
    
    # Match Score Section
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        match_score = result.get("match_score", 0)
        
        # Create gauge chart for match score
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = match_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Match Score"},
            delta = {'reference': 80},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Match score interpretation
        if match_score >= 80:
            st.success(f"🎉 Excellent match! Your resume aligns very well with the job requirements.")
        elif match_score >= 60:
            st.info(f"👍 Good match! Your resume has decent alignment with the job requirements.")
        elif match_score >= 40:
            st.warning(f"⚠️ Moderate match. Consider improving your resume for better alignment.")
        else:
            st.error(f"❌ Low match. Significant improvements needed to align with job requirements.")
    
    # Skills Analysis Section
    col_skills1, col_skills2 = st.columns(2)
    
    with col_skills1:
        st.subheader("✅ Matching Skills")
        matching_skills = result.get("matching_skills", [])
        
        if matching_skills:
            for skill in matching_skills:
                st.success(f"• {skill}")
        else:
            st.info("No matching skills found")
    
    with col_skills2:
        st.subheader("❌ Missing Skills")
        missing_skills = result.get("missing_skills", [])
        
        if missing_skills:
            for skill in missing_skills:
                st.error(f"• {skill}")
        else:
            st.success("No missing skills found!")
    
    # Suggestions Section
    st.subheader("💡 Suggestions for Improvement")
    suggestions = result.get("suggestions", [])
    
    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            st.info(f"{i}. {suggestion}")
    else:
        st.success("🎉 Your resume looks great! No specific suggestions at this time.")
    
    # Detailed Analytics
    with st.expander("📈 Detailed Analytics"):
        col_analytics1, col_analytics2 = st.columns(2)
        
        with col_analytics1:
            # Skills breakdown chart
            matching_count = len(matching_skills)
            missing_count = len(missing_skills)
            
            if matching_count > 0 or missing_count > 0:
                fig_pie = go.Figure(data=[go.Pie(
                    labels=['Matching Skills', 'Missing Skills'],
                    values=[matching_count, missing_count],
                    hole=0.3,
                    marker_colors=['green', 'red']
                )])
                fig_pie.update_layout(title="Skills Breakdown")
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_analytics2:
            # Skills statistics
            total_skills = matching_count + missing_count
            match_percentage = (matching_count / total_skills * 100) if total_skills > 0 else 0
            
            st.metric("Total Skills Analyzed", total_skills)
            st.metric("Skill Match Rate", f"{match_percentage:.1f}%")
            st.metric("Matching Skills", matching_count)
            st.metric("Missing Skills", missing_count)


if __name__ == "__main__":
    main()
