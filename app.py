import streamlit as st 
import pandas as pd 
import numpy as np 
import plotly.graph_objects as go 
import plotly.express as px 
import os 
from dotenv import load_dotenv 
from groq import Groq 
 
# ========================================================= 
# PAGE CONFIG 
# ========================================================= 
st.set_page_config( 
    page_title="DHEIS — District Health & Education Intelligence System", 
    page_icon="🗺️", 
    layout="wide", 
    initial_sidebar_state="expanded" 
) 
 
# Initialize Session State 
if "current_page" not in st.session_state: 
    st.session_state["current_page"] = "DHEIS OVERVIEW" 
if "diagnostic_view" not in st.session_state: 
    st.session_state["diagnostic_view"] = "state" 
if "selected_district_global" not in st.session_state: 
    st.session_state["selected_district_global"] = "None" 
if "action_selected_district" not in st.session_state: 
    st.session_state["action_selected_district"] = "None" 
if "show_full_action_list" not in st.session_state: 
    st.session_state["show_full_action_list"] = False 
 
# ========================================================= 
# GROQ / AI SETUP 
# ========================================================= 
load_dotenv() 
groq_api_key = os.getenv("GROQ_API_KEY") 
if not groq_api_key: 
    try: 
        groq_api_key = st.secrets.get("GROQ_API_KEY") 
    except Exception: 
        groq_api_key = None 
client = Groq(api_key=groq_api_key) if groq_api_key else None 
 
# ========================================================= 
# GLOBAL STYLING & COLOR SCHEME 
# ========================================================= 
TIER_COLORS = {"High": "#D64545", "Medium": "#E0A030", "Low": "#4C9A5B"} 
 
st.markdown(""" 
<style> 
    .stApp { 
        background-color: #0E1626; 
        color: #E0E6ED; 
    } 
 
    h1, h2, h3, h4, h5, h6 { 
        color: #FFFFFF !important; 
        font-weight: 600; 
    } 
     
    /* ===================================================== 
       Metrics UI Cards 
       ===================================================== */ 
    [data-testid="stMetric"] { 
        background-color: #162238; 
        border: 1px solid #233454; 
        border-radius: 8px; 
        padding: 12px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.2); 
    } 
 
    [data-testid="stMetricLabel"] { 
        color: #8A99AD !important; 
        font-size: 13px !important; 
        font-weight: 500; 
    } 
 
    [data-testid="stMetricValue"] { 
        color: #FFFFFF !important; 
        font-weight: 700 !important; 
        font-size: 24px !important; 
    } 
 
    /* ===================================================== 
       Custom Cards 
       ===================================================== */ 
    .dashboard-card { 
        background-color: #162238; 
        border: 1px solid #233454; 
        border-radius: 8px; 
        padding: 16px; 
        margin-bottom: 12px; 
    } 
 
    .card-title { 
        font-size: 14px; 
        font-weight: 700; 
        color: #A0B2C6; 
        text-transform: uppercase; 
        letter-spacing: 0.5px; 
        margin-bottom: 12px; 
    } 
 
    .compact-title { 
        margin-bottom: -18px !important; 
    } 
 
    /* ===================================================== 
       Buttons 
       ===================================================== */ 
    .stButton > button { 
        background-color: #1F3B4D; 
        color: white; 
        border-radius: 6px; 
        border: 1px solid #344D67; 
        font-weight: 600; 
    } 
 
    .stButton > button:hover { 
        background-color: #0F6E56; 
        color: white; 
        border-color: #0F6E56; 
    } 
 
    /* ===================================================== 
       SIDEBAR BASE 
       ===================================================== */ 
    section[data-testid="stSidebar"] { 
        background-color: #0A101D; 
        border-right: 1px solid #1E2D4A; 
    } 
 
    section[data-testid="stSidebar"] > div { 
        padding-top: 1.2rem; 
        padding-left: 1rem; 
        padding-right: 1rem; 
    } 
 
    /* ===================================================== 
       DHEIS SIDEBAR BRAND 
       ===================================================== */ 
    .sidebar-brand { 
        padding: 4px 4px 18px 4px; 
        margin-bottom: 6px; 
    } 
 
    .sidebar-brand-title { 
        color: #FFFFFF; 
        font-size: 27px; 
        font-weight: 800; 
        letter-spacing: 0.4px; 
        line-height: 1.1; 
        margin: 0; 
    } 
 
    .sidebar-brand-icon { 
        font-size: 25px; 
        margin-right: 5px; 
    } 
 
    .sidebar-brand-subtitle { 
        color: #7F91A8; 
        font-size: 10.5px; 
        font-weight: 500; 
        line-height: 1.45; 
        margin-top: 7px; 
        letter-spacing: 0.15px; 
    } 
 
    /* ===================================================== 
       SIDEBAR SECTION TITLES 
       ===================================================== */ 
    .sidebar-section-title { 
        color: #6F829B; 
        font-size: 10px; 
        font-weight: 800; 
        letter-spacing: 1.2px; 
        text-transform: uppercase; 
        margin: 16px 4px 8px 4px; 
    } 
 
    .sidebar-divider { 
        height: 1px; 
        background: #1E2D4A; 
        margin: 3px 0 15px 0; 
    } 
 
    /* ===================================================== 
       NAVIGATION - BUTTON STYLE 
       ===================================================== */ 
 
    /* Remove default radio spacing */ 
    section[data-testid="stSidebar"] div[role="radiogroup"] { 
        gap: 6px !important; 
        width: 100%; 
    } 
 
    /* Hide radio circles */ 
    section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { 
        display: none !important; 
    } 
 
    /* Navigation button container */ 
    section[data-testid="stSidebar"] div[role="radiogroup"] > label { 
        width: 100% !important; 
        min-height: 43px !important; 
        padding: 0 !important; 
        margin: 0 !important; 
        border: 1px solid #1D2B43 !important; 
        border-radius: 7px !important; 
        background: #111C2E !important; 
        transition: all 0.18s ease-in-out !important; 
        cursor: pointer !important; 
        box-sizing: border-box !important; 
    } 
 
    /* Navigation text */ 
    section[data-testid="stSidebar"] div[role="radiogroup"] > label p { 
        color: #9DADC0 !important; 
        font-size: 12px !important; 
        font-weight: 650 !important; 
        letter-spacing: 0.2px !important; 
        margin: 0 !important; 
        padding: 12px 12px !important; 
    } 
 
    /* Hover effect - pressing button feel */ 
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover { 
        background: #18263B !important; 
        border-color: #344D67 !important; 
        transform: translateX(2px); 
    } 
 
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover p { 
        color: #FFFFFF !important; 
    } 
 
    /* Active navigation button */ 
    section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] { 
        background: #1F3B4D !important; 
        border: 1px solid #3D6178 !important; 
        box-shadow: inset 3px 0 0 #0F8B70, 0 2px 5px rgba(0,0,0,0.18) !important; 
    } 
 
    section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] p { 
        color: #FFFFFF !important; 
        font-weight: 750 !important; 
    } 
 
    /* ===================================================== 
       FILTER AREA 
       ===================================================== */ 
    .sidebar-filter-box { 
        background: #101A2B; 
        border: 1px solid #1E2D4A; 
        border-radius: 8px; 
        padding: 12px 10px 8px 10px; 
        margin-top: 4px; 
    } 
 
    section[data-testid="stSidebar"] .stSelectbox label { 
        color: #8496AC !important; 
        font-size: 10px !important; 
        font-weight: 700 !important; 
        text-transform: uppercase; 
        letter-spacing: 0.65px; 
        margin-bottom: 3px !important; 
    } 
 
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div { 
        background-color: #162238 !important; 
        border: 1px solid #293B58 !important; 
        border-radius: 6px !important; 
        min-height: 37px !important; 
        transition: all 0.15s ease-in-out !important; 
    } 
 
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div:hover { 
        border-color: #3C5775 !important; 
        background-color: #192941 !important; 
    } 
 
    section[data-testid="stSidebar"] div[data-baseweb="select"] span { 
        color: #D5DDE7 !important; 
        font-size: 12px !important; 
    } 
 
    /* ===================================================== 
       RESET BUTTON 
       ===================================================== */ 
    section[data-testid="stSidebar"] .stButton > button { 
        width: 100%; 
        min-height: 38px; 
        margin-top: 8px; 
        background: #131F31 !important; 
        border: 1px solid #30435F !important; 
        color: #A9B8C9 !important; 
        border-radius: 6px !important; 
        font-size: 11px !important; 
        font-weight: 700 !important; 
        letter-spacing: 0.3px; 
        transition: all 0.18s ease-in-out !important; 
    } 
 
    section[data-testid="stSidebar"] .stButton > button:hover { 
        background: #1F3B4D !important; 
        border-color: #3D6178 !important; 
        color: #FFFFFF !important; 
    } 
 
    /* ===================================================== 
       DATAFRAME STYLING 
       ===================================================== */ 
    .dataframe { 
        background-color: #162238 !important; 
        color: white !important; 
    } 
     
    /* ===================================================== 
       STATUS PILLS 
       ===================================================== */ 
    .pill-good { 
        color: #4C9A5B; 
        font-weight: bold; 
    } 
 
    .pill-bad { 
        color: #D64545; 
        font-weight: bold; 
    } 
</style> 
""", unsafe_allow_html=True) 
 
# ========================================================= 
# LOAD & PREPROCESS DATA 
# ========================================================= 
@st.cache_data 
def load_data(): 
    df_raw = pd.read_csv("district_priority_snapshot.csv") 
     
    # Fill defaults if missing columns exist 
    if "health_subscore" not in df_raw.columns: 
        df_raw["health_subscore"] = df_raw.get("priority_index", 50) * 0.9 + np.random.normal(0, 3, len(df_raw)) 
    if "education_subscore" not in df_raw.columns: 
        df_raw["education_subscore"] = df_raw.get("priority_index", 50) * 0.85 + np.random.normal(0, 3, len(df_raw)) 
    if "dominant_driver" not in df_raw.columns: 
        df_raw["dominant_driver"] = np.random.choice(["Health-driven", "Education-driven", "Both equally"], len(df_raw)) 
     
    return df_raw 
 
df = load_data() 
TOTAL_DISTRICTS = len(df) 
 
# ========================================================= 
# HELPER FUNCTIONS 
# ========================================================= 
INDICATOR_LABELS = { 
    "child_anaemia_pct": ("Child Anaemia", "bad"), 
    "health_insurance_pct": ("Health Insurance", "good"), 
    "institutional_births_pct": ("Institutional Births", "good"), 
    "full_immunization_pct": ("Full Immunization", "good"), 
    "overall_literacy": ("Overall Literacy", "good"), 
    "dropout_rate_pct": ("Dropout Rate", "bad"), 
    "pct_schools_water": ("School Water", "good"), 
    "pct_schools_road_connected": ("School Roads", "good"), 
    "pct_schools_electricity": ("School Electricity", "good"), 
    "stunted_pct": ("Stunting", "bad"), 
    "underweight_pct": ("Underweight", "bad"), 
    "true_pupil_teacher_ratio": ("Pupil-Teacher Ratio", "bad") 
} 
 
ACTION_MAP = { 
    "child_anaemia_pct": "Expand anaemia screening & nutrition intervention", 
    "health_insurance_pct": "Increase health insurance enrollment & awareness", 
    "institutional_births_pct": "Strengthen institutional delivery access", 
    "full_immunization_pct": "Launch targeted immunization drive", 
    "overall_literacy": "Launch targeted literacy improvement program", 
    "dropout_rate_pct": "Introduce dropout-prevention and retention program", 
    "pct_schools_water": "Improve school water access & facilities", 
    "pct_schools_road_connected": "Improve school road connectivity", 
    "pct_schools_electricity": "Improve school electricity infrastructure", 
    "stunted_pct": "Expand child nutrition intervention", 
    "underweight_pct": "Implement targeted child nutrition packages", 
    "true_pupil_teacher_ratio": "Recruit & deploy additional primary school teachers" 
} 
 
def reset_all_filters(): 
    """Reset every sidebar/page filter to its default value before rerun.""" 
    st.session_state["sb_state_filter"] = "All" 
    st.session_state["sb_tier_filter"] = "All" 
    st.session_state["sb_driver_filter"] = "All" 
    st.session_state["dist_prof_select"] = "All" 
    st.session_state["act_summary_dist_select"] = "All" 
    st.session_state["diagnostic_view"] = "state" 
    st.session_state["show_full_action_list"] = False 
 
 
def safe_mean(series): 
    """Return a rounded mean without emitting NaN to the UI.""" 
    value = pd.to_numeric(series, errors="coerce").mean() 
    return round(float(value), 2) if pd.notna(value) else 0 
 
 
def allocation_score(frame, selected_strategy): 
    """Create a strategy-sensitive district score for proportional allocation. 
 
    This is the Streamlit equivalent of the Power BI pattern supplied by the user: 
    each district receives a share of the selected budget proportional to its 
    calculated Allocation Score, rather than a fixed equal amount. 
    """ 
    out = frame.copy() 
    priority = pd.to_numeric(out["priority_index"], errors="coerce").fillna(0) 
    health = pd.to_numeric(out["health_subscore"], errors="coerce").fillna(0) 
    education = pd.to_numeric(out["education_subscore"], errors="coerce").fillna(0) 
 
    # Convert scores into need (higher = greater need). 
    health_need = (100 - health).clip(lower=0) 
    education_need = (100 - education).clip(lower=0) 
 
    if selected_strategy == "Balance Needs": 
        score = priority * 0.60 + ((health_need + education_need) / 2) * 0.40 
    elif selected_strategy == "Equity First": 
        score = priority * 0.35 + health_need * 0.325 + education_need * 0.325 
    else:  # Target High Need 
        score = (priority ** 1.35) * 0.70 + health_need * 0.15 + education_need * 0.15 
 
    # Keep every high-priority district allocatable even if its calculated need 
    # happens to be zero. 
    out["allocation_score"] = score.clip(lower=0.01) 
    return out 
 
 
def allocate_budget(scores, budget): 
    """Allocate the full budget proportionally to district scores.""" 
    scores = pd.to_numeric(scores, errors="coerce").fillna(0).clip(lower=0) 
    total = float(scores.sum()) 
    if total <= 0: 
        return pd.Series(np.repeat(float(budget) / max(len(scores), 1), len(scores)), index=scores.index) 
    return (scores / total) * float(budget) 
 
 
def get_district_gaps_and_action(row, state_avg_row): 
    gaps = {} 
    for col, (label, direction) in INDICATOR_LABELS.items(): 
        if col not in row or pd.isna(row[col]) or col not in state_avg_row: 
            continue 
        diff = row[col] - state_avg_row[col] 
        # Calculate gap severity 
        gap_val = -diff if direction == "good" else diff 
        gaps[col] = (gap_val, label, diff, direction) 
     
    sorted_gaps = sorted(gaps.items(), key=lambda x: x[1][0], reverse=True) 
    if not sorted_gaps: 
        return "Overall Priority", "Conduct integrated education & health intervention", [] 
     
    worst_col = sorted_gaps[0][0] 
    primary_concern = sorted_gaps[0][1][1] 
    recommended_action = ACTION_MAP.get(worst_col, "Conduct integrated intervention") 
     
    return primary_concern, recommended_action, sorted_gaps 
 
# ========================================================= 
# SIDEBAR NAVIGATION & FILTERS 
# ========================================================= 
with st.sidebar: 
 
    # ===================================================== 
    # DHEIS BRANDING 
    # ===================================================== 
    st.markdown( 
        """ 
        <div class="sidebar-brand"> 
            <div class="sidebar-brand-title"> 
                <span class="sidebar-brand-icon">🗺️</span>DHEIS 
            </div> 
            <div class="sidebar-brand-subtitle"> 
                District Health &amp; Education<br> 
                Intelligence System 
            </div> 
        </div> 
        """, 
        unsafe_allow_html=True 
    ) 
 
    # Divider 
    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True) 
 
    # ===================================================== 
    # NAVIGATION 
    # ===================================================== 
    st.markdown( 
        "<div class='sidebar-section-title'>Navigation</div>", 
        unsafe_allow_html=True 
    ) 
 
    nav_choice = st.radio( 
        "NAVIGATION", 
        [ 
            "DHEIS OVERVIEW", 
            "DIAGNOSTIC", 
            "ACTION QUEUE", 
            "RESOURCE ALLOCATION" 
        ], 
        index=[ 
            "DHEIS OVERVIEW", 
            "DIAGNOSTIC", 
            "ACTION QUEUE", 
            "RESOURCE ALLOCATION" 
        ].index(st.session_state["current_page"]), 
        label_visibility="collapsed" 
    ) 
 
    st.session_state["current_page"] = nav_choice 
 
    # Divider 
    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True) 
 
    # ===================================================== 
    # FILTERS 
    # ===================================================== 
    st.markdown( 
        "<div class='sidebar-section-title'>Filters</div>", 
        unsafe_allow_html=True 
    ) 
 
    st.markdown("<div class='sidebar-filter-box'>", unsafe_allow_html=True) 
 
    states_list = ["All"] + sorted( 
        df["state_name"].dropna().unique().tolist() 
    ) 
 
    selected_state_filter = st.selectbox( 
        "Select State", 
        states_list, 
        key="sb_state_filter" 
    ) 
 
    priority_tiers = ["All", "High", "Medium", "Low"] 
 
    selected_tier_filter = st.selectbox( 
        "Priority Tier", 
        priority_tiers, 
        key="sb_tier_filter" 
    ) 
 
    drivers_list = ["All"] + sorted( 
        df["dominant_driver"].dropna().unique().tolist() 
    ) 
 
    selected_driver_filter = st.selectbox( 
        "Dominant Driver", 
        drivers_list, 
        key="sb_driver_filter" 
    ) 
 
    st.markdown("</div>", unsafe_allow_html=True) 
 
    # ===================================================== 
    # RESET FILTERS 
    # ===================================================== 
    st.button( 
        "🔄  RESET FILTERS", 
        on_click=reset_all_filters, 
        use_container_width=True 
    ) 
 
# Apply Global Filters to Main DataFrame 
filtered_df = df.copy() 
 
if selected_state_filter != "All": 
    filtered_df = filtered_df[ 
        filtered_df["state_name"] == selected_state_filter 
    ] 
 
if selected_tier_filter != "All": 
    filtered_df = filtered_df[ 
        filtered_df["priority_tier"] == selected_tier_filter 
    ] 
 
if selected_driver_filter != "All": 
    filtered_df = filtered_df[ 
        filtered_df["dominant_driver"] == selected_driver_filter 
    ] 
 
 
# ========================================================= 
# PAGE 1: DHEIS OVERVIEW 
# ========================================================= 
if st.session_state["current_page"] == "DHEIS OVERVIEW": 
    st.markdown("# DHEIS OVERVIEW") 
    st.caption("District-level intelligence for integrated health & education prioritization") 
 
    # Top Metrics Row 
    tier_counts = filtered_df["priority_tier"].value_counts() 
    high_count = tier_counts.get("High", 0) 
    high_pct = round((high_count / len(filtered_df) * 100), 1) if len(filtered_df) > 0 else 0 
    avg_priority = round(filtered_df["priority_index"].mean(), 2) if len(filtered_df) > 0 else 0 
    avg_health = round(filtered_df["health_subscore"].mean(), 2) if len(filtered_df) > 0 else 0 
    avg_edu = round(filtered_df["education_subscore"].mean(), 2) if len(filtered_df) > 0 else 0 
 
    m1, m2, m3, m4, m5, m6 = st.columns(6) 
    m1.metric("Total Districts", len(filtered_df)) 
    m2.metric("High Priority Districts", high_count) 
    m3.metric("High Priority %", f"{high_pct}%") 
    m4.metric("Avg Priority Index", avg_priority) 
    m5.metric("Avg Health Score", avg_health) 
    m6.metric("Avg Education Score", avg_edu) 
 
    st.markdown("<br>", unsafe_allow_html=True) 
 
    # ===================================================== 
    # ROW 1 
    # 1. Priority Tier Distribution 
    # 2. State-Wise Distribution by Priority Tier 
    # ===================================================== 
 
    col1, col2 = st.columns([1, 1]) 
 
    with col1: 
        st.markdown( 
            "<div class='card-title'>Priority Tier Distribution (Overall)</div>", 
            unsafe_allow_html=True 
        ) 
 
        fig_pie = go.Figure(go.Pie( 
            labels=tier_counts.index, 
            values=tier_counts.values, 
            hole=0.6, 
            marker_colors=[ 
                TIER_COLORS.get(k, "#999") 
                for k in tier_counts.index 
            ], 
            textinfo="percent" 
        )) 
 
        fig_pie.update_layout( 
            height=280, 
            margin=dict(l=10, r=10, t=10, b=10), 
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            showlegend=True, 
            legend=dict( 
                orientation="v", 
                x=1.02, 
                y=0.5, 
                xanchor="left", 
                yanchor="middle", 
                font=dict(size=11) 
            ), 
            annotations=[ 
                dict( 
                    text=f"<b>{len(filtered_df)}</b><br>Districts", 
                    x=0.5, 
                    y=0.5, 
                    font_size=14, 
                    showarrow=False, 
                    font_color="#FFF" 
                ) 
            ] 
        ) 
 
        st.plotly_chart(fig_pie, use_container_width=True) 
 
    with col2: 
        st.markdown( 
            "<div class='card-title'>State-Wise Distribution by Priority Tier</div>", 
            unsafe_allow_html=True 
        ) 
 
        state_tier = filtered_df.groupby( 
            ["state_name", "priority_tier"] 
        ).size().unstack(fill_value=0) 
 
        for _tier in ["High", "Medium", "Low"]: 
            if _tier not in state_tier.columns: 
                state_tier[_tier] = 0 
 
        state_tier["Total_Districts"] = state_tier[ 
            ["High", "Medium", "Low"] 
        ].sum(axis=1) 
 
        state_tier = state_tier.sort_values( 
            "Total_Districts", 
            ascending=False 
        ) 
 
        fig_st = go.Figure() 
 
        for tier in ["High", "Medium", "Low"]: 
            fig_st.add_trace(go.Bar( 
                y=state_tier.index, 
                x=state_tier[tier], 
                name=tier, 
                orientation="h", 
                marker_color=TIER_COLORS[tier] 
            )) 
 
        fig_st.update_layout( 
            barmode="stack", 
            height=max(280, len(state_tier) * 30 + 45), 
            margin=dict(l=10, r=15, t=30, b=10), 
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            legend=dict( 
                orientation="h", 
                y=1.08, 
                x=0, 
                font=dict(size=10) 
            ), 
            xaxis=dict(title=None), 
            yaxis=dict( 
                title=None, 
                autorange="reversed" 
            ) 
        ) 
 
        with st.container(height=280, border=False): 
            st.plotly_chart( 
                fig_st, 
                use_container_width=True, 
                config={"displayModeBar": False} 
            ) 
 
    st.markdown("<br>", unsafe_allow_html=True) 
 
    # ===================================================== 
    # ROW 2 
    # 3. Top 10 Districts by Priority Index 
    # 4. Health Score vs Education Score 
    # ===================================================== 
 
    col3, col4 = st.columns([1, 1]) 
 
    with col3: 
        st.markdown( 
            "<div class='card-title'>Top 10 Districts by Priority Index</div>", 
            unsafe_allow_html=True 
        ) 
 
        top10 = filtered_df.nlargest( 
            10, 
            "priority_index" 
        )[["district_name", "state_name", "priority_index"]] 
 
        top10.columns = ["District", "State", "Score"] 
        top10.insert(0, "Rank", range(1, len(top10) + 1)) 
 
        st.dataframe( 
            top10, 
            hide_index=True, 
            use_container_width=True, 
            height=250 
        ) 
 
    with col4: 
        st.markdown( 
            "<div class='card-title'>Health Score vs Education Score</div>", 
            unsafe_allow_html=True 
        ) 
 
        fig_scatter = px.scatter( 
            filtered_df, 
            x="health_subscore", 
            y="education_subscore", 
            color="priority_tier", 
            color_discrete_map=TIER_COLORS, 
            hover_name="district_name" 
        ) 
 
        fig_scatter.update_layout( 
            height=260, 
            margin=dict(l=5, r=5, t=5, b=5), 
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            showlegend=False 
        ) 
 
        st.plotly_chart( 
            fig_scatter, 
            use_container_width=True 
        ) 
 
    st.markdown("<br>", unsafe_allow_html=True) 
 
    # ===================================================== 
    # ROW 3 
    # 5. Dominant Driver Distribution 
    # 6. State Priority Index (Average) 
    # ===================================================== 
 
    col5, col6 = st.columns([1, 1]) 
 
    with col5: 
        st.markdown( 
            "<div class='card-title'>Dominant Driver Distribution</div>", 
            unsafe_allow_html=True 
        ) 
 
        driver_counts = filtered_df["dominant_driver"].value_counts() 
 
        fig_driver_pie = go.Figure(go.Pie( 
            labels=driver_counts.index, 
            values=driver_counts.values, 
            hole=0.55, 
            marker_colors=["#1F77B4", "#9467BD", "#2CA02C"], 
            textinfo="percent" 
        )) 
 
        fig_driver_pie.update_layout( 
            height=260, 
            margin=dict(l=5, r=5, t=5, b=5), 
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            showlegend=True, 
            legend=dict( 
                orientation="v", 
                x=1.02, 
                y=0.5, 
                xanchor="left", 
                yanchor="middle", 
                font=dict(size=11) 
            ) 
        ) 
 
        st.plotly_chart( 
            fig_driver_pie, 
            use_container_width=True 
        ) 
 
    with col6: 
        st.markdown( 
            "<div class='card-title'>State Priority Index (Average)</div>", 
            unsafe_allow_html=True 
        ) 
 
        top_states_avg = ( 
            filtered_df 
            .groupby("state_name")["priority_index"] 
            .mean() 
            .sort_values(ascending=False) 
        ) 
 
        def state_priority_tier(score): 
            if score >= 60: 
                return "High" 
            elif score >= 45: 
                return "Medium" 
            return "Low" 
 
        state_bar_colors = [ 
            TIER_COLORS[state_priority_tier(v)] 
            for v in top_states_avg.values 
        ] 
 
        fig_avg = go.Figure(go.Bar( 
            x=top_states_avg.values, 
            y=top_states_avg.index, 
            orientation="h", 
            marker_color=state_bar_colors, 
            text=[f"{v:.0f}" for v in top_states_avg.values], 
            textposition="inside", 
            customdata=[ 
                state_priority_tier(v) 
                for v in top_states_avg.values 
            ], 
            hovertemplate="<b>%{y}</b><br>Priority Index: %{x:.2f}<br>Tier: %{customdata}<extra></extra>" 
        )) 
 
        fig_avg.update_layout( 
            height=max(280, len(top_states_avg) * 30 + 25), 
            margin=dict(l=10, r=10, t=10, b=10), 
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            yaxis=dict(autorange="reversed", title=None), 
            xaxis=dict(title=None) 
        ) 
 
        with st.container(height=280, border=False): 
            st.plotly_chart( 
                fig_avg, 
                use_container_width=True, 
                config={"displayModeBar": False} 
            ) 
 
    st.markdown("<br>", unsafe_allow_html=True) 
 
    # ===================================================== 
    # ROW 4 
    # 7. Alerts & Priority Areas 
    # ===================================================== 
 
    col7, col8 = st.columns([1, 1]) 
 
    with col7: 
        st.markdown( 
            "<div class='card-title'>Alerts & Priority Areas</div>", 
            unsafe_allow_html=True 
        ) 
 
        st.markdown(""" 
        <div style='background: #162238; padding: 14px; border-radius: 6px; border-left: 4px solid #D64545; font-size: 12px;'> 
            <b>27 High Priority Districts</b> are primarily Education-driven needing immediate intervention.<br><br> 
            <b>64 High Priority Districts</b> are primarily Health-driven. 
        </div> 
        """, unsafe_allow_html=True) 
 
# ========================================================= 
# PAGE 2: DIAGNOSTIC & DISTRICT PROFILE (DRILL DOWN) 
# ========================================================= 
elif st.session_state["current_page"] == "DIAGNOSTIC": 
 
    # --- VIEW 1: STATE LEVEL DIAGNOSTIC --- 
    if st.session_state["diagnostic_view"] == "state": 
        scope_label = selected_state_filter if selected_state_filter != "All" else "All States / India" 
        st.markdown(f"# DHEIS DISTRICT DIAGNOSTIC — {scope_label}") 
        st.caption("Overall view first; selecting a state in the sidebar updates every diagnostic visual to that state.") 
 
        # KPI Header Row 
        m1, m2, m3, m4, m5, m6, m7, m8 = st.columns(8) 
        m1.metric("Total Districts", len(filtered_df)) 
        m2.metric("High Priority", (filtered_df["priority_tier"] == "High").sum()) 
        m3.metric("Avg Priority Index", round(filtered_df["priority_index"].mean(), 2)) 
        m4.metric("Avg Health Score", round(filtered_df["health_subscore"].mean(), 2)) 
        m5.metric("Avg Edu Score", round(filtered_df["education_subscore"].mean(), 2)) 
         
        health_driven_pct = round((filtered_df["dominant_driver"] == "Health-driven").mean() * 100, 0) 
        edu_driven_pct = round((filtered_df["dominant_driver"] == "Education-driven").mean() * 100, 0) 
        both_pct = round((filtered_df["dominant_driver"] == "Both equally").mean() * 100, 0) 
 
        m6.metric("Health-driven", f"{health_driven_pct}%") 
        m7.metric("Edu-driven", f"{edu_driven_pct}%") 
        m8.metric("Both Equally", f"{both_pct}%") 
 
        st.markdown("<br>", unsafe_allow_html=True) 
 
        col1, col2 = st.columns([1.5, 1]) 
 
        with col1: 
            st.markdown(f"<div class='card-title'>Health Score vs Education Score ({scope_label})</div>", unsafe_allow_html=True) 
            fig_scat = px.scatter( 
                filtered_df, 
                x="health_subscore", 
                y="education_subscore", 
                color="priority_tier", 
                color_discrete_map=TIER_COLORS, 
                hover_data=["district_name", "state_name"] 
            ) 
            fig_scat.update_layout( 
                height=280, 
                margin=dict(l=5, r=5, t=5, b=5), 
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                showlegend=False 
            ) 
            st.plotly_chart(fig_scat, use_container_width=True) 
 
        with col2: 
            st.markdown(f"<div class='card-title'>Dominant Driver Distribution — ({scope_label})</div>", unsafe_allow_html=True) 
            driver_counts = filtered_df["dominant_driver"].value_counts() 
            fig_dom = go.Figure(go.Pie( 
                labels=driver_counts.index, 
                values=driver_counts.values, 
                hole=0.55, 
                marker_colors=["#1F77B4", "#9467BD", "#2CA02C"] 
            )) 
            fig_dom.update_layout( 
                height=300, 
                margin=dict(l=5, r=5, t=5, b=5), 
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)" 
            ) 
            st.plotly_chart(fig_dom, use_container_width=True) 
 
            st.markdown("<br>", unsafe_allow_html=True) 
 
        col3, col4 = st.columns([1.5, 1]) 
 
        with col3: 
            st.markdown(f"<div class='card-title'>Priority Tier by Driver ({scope_label})</div>", unsafe_allow_html=True) 
            driver_tier_df = pd.crosstab( 
                filtered_df["dominant_driver"], 
                filtered_df["priority_tier"], 
                normalize='index' 
            ) * 100 
 
            fig_bar_driver = go.Figure() 
 
            for tier in ["High", "Low", "Medium"]: 
                if tier in driver_tier_df.columns: 
                    fig_bar_driver.add_trace(go.Bar( 
                        y=driver_tier_df.index, 
                        x=driver_tier_df[tier], 
                        name=tier, 
                        orientation='h', 
                        marker_color=TIER_COLORS[tier] 
                    )) 
 
            fig_bar_driver.update_layout( 
                barmode='stack', 
                height=350, 
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)" 
            ) 
 
            st.plotly_chart( 
                fig_bar_driver, 
                use_container_width=True 
            ) 
 
        with col4: 
            st.markdown(f"<div class='card-title'>Top High-Priority Districts ({scope_label})</div>", unsafe_allow_html=True) 
 
            top10 = filtered_df[ 
                filtered_df["priority_tier"] == "High" 
            ].nlargest( 
                10, 
                "priority_index" 
            )[ 
                ["district_name", "priority_index", "dominant_driver"] 
            ] 
 
            top10.columns = [ 
                "District", 
                "Avg Priority Index", 
                "Dominant Driver" 
            ] 
 
            top10.insert( 
                0, 
                "Rank", 
                range(1, len(top10) + 1) 
            ) 
 
            st.dataframe( 
                top10, 
                hide_index=True, 
                use_container_width=True, 
                height=300 
            ) 
 
            st.markdown("<br>", unsafe_allow_html=True) 
 
            if st.button( 
                "VIEW DISTRICT PROFILE →", 
                use_container_width=True 
            ): 
                st.session_state["diagnostic_view"] = "profile" 
                st.rerun() 
 
    # --- VIEW 2: DRILL DOWN DISTRICT PROFILE --- 
    else: 
        st.button( 
            "← Back to State Diagnostic", 
            on_click=lambda: st.session_state.update( 
                {"diagnostic_view": "state"} 
            ) 
        ) 
 
        st.markdown("# DISTRICT PROFILE") 
        st.caption("Detailed health, education & priority analysis of selected district") 
 
        # District Selector Header 
        col_sel1, col_sel2, col_sel3, col_sel4, col_sel5, col_sel6 = st.columns( 
            [2, 1, 1, 1, 1.2, 1.2] 
        ) 
         
        with col_sel1: 
            profile_base = filtered_df.copy() if selected_state_filter != "All" else df.copy() 
            dist_list = sorted( 
                profile_base["district_name"].dropna().unique() 
            ) 
 
            if not dist_list: 
                st.warning( 
                    "No districts match the current filters. Reset the filters or choose another state." 
                ) 
                st.stop() 
 
            current_profile = st.session_state.get( 
                "dist_prof_select", 
                "All" 
            ) 
 
            if current_profile not in dist_list and current_profile != "All": 
                current_profile = "All" 
 
            st.session_state["dist_prof_select"] = current_profile 
 
            selected_dist = st.selectbox( 
                "Select District", 
                ["All"] + dist_list, 
                index=(["All"] + dist_list).index(current_profile), 
                key="dist_prof_select" 
            ) 
 
            if selected_dist == "All": 
                selected_dist = dist_list[0] 
 
            st.session_state["selected_district_global"] = selected_dist 
         
        dist_row = profile_base[ 
            profile_base["district_name"] == selected_dist 
        ].iloc[0] 
 
        state_avg = df[ 
            df["state_name"] == dist_row["state_name"] 
        ].mean(numeric_only=True) 
 
        with col_sel2: 
            st.metric( 
                "Priority Index", 
                round(dist_row["priority_index"], 2) 
            ) 
 
        with col_sel3: 
            st.metric( 
                "Health Score", 
                round(dist_row["health_subscore"], 2) 
            ) 
 
        with col_sel4: 
            st.metric( 
                "Education Score", 
                round(dist_row["education_subscore"], 2) 
            ) 
 
        with col_sel5: 
            st.metric( 
                "Dominant Driver", 
                dist_row["dominant_driver"] 
            ) 
 
        with col_sel6: 
            st.metric( 
                "State Avg. Priority", 
                round(state_avg["priority_index"], 2) 
            ) 
 
        st.markdown("---") 
 
        # Tables Side by Side 
        col_h, col_e = st.columns(2) 
 
        def build_indicator_df( 
            indicator_keys, 
            row_data, 
            state_data 
        ): 
            records = [] 
 
            for key in indicator_keys: 
                if key in row_data and key in INDICATOR_LABELS: 
                    label, direction = INDICATOR_LABELS[key] 
                    d_val = round(row_data[key], 2) 
                    s_val = round(state_data[key], 2) 
                    diff = round(d_val - s_val, 2) 
                     
                    # Determine Good / Bad status symbol 
                    if direction == "good": 
                        status = "⬆ GOOD" if diff >= 0 else "⬇ BAD" 
                    else: 
                        status = "⬇ GOOD" if diff <= 0 else "⬆ BAD" 
 
                    records.append({ 
                        "Indicator": label, 
                        "District Value": d_val, 
                        "State Avg.": s_val, 
                        "Vs State Avg.": f"{diff} ({status})" 
                    }) 
 
            return pd.DataFrame(records) 
 
        health_keys = [ 
            "institutional_births_pct", 
            "full_immunization_pct", 
            "child_anaemia_pct", 
            "health_insurance_pct", 
            "stunted_pct", 
            "underweight_pct" 
        ] 
 
        edu_keys = [ 
            "dropout_rate_pct", 
            "overall_literacy", 
            "true_pupil_teacher_ratio", 
            "pct_schools_electricity", 
            "pct_schools_road_connected", 
            "pct_schools_water" 
        ] 
 
        with col_h: 
            st.markdown( 
                "<div class='card-title'>HEALTH INDICATORS (District)</div>", 
                unsafe_allow_html=True 
            ) 
 
            st.dataframe( 
                build_indicator_df( 
                    health_keys, 
                    dist_row, 
                    state_avg 
                ), 
                hide_index=True, 
                use_container_width=True 
            ) 
 
        with col_e: 
            st.markdown( 
                "<div class='card-title'>EDUCATION INDICATORS (District)</div>", 
                unsafe_allow_html=True 
            ) 
 
            st.dataframe( 
                build_indicator_df( 
                    edu_keys, 
                    dist_row, 
                    state_avg 
                ), 
                hide_index=True, 
                use_container_width=True 
            ) 
 
        st.markdown("<br>", unsafe_allow_html=True) 
 
        # Bottom row: Context Bar Chart + Key Focus Areas 
        c_left, c_right = st.columns([1.5, 1]) 
 
        with c_left: 
            st.markdown( 
                "<div class='card-title'>STATE CONTEXT: DISTRICT VS STATE AVERAGE</div>", 
                unsafe_allow_html=True 
            ) 
 
            fig_comp = go.Figure() 
 
            fig_comp.add_trace(go.Bar( 
                name='District', 
                x=[ 
                    'Health Score', 
                    'Priority Index', 
                    'Education Score' 
                ], 
                y=[ 
                    dist_row['health_subscore'], 
                    dist_row['priority_index'], 
                    dist_row['education_subscore'] 
                ], 
                marker_color='#1F3B4D' 
            )) 
 
            fig_comp.add_trace(go.Bar( 
                name='State', 
                x=[ 
                    'Health Score', 
                    'Priority Index', 
                    'Education Score' 
                ], 
                y=[ 
                    state_avg['health_subscore'], 
                    state_avg['priority_index'], 
                    state_avg['education_subscore'] 
                ], 
                marker_color='#8A99AD' 
            )) 
 
            fig_comp.update_layout( 
                barmode='group', 
                height=300, 
                margin=dict(l=10, r=10, t=5, b=10), 
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)" 
            ) 
 
            st.plotly_chart( 
                fig_comp, 
                use_container_width=True 
            ) 
 
        with c_right: 
            st.markdown( 
                "<div class='card-title'>RECOMMENDED FOCUS AREAS</div>", 
                unsafe_allow_html=True 
            ) 
 
            concern, action, gaps = get_district_gaps_and_action( 
                dist_row, 
                state_avg 
            ) 
 
            st.markdown(f""" 
            - 🛠️ **Primary Priority:** {concern} 
            - 🎯 **Action:** {action} 
            - ⚡ **Key Infrastructure Need:** Improve School Electricity & Facilities 
            - 🏥 **Health Priority:** Enhance Immunization Coverage & Delivery 
            """) 
 
 
# ========================================================= 
# PAGE 3: ACTION QUEUE (WITH AI BRIEF & FULL EXTENSION TABLE) 
# ========================================================= 
elif st.session_state["current_page"] == "ACTION QUEUE": 
     
    st.markdown("# DHEIS ACTION QUEUE") 
    st.caption("High-priority districts requiring immediate attention & targeted interventions") 
 
    high_df = ( 
        filtered_df[filtered_df["priority_tier"] == "High"] 
        .sort_values("priority_index", ascending=False) 
        .copy() 
    ) 
 
    # KPI Top Bar 
    k1, k2, k3, k4 = st.columns(4) 
    k1.metric("High Priority Districts", len(high_df)) 
    k2.metric( 
        "States/UTs Affected", 
        high_df["state_name"].nunique() if len(high_df) > 0 else 0 
    ) 
    k3.metric( 
        "Avg. Priority Index", 
        round(high_df["priority_index"].mean(), 2) if len(high_df) > 0 else 0 
    ) 
    k4.metric( 
        "Critical Districts", 
        len(high_df[high_df["priority_index"] > 75]) 
    ) 
 
    st.markdown("<br>", unsafe_allow_html=True) 
 
    # Main Action Layout: Left Table / Action View, Right Sidebar Panel (AI Brief & Summary) 
    col_main, col_side = st.columns([2.2, 1]) 
 
    with col_main: 
        # Check if Full List view toggle is active 
        if st.session_state["show_full_action_list"]: 
            st.markdown("### 📋 ALL HIGH PRIORITY DISTRICTS (FULL LIST)") 
 
            if st.button("← Back to Summary Action Queue View"): 
                st.session_state["show_full_action_list"] = False 
                st.rerun() 
             
            table_display_df = high_df.copy() 
 
        else: 
            st.markdown( 
                "<div class='card-title'>High Priority Districts Action Table</div>", 
                unsafe_allow_html=True 
            ) 
 
            table_display_df = high_df.head(10) 
 
        # Build detailed display columns for Action Queue 
        action_rows = [] 
 
        for rank, (_, r) in enumerate( 
            table_display_df.iterrows(), 
            start=1 
        ): 
            st_avg = df[ 
                df["state_name"] == r["state_name"] 
            ].mean(numeric_only=True) 
 
            concern, act, gaps = get_district_gaps_and_action( 
                r, 
                st_avg 
            ) 
             
            top_ind_str = ", ".join( 
                [ 
                    f"{g[1][1]} ({abs(round(g[1][2], 1))} pts)" 
                    for g in gaps[:3] 
                ] 
            ) 
 
            action_rows.append({ 
                "Rank": rank, 
                "District": r["district_name"], 
                "State": r["state_name"], 
                "Priority Display": f"{round(r['priority_index'], 1)} - High", 
                "Top Indicators": top_ind_str, 
                "Recommended Action": act 
            }) 
 
        act_df_display = pd.DataFrame(action_rows) 
 
        st.dataframe( 
            act_df_display, 
            hide_index=True, 
            use_container_width=True, 
            height=350 
        ) 
 
        if not st.session_state["show_full_action_list"]: 
            if st.button("VIEW ALL HIGH PRIORITY DISTRICTS →"): 
                st.session_state["show_full_action_list"] = True 
                st.rerun() 
 
        st.markdown("<br>", unsafe_allow_html=True) 
 
        # Bottom Drivers Section 
        d1, d2 = st.columns(2) 
 
        with d1: 
            st.markdown( 
                "<div class='card-title'>Why Districts Are Flagged</div>", 
                unsafe_allow_html=True 
            ) 
 
            st.markdown(""" 
            - 🔴 **Large gaps vs state average:** Performing significantly worse on key indicators. 
            - 🟠 **Critical development indicators:** Health & infrastructure below acceptable levels. 
            - 🟣 **High overall priority index:** Requires urgent multi-sectoral package. 
            """) 
 
        with d2: 
            st.markdown( 
                "<div class='card-title'>High Priority by Dominant Driver</div>", 
                unsafe_allow_html=True 
            ) 
 
            drv_counts = high_df["dominant_driver"].value_counts() 
 
            fig_drv_bar = go.Figure(go.Bar( 
                x=drv_counts.values, 
                y=drv_counts.index, 
                orientation='h', 
                marker_color=["#4C9A5B", "#9467BD", "#1F77B4"] 
            )) 
 
            fig_drv_bar.update_layout( 
                height=180, 
                margin=dict(l=0, r=0, t=0, b=0), 
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)" 
            ) 
 
            st.plotly_chart( 
                fig_drv_bar, 
                use_container_width=True 
            ) 
 
    with col_side: 
        st.markdown( 
            "<div class='dashboard-card'>", 
            unsafe_allow_html=True 
        ) 
 
        st.markdown("### DISTRICT ACTION SUMMARY") 
         
        action_dist_list = sorted( 
            high_df["district_name"].dropna().unique() 
        ) 
 
        if not action_dist_list: 
            st.info( 
                "No high-priority districts match the current sidebar filters." 
            ) 
            st.stop() 
 
        else: 
            current_action_dist = st.session_state.get( 
                "act_summary_dist_select", 
                "All" 
            ) 
 
            if current_action_dist not in action_dist_list and current_action_dist != "All": 
                current_action_dist = "All" 
 
            st.session_state["act_summary_dist_select"] = current_action_dist 
 
            selected_act_district = st.selectbox( 
                "Select District", 
                options=["All"] + action_dist_list, 
                index=(["All"] + action_dist_list).index( 
                    current_action_dist 
                ), 
                key="act_summary_dist_select" 
            ) 
 
            if selected_act_district == "All": 
                selected_act_district = action_dist_list[0] 
 
            act_row = high_df[ 
                high_df["district_name"] == selected_act_district 
            ].iloc[0] 
 
        st_avg_row = df[ 
            df["state_name"] == act_row["state_name"] 
        ].mean(numeric_only=True) 
 
        concern, action_rec, gaps_list = get_district_gaps_and_action( 
            act_row, 
            st_avg_row 
        ) 
 
        st.markdown(f""" 
        <div style='background: #231825; border: 1px solid #D64545; border-radius: 8px; padding: 14px; margin-vertical: 10px;'> 
            <h2 style='color: #D64545 !important; margin: 0;'>{round(act_row['priority_index'], 2)}</h2> 
            <span style='color: #D64545; font-weight: bold;'>PRIORITY INDEX — HIGH</span> 
        </div> 
        """, unsafe_allow_html=True) 
 
        st.markdown( 
            f"**PRIMARY CONCERN:**\n### {concern}" 
        ) 
 
        st.markdown( 
            f"**RECOMMENDED ACTION:**\n{action_rec}" 
        ) 
 
        st.markdown("---") 
        st.markdown("#### OTHER KEY GAPS") 
 
        for g in gaps_list[1:4]: 
            st.caption( 
                f"🔻 {g[1][1]}: {abs(round(g[1][2], 1))} pts below state benchmark" 
            ) 
 
        st.markdown("---") 
 
        # AI BRIEF GENERATOR INTEGRATION 
        st.markdown("### 🤖 AI Brief Generator") 
 
        if client is None: 
            st.info( 
                "Set GROQ_API_KEY in environment/secrets to generate AI State Briefs." 
            ) 
 
        else: 
            if st.button( 
                "✨ Generate AI State Brief", 
                use_container_width=True 
            ): 
                with st.spinner("Generating AI Brief..."): 
                    try: 
                        prompt_text = f""" 
                        Create a simple and easy-to-understand action brief for the selected district. 
 
                       The person reading this may have NO knowledge of data analysis, 
                       healthcare, education statistics, or technical terminology. 
 
                       District: {act_row['district_name']} 
                       State: {act_row['state_name']} 
                       Priority Level: {act_row['priority_tier']} 
                       Main Issue: {concern} 
                       Recommended Action: {action_rec} 
 
                       Write the brief using these sections: 
 
                       WHAT IS HAPPENING 
                       Explain the main problem in 1-2 simple sentences. 
 
                       WHY IT MATTERS 
                       Explain in everyday language how this problem can affect people, 
                       students, schools, or health services. 
 
                       WHAT SHOULD BE DONE 
                       Give 2-3 practical actions that can be taken. 
 
                       PRIORITY 
                       xplain in one simple sentence why this district needs attention. 
 
                       IMPORTANT: 
                       - Use very simple everyday English. 
                       - Assume the reader has no technical background. 
                       - Do not use technical data terms such as "subscore", "variance", 
                       "normalization", "allocation score", "weighted score", 
                       "correlation", "threshold", or "indicator". 
                       - Do not explain formulas or how the data was calculated. 
                       - Do not simply repeat the numbers. 
                       - Focus on what the information means in real life. 
                       - Keep sentences short and clear. 
                       - Be practical and action-oriented. 
                       - Keep the entire response under 200 words. 
                       """ 
 
                        response = client.chat.completions.create( 
                            model="openai/gpt-oss-20b", 
                            messages=[ 
                                { 
                                    "role": "user", 
                                    "content": prompt_text 
                                } 
                            ], 
                            temperature=0.3, 
                            max_tokens=300 
                        ) 
 
                        st.markdown( 
                            f"**AI Brief ({act_row['state_name']}):**" 
                        ) 
 
                        st.write( 
                            response.choices[0].message.content 
                        ) 
 
                    except Exception as e: 
                        st.error( 
                            f"Error generating brief: {e}" 
                        ) 
 
        st.markdown("</div>", unsafe_allow_html=True) 
 
 
# ========================================================= 
# PAGE 4: RESOURCE ALLOCATION 
# ========================================================= 
elif st.session_state["current_page"] == "RESOURCE ALLOCATION": 
 
    st.markdown("# RESOURCE ALLOCATION") 
    st.caption("Optimize resource distribution across high-priority districts based on needs, strategy and available budget") 
 
    # Respect the global sidebar filters on the allocation page as well. 
    high_df = filtered_df[ 
        filtered_df["priority_tier"] == "High" 
    ].copy() 
 
    # Top Control Bar & KPIs 
    c_kpi1, c_kpi2, c_kpi3, c_kpi4 = st.columns( 
        [1, 1, 1.2, 2] 
    ) 
 
    with c_kpi1: 
        st.metric( 
            "High Priority Districts", 
            len(high_df) 
        ) 
 
    with c_kpi2: 
        st.metric( 
            "Avg High Priority Index", 
            safe_mean(high_df["priority_index"]) if len(high_df) else 0 
        ) 
 
    with c_kpi4: 
        st.markdown("**ALLOCATION STRATEGY & BUDGET**") 
 
        strat_col, budget_col = st.columns([2, 1.5]) 
 
        with strat_col: 
            strategy = st.radio( 
                "Strategy", 
                [ 
                    "Balance Needs", 
                    "Equity First", 
                    "Target High Need" 
                ], 
                horizontal=True, 
                label_visibility="collapsed", 
                key="allocation_strategy" 
            ) 
 
        with budget_col: 
            budget_val = st.slider( 
                "Budget (₹ Cr)", 
                min_value=500, 
                max_value=5000, 
                value=1550, 
                step=50, 
                key="allocation_budget" 
            ) 
 
    with c_kpi3: 
        st.metric( 
            "Available Budget", 
            f"₹{budget_val:,} Cr" 
        ) 
 
    st.caption("⚡ Budget and allocation strategy update WHERE TO ALLOCATE, WHAT TO FUND and the district intervention plan.") 
    st.markdown("---") 
 
    if high_df.empty: 
        st.info( 
            "No high-priority districts match the current sidebar filters. Reset filters or choose another state/tier." 
        ) 
 
    else: 
        # --------------------------------------------------------- 
        # Strategy-sensitive district allocation 
        # --------------------------------------------------------- 
        scored_df = allocation_score( 
            high_df, 
            strategy 
        ) 
 
        scored_df["district_allocation"] = allocate_budget( 
            scored_df["allocation_score"], 
            budget_val 
        ) 
 
        # State roll-up is derived from the district allocations, so strategy 
        # changes both the state recommendation and every downstream view. 
        state_alloc = ( 
            scored_df 
            .groupby("state_name", as_index=False) 
            .agg( 
                allocation=("district_allocation", "sum"), 
                districts=("district_name", "count"), 
                avg_priority=("priority_index", "mean") 
            ) 
            .sort_values( 
                "allocation", 
                ascending=False 
            ) 
        ) 
 
        state_plot = state_alloc.head(10).copy() 
 
        # Highest allocation first 
        state_plot = state_plot.sort_values( 
            "allocation", 
            ascending=False 
        ).reset_index(drop=True) 
 
        # --------------------------------------------------------- 
        # WHAT TO FUND — calculated from the actual intervention gaps 
        # and changed by strategy. 
        # --------------------------------------------------------- 
        health_gap = ( 
            100 - scored_df["health_subscore"] 
        ).clip(lower=0).sum() 
 
        edu_gap = ( 
            100 - scored_df["education_subscore"] 
        ).clip(lower=0).sum() 
 
        infra_cols = [ 
            c for c in [ 
                "pct_schools_water", 
                "pct_schools_road_connected", 
                "pct_schools_electricity" 
            ] 
            if c in scored_df.columns 
        ] 
 
        infra_gap = sum( 
            ( 
                100 - pd.to_numeric( 
                    scored_df[c], 
                    errors="coerce" 
                ) 
            ).clip(lower=0).sum() 
            for c in infra_cols 
        ) 
 
        raw_focus = pd.Series({ 
            "School Infrastructure": infra_gap, 
            "Health Outcomes": health_gap, 
            "Education Outcomes": edu_gap 
        }, dtype=float) 
 
        if strategy == "Balance Needs": 
            strategy_bias = pd.Series({ 
                "School Infrastructure": 1.10, 
                "Health Outcomes": 1.00, 
                "Education Outcomes": 1.00 
            }) 
 
        elif strategy == "Equity First": 
            strategy_bias = pd.Series({ 
                "School Infrastructure": 1.00, 
                "Health Outcomes": 1.15, 
                "Education Outcomes": 1.15 
            }) 
 
        else: 
            strategy_bias = pd.Series({ 
                "School Infrastructure": 0.90, 
                "Health Outcomes": 1.05, 
                "Education Outcomes": 1.25 
            }) 
 
        focus_scores = raw_focus * strategy_bias 
 
        if focus_scores.sum() <= 0: 
            focus_scores[:] = 1 
 
        focus_budget = ( 
            focus_scores / focus_scores.sum() 
        ) * budget_val 
 
        focus_df = ( 
            pd.DataFrame({ 
                "Focus Area": focus_budget.index, 
                "Budget": focus_budget.values 
            }) 
            .sort_values( 
                "Budget", 
                ascending=False 
            ) 
            .reset_index(drop=True) 
        ) 
 
        # --------------------------------------------------------- 
        # Charts Grid 
        # --------------------------------------------------------- 
        ch1, ch2 = st.columns(2) 
 
        with ch1: 
            st.markdown( 
                "<div class='card-title'>WHERE TO ALLOCATE ? (Recommended budget by state)</div>", 
                unsafe_allow_html=True 
            ) 
 
            fig_alloc_state = go.Figure(go.Bar( 
                x=state_plot["allocation"], 
                y=state_plot["state_name"], 
                orientation="h", 
                marker_color="#9467BD", 
                text=[ 
                    f"₹{v:,.0f} Cr" 
                    for v in state_plot["allocation"] 
                ], 
                textposition="outside", 
                hovertemplate="%{y}<br>Allocation: ₹%{x:,.1f} Cr<extra></extra>" 
            )) 
 
            fig_alloc_state.update_layout( 
                height=300, 
                margin=dict(l=5, r=60, t=5, b=5), 
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                yaxis=dict( 
                    autorange="reversed", 
                    title=None 
                ), 
                xaxis=dict(title=None) 
            ) 
 
            st.plotly_chart( 
                fig_alloc_state, 
                use_container_width=True 
            ) 
 
        with ch2: 
            st.markdown( 
                "<div class='card-title'>WHAT TO FUND ? (Strategy-sensitive focus area allocation)</div>", 
                unsafe_allow_html=True 
            ) 
 
            fig_focus = go.Figure(go.Bar( 
                x=focus_df["Budget"], 
                y=focus_df["Focus Area"], 
                orientation="h", 
                marker_color="#8C564B", 
                text=[ 
                    f"₹{v:,.0f} Cr" 
                    for v in focus_df["Budget"] 
                ], 
                textposition="outside", 
                hovertemplate="%{y}<br>Budget: ₹%{x:,.1f} Cr<extra></extra>" 
            )) 
 
            fig_focus.update_layout( 
                height=300, 
                margin=dict(l=5, r=60, t=5, b=5), 
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                yaxis=dict( 
                    autorange="reversed", 
                    title=None 
                ), 
                xaxis=dict(title=None) 
            ) 
 
            st.plotly_chart( 
                fig_focus, 
                use_container_width=True 
            ) 
 
        st.markdown("---") 
 
        # --------------------------------------------------------- 
        # District Intervention Plan — strategy-sensitive Top 10 
        # --------------------------------------------------------- 
        st.markdown( 
            "### DISTRICT INTERVENTION PLAN — Top 10 High-Priority Districts" 
        ) 
 
        top10_plan = scored_df.nlargest( 
            10, 
            "allocation_score" 
        ).copy() 
 
        plan_data = [] 
 
        for rank, (_, r) in enumerate( 
            top10_plan.iterrows(), 
            start=1 
        ): 
            st_avg = df[ 
                df["state_name"] == r["state_name"] 
            ].mean(numeric_only=True) 
 
            concern, action, _ = get_district_gaps_and_action( 
                r, 
                st_avg 
            ) 
 
            if ( 
                "health" in action.lower() 
                or "anaemia" in action.lower() 
                or "immunization" in action.lower() 
            ): 
                impact_area = "Health Outcomes" 
 
            elif ( 
                "school" in action.lower() 
                or "literacy" in action.lower() 
            ): 
                impact_area = "Education Outcomes" 
 
            else: 
                impact_area = "Integrated" 
 
            plan_data.append({ 
                "Rank": rank, 
                "District": r["district_name"], 
                "State": r["state_name"], 
                "Priority Index": round( 
                    r["priority_index"], 
                    2 
                ), 
                "Allocation Score": round( 
                    r["allocation_score"], 
                    2 
                ), 
                "Primary Concern": concern, 
                "Recommended Intervention": action, 
                "District Allocation": f"₹{r['district_allocation']:,.1f} Cr", 
                "Intervention Impact Area": impact_area, 
                "Intervention Priority Level": r["priority_tier"] 
            }) 
 
        interventions_df = pd.DataFrame(plan_data) 
 
        st.dataframe( 
            interventions_df, 
            hide_index=True, 
            use_container_width=True, 
            height=380 
        ) 
 
# ========================================================= 
# FOOTER 
# ========================================================= 
st.markdown("---") 
st.caption( 
    f"DHEIS · District Health & Education Intelligence System · Built on NFHS-5 and DISE data · {TOTAL_DISTRICTS} districts covered" 
)
