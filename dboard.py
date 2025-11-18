import streamlit as st
import requests
import json
import plotly.graph_objects as go
import plotly.express as px
from urllib.parse import urlparse
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Instagram Sentiment Analysis",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        margin: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
    }
    
    .metric-card > div {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;    
    }
    
    .sentiment-positive {
        background: rgba(16, 185, 129, 0.3);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .sentiment-negative {
        background: rgba(239, 68, 68, 0.3);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .sentiment-neutral {
        background: rgba(107, 114, 128, 0.3);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .improved-caption-card {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3rem;
        font-weight: 600;
    }
    .comparison-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e5e7eb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title with gradient
st.markdown("""
<div class="main-header">
    <h1>SocioLens Sentiment Classifier</h1>
    <p>Analyze and improve Instagram post captions with AI-powered sentiment analysis</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    backend_url = st.text_input(
        "Sentiment Analysis URL",
        value="http://localhost:8000",
        help="URL of your sentiment analysis backend"
    )
    
    # paraphrase_url = st.text_input(
    #     "Caption Improvement URL",
    #     value="http://example.com/paraphrase",
    #     help="URL of your LLM paraphrase endpoint"
    # )
    
    st.markdown("---")
    
    st.markdown("### 📖 How to use:")
    st.markdown("""
    1. 📱 Paste an Instagram post URL or enter caption text
    2. 🔍 Click 'Analyze Sentiment'
    3. ✨ Optionally improve your caption with AI
    4. 📋 Copy the improved version
    """)
    
    st.markdown("---")
    
    st.markdown("### 🎨 Features:")
    st.markdown("""
    - Real-time sentiment analysis
    - AI-powered caption improvement
    - Visual sentiment distribution
    - Side-by-side comparison
    - One-click copy to clipboard
    """)

# Initialize session state
if "url_caption_input" not in st.session_state:
    st.session_state["url_caption_input"] = ""
if "direct_caption_input" not in st.session_state:
    st.session_state["direct_caption_input"] = ""
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None
if "improved_caption" not in st.session_state:
    st.session_state["improved_caption"] = None
if "original_caption" not in st.session_state:
    st.session_state["original_caption"] = ""

# Main input section
col1, col2 = st.columns([2, 1])

with col1:
    input_method = st.radio(
        "Choose input method:",
        ["Instagram Post URL", "Direct Caption Text"],
        horizontal=True
    )
    
    caption_text = ""

    if input_method == "Instagram Post URL":
        post_url = st.text_input(
            "Instagram Post URL",
            placeholder="https://www.instagram.com/p/...",
            help="Paste the Instagram post link here"
        )
        
        fetch_caption_button = st.button("🔗 Fetch Caption from URL", use_container_width=True)
        
        if fetch_caption_button:
            if not post_url:
                st.error("⚠️ Please provide a valid URL to fetch caption from.")
                st.stop()
            with st.spinner("🔄 Fetching caption from Instagram..."):
                try:
                    caption_text_fetched = None
                    caption_text_fetched_response = requests.post(
                        f"{backend_url}/service/caption/instagram",
                        json={"url": post_url},
                        headers={"Content-Type": "application/json"},
                        timeout=120
                    )
                
                    try:
                        if caption_text_fetched_response.status_code == 200:
                            # Try to parse JSON safely
                            try:
                                caption_text_fetched = caption_text_fetched_response.json()
                            except Exception:
                                st.warning("⚠️ Could not parse response as JSON.")
                                st.session_state['url_caption_input'] = ""
                                st.stop()

                            # Case: valid JSON & caption exists
                            if caption_text_fetched:
                                st.session_state['url_caption_input'] = caption_text_fetched['caption']
                                st.success("✅ Caption fetched successfully!")
                            else:
                                # JSON ok but empty caption
                                st.session_state['url_caption_input'] = ""
                                st.warning("⚠️ No caption found or caption is empty.")

                        else:
                            # Handle non-200 HTTP responses
                            st.session_state['url_caption_input'] = ""
                            st.error(f"❌ Server returned an error: {caption_text_fetched_response.status_code}")

                    except Exception as e:
                        # Network error / request failed / unknown error
                        st.session_state['url_caption_input'] = ""
                        st.error(f"❌ Failed to fetch caption: {str(e)}")

                except Exception as e:
                    st.session_state['url_caption_input'] = ""
                    st.error(f"❌ Error fetching caption: {str(e)}")
        
        if st.session_state.get('url_caption_input'):
            st.markdown("### 📝 Fetched Caption (editable)")
            caption_text = st.text_area(
                "Caption:",
                height=150,
                key="url_caption_input"
            )
        else:
            caption_text = ""

    else:
        caption_text = st.text_area(
            "Enter caption text:",
            height=150,
            placeholder="Type or paste the text you want to analyze...",
            key="direct_caption_input"
        )

with col2:
    st.markdown("### 📊 Quick Stats")
    if caption_text:
        char_count = len(caption_text)
        word_count = len(caption_text.split())
        
        st.markdown(f"""
        <div class="metric-card">
            <div>{char_count}</idv>
            <div>Characters</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <div>{word_count}</div>
            <div>Words</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("📝 Enter caption to see stats")

# Analyze button
st.markdown("---")
analyze_button = st.button("🔍 Analyze Sentiment", type="primary", use_container_width=True)

# Analysis section
if analyze_button:
    if not caption_text or caption_text.strip() == "":
        st.error("⚠️ Please enter some text to analyze!")
    else:
        st.session_state["original_caption"] = caption_text
        st.session_state["improved_caption"] = None  # Reset improved caption
        
        with st.spinner("Analyzing sentiment..."):
            try:
                response = requests.post(
                    f"{backend_url}/service",
                    json={"text": caption_text},
                    headers={"Content-Type": "application/json"},
                    timeout=120
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state["analysis_result"] = result
                    
                else:
                    st.error(f"❌ Error: Backend returned status code {response.status_code}")
                    st.error(f"Response: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend. Please ensure your backend is running at the specified URL.")
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. The backend took too long to respond.")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")

# Display results if available
if st.session_state.get("analysis_result"):
    result = st.session_state["analysis_result"]
    
    st.success("✅ Analysis Complete!")
    
    # Main sentiment result with gradient background
    sentiment = result['predicted_label']
    confidence_pct = result['confidence'] * 100
    
    sentiment_class = f"sentiment-{sentiment}"
    
    st.markdown(f"""
    <div class="{sentiment_class}">
        <h2>🎯 Predicted Sentiment: {sentiment.upper()}</h2>
        <h3>Confidence: {confidence_pct:.2f}%</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Visualization section
    st.markdown("---")
    st.subheader("📊 Sentiment Distribution")
    
    chart_col1, chart_col2, chart_col3 = st.columns(3)
    
    scores_dict = result['all_scores']
    labels = list(scores_dict.keys())
    values = [scores_dict[label] * 100 for label in labels]
    
    with chart_col1:
        # Bar chart
        colors = ['#667eea' if label == result['predicted_label'] else '#e5e7eb' 
                 for label in labels]
        
        fig_bar = go.Figure(data=[
            go.Bar(
                x=labels,
                y=values,
                marker_color=colors,
                text=[f"{v:.2f}%" for v in values],
                textposition='auto',
            )
        ])
        
        fig_bar.update_layout(
            title="Sentiment Scores",
            xaxis_title="Sentiment",
            yaxis_title="Confidence (%)",
            height=350,
            showlegend=False,
            hovermode='x',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with chart_col2:
        # Pie chart
        fig_pie = go.Figure(data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker=dict(
                    colors=['#667eea', '#764ba2', '#f59e0b', '#10b981'][:len(labels)]
                ),
                textinfo='label+percent',
                textposition='auto'
            )
        ])
        
        fig_pie.update_layout(
            title="Distribution",
            height=350,
            showlegend=True,
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with chart_col3:
        # Radar chart
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=values,
            theta=labels,
            fill='toself',
            line_color='#667eea'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=False,
            title="Radar View",
            height=350,
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
    
    # Detailed scores
    st.markdown("---")
    st.subheader("📈 Detailed Scores")
    
    scores_df = pd.DataFrame([
        {
            "Sentiment": label.upper(),
            "Score": score,
            "Percentage": f"{score * 100:.2f}%",
            "Status": "✅ Predicted" if label == result['predicted_label'] else ""
        }
        for label, score in sorted(
            result['all_scores'].items(),
            key=lambda x: x[1],
            reverse=True
        )
    ])
    
    st.dataframe(
        scores_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Caption Improvement Section
    st.markdown("---")
    st.subheader("Caption Enhancement")
    
    improve_col1, improve_col2 = st.columns([1, 3])
    
    with improve_col1:
        improve_button = st.button(
            "🚀 Improve Caption with AI",
            type="secondary",
            use_container_width=True,
            help="Use LLM to generate an improved version of your caption"
        )
    
    with improve_col2:
        st.info("💡 Click to generate an AI-enhanced version of your caption with better sentiment")
    
    if improve_button:
        with st.spinner("Generating improved caption..."):
            try:
                paraphrase_response = requests.post(
                    f"{backend_url}/service/caption/optimize",
                    json={
                        "caption": st.session_state["original_caption"],
                        "sentiment": result['predicted_label'],
                        # "target_sentiment": "positive"  # Optional: specify target sentiment
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=120
                )
                
                if paraphrase_response.status_code == 200:
                    improved_data = paraphrase_response.json()
                    # Assuming the response has 'improved_text' field
                    st.session_state["improved_caption"] = improved_data['caption']
                    st.success("✅ Caption improved successfully!")
                else:
                    st.error(f"❌ Error: Paraphrase API returned status code {paraphrase_response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to paraphrase API. Please check the URL.")
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out.")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
    
    # Display improved caption if available
    if st.session_state.get("improved_caption"):
        st.markdown("### Comparison")
        
        comp_col1, comp_col2 = st.columns(2)
        
        with comp_col1:
            st.markdown("#### 📝 Original Caption")
            st.markdown(st.session_state["original_caption"])
            
            # st.markdown(f"""
            # <div class="comparison-card">
            #     <p>{st.session_state["original_caption"]}</p>
            # </div>
            # """, unsafe_allow_html=True)
            
            if st.button("📋 Copy Original", key="copy_original", use_container_width=True):
                st.code(st.session_state["original_caption"], language=None)
                st.success("✅ Original caption ready to copy!")
        
        with comp_col2:
            st.markdown("#### Improved Caption")
            st.markdown(st.session_state["improved_caption"])
            # st.markdown(f"""
            # <div class="improved-caption-card">
            #     <p>{st.session_state["improved_caption"]}</p>
            # </div>
            # """, unsafe_allow_html=True)
            
            if st.button("📋 Copy Improved", key="copy_improved", use_container_width=True):
                st.code(st.session_state["improved_caption"], language=None)
                st.success("✅ Improved caption ready to copy!")
        
        # Re-analyze improved caption option
        st.markdown("---")
        if st.button("🔄 Re-analyze Improved Caption", use_container_width=True):
            with st.spinner("🔄 Analyzing improved caption..."):
                try:
                    reanalysis_response = requests.post(
                        backend_url,
                        json={"text": st.session_state["improved_caption"]},
                        headers={"Content-Type": "application/json"},
                        timeout=120
                    )
                    
                    if reanalysis_response.status_code == 200:
                        new_result = reanalysis_response.json()
                        
                        st.success("✅ Re-analysis Complete!")
                        
                        # Show comparison metrics
                        metric_col1, metric_col2, metric_col3 = st.columns(3)
                        
                        with metric_col1:
                            st.metric(
                                "Original Sentiment",
                                result['predicted_label'].upper(),
                                help="Original caption sentiment"
                            )
                        
                        with metric_col2:
                            st.metric(
                                "Improved Sentiment",
                                new_result['predicted_label'].upper(),
                                delta=f"{(new_result['confidence'] - result['confidence']) * 100:.1f}%",
                                help="Improved caption sentiment"
                            )
                        
                        with metric_col3:
                            confidence_change = (new_result['confidence'] - result['confidence']) * 100
                            st.metric(
                                "Confidence Change",
                                f"{confidence_change:+.2f}%",
                                help="Change in confidence score"
                            )
                        
                except Exception as e:
                    st.error(f"❌ Error during re-analysis: {str(e)}")
    
    # Show raw response (optional)
    with st.expander("🔍 View Raw API Response"):
        st.json(result)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p style='font-size: 14px;'>⚡ Powered by <strong>SocioLens</strong></p>
    <p style='font-size: 12px;'>AI-Powered Sentiment Analysis & Caption Enhancement</p>
</div>
""", unsafe_allow_html=True)