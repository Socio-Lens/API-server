import streamlit as st
import requests
import json
import plotly.graph_objects as go
import plotly.express as px
from urllib.parse import urlparse
from scripts.scrapper import caption_from_post_url

# Page configuration
st.set_page_config(
    page_title="Instagram Sentiment Analysis",
    page_icon="assets/logo.png",
    layout="wide"
)

# Title and description
st.title("SocioLens Sentiment Classifier")
st.markdown("Analyze the sentiment of Instagram post captions using AI-powered sentiment analysis.")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    backend_url = st.text_input(
        "Backend URL",
        value="http://localhost:8000/service",
        help="URL of your sentiment analysis backend"
    )
    st.markdown("---")
    st.markdown("### How to use:")
    st.markdown("1. Paste an Instagram post URL")
    st.markdown("2. Or directly enter the caption text")
    st.markdown("3. Click 'Analyze Sentiment'")

# Ensure session state keys exist to avoid KeyError
if "url_caption_input" not in st.session_state:
    st.session_state["url_caption_input"] = ""
if "direct_caption_input" not in st.session_state:
    st.session_state["direct_caption_input"] = ""

# Main input section
col1, col2 = st.columns([2, 1])

with col1:
    input_method = st.radio(
        "Choose input method:",
        ["Instagram Post URL", "Direct Caption Text"],
        horizontal=True
    )
    
    caption_text = ""  # ensure caption_text is always defined for later use

    if input_method == "Instagram Post URL":
        post_url = st.text_input(
            "Instagram Post URL",
            placeholder="https://www.instagram.com/p/...",
            help="Paste the Instagram post link here"
        )
        
        fetch_caption_button = st.button("🔗 Fetch Caption from URL", use_container_width=True)
        
        if fetch_caption_button:
            if not post_url:
                st.error("Provide a valid URL to fetch caption from.")
                st.stop()
            with st.spinner("Fetching caption from Instagram..."):
                try:
                    caption_text_fetched = caption_from_post_url(post_url)
                    if caption_text_fetched:
                        # Store fetched caption into the text_area's session_state key
                        st.session_state['url_caption_input'] = caption_text_fetched
                        st.success("✅ Caption fetched successfully!")
                    else:
                        st.session_state['url_caption_input'] = ""
                        st.warning("⚠️ No caption found or caption is empty.")
                except Exception as e:
                    st.session_state['url_caption_input'] = ""
                    st.error(f"❌ Error fetching caption: {str(e)}")
        
        # ONLY show the caption text area if a caption has been fetched
        if st.session_state.get('url_caption_input'):
            st.markdown("### ✏️ Fetched Caption (editable)")
            caption_text = st.text_area(
                "Caption:",
                height=150,
                key="url_caption_input"
            )
            # small control row to clear fetched caption
            clear_col1, clear_col2 = st.columns([1, 3])
            with clear_col1:
                if st.button("Clear fetched caption"):
                    st.session_state['url_caption_input'] = ""
                    st.experimental_rerun()
        else:
            caption_text = ""  # no caption available yet; keep blank

    else:
        # Direct caption text area bound to its own key
        caption_text = st.text_area(
            "Enter caption text:",
            height=150,
            placeholder="Type or paste the text you want to analyze...",
            key="direct_caption_input"
        )

with col2:
    st.markdown("### Quick Stats")
    if caption_text:
        char_count = len(caption_text)
        word_count = len(caption_text.split())
        st.metric("Characters", char_count)
        st.metric("Words", word_count)
    else:
        st.write("No caption to analyze yet.")

# Analyze button
analyze_button = st.button("🔍 Analyze Sentiment", type="primary", use_container_width=True)

# Analysis section
if analyze_button:
    if not caption_text or caption_text.strip() == "":
        st.error("⚠️ Please enter some text to analyze!")
    else:
        with st.spinner("Analyzing sentiment..."):
            try:
                # Make API call to backend
                response = requests.post(
                    backend_url,
                    json={"text": caption_text},
                    headers={"Content-Type": "application/json"},
                    timeout=120
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display results
                    st.success("Analysis Complete!")
                    
                    # Main metrics
                    st.markdown("---")
                    st.subheader("Sentiment Results")
                    
                    metric_col1, metric_col2 = st.columns(2)
                    
                    with metric_col1:
                        st.metric(
                            "Predicted Sentiment",
                            result['predicted_label'].upper(),
                            help="The predicted sentiment category"
                        )
                    
                    with metric_col2:
                        confidence_pct = result['confidence'] * 100
                        st.metric(
                            "Confidence",
                            f"{confidence_pct:.2f}%",
                            help="Model's confidence in the prediction"
                        )
                    
                    # Visualization section
                    st.markdown("---")
                    st.subheader("Sentiment Distribution")
                    
                    chart_col1, chart_col2 = st.columns(2)
                    
                    with chart_col1:
                        # Bar chart
                        scores_dict = result['all_scores']
                        labels = list(scores_dict.keys())
                        values = [scores_dict[label] * 100 for label in labels]
                        
                        # Color code based on predicted label
                        colors = ['#FF4B4B' if label == result['predicted_label'] else '#E0E0E0' 
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
                            title="Sentiment Scores (Bar Chart)",
                            xaxis_title="Sentiment",
                            yaxis_title="Confidence (%)",
                            height=400,
                            showlegend=False,
                            hovermode='x'
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
                                    colors=px.colors.qualitative.Set3[:len(labels)]
                                ),
                                textinfo='label+percent',
                                textposition='auto'
                            )
                        ])
                        
                        fig_pie.update_layout(
                            title="Sentiment Distribution (Pie Chart)",
                            height=400,
                            showlegend=True
                        )
                        
                        st.plotly_chart(fig_pie, use_container_width=True)
                    
                    # Detailed scores table
                    st.markdown("---")
                    st.subheader("Detailed Scores")
                    
                    # Create a formatted table
                    import pandas as pd
                    
                    scores_df = pd.DataFrame([
                        {
                            "Sentiment": label.upper(),
                            "Score": score,
                            "Percentage": f"{score * 100:.2f}%",
                            "Is Predicted": "✅" if label == result['predicted_label'] else ""
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
                    
                    # Show raw response (optional)
                    with st.expander("View Raw API Response"):
                        st.json(result)
                    
                else:
                    st.error(f"Error: Backend returned status code {response.status_code}")
                    st.error(f"Response: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend. Please ensure your backend is running at the specified URL.")
            except requests.exceptions.Timeout:
                st.error("Request timed out. The backend took too long to respond.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Powered by SocioLens</p>
    </div>
    """,
    unsafe_allow_html=True
)
