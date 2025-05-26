import streamlit as st
import pandas as pd
import plotly.express as px

# Set page title and wide layout for better visualization
st.set_page_config(page_title="Interactive Media Intelligence Dashboard – Ramadan Campaign", layout="wide")

# --- Title ---
st.title("📊 Interactive Media Intelligence Dashboard")
st.markdown("## Ramadan Campaign Performance Overview")
st.markdown("Upload your media data to analyze sentiment, engagement trends, platform performance, and more.")

# --- 1. Ask the user to upload a CSV file ---
st.header("1. Upload Your Data")
uploaded_file = st.file_uploader("Drag and drop your CSV file here or click to browse", type=["csv"])

df = None # Initialize df outside the if block

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("CSV file uploaded successfully! Processing data...")

        # --- 2. Clean the data (silent processing) ---
        # Normalize column names
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

        # Check for required columns before proceeding
        required_columns = ['date', 'platform', 'sentiment', 'location', 'engagements', 'media_type']
        if not all(col in df.columns for col in required_columns):
            st.error(f"Error: Missing one or more required columns after cleaning. Please ensure your CSV has these columns: **{', '.join(col.capitalize() for col in required_columns)}**.")
            df = None # Invalidate df if columns are missing
        else:
            # Convert 'Date' to datetime
            try:
                df['date'] = pd.to_datetime(df['date'])
            except Exception:
                st.error("Error: 'Date' column could not be converted to a datetime format. Please check your data.")
                df = None

            # Fill missing 'Engagements' with 0 and ensure numeric
            if df is not None: # Check if df is still valid after date conversion
                df['engagements'] = pd.to_numeric(df['engagements'], errors='coerce').fillna(0)
                # If there were NaNs due to coercion, a warning could be added here if desired,
                # but for cleaner UI, we'll keep it silent unless critical.

            if df is not None:
                st.success("Data successfully cleaned and prepared for analysis!")
                # Optional: Show a small glimpse of cleaned data if user insists (e.g., via expander)
                with st.expander("Preview Cleaned Data"):
                    st.dataframe(df.head())

    except pd.errors.EmptyDataError:
        st.error("The uploaded CSV file is empty. Please upload a file with data.")
        df = None
    except pd.errors.ParserError:
        st.error("Could not parse the CSV file. Please ensure it's a valid CSV format.")
        df = None
    except Exception as e:
        st.error(f"An unexpected error occurred during file processing: {e}. Please check your CSV file and try again.")
        df = None

# Only display charts if data was successfully loaded and cleaned
if df is not None:
    st.markdown("---")
    # --- 3. Build 5 interactive charts using Plotly ---
    st.header("3. Interactive Campaign Performance Charts")
    st.markdown("Explore key metrics and insights from your media data.")

    # Using columns for better layout of charts
    col1, col2 = st.columns(2)

    with col1:
        # 1. Pie chart: Sentiment Breakdown
        st.subheader("😄 Sentiment Breakdown")
        sentiment_counts = df['sentiment'].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        fig_sentiment = px.pie(sentiment_counts, values='Count', names='Sentiment',
                               title='**Overall Sentiment Distribution**', hole=0.3,
                               color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_sentiment.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_sentiment, use_container_width=True)
        st.markdown("""
        **Top 3 Insights: Sentiment Breakdown**
        * Quickly grasp the **overall tone** of your media mentions (positive, negative, neutral).
        * Identify if your campaign is generating more positive buzz or requires **attention to negative feedback**.
        * Benchmark current sentiment against past campaigns to track **brand perception evolution**.
        """)

    with col2:
        # 2. Bar chart: Platform Engagements
        st.subheader("🌐 Engagements by Platform")
        platform_engagements = df.groupby('platform')['engagements'].sum().reset_index()
        platform_engagements = platform_engagements.sort_values(by='engagements', ascending=False)
        fig_platform_engagements = px.bar(platform_engagements, x='engagements', y='platform', orientation='h',
                                           title='**Total Engagements Across Platforms**',
                                           labels={'platform': 'Platform', 'engagements': 'Total Engagements'},
                                           color_discrete_sequence=px.colors.qualitative.Plotly)
        fig_platform_engagements.update_layout(yaxis={'categoryorder':'total ascending'}) # Ensure highest is at top
        st.plotly_chart(fig_platform_engagements, use_container_width=True)
        st.markdown("""
        **Top 3 Insights: Platform Engagements**
        * Discover **which platforms are driving the most engagement**, indicating where your audience is most active.
        * Allocate your marketing budget and effort more effectively to **high-performing platforms**.
        * Identify platforms that might be **underperforming** and require a revised content strategy.
        """)

    st.markdown("---")

    # Line chart gets its own full width
    st.subheader("📈 Engagement Trend Over Time")
    engagements_over_time = df.groupby('date')['engagements'].sum().reset_index()
    fig_engagement_trend = px.line(engagements_over_time, x='date', y='engagements',
                                   title='**Total Engagements Trend Throughout the Campaign**',
                                   labels={'date': 'Date', 'engagements': 'Total Engagements'},
                                   markers=True, line_shape='spline',
                                   color_discrete_sequence=['#FF4B4B']) # Streamlit red-ish
    fig_engagement_trend.update_xaxes(rangeselector_buttons=list([
        dict(count=1, label="1m", step="month", stepmode="backward"),
        dict(count=6, label="6m", step="month", stepmode="backward"),
        dict(count=1, label="YTD", step="year", stepmode="todate"),
        dict(count=1, label="1y", step="year", stepmode="backward"),
        dict(step="all")
    ]))
    st.plotly_chart(fig_engagement_trend, use_container_width=True)
    st.markdown("""
    **Top 3 Insights: Engagement Trend Over Time**
    * Pinpoint **peak engagement periods**, which could correlate with specific campaign launches or events.
    * Observe the **growth or decline** of engagement, indicating campaign momentum or waning interest.
    * Detect any **sudden spikes or dips** that might be linked to external factors or PR incidents.
    """)

    st.markdown("---")

    col3, col4 = st.columns(2)

    with col3:
        # 4. Pie chart: Media Type Mix
        st.subheader("🖼️ Media Type Mix")
        media_type_counts = df['media_type'].value_counts().reset_index()
        media_type_counts.columns = ['Media Type', 'Count']
        fig_media_type = px.pie(media_type_counts, values='Count', names='Media Type',
                               title='**Distribution of Content Media Types**', hole=0.3,
                               color_discrete_sequence=px.colors.qualitative.Set3)
        fig_media_type.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_media_type, use_container_width=True)
        st.markdown("""
        **Top 3 Insights: Media Type Mix**
        * Understand the **prevalence of different content formats** (e.g., video, image, text) in your campaign.
        * Assess if your media mix aligns with **audience preferences** and platform best practices.
        * Identify opportunities to diversify content to **reach broader segments** of your target audience.
        """)

    with col4:
        # 5. Bar chart: Top 5 Locations
        st.subheader("📍 Top 5 Locations")
        location_engagements = df.groupby('location')['engagements'].sum().reset_index()
        top_5_locations = location_engagements.sort_values(by='engagements', ascending=False).head(5)
        fig_top_locations = px.bar(top_5_locations, x='location', y='engagements',
                                   title='**Top 5 Locations by Total Engagements**',
                                   labels={'location': 'Location', 'engagements': 'Total Engagements'},
                                   color_discrete_sequence=px.colors.qualitative.Vivid)
        st.plotly_chart(fig_top_locations, use_container_width=True)
        st.markdown("""
        **Top 3 Insights: Top 5 Locations**
        * Pinpoint the **geographic hotspots** where your campaign is generating the most interest.
        * Inform **localized marketing efforts** and resource allocation in high-engagement areas.
        * Discover potential **untapped markets** if key target regions are not appearing in the top 5.
        """)

    st.markdown("---")

else:
    st.info("Please upload your CSV file above to start analyzing your Ramadan Campaign data.")

# --- Suggestions for Improvement (Sidebar) ---
st.sidebar.header("🚀 Enhance Your Dashboard")
st.sidebar.markdown("""
Consider adding these features for an even more powerful analysis:

* **Date Range Filtering:** Allow users to select specific date ranges for analysis.
* **Interactive Filters:** Add dropdowns or multi-select options for `Platform`, `Sentiment`, and `Media Type`.
* **Dynamic Top N:** Let users choose how many top locations or platforms to display.
* **Export Options:** Enable downloading charts or a summary report.
* **Deep Dive Analytics:** Implement more specific charts, like sentiment trend per platform, or engagement by media type over time.
* **Performance Metrics:** Calculate and display key performance indicators (KPIs) like average engagement rate.
""")
