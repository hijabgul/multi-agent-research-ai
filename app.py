import html
import re
from io import BytesIO

import streamlit as st

from crewai import Agent, Task, Crew, Process

from planner import create_planner
from researcher import create_researcher
from analyst import create_analyst
from fact_checker import create_fact_checker
from report_writer import create_report_writer


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ResearchAI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# BLACK + GOLD UI
# ============================================================

st.html("""
<style>

    /* --------------------------------------------------------
       GLOBAL
    -------------------------------------------------------- */

    .stApp {
        background:
            radial-gradient(
                circle at 80% 0%,
                rgba(212, 175, 55, 0.08),
                transparent 30%
            ),
            #080808;
        color: #f5f5f5;
    }

    .main {
        background: #080808;
    }

    /* Hide Streamlit default elements */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }


    /* --------------------------------------------------------
       SIDEBAR
    -------------------------------------------------------- */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #0c0c0c 0%,
                #090909 100%
            );

        border-right: 1px solid rgba(212, 175, 55, 0.25);
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
    }


    /* --------------------------------------------------------
       BRAND
    -------------------------------------------------------- */

    .brand {
        padding: 8px 4px 20px 4px;
        border-bottom: 1px solid rgba(212, 175, 55, 0.18);
        margin-bottom: 22px;
    }

    .brand-title {
        color: #d4af37;
        font-size: 27px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
    }

    .brand-subtitle {
        color: #888888;
        font-size: 12px;
        line-height: 1.5;
    }


    /* --------------------------------------------------------
       SIDEBAR TOOL CARD
    -------------------------------------------------------- */

    .tool-card {
        background:
            linear-gradient(
                145deg,
                rgba(212, 175, 55, 0.10),
                rgba(255, 255, 255, 0.025)
            );

        border: 1px solid rgba(212, 175, 55, 0.30);
        border-radius: 14px;
        padding: 15px;
        margin: 12px 0 20px 0;
    }

    .tool-header {
        display: flex;
        align-items: center;
        gap: 9px;
        color: #d4af37;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .tool-icon {
        width: 28px;
        height: 28px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(212, 175, 55, 0.14);
        border: 1px solid rgba(212, 175, 55, 0.25);
    }

    .tool-name {
        color: #ffffff;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 4px;
    }

    .tool-description {
        color: #858585;
        font-size: 11px;
        line-height: 1.5;
    }

    .tool-status {
        margin-top: 11px;
        color: #d4af37;
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.7px;
    }


    /* --------------------------------------------------------
       SIDEBAR INFO
    -------------------------------------------------------- */

    .sidebar-section-title {
        color: #d4af37;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 22px 0 10px 2px;
    }

    .sidebar-info {
        color: #858585;
        font-size: 12px;
        line-height: 1.7;
    }

    .sidebar-info strong {
        color: #d0d0d0;
    }


    /* --------------------------------------------------------
       MAIN HERO
    -------------------------------------------------------- */

    .hero {
        padding: 20px 0 25px 0;
    }

    .hero-eyebrow {
        color: #d4af37;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 9px;
    }

    .hero-title {
        color: #ffffff;
        font-size: 48px;
        font-weight: 800;
        letter-spacing: -2px;
        line-height: 1.05;
        margin: 0;
    }

    .hero-title span {
        color: #d4af37;
    }

    .hero-description {
        color: #8d8d8d;
        font-size: 15px;
        max-width: 720px;
        line-height: 1.7;
        margin-top: 13px;
    }


    /* --------------------------------------------------------
       SECTION LABEL
    -------------------------------------------------------- */

    .section-label {
        color: #d4af37;
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        margin: 18px 0 10px 0;
    }


    /* --------------------------------------------------------
       AGENT CURRENT CARD
    -------------------------------------------------------- */

    .agent-card {
        background:
            linear-gradient(
                135deg,
                rgba(212, 175, 55, 0.09),
                rgba(255, 255, 255, 0.025)
            );

        border: 1px solid rgba(212, 175, 55, 0.22);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 14px;
    }

    .agent-current {
        border-color: rgba(212, 175, 55, 0.55);
        box-shadow:
            0 0 35px rgba(212, 175, 55, 0.06);
    }

    .agent-label {
        color: #d4af37;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 9px;
    }

    .agent-title {
        color: #ffffff;
        font-size: 22px;
        font-weight: 750;
        margin-bottom: 6px;
    }

    .agent-description {
        color: #8c8c8c;
        font-size: 13px;
        line-height: 1.6;
    }


    /* --------------------------------------------------------
       PIPELINE
    -------------------------------------------------------- */

    .pipeline {
        background: rgba(255, 255, 255, 0.018);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 15px;
        padding: 8px 16px;
        margin-bottom: 22px;
    }

    .pipeline-row {
        display: flex;
        align-items: center;
        min-height: 52px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.045);
    }

    .pipeline-row:last-child {
        border-bottom: none;
    }

    .dot {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        margin-right: 13px;
        flex-shrink: 0;
    }

    .dot-done {
        background: #d4af37;
        box-shadow: 0 0 9px rgba(212, 175, 55, 0.45);
    }

    .dot-working {
        background: #f3d76b;
        box-shadow:
            0 0 0 4px rgba(212, 175, 55, 0.10),
            0 0 14px rgba(212, 175, 55, 0.65);
    }

    .dot-waiting {
        background: #343434;
        border: 1px solid #505050;
    }

    .pipeline-name {
        color: #dedede;
        font-size: 13px;
        font-weight: 600;
        flex: 1;
    }

    .pipeline-status {
        color: #737373;
        font-size: 11px;
    }


    /* --------------------------------------------------------
       INPUT
    -------------------------------------------------------- */

    div[data-testid="stTextArea"] textarea {
        background: #101010 !important;
        color: #f5f5f5 !important;
        border: 1px solid #303030 !important;
        border-radius: 13px !important;
        padding: 15px !important;
    }

    div[data-testid="stTextArea"] textarea:focus {
        border: 1px solid #d4af37 !important;
        box-shadow:
            0 0 0 1px rgba(212, 175, 55, 0.15) !important;
    }


    /* --------------------------------------------------------
       BUTTON
    -------------------------------------------------------- */

    .stButton > button {
        background: #d4af37 !important;
        color: #080808 !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        min-height: 45px;
        transition: 0.2s ease;
    }

    .stButton > button:hover {
        background: #e6c653 !important;
        color: #000000 !important;
        border: none !important;
        transform: translateY(-1px);
    }


    /* --------------------------------------------------------
       REPORT CARD
    -------------------------------------------------------- */

    .report-card {
        background: #0d0d0d;
        border: 1px solid rgba(212, 175, 55, 0.25);
        border-radius: 16px;
        padding: 25px;
        margin-top: 20px;
    }

    .report-header {
        color: #d4af37;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 800;
        margin-bottom: 12px;
    }


    /* --------------------------------------------------------
       SOURCE CARD
    -------------------------------------------------------- */

    .source-card {
        background: #101010;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 11px;
        padding: 12px 14px;
        margin: 8px 0;
    }

    .source-number {
        color: #d4af37;
        font-size: 11px;
        font-weight: 800;
    }

    .source-title {
        color: #e4e4e4;
        font-size: 12px;
        margin-top: 3px;
    }

    .source-url {
        color: #777777;
        font-size: 10px;
        margin-top: 4px;
        word-break: break-all;
    }


    /* --------------------------------------------------------
       METRIC CARDS
    -------------------------------------------------------- */

    .metric-card {
        background: #101010;
        border: 1px solid rgba(212, 175, 55, 0.18);
        border-radius: 13px;
        padding: 16px;
        text-align: center;
    }

    .metric-number {
        color: #d4af37;
        font-size: 25px;
        font-weight: 800;
    }

    .metric-label {
        color: #777777;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 3px;
    }


    /* --------------------------------------------------------
       DIVIDER
    -------------------------------------------------------- */

    hr {
        border-color: rgba(255, 255, 255, 0.07) !important;
    }


    /* --------------------------------------------------------
       EXPANDER
    -------------------------------------------------------- */

    div[data-testid="stExpander"] {
        background: #0d0d0d;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 13px;
    }

</style>
""")


# ============================================================
# AGENT NAMES
# ============================================================

agent_names = [
    "Research Planner",
    "Web Researcher",
    "Source Analyst",
    "Fact Checker",
    "Research Report Writer"
]


# ============================================================
# SESSION STATE
# ============================================================

if "research_started" not in st.session_state:
    st.session_state.research_started = False

if "research_complete" not in st.session_state:
    st.session_state.research_complete = False

if "final_report" not in st.session_state:
    st.session_state.final_report = ""

if "research_sources" not in st.session_state:
    st.session_state.research_sources = []

if "topic" not in st.session_state:
    st.session_state.topic = ""


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.html("""
    <div class="brand">

        <div class="brand-title">
            ✦ ResearchAI
        </div>

        <div class="brand-subtitle">
            Multi-agent research intelligence
            powered by CrewAI.
        </div>

    </div>
    """)

    st.html("""
    <div class="sidebar-section-title">
        Research Tools
    </div>

    <div class="tool-card">

        <div class="tool-header">
            <div class="tool-icon">⌕</div>
            Web Research Tool
        </div>

        <div class="tool-name">
            DuckDuckGo Search
        </div>

        <div class="tool-description">
            Searches current web sources and collects
            evidence for the research agents.
        </div>

        <div class="tool-status">
            ● Connected
        </div>

    </div>
    """)

    st.html("""
    <div class="sidebar-section-title">
        AI Pipeline
    </div>

    <div class="sidebar-info">

        <strong>01</strong> Research Planning<br>
        <strong>02</strong> Web Research<br>
        <strong>03</strong> Source Analysis<br>
        <strong>04</strong> Fact Checking<br>
        <strong>05</strong> Report Writing

    </div>
    """)

    st.html("""
    <div class="sidebar-section-title">
        Technology
    </div>

    <div class="sidebar-info">

        <strong>Agents:</strong> CrewAI<br>
        <strong>LLM:</strong> Groq<br>
        <strong>Search:</strong> DuckDuckGo<br>
        <strong>Interface:</strong> Streamlit

    </div>
    """)


# ============================================================
# HERO
# ============================================================

st.html("""
<div class="hero">

    <div class="hero-eyebrow">
        Multi-Agent Research System
    </div>

    <h1 class="hero-title">
        Research <span>Intelligently.</span>
    </h1>

    <div class="hero-description">
        Ask a research question and let five specialized AI agents
        plan, search, analyze, verify and write the final report.
    </div>

</div>
""")


# ============================================================
# INPUT AREA
# ============================================================

st.html("""
<div class="section-label">
    Research Question
</div>
""")

topic = st.text_area(
    "Research Question",
    placeholder=(
        "Example: What are the current impacts of artificial "
        "intelligence on education?"
    ),
    height=120,
    label_visibility="collapsed"
)


# ============================================================
# START BUTTON
# ============================================================

start_col1, start_col2, start_col3 = st.columns([1, 1, 3])

with start_col1:

    analyze_clicked = st.button(
        "✦ Analyze Research",
        use_container_width=True
    )


# ============================================================
# STATUS CONTAINERS
# ============================================================

status_box = st.empty()


# ============================================================
# STATUS DISPLAY
# ============================================================

def show_status(current_agent, message):

    current_index = agent_names.index(current_agent)

    pipeline_rows = ""

    for index, agent in enumerate(agent_names):

        if index < current_index:

            dot_class = "dot-done"
            status = "Completed"

        elif index == current_index:

            dot_class = "dot-working"
            status = "Working"

        else:

            dot_class = "dot-waiting"
            status = "Waiting"

        pipeline_rows += f"""
        <div class="pipeline-row">

            <div class="dot {dot_class}"></div>

            <div class="pipeline-name">
                {html.escape(agent)}
            </div>

            <div class="pipeline-status">
                {status}
            </div>

        </div>
        """

    status_html = f"""

    <div class="status-wrapper">

        <div class="section-label">
            Agent Activity
        </div>

        <div class="agent-card agent-current">

            <div class="agent-label">
                ● Currently Working
            </div>

            <div class="agent-title">
                {html.escape(current_agent)}
            </div>

            <div class="agent-description">
                {html.escape(message)}
            </div>

        </div>

        <div class="pipeline">

            {pipeline_rows}

        </div>

    </div>

    """

    with status_box.container():

        st.html(status_html)


# ============================================================
# COMPLETED STATUS
# ============================================================

def show_completed_status():

    pipeline_rows = ""

    for agent in agent_names:

        pipeline_rows += f"""

        <div class="pipeline-row">

            <div class="dot dot-done"></div>

            <div class="pipeline-name">
                {html.escape(agent)}
            </div>

            <div class="pipeline-status">
                Completed
            </div>

        </div>

        """

    status_html = f"""

    <div class="status-wrapper">

        <div class="section-label">
            Agent Activity
        </div>

        <div class="agent-card">

            <div class="agent-label">
                ● Research Complete
            </div>

            <div class="agent-title">
                All research agents completed
            </div>

            <div class="agent-description">
                The research has been planned, collected,
                analyzed, fact-checked and written into a final report.
            </div>

        </div>

        <div class="pipeline">

            {pipeline_rows}

        </div>

    </div>

    """

    with status_box.container():

        st.html(status_html)


# ============================================================
# RUN RESEARCH
# ============================================================

if analyze_clicked:

    if not topic.strip():

        st.warning("Please enter a research question first.")

        st.stop()


    # --------------------------------------------------------
    # RESET
    # --------------------------------------------------------

    st.session_state.research_started = True
    st.session_state.research_complete = False
    st.session_state.final_report = ""
    st.session_state.research_sources = []
    st.session_state.topic = topic.strip()


    # ========================================================
    # 1. RESEARCH PLANNER
    # ========================================================

    show_status(
        "Research Planner",
        "Understanding the research question and creating a focused research plan."
    )

    try:

        planner = create_planner()

        planning_task = Task(
            description=f"""
            Create a detailed research plan for the following question:

            {topic}

            Break the question into the most important research areas.

            Identify:
            - Main research questions
            - Important subtopics
            - Types of evidence required
            - Important facts that need verification
            - Information that should be included in the final report

            Do not write the final report.
            Only create the research plan.
            """,

            expected_output=(
                "A structured research plan containing research questions, "
                "subtopics, evidence requirements and verification points."
            ),

            agent=planner
        )

        planner_crew = Crew(
            agents=[planner],
            tasks=[planning_task],
            process=Process.sequential,
            verbose=False
        )

        planning_result = planner_crew.kickoff()

        planning_text = str(planning_result)

    except Exception as e:

        st.error(
            "Research Planner encountered an error:\n\n"
            + str(e)
        )

        st.stop()


    # ========================================================
    # 2. WEB RESEARCHER
    # ========================================================

    show_status(
        "Web Researcher",
        "Searching current web sources and collecting relevant evidence."
    )

    try:

        researcher = create_researcher()

        research_task = Task(
            description=f"""
            Research the following question using your web research tool:

            {topic}

            Here is the research plan created by the Research Planner:

            {planning_text}

            Search for current, relevant and reliable web sources.

            For every important finding:
            - State the finding
            - Give supporting evidence
            - Include the source title
            - Include the source URL
            - Prefer authoritative and recent sources

            Do not invent sources or URLs.

            Produce detailed research notes for the Source Analyst.
            """,

            expected_output=(
                "Detailed research notes containing findings, evidence "
                "and source titles and URLs."
            ),

            agent=researcher
        )

        researcher_crew = Crew(
            agents=[researcher],
            tasks=[research_task],
            process=Process.sequential,
            verbose=False
        )

        research_result = researcher_crew.kickoff()

        research_text = str(research_result)

    except Exception as e:

        st.error(
            "Web Researcher encountered an error:\n\n"
            + str(e)
        )

        st.stop()


    # ========================================================
    # 3. SOURCE ANALYST
    # ========================================================

    show_status(
        "Source Analyst",
        "Examining the collected research and organizing the strongest evidence."
    )

    try:

        analyst = create_analyst()

        analysis_task = Task(
            description=f"""
            Analyze the research collected for this question:

            {topic}

            RESEARCH PLAN:

            {planning_text}

            WEB RESEARCH:

            {research_text}

            Your job is to:

            1. Identify the most important findings.
            2. Separate factual information from opinions.
            3. Identify supporting evidence.
            4. Identify weak, unclear or unsupported claims.
            5. Organize the evidence logically.
            6. Identify claims that should receive additional fact checking.

            Do not write the final report.
            Prepare a structured evidence analysis for the Fact Checker
            and Report Writer.
            """,

            expected_output=(
                "A structured analysis of the research, including "
                "important evidence, supported claims and claims "
                "requiring verification."
            ),

            agent=analyst
        )

        analyst_crew = Crew(
            agents=[analyst],
            tasks=[analysis_task],
            process=Process.sequential,
            verbose=False
        )

        analysis_result = analyst_crew.kickoff()

        analysis_text = str(analysis_result)

    except Exception as e:

        st.error(
            "Source Analyst encountered an error:\n\n"
            + str(e)
        )

        st.stop()


    # ========================================================
    # 4. FACT CHECKER
    # ========================================================

    show_status(
        "Fact Checker",
        "Independently verifying important claims against web sources."
    )

    try:

        fact_checker = create_fact_checker()

        fact_check_task = Task(
            description=f"""
            Fact-check the following research.

            ORIGINAL QUESTION:

            {topic}

            RESEARCH:

            {research_text}

            SOURCE ANALYSIS:

            {analysis_text}

            Verify the most important factual claims using your web
            research tool.

            For each major claim:

            - State the claim.
            - Determine whether it is supported, partially supported,
              contradicted, or cannot be verified.
            - Give the evidence.
            - Provide the source title and URL where possible.

            Do not invent evidence.

            Focus on factual accuracy and source reliability.
            """,

            expected_output=(
                "A fact-checking report containing verified claims, "
                "uncertain claims, evidence and source URLs."
            ),

            agent=fact_checker
        )

        fact_checker_crew = Crew(
            agents=[fact_checker],
            tasks=[fact_check_task],
            process=Process.sequential,
            verbose=False
        )

        fact_check_result = fact_checker_crew.kickoff()

        fact_check_text = str(fact_check_result)

    except Exception as e:

        st.error(
            "Fact Checker encountered an error:\n\n"
            + str(e)
        )

        st.stop()


    # ========================================================
    # 5. REPORT WRITER
    # ========================================================

    show_status(
        "Research Report Writer",
        "Combining verified evidence into the final research report."
    )

    try:

        report_writer = create_report_writer()

        report_task = Task(
            description=f"""
            Write a professional research report answering:

            {topic}

            Use the following materials.

            RESEARCH PLAN:
            {planning_text}

            WEB RESEARCH:
            {research_text}

            SOURCE ANALYSIS:
            {analysis_text}

            FACT CHECK:
            {fact_check_text}

            Create a clear evidence-based report.

            Use this structure:

            # Research Report

            ## Executive Summary

            ## Introduction

            ## Key Findings

            ## Detailed Analysis

            ## Evidence and Discussion

            ## Limitations

            ## Conclusion

            ## Sources

            Important requirements:

            - Use only information supported by the supplied research.
            - Do not invent facts.
            - Do not invent citations.
            - Clearly distinguish uncertain information.
            - Keep the writing professional and readable.
            - Include source URLs in the Sources section when available.
            """,

            expected_output=(
                "A complete professional research report with headings, "
                "analysis, conclusion and source URLs."
            ),

            agent=report_writer
        )

        report_crew = Crew(
            agents=[report_writer],
            tasks=[report_task],
            process=Process.sequential,
            verbose=False
        )

        report_result = report_crew.kickoff()

        final_report = str(report_result)

    except Exception as e:

        st.error(
            "Research Report Writer encountered an error:\n\n"
            + str(e)
        )

        st.stop()


    # ========================================================
    # FINISHED
    # ========================================================

    st.session_state.final_report = final_report
    st.session_state.research_complete = True

    show_completed_status()


# ============================================================
# SHOW EXISTING REPORT
# ============================================================

if st.session_state.research_complete:

    final_report = st.session_state.final_report

    st.html("""
    <div class="section-label">
        Final Research Report
    </div>
    """)

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    words = len(final_report.split())

    metric1, metric2, metric3 = st.columns(3)

    with metric1:

        st.html(f"""
        <div class="metric-card">

            <div class="metric-number">
                5
            </div>

            <div class="metric-label">
                AI Agents
            </div>

        </div>
        """)

    with metric2:

        st.html(f"""
        <div class="metric-card">

            <div class="metric-number">
                {words:,}
            </div>

            <div class="metric-label">
                Report Words
            </div>

        </div>
        """)

    with metric3:

        st.html("""
        <div class="metric-card">

            <div class="metric-number">
                ✓
            </div>

            <div class="metric-label">
                Fact Checked
            </div>

        </div>
        """)


    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    st.html("""
    <div class="report-card">

        <div class="report-header">
            Evidence-Based Research
        </div>

    </div>
    """)

    st.markdown(
        final_report
    )


    # ========================================================
    # PDF GENERATION
    # ========================================================

    def create_pdf(text):

        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer
        )

        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm
        )

        styles = getSampleStyleSheet()

        title_style = styles["Title"]
        title_style.alignment = TA_LEFT

        heading_style = styles["Heading2"]

        body_style = styles["BodyText"]

        story = []

        lines = text.splitlines()

        for line in lines:

            clean_line = line.strip()

            if not clean_line:

                story.append(
                    Spacer(1, 6)
                )

                continue


            # Remove markdown formatting

            clean_line = re.sub(
                r"\*\*(.*?)\*\*",
                r"\1",
                clean_line
            )

            clean_line = re.sub(
                r"\*(.*?)\*",
                r"\1",
                clean_line
            )


            if clean_line.startswith("# "):

                content = clean_line[2:].strip()

                story.append(
                    Paragraph(
                        html.escape(content),
                        title_style
                    )
                )

                story.append(
                    Spacer(1, 10)
                )

            elif clean_line.startswith("## "):

                content = clean_line[3:].strip()

                story.append(
                    Paragraph(
                        html.escape(content),
                        heading_style
                    )
                )

                story.append(
                    Spacer(1, 6)
                )

            elif clean_line.startswith("### "):

                content = clean_line[4:].strip()

                story.append(
                    Paragraph(
                        html.escape(content),
                        heading_style
                    )
                )

                story.append(
                    Spacer(1, 4)
                )

            else:

                story.append(
                    Paragraph(
                        html.escape(clean_line),
                        body_style
                    )
                )

                story.append(
                    Spacer(1, 5)
                )


        document.build(story)

        buffer.seek(0)

        return buffer.getvalue()


    # --------------------------------------------------------
    # DOWNLOAD BUTTON
    # --------------------------------------------------------

    pdf_data = create_pdf(final_report)

    st.download_button(
        label="⬇ Download Research Report PDF",
        data=pdf_data,
        file_name="research_report.pdf",
        mime="application/pdf",
        use_container_width=True
    )


# ============================================================
# FOOTER
# ============================================================

st.html("""
<div style="
    text-align:center;
    margin-top:45px;
    padding:20px 0;
    border-top:1px solid rgba(255,255,255,0.06);
    color:#555;
    font-size:11px;
">
    ResearchAI · Multi-Agent Research System
</div>
""")
