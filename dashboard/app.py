"""Streamlit dashboard for the Twitter Bot Showdown."""

import streamlit as st
import sqlite3
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="I Wonder Bot Showdown",
    page_icon="🤖",
    layout="wide"
)

# Title and header
st.title("🤖 I Wonder Social-Bot Showdown")
st.markdown("*One Twitter handle, five self-improving bots, emoji-signed shifts*")

# Check if database exists
db_path = "bot_showdown.db"
if not Path(db_path).exists():
    st.error("No bot showdown data found. Please start the orchestrator first!")
    st.code("python scripts/orchestrator.py")
    st.stop()

@st.cache_data(ttl=30)  # Cache for 30 seconds
def load_data():
    """Load data from SQLite database."""
    conn = sqlite3.connect(db_path)
    
    # Load tweets
    tweets_df = pd.read_sql_query(
        "SELECT * FROM tweets ORDER BY posted_at DESC",
        conn
    )
    
    # Load metrics
    metrics_df = pd.read_sql_query(
        "SELECT * FROM metrics ORDER BY timestamp DESC",
        conn
    )
    
    conn.close()
    
    return tweets_df, metrics_df

def get_latest_metrics(metrics_df):
    """Get the latest metrics."""
    if metrics_df.empty:
        return {
            'followers': 0,
            'total_tweets': 0,
            'total_likes': 0,
            'total_impressions': 0,
            'bot_stats': {}
        }
    
    latest = metrics_df.iloc[0]
    bot_stats = json.loads(latest['bot_stats']) if latest['bot_stats'] else {}
    
    return {
        'followers': latest['followers'],
        'total_tweets': latest['total_tweets'],
        'total_likes': latest['total_likes'],
        'total_impressions': latest['total_impressions'],
        'bot_stats': bot_stats
    }

# Load data
tweets_df, metrics_df = load_data()
latest_metrics = get_latest_metrics(metrics_df)

# Main metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "👥 Followers",
        latest_metrics['followers'],
        delta=None  # TODO: Calculate change
    )

with col2:
    st.metric(
        "📝 Total Tweets",
        latest_metrics['total_tweets'],
        delta=None
    )

with col3:
    st.metric(
        "❤️ Total Likes",
        latest_metrics['total_likes'],
        delta=None
    )

with col4:
    st.metric(
        "👁️ Total Impressions",
        latest_metrics['total_impressions'],
        delta=None
    )

# Progress towards goal
st.subheader("🎯 Progress Towards Goal")
target_followers = 1000
progress = min(latest_metrics['followers'] / target_followers, 1.0)
st.progress(progress)
st.caption(f"{latest_metrics['followers']}/{target_followers} followers ({progress*100:.1f}%)")

# Bot performance section
st.subheader("🤖 Bot Performance")

if latest_metrics['bot_stats']:
    bot_cols = st.columns(len(latest_metrics['bot_stats']))
    
    for i, (bot_type, stats) in enumerate(latest_metrics['bot_stats'].items()):
        with bot_cols[i]:
            st.markdown(f"### {stats['emoji']} {stats['name']}")
            st.metric("Posts Created", stats['stats']['posts_created'])
            st.metric("Improvements", stats['stats']['improvements_made'])
            
            if stats['enabled']:
                st.success("✅ Active")
            else:
                st.warning("⏸️ Disabled")

# Recent tweets
st.subheader("📱 Recent Tweets")

if not tweets_df.empty:
    # Show last 10 tweets
    recent_tweets = tweets_df.head(10)
    
    for _, tweet in recent_tweets.iterrows():
        # Get bot emoji
        bot_emoji = "🤖"  # Default
        if latest_metrics['bot_stats'].get(tweet['bot_type']):
            bot_emoji = latest_metrics['bot_stats'][tweet['bot_type']]['emoji']
        
        with st.container():
            col1, col2 = st.columns([1, 4])
            
            with col1:
                st.markdown(f"### {bot_emoji}")
                st.caption(tweet['bot_type'].replace('_', ' ').title())
                st.caption(pd.to_datetime(tweet['posted_at']).strftime("%H:%M"))
            
            with col2:
                st.markdown(f"**{tweet['content']}**")
                
                # Engagement metrics
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                with metrics_col1:
                    st.caption(f"❤️ {tweet['likes']}")
                with metrics_col2:
                    st.caption(f"💬 {tweet['replies']}")
                with metrics_col3:
                    st.caption(f"👁️ {tweet['impressions']}")
        
        st.divider()

else:
    st.info("No tweets posted yet. The orchestrator will start posting soon.")

# Charts section
if not metrics_df.empty and len(metrics_df) > 1:
    st.subheader("📊 Analytics")
    
    # Prepare time series data
    metrics_df['timestamp'] = pd.to_datetime(metrics_df['timestamp'])
    metrics_df = metrics_df.sort_values('timestamp')
    
    # Followers over time
    fig_followers = px.line(
        metrics_df, 
        x='timestamp', 
        y='followers',
        title="Followers Over Time",
        labels={'followers': 'Followers', 'timestamp': 'Time'}
    )
    st.plotly_chart(fig_followers, use_container_width=True)
    
    # Tweet engagement
    if not tweets_df.empty:
        # Engagement by bot type
        engagement_by_bot = tweets_df.groupby('bot_type').agg({
            'likes': 'sum',
            'replies': 'sum',
            'impressions': 'sum'
        }).reset_index()
        
        fig_engagement = px.bar(
            engagement_by_bot,
            x='bot_type',
            y=['likes', 'replies', 'impressions'],
            title="Engagement by Bot Type",
            labels={'value': 'Count', 'bot_type': 'Bot Type'}
        )
        st.plotly_chart(fig_engagement, use_container_width=True)

# Bot showdown rules
with st.expander("📋 Showdown Rules"):
    st.markdown("""
    ### The Bots
    - **🪲 Self-Refine Bot**: Draft → self-critique → rewrite (every post)
    - **👾 DPO Bot**: A/B test tweets, mini-LoRA after +5 likes delta (continuous)
    - **🐾 RLAIF Bot**: GPT-4o judge scores with PPO updates (every 3 drafts)
    - **🦕 Mind-Pool Bot**: 6 personas compete, top-2 survive (every 50 impressions)
    - **🦍 DevOps Self-Fix Bot**: Monitors & auto-patches other bots (every 60s)
    
    ### Goals
    - 🎯 **1,000 followers** in ≤ 7 days
    - 📚 **80% accuracy** in identifying which bot posted what
    - 🧠 **50% of viewers** can apply ≥ 2 improvement loops
    - ⭐ **250 GitHub stars** in 30 days
    """)

# Auto-refresh
st.markdown("---")
st.caption("Dashboard auto-refreshes every 30 seconds. Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# Add some styling
st.markdown("""
<style>
    .stMetric > label {
        font-size: 14px !important;
    }
    .stProgress .st-bo {
        background-color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True) 