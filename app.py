import html
import re
import time
from io import BytesIO

import streamlit as st
from crewai import Crew, Task, Process

from planner import create_planner
from researcher import create_researcher
from analyst import create_analyst
from fact_checker import create_fact_checker
from report_writer import create_report_writer


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ResearchAI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# BLACK + GOLD UI
# ============================================================

st.html("""
<style>

.stApp {
    background:
        radial-gradient(
            circle at 80% 0%,
            rgba(212,175,55,0.09),
            transparent 30%
        ),
        #080808;
    color: #f5f5f5;
}

.main {
    background: #080808;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    background: transparent !important;
}


/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: #090909;
    border-right: 1px solid rgba(212,175,55,0.25);
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.5rem;
}


/* BRAND */

.brand {
    padding: 8px 4px 20px 4px;
    border-bottom: 1px solid rgba(212,175,55,0.18);
    margin-bottom: 22px;
}

.brand-title {
    color: #d4af37;
    font-size: 28px;
    font-weight: 800;
}

.brand-subtitle {
    color: #858585;
    font-size: 12px;
    line-height: 1.5;
}


/* SIDEBAR TITLES */

.sidebar-section-title {
    color: #d4af37;
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin: 22px 0 10px 2px;
}


/* TOOL CARD */

.tool-card {
    background:
        linear-gradient(
            145deg,
            rgba(212,175,55,0.11),
            rgba(255,255,255,0.025)
        );

    border: 1px solid rgba(212,175,55,0.30);
    border-radius: 14px;
    padding: 15px;
    margin-bottom: 18px;
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
    background: rgba(212,175,55,0.14);
    border: 1px solid rgba(212,175,55,0.25);
}

.tool-name {
    color: #ffffff;
    font-size: 13px;
    font-weight: 600;
}

.tool-description {
    color: #858585;
    font-size: 11px;
    line-height: 1.5;
    margin-top: 5px;
}

.tool-status {
    color: #d4af37;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.7px;
    margin-top: 11px;
}


/* SIDEBAR INFO */

.sidebar-info {
    color: #858585;
    font-size: 12px;
    line-height: 1.9;
}

.sidebar-info strong {
    color: #d0d0d0;
}


/* HERO */

.hero {
    padding: 20px 0 25px 0;
}

.hero-eyebrow {
    color: #d4af37;
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.hero-title {
    color: #ffffff;
    font-size: 48px;
    font-weight: 850;
    letter-spacing: -2px;
    line-height: 1.05;
    margin: 8px 0 0 0;
}

.hero-title span {
    color: #d4af37;
}

.hero-description {
    color: #8d8d8d;
    font-size: 15px;
    max-width: 730px;
    line-height: 1.7;
    margin-top: 13px;
}


/* LABEL */

.section-label {
    color: #d4af37;
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1.4px;
    margin: 18px 0 10px 0;
}


/* AGENT CARD */

.agent-card {
    background:
        linear-gradient(
            135deg,
            rgba(212,175,55,0.09),
            rgba(255,255,255,0.025)
        );

    border: 1px solid rgba(212,175,55,0.22);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 14px;
}

.agent-current {
    border-color: rgba(212,175,55,0.55);
    box-shadow: 0 0 35px rgba(212,175,55,0.06);
}

.agent-label {
    color: #d4af37;
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 9px;
}

.agent-title {
    color: #ffffff;
    font-size: 22px;
    font-weight: 750;
}

.agent-description {
    color: #8c8c8c;
    font-size: 13px;
    line-height: 1.6;
    margin-top: 6px;
}


/* PIPELINE */

.pipeline {
    background: rgba(255,255,255,0.018);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 15px;
    padding: 8px 16px;
    margin-bottom: 22px;
}

.pipeline-row {
    display: flex;
    align-items: center;
    min-height: 52px;
    border-bottom: 1px solid rgba(255,255,255,0.045);
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
    box-shadow: 0 0 9px rgba(212,175,55,0.45);
}

.dot-working {
    background: #f3d76b;
    box-shadow:
        0 0 0 4px rgba(212,175,55,0.10),
        0 0 14px rgba(212,175,55,0.65);
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


/* TEXT AREA */

div[data-testid="stTextArea"] textarea {
    background: #101010 !important;
    color: #f5f5f5 !important;
    border: 1px solid #303030 !important;
    border-radius: 13px !important;
    padding: 15px !important;
}

div[data-testid="stTextArea"] textarea:focus {
    border: 1px solid #d4af37 !important;
    box-shadow: 0 0 0 1px rgba(212,175,55,0.15) !important;
}


/* BUTTON */

.stButton > button {
    background: #d4af37 !important;
    color: #080808 !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
    min-height: 45px;
}

.stButton > button:hover {
    background: #e6c653 !important;
    color: #000000 !important;
}


/* REPORT */

.report-card {
    background: #0d0d0d;
    border: 1px solid rgba(212,175,55,0.25);
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
}


/* METRICS */

.metric-card {
    background: #101010;
    border: 1px solid rgba(212,175,55,0.18);
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


/* EXPANDER */

div[data-testid="stExpander"] {
    background: #0d0d0d;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 13px;
}

</style>
""")


# ============================================================
# AGENTS
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

if "research_complete" not in st.session_state:
    st.session_state.research_complete = False

if "final_report" not in st.session_state:
    st.session_state.final_report = ""

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

    <div class="hero-title">
        Research <span>Intelligently.</span>
    </div>

    <div class="hero-description">
        Ask a research question and let five specialized AI agents
        plan, search, analyze, verify and write the final report.
    </div>

</div>
""")


# ============================================================
# INPUT
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
# BUTTON
# ============================================================

button_col, empty_col = st.columns([1, 3])

with button_col:

    analyze_clicked = st.button(
        "✦ Analyze Research",
        use_container_width=True
    )


# ============================================================
# STATUS CONTAINER
# ============================================================

status_box = st.empty()


# ============================================================
# SHOW STATUS
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
    <div>

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
    <div>

        <div class="section-label">
            Agent Activity
        </div>

        <div class="agent-card">

            <div class="agent-label">
                ● Research Complete
            </div>

            <div class="agent-title">
                All five agents completed
            </div>

            <div class="agent-description">
                Planning, web research, analysis,
                fact checking and report writing are complete.
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
# RATE-LIMIT SAFE CREW RUNNER
# ============================================================

def run_crew_with_retry(crew, agent_name, max_retries=3):

    for attempt in range(max_retries):

        try:

            return crew.kickoff()

        except Exception as e:

            error_text = str(e)

            is_rate_limit = (
                "RateLimitError" in error_text
                or "rate_limit_exceeded" in error_text
                or "tokens per minute" in error_text
                or "429" in error_text
            )

            if not is_rate_limit:
                raise

            # -----------------------------------------------
            # Try to read Groq's suggested wait time
            # -----------------------------------------------

            wait_seconds = 40

            match = re.search(
                r"try again in\s+([\d.]+)s",
                error_text,
                re.IGNORECASE
            )

            if match:

                try:
                    wait_seconds = float(match.group(1)) + 3
                except ValueError:
                    wait_seconds = 40

            wait_seconds = max(10, min(wait_seconds, 90))

            if attempt == max_retries - 1:

                raise RuntimeError(
                    f"{agent_name} reached the Groq token limit "
                    f"after {max_retries} attempts. "
                    f"Please wait about one minute and try again."
                )

            # -----------------------------------------------
            # Visible retry message
            # -----------------------------------------------

            show_status(
                agent_name,
                (
                    f"Groq token limit reached. "
                    f"Waiting {int(wait_seconds)} seconds before retry "
                    f"({attempt + 1}/{max_retries})."
                )
            )

            time.sleep(wait_seconds)

    raise RuntimeError("Unable to complete the agent task.")


# ============================================================
# RUN RESEARCH
# ============================================================

if analyze_clicked:

    if not topic.strip():

        st.warning("Please enter a research question first.")

        st.stop()

    topic = topic.strip()

    st.session_state.topic = topic
    st.session_state.research_complete = False
    st.session_state.final_report = ""


    # ========================================================
    # 1. PLANNER
    # ========================================================

    show_status(
        "Research Planner",
        "Breaking your question into a focused research plan."
    )

    try:

        planner = create_planner()

        planning_task = Task(
            description=f"""
            Create a short research plan for:

            {topic}

            Give:
            1. Main question
            2. 3-5 research areas
            3. Important facts to verify

            Keep the plan concise.
            """,

            expected_output=(
                "A concise research plan with 3-5 research areas "
                "and key verification points."
            ),

            agent=planner
        )

        crew = Crew(
            agents=[planner],
            tasks=[planning_task],
            process=Process.sequential,
            verbose=False
        )

        planning_result = run_crew_with_retry(
            crew,
            "Research Planner"
        )

        planning_text = str(planning_result)

    except Exception as e:

        st.error(f"Research Planner failed: {e}")
        st.stop()


    # ========================================================
    # 2. WEB RESEARCHER
    # ========================================================

    show_status(
        "Web Researcher",
        "Searching the web for current evidence and reliable sources."
    )

    try:

        researcher = create_researcher()

        research_task = Task(
            description=f"""
            Research this question using the web search tool:

            {topic}

            Research plan:
            {planning_text[:5000]}

            Find the most important current information.

            Return ONLY:
            - 5-8 key findings
            - source title
            - source URL

            Be concise.
            Do not write a report.
            Do not invent sources.
            """,

            expected_output=(
                "5-8 concise findings with source titles and URLs."
            ),

            agent=researcher
        )

        crew = Crew(
            agents=[researcher],
            tasks=[research_task],
            process=Process.sequential,
            verbose=False
        )

        research_result = run_crew_with_retry(
            crew,
            "Web Researcher"
        )

        research_text = str(research_result)

    except Exception as e:

        st.error(f"Web Researcher failed: {e}")
        st.stop()


    # ========================================================
    # 3. SOURCE ANALYST
    # ========================================================

    show_status(
        "Source Analyst",
        "Comparing findings and identifying the strongest evidence."
    )

    try:

        analyst = create_analyst()

        analysis_task = Task(
            description=f"""
            Analyze this research.

            Question:
            {topic}

            Research:
            {research_text[:7000]}

            Identify:
            - strongest findings
            - weak or unclear claims
            - important evidence
            - claims needing fact checking

            Keep the analysis concise.
            """,

            expected_output=(
                "A concise evidence analysis with strong findings "
                "and claims requiring verification."
            ),

            agent=analyst
        )

        crew = Crew(
            agents=[analyst],
            tasks=[analysis_task],
            process=Process.sequential,
            verbose=False
        )

        analysis_result = run_crew_with_retry(
            crew,
            "Source Analyst"
        )

        analysis_text = str(analysis_result)

    except Exception as e:

        st.error(f"Source Analyst failed: {e}")
        st.stop()


    # ========================================================
    # 4. FACT CHECKER
    # ========================================================

    show_status(
        "Fact Checker",
        "Independently checking the most important claims."
    )

    try:

        fact_checker = create_fact_checker()

        fact_task = Task(
            description=f"""
            Fact-check the important claims below.

            Question:
            {topic}

            Claims and analysis:
            {analysis_text[:5000]}

            Use the web search tool.

            For each important claim give:
            - Supported
            - Partially supported
            - Not verified

            Give a source URL when available.

            Keep the response concise.
            """,

            expected_output=(
                "A concise fact-check with claim status and source URLs."
            ),

            agent=fact_checker
        )

        crew = Crew(
            agents=[fact_checker],
            tasks=[fact_task],
            process=Process.sequential,
            verbose=False
        )

        fact_result = run_crew_with_retry(
            crew,
            "Fact Checker"
        )

        fact_text = str(fact_result)

    except Exception as e:

        st.error(f"Fact Checker failed: {e}")
        st.stop()


    # ========================================================
    # 5. REPORT WRITER
    # ========================================================

    show_status(
        "Research Report Writer",
        "Writing the final evidence-based research report."
    )

    try:

        writer = create_report_writer()

        report_task = Task(
            description=f"""
            Write a professional research report about:

            {topic}

            Use only the information below.

            Research:
            {research_text[:6000]}

            Analysis:
            {analysis_text[:4000]}

            Fact check:
            {fact_text[:4000]}

            Structure:

            # Research Report

            ## Executive Summary

            ## Introduction

            ## Key Findings

            ## Analysis

            ## Limitations

            ## Conclusion

            ## Sources

            Keep it clear and concise.

            Do not invent facts or citations.
            Include source URLs provided by the research.
            """,

            expected_output=(
                "A concise professional research report with "
                "sections and source URLs."
            ),

            agent=writer
        )

        crew = Crew(
            agents=[writer],
            tasks=[report_task],
            process=Process.sequential,
            verbose=False
        )

        report_result = run_crew_with_retry(
            crew,
            "Research Report Writer"
        )

        final_report = str(report_result)

    except Exception as e:

        st.error(f"Research Report Writer failed: {e}")
        st.stop()


    # ========================================================
    # COMPLETE
    # ========================================================

    st.session_state.final_report = final_report
    st.session_state.research_complete = True

    show_completed_status()


# ============================================================
# FINAL REPORT
# ============================================================

if st.session_state.research_complete:

    final_report = st.session_state.final_report

    st.html("""
    <div class="section-label">
        Final Research Report
    </div>
    """)

    words = len(final_report.split())

    col1, col2, col3 = st.columns(3)

    with col1:

        st.html("""
        <div class="metric-card">
            <div class="metric-number">5</div>
            <div class="metric-label">AI Agents</div>
        </div>
        """)

    with col2:

        st.html(f"""
        <div class="metric-card">
            <div class="metric-number">{words:,}</div>
            <div class="metric-label">Report Words</div>
        </div>
        """)

    with col3:

        st.html("""
        <div class="metric-card">
            <div class="metric-number">✓</div>
            <div class="metric-label">Fact Checked</div>
        </div>
        """)


    st.html("""
    <div class="report-card">
        <div class="report-header">
            Evidence-Based Research
        </div>
    </div>
    """)

    st.markdown(final_report)


    # ========================================================
    # PDF
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

        for line in text.splitlines():

            clean_line = line.strip()

            if not clean_line:

                story.append(Spacer(1, 6))
                continue

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

                story.append(
                    Paragraph(
                        html.escape(clean_line[2:]),
                        title_style
                    )
                )

                story.append(Spacer(1, 10))

            elif clean_line.startswith("## "):

                story.append(
                    Paragraph(
                        html.escape(clean_line[3:]),
                        heading_style
                    )
                )

                story.append(Spacer(1, 6))

            else:

                story.append(
                    Paragraph(
                        html.escape(clean_line),
                        body_style
                    )
                )

                story.append(Spacer(1, 5))

        document.build(story)

        buffer.seek(0)

        return buffer.getvalue()


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
