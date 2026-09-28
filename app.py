import os
import html
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
    page_title="Research AI",
    page_icon="✦",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- MAIN PAGE ---------- */

    .stApp {
        background: #f7f8fc;
    }

    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }


    /* ---------- HEADER ---------- */

    .brand {
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 2px;
        color: #6366f1;
        margin-bottom: 10px;
    }

    .main-title {
        font-size: 46px;
        font-weight: 800;
        line-height: 1.1;
        color: #171923;
        margin-bottom: 10px;
    }

    .subtitle {
        font-size: 17px;
        color: #6b7280;
        margin-bottom: 30px;
    }


    /* ---------- SEARCH BOX ---------- */

    .search-label {
        font-size: 14px;
        font-weight: 700;
        color: #374151;
        margin-bottom: 8px;
    }


    /* ---------- AGENT STATUS ---------- */

    .status-wrapper {
        margin-top: 25px;
        margin-bottom: 25px;
    }

    .section-label {
        font-size: 13px;
        font-weight: 700;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }

    .agent-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.04);
    }

    .agent-current {
        border-left: 4px solid #6366f1;
    }

    .agent-label {
        font-size: 12px;
        font-weight: 700;
        color: #6366f1;
        margin-bottom: 6px;
    }

    .agent-title {
        font-size: 21px;
        font-weight: 750;
        color: #171923;
        margin-bottom: 5px;
    }

    .agent-description {
        font-size: 14px;
        color: #6b7280;
    }


    /* ---------- PIPELINE ---------- */

    .pipeline {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 8px 18px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.04);
    }

    .pipeline-row {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 14px 0;
        border-bottom: 1px solid #f0f0f0;
    }

    .pipeline-row:last-child {
        border-bottom: none;
    }

    .dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        flex-shrink: 0;
    }

    .dot-done {
        background: #22c55e;
    }

    .dot-working {
        background: #6366f1;
        box-shadow: 0 0 0 5px rgba(99,102,241,0.12);
    }

    .dot-waiting {
        background: #d1d5db;
    }

    .pipeline-name {
        flex: 1;
        font-size: 14px;
        font-weight: 600;
        color: #374151;
    }

    .pipeline-status {
        font-size: 12px;
        color: #6b7280;
    }


    /* ---------- REPORT ---------- */

    .report-box {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 28px;
        margin-top: 25px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.04);
    }

    .report-title {
        font-size: 25px;
        font-weight: 800;
        color: #171923;
        margin-bottom: 15px;
    }


    /* ---------- SOURCE BOX ---------- */

    .source-box {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 15px;
        margin-top: 10px;
    }


    /* ---------- BUTTON ---------- */

    .stButton > button {
        border-radius: 10px;
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True
)


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
# STATUS CONTAINER
# ============================================================

status_box = st.empty()


# ============================================================
# SHOW AGENT STATUS
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

    complete_html = f"""
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

        st.markdown(
            complete_html,
            unsafe_allow_html=True
        )


# ============================================================
# SHOW COMPLETED STATUS
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

    complete_html = f"""
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

        st.markdown(
            complete_html,
            unsafe_allow_html=True
        )


# ============================================================
# PAGE HEADER
# ============================================================

st.markdown(
    '<div class="brand">✦ RESEARCH AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-title">Multi-Agent Research Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Research complex topics using specialized AI agents, '
    'web sources and fact checking.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SEARCH INPUT
# ============================================================

st.markdown(
    '<div class="search-label">What would you like to research?</div>',
    unsafe_allow_html=True
)

topic = st.text_area(
    "",
    placeholder="Example: What are the effects of artificial intelligence on education?",
    height=120,
    label_visibility="collapsed"
)


# ============================================================
# SEARCH BUTTON
# ============================================================

search_clicked = st.button(
    "Search",
    type="primary",
    use_container_width=True
)


# ============================================================
# RUN RESEARCH
# ============================================================

if search_clicked:

    if not topic.strip():

        st.warning("Please enter a research topic first.")
        st.stop()


    # --------------------------------------------------------
    # CREATE AGENTS
    # --------------------------------------------------------

    try:

        planner = create_planner()
        researcher = create_researcher()
        analyst = create_analyst()
        fact_checker = create_fact_checker()
        report_writer = create_report_writer()

    except Exception as error:

        st.error(
            "Unable to initialize the AI agents. "
            "Please check your Groq API key and installed packages."
        )

        st.exception(error)

        st.stop()


    # --------------------------------------------------------
    # TASK 1 - PLANNING
    # --------------------------------------------------------

    show_status(
        "Research Planner",
        "Breaking your question into focused research areas."
    )

    planning_task = Task(
        description=f"""
        Create a detailed research plan for this question:

        {topic}

        Identify:
        1. The main research question
        2. Important subtopics
        3. Types of evidence that should be collected
        4. Important facts that need verification

        Do not write the final report.
        """,
        expected_output=(
            "A clear and structured research plan "
            "with research questions and evidence requirements."
        ),
        agent=planner
    )


    # --------------------------------------------------------
    # TASK 2 - WEB RESEARCH
    # --------------------------------------------------------

    show_status(
        "Web Researcher",
        "Searching current web sources and collecting evidence."
    )

    research_task = Task(
        description=f"""
        Research the following topic using the research plan:

        {topic}

        Search for reliable and relevant web sources.

        Collect:
        - Important facts
        - Statistics where available
        - Explanations
        - Evidence
        - Source titles
        - Source URLs

        Prefer trustworthy and recent sources.

        Do not invent information.
        """,
        expected_output=(
            "A collection of researched evidence with source titles "
            "and URLs."
        ),
        agent=researcher,
        context=[planning_task]
    )


    # --------------------------------------------------------
    # TASK 3 - ANALYSIS
    # --------------------------------------------------------

    show_status(
        "Source Analyst",
        "Analyzing the collected research and organizing the evidence."
    )

    analysis_task = Task(
        description=f"""
        Analyze the research collected for:

        {topic}

        Identify:
        - Key findings
        - Strong evidence
        - Important statistics
        - Agreements between sources
        - Differences between sources
        - Claims that require additional verification

        Clearly separate facts from opinions or interpretations.

        Do not invent information.
        """,
        expected_output=(
            "A structured analysis of the research evidence "
            "and important findings."
        ),
        agent=analyst,
        context=[research_task]
    )


    # --------------------------------------------------------
    # TASK 4 - FACT CHECKING
    # --------------------------------------------------------

    show_status(
        "Fact Checker",
        "Cross-checking important claims against independent sources."
    )

    fact_check_task = Task(
        description=f"""
        Fact-check the important claims in the research about:

        {topic}

        Verify important claims using independent web sources.

        For each important claim:
        - State the claim
        - Determine whether it is supported
        - Identify supporting sources
        - Identify conflicting information if present
        - Mark information that cannot be confirmed

        Do not assume a claim is true simply because it appears
        in one source.

        Do not invent information.
        """,
        expected_output=(
            "A fact-checking report showing which major claims "
            "are supported, disputed or unverified."
        ),
        agent=fact_checker,
        context=[research_task, analysis_task]
    )


    # --------------------------------------------------------
    # TASK 5 - FINAL REPORT
    # --------------------------------------------------------

    show_status(
        "Research Report Writer",
        "Writing the final evidence-based research report."
    )

    report_task = Task(
        description=f"""
        Write a professional research report about:

        {topic}

        Use the research, analysis and fact-checking results.

        Structure the report with:

        # Research Report

        ## Introduction

        ## Key Findings

        ## Detailed Analysis

        ## Evidence and Discussion

        ## Fact-Checked Findings

        ## Conclusion

        ## Sources

        Important requirements:

        - Use only information supported by the research.
        - Do not invent statistics or facts.
        - Clearly distinguish facts from interpretations.
        - Include source titles and URLs where available.
        - Make the report clear and readable.
        - Do not mention internal agent processes.
        """,
        expected_output=(
            "A complete professional research report "
            "with sections and source URLs."
        ),
        agent=report_writer,
        context=[
            planning_task,
            research_task,
            analysis_task,
            fact_check_task
        ]
    )


    # --------------------------------------------------------
    # CREW
    # --------------------------------------------------------

    crew = Crew(
        agents=[
            planner,
            researcher,
            analyst,
            fact_checker,
            report_writer
        ],
        tasks=[
            planning_task,
            research_task,
            analysis_task,
            fact_check_task,
            report_task
        ],
        process=Process.sequential,
        verbose=False
    )


    # --------------------------------------------------------
    # RUN CREW
    # --------------------------------------------------------

    try:

        result = crew.kickoff()

    except Exception as error:

        st.error(
            "The research process failed."
        )

        st.exception(error)

        st.stop()


    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    show_completed_status()


    # ========================================================
    # FINAL REPORT
    # ========================================================

    report_text = str(result)

    st.markdown(
        """
        <div class="report-box">
            <div class="report-title">
                Research Report
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(report_text)


    # ========================================================
    # DOWNLOAD REPORT
    # ========================================================

    st.download_button(
        label="Download Report",
        data=report_text,
        file_name="research_report.txt",
        mime="text/plain",
        use_container_width=True
    )
