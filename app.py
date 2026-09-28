import os

import streamlit as st

from crewai import Crew, Process, Task

from planner import create_planner
from researcher import create_researcher
from analyst import create_analyst
from fact_checker import create_fact_checker
from report_writer import create_report_writer


# ==========================================================
# PAGE SETTINGS
# ==========================================================

st.set_page_config(
    page_title="Research AI",
    page_icon="✦",
    layout="wide"
)


# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown(
    """
    <style>

    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap'
    );

    * {
        font-family: 'Inter', sans-serif;
    }

    .stApp {

        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(91, 105, 255, 0.14),
                transparent 30%
            ),

            radial-gradient(
                circle at 90% 20%,
                rgba(132, 88, 255, 0.12),
                transparent 30%
            ),

            #080A0F;

        color: #F5F7FA;
    }


    .block-container {

        max-width: 1150px;

        padding-top: 3rem;

        padding-bottom: 4rem;
    }


    /* HERO */

    .hero {

        text-align: center;

        padding:
            2rem
            0
            2.5rem;
    }


    .eyebrow {

        color: #8E9AAF;

        font-size: 0.78rem;

        letter-spacing: 0.15em;

        text-transform: uppercase;

        margin-bottom: 0.8rem;
    }


    .hero h1 {

        font-size: 3.5rem;

        font-weight: 700;

        letter-spacing: -0.05em;

        margin-bottom: 0.7rem;
    }


    .hero p {

        color: #9AA4B2;

        font-size: 1.05rem;

        max-width: 650px;

        margin: auto;

        line-height: 1.7;
    }


    /* GLASS CARD */

    .glass-card {

        background:
            rgba(255, 255, 255, 0.045);

        border:
            1px solid
            rgba(255, 255, 255, 0.09);

        border-radius: 24px;

        padding: 1.5rem;

        backdrop-filter: blur(20px);

        box-shadow:
            0 20px 60px
            rgba(0, 0, 0, 0.25);
    }


    /* CURRENT AGENT */

    .current-agent {

        background:
            rgba(105, 120, 255, 0.10);

        border:
            1px solid
            rgba(125, 140, 255, 0.25);

        border-radius: 18px;

        padding: 1.1rem 1.25rem;

        margin:
            1.5rem 0
            1.3rem;
    }


    .current-label {

        color: #8995FF;

        font-size: 0.72rem;

        font-weight: 700;

        letter-spacing: 0.12em;

        text-transform: uppercase;
    }


    .current-name {

        font-size: 1.2rem;

        font-weight: 600;

        margin-top: 0.35rem;
    }


    .current-description {

        color: #9AA4B2;

        margin-top: 0.25rem;

        font-size: 0.9rem;
    }


    /* AGENT ROW */

    .agent-row {

        display: flex;

        align-items: center;

        gap: 12px;

        padding: 0.8rem 0;

        border-bottom:
            1px solid
            rgba(255, 255, 255, 0.05);
    }


    .agent-row:last-child {

        border-bottom: none;
    }


    .agent-dot {

        width: 10px;

        height: 10px;

        border-radius: 50%;

        flex-shrink: 0;
    }


    .done {

        background: #69D39B;

        box-shadow:
            0 0 12px
            rgba(105, 211, 155, 0.5);
    }


    .working {

        background: #8995FF;

        box-shadow:
            0 0 15px
            rgba(137, 149, 255, 0.7);
    }


    .waiting {

        background: #414754;
    }


    .agent-name {

        font-size: 0.9rem;
    }


    .agent-status {

        margin-left: auto;

        color: #737D8D;

        font-size: 0.78rem;
    }


    /* REPORT */

    .report {

        background:
            rgba(255, 255, 255, 0.035);

        border:
            1px solid
            rgba(255, 255, 255, 0.08);

        border-radius: 24px;

        padding: 2rem;

        line-height: 1.8;

        margin-top: 1.5rem;
    }


    /* BUTTON */

    div.stButton > button {

        border-radius: 14px;

        border:
            1px solid
            rgba(255, 255, 255, 0.12);

        background:
            rgba(255, 255, 255, 0.07);

        color: white;

        min-height: 48px;

        transition:
            all 0.2s ease;
    }


    div.stButton > button:hover {

        border-color:
            rgba(137, 149, 255, 0.55);

        background:
            rgba(137, 149, 255, 0.12);

        transform:
            translateY(-1px);
    }


    textarea {

        background:
            rgba(255, 255, 255, 0.045)
            !important;

        border-radius:
            16px
            !important;
    }


    @media (max-width: 700px) {

        .hero h1 {

            font-size: 2.4rem;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# HERO
# ==========================================================

st.markdown(
    """
    <div class="hero">

        <div class="eyebrow">
            Multi-Agent Research Workspace
        </div>

        <h1>
            Research AI
        </h1>

        <p>
            Ask a question and let a team of specialized
            AI agents research, analyze, verify and write.
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# AGENTS
# ==========================================================

agent_names = [

    "Research Planner",

    "Web Researcher",

    "Source Analyst",

    "Fact Checker",

    "Report Writer"
]


# ==========================================================
# STATUS PLACEHOLDER
# ==========================================================

status_box = st.empty()


def show_status(
    current_agent,
    message
):

    current_index = agent_names.index(
        current_agent
    )

    with status_box.container():

        # Current agent

        st.markdown(
            f"""
            <div class="current-agent">

                <div class="current-label">
                    ● Current Agent
                </div>

                <div class="current-name">
                    {current_agent}
                </div>

                <div class="current-description">
                    {message}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        # Pipeline

        st.markdown(
            '<div class="glass-card">',
            unsafe_allow_html=True
        )


        for index, agent in enumerate(
            agent_names
        ):

            if index < current_index:

                dot = "done"

                status = "Completed"

            elif index == current_index:

                dot = "working"

                status = "Working"

            else:

                dot = "waiting"

                status = "Waiting"


            st.markdown(
                f"""
                <div class="agent-row">

                    <div class="agent-dot {dot}">
                    </div>

                    <div class="agent-name">
                        {agent}
                    </div>

                    <div class="agent-status">
                        {status}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


# ==========================================================
# QUESTION INPUT
# ==========================================================

st.markdown(
    '<div class="glass-card">',
    unsafe_allow_html=True
)


question = st.text_area(

    "Research Question",

    placeholder=(
        "Example: How is artificial intelligence "
        "changing education in 2026?"
    ),

    height=130,

    label_visibility="collapsed"
)


start = st.button(

    "Start Research  →",

    use_container_width=True
)


st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# ==========================================================
# START RESEARCH
# ==========================================================

if start:

    # ------------------------------------------------------
    # Validate question
    # ------------------------------------------------------

    if not question.strip():

        st.warning(
            "Please enter a research question."
        )

        st.stop()


    # ------------------------------------------------------
    # Get Groq key
    # ------------------------------------------------------

    groq_key = st.secrets.get(

        "GROQ_API_KEY",

        os.environ.get(
            "GROQ_API_KEY"
        )
    )


    if not groq_key:

        st.error(
            "GROQ_API_KEY is missing. "
            "Add it to Streamlit Secrets."
        )

        st.stop()


    os.environ[
        "GROQ_API_KEY"
    ] = groq_key


    # ======================================================
    # AGENT 1 — PLANNER
    # ======================================================

    show_status(

        "Research Planner",

        "Breaking your question into focused research areas."
    )


    planner = create_planner()


    planning_task = Task(

        description=f"""

        Create a concise research plan.

        Research question:

        {question}

        Identify:

        1. Main research objectives
        2. Important subtopics
        3. Evidence that should be collected
        4. Important questions the final report should answer

        Keep the plan practical and focused.

        """,

        expected_output=(
            "A clear research plan containing "
            "objectives, subtopics and evidence requirements."
        ),

        agent=planner
    )


    planner_crew = Crew(

        agents=[
            planner
        ],

        tasks=[
            planning_task
        ],

        process=Process.sequential,

        verbose=False
    )


    plan_result = planner_crew.kickoff()


    plan_text = str(
        plan_result
    )


    # ======================================================
    # AGENT 2 — WEB RESEARCHER
    # ======================================================

    show_status(

        "Web Researcher",

        "Searching current web sources and collecting evidence."
    )


    researcher = create_researcher()


    research_task = Task(

        description=f"""

        Research this question:

        {question}

        Research plan:

        {plan_text}

        You MUST use your Web Research Tool.

        Find relevant and reasonably reliable sources.

        For useful sources collect:

        - Source title
        - URL
        - Important evidence
        - Relevant facts
        - Publication information when available

        Do not invent sources.

        """,

        expected_output=(
            "A research package containing "
            "source titles, URLs and evidence."
        ),

        agent=researcher
    )


    researcher_crew = Crew(

        agents=[
            researcher
        ],

        tasks=[
            research_task
        ],

        process=Process.sequential,

        verbose=False
    )


    research_result = (
        researcher_crew.kickoff()
    )


    research_text = str(
        research_result
    )


    # ======================================================
    # AGENT 3 — ANALYST
    # ======================================================

    show_status(

        "Source Analyst",

        "Analyzing the collected evidence and identifying findings."
    )


    analyst = create_analyst()


    analysis_task = Task(

        description=f"""

        Analyze the research package.

        Original question:

        {question}

        Research:

        {research_text}

        Identify:

        - Important findings
        - Important facts
        - Statistics
        - Patterns
        - Agreements
        - Disagreements
        - Claims that require verification

        Do not invent evidence.

        """,

        expected_output=(
            "A structured evidence analysis "
            "with key findings and claims requiring verification."
        ),

        agent=analyst
    )


    analyst_crew = Crew(

        agents=[
            analyst
        ],

        tasks=[
            analysis_task
        ],

        process=Process.sequential,

        verbose=False
    )


    analysis_result = (
        analyst_crew.kickoff()
    )


    analysis_text = str(
        analysis_result
    )


    # ======================================================
    # AGENT 4 — FACT CHECKER
    # ======================================================

    show_status(

        "Fact Checker",

        "Cross-checking important claims against web sources."
    )


    fact_checker = (
        create_fact_checker()
    )


    fact_task = Task(

        description=f"""

        Fact-check the research.

        Original question:

        {question}

        Research:

        {research_text}

        Analysis:

        {analysis_text}

        You MUST use your Web Research Tool.

        Independently verify important claims.

        Classify claims as:

        SUPPORTED
        PARTIALLY SUPPORTED
        CONFLICTING
        NOT VERIFIED

        Explain the reason briefly.

        Include source URLs where possible.

        Do not invent verification.

        """,

        expected_output=(
            "A fact-checking report identifying "
            "supported, partially supported, "
            "conflicting and unverified claims."
        ),

        agent=fact_checker
    )


    fact_crew = Crew(

        agents=[
            fact_checker
        ],

        tasks=[
            fact_task
        ],

        process=Process.sequential,

        verbose=False
    )


    fact_result = (
        fact_crew.kickoff()
    )


    fact_text = str(
        fact_result
    )


    # ======================================================
    # AGENT 5 — REPORT WRITER
    # ======================================================

    show_status(

        "Report Writer",

        "Writing the final research report."
    )


    writer = (
        create_report_writer()
    )


    writing_task = Task(

        description=f"""

        Write the final research report.

        Research question:

        {question}

        Research:

        {research_text}

        Analysis:

        {analysis_text}

        Fact checking:

        {fact_text}

        Use these sections:

        # Title

        ## Executive Summary

        ## Introduction

        ## Key Findings

        ## Evidence and Analysis

        ## Fact-Checking Notes

        ## Conclusion

        ## Sources

        Important rules:

        - Do not invent facts.
        - Do not invent citations.
        - Use URLs provided by the research.
        - Clearly identify uncertain claims.
        - Keep the report professional and readable.

        """,

        expected_output=(
            "A polished research report in Markdown "
            "with a Sources section."
        ),

        agent=writer
    )


    writer_crew = Crew(

        agents=[
            writer
        ],

        tasks=[
            writing_task
        ],

        process=Process.sequential,

        verbose=False
    )


    final_result = (
        writer_crew.kickoff()
    )


    final_report = str(
        final_result
    )


    # ======================================================
    # COMPLETE
    # ======================================================

    with status_box.container():

        st.markdown(
            """
            <div class="current-agent">

                <div class="current-label">
                    ✓ Research Complete
                </div>

                <div class="current-name">
                    All agents finished
                </div>

                <div class="current-description">
                    Your research report is ready.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        st.markdown(
            '<div class="glass-card">',
            unsafe_allow_html=True
        )


        for agent in agent_names:

            st.markdown(
                f"""
                <div class="agent-row">

                    <div class="agent-dot done">
                    </div>

                    <div class="agent-name">
                        {agent}
                    </div>

                    <div class="agent-status">
                        Completed
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


    # ======================================================
    # REPORT
    # ======================================================

    st.markdown(
        '<div class="report">',
        unsafe_allow_html=True
    )


    st.markdown(
        final_report
    )


    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


    # ======================================================
    # DOWNLOAD
    # ======================================================

    st.download_button(

        label="Download Research Report",

        data=final_report,

        file_name="research_report.md",

        mime="text/markdown",

        use_container_width=True
    )
