import os

import streamlit as st
from crewai import Crew, Process, Task

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
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- MAIN APP ---------- */

    .stApp {
        background: #090A0F;
    }

    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }


    /* ---------- REMOVE DEFAULT STREAMLIT ELEMENTS ---------- */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }


    /* ---------- TOP BRAND ---------- */

    .brand {
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        color: #A7B0C0;
        margin-bottom: 3rem;
    }

    .brand-symbol {
        color: #8B7CFF;
        font-size: 1.1rem;
        margin-right: 8px;
    }


    /* ---------- HERO ---------- */

    .hero-title {
        font-size: 3.8rem;
        font-weight: 700;
        letter-spacing: -0.055em;
        line-height: 1.05;
        color: #F5F7FB;
        margin-bottom: 1rem;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        line-height: 1.7;
        color: #8E97A8;
        max-width: 650px;
        margin-bottom: 2rem;
    }


    /* ---------- QUESTION CARD ---------- */

    .question-card {
        background: #11131A;
        border: 1px solid #242833;
        border-radius: 22px;
        padding: 1.4rem;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
    }


    /* ---------- TEXT AREA ---------- */

    textarea {
        background: #0D0F15 !important;
        color: #F5F7FB !important;
        border: 1px solid #292E39 !important;
        border-radius: 15px !important;
    }

    textarea:focus {
        border: 1px solid #7568FF !important;
        box-shadow: 0 0 0 1px #7568FF !important;
    }


    /* ---------- BUTTON ---------- */

    div.stButton > button {
        width: 100%;
        min-height: 50px;

        border-radius: 14px;

        background: #7568FF;

        color: white;

        border: none;

        font-size: 0.95rem;

        font-weight: 600;

        transition: 0.2s ease;
    }

    div.stButton > button:hover {
        background: #887DFF;
        transform: translateY(-1px);
    }

    div.stButton > button:active {
        transform: scale(0.99);
    }


    /* ---------- SECTION TITLES ---------- */

    .section-label {
        color: #727B8D;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-top: 2rem;
        margin-bottom: 0.8rem;
    }


    /* ---------- AGENT CARD ---------- */

    .agent-card {
        background: #11131A;
        border: 1px solid #242833;
        border-radius: 20px;
        padding: 1.2rem 1.3rem;
        margin-bottom: 1rem;
    }


    .agent-current {
        background: linear-gradient(
            135deg,
            rgba(117, 104, 255, 0.13),
            rgba(117, 104, 255, 0.035)
        );

        border: 1px solid rgba(117, 104, 255, 0.32);
    }


    .agent-label {
        color: #7568FF;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.13em;
        text-transform: uppercase;
    }


    .agent-title {
        color: #F5F7FB;
        font-size: 1.35rem;
        font-weight: 650;
        margin-top: 0.4rem;
    }


    .agent-description {
        color: #8992A3;
        font-size: 0.88rem;
        margin-top: 0.35rem;
    }


    /* ---------- PIPELINE ---------- */

    .pipeline {
        background: #11131A;
        border: 1px solid #242833;
        border-radius: 20px;
        padding: 0.7rem 1.2rem;
    }


    .pipeline-row {
        display: flex;
        align-items: center;
        padding: 0.95rem 0;

        border-bottom: 1px solid #20242D;
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
        background: #5ED49A;
        box-shadow: 0 0 10px rgba(94, 212, 154, 0.45);
    }


    .dot-working {
        background: #7568FF;
        box-shadow: 0 0 12px rgba(117, 104, 255, 0.65);
    }


    .dot-waiting {
        background: #3C424E;
    }


    .pipeline-name {
        color: #E6E9EF;
        font-size: 0.88rem;
    }


    .pipeline-status {
        margin-left: auto;
        color: #737C8D;
        font-size: 0.75rem;
    }


    /* ---------- REPORT ---------- */

    .report-header {
        margin-top: 2.5rem;
        margin-bottom: 1rem;
    }


    .report-box {
        background: #101219;
        border: 1px solid #252A35;
        border-radius: 22px;
        padding: 2rem;
    }


    /* ---------- DOWNLOAD BUTTON ---------- */

    div.stDownloadButton > button {
        border-radius: 13px;
        background: #171A22;
        color: #E9ECF2;
        border: 1px solid #303541;
    }

    div.stDownloadButton > button:hover {
        border-color: #7568FF;
        color: white;
    }


    /* ---------- MOBILE ---------- */

    @media (max-width: 700px) {

        .hero-title {
            font-size: 2.6rem;
        }

        .hero-subtitle {
            font-size: 0.95rem;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# BRAND
# ============================================================

st.markdown(
    """
    <div class="brand">
        <span class="brand-symbol">✦</span>
        RESEARCH AI
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero-title">
        Turn a question<br>
        into a research report.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="hero-subtitle">
        A team of specialized AI agents researches the web,
        analyzes evidence, verifies important claims,
        and produces a structured research report.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# QUESTION
# ============================================================

st.markdown(
    '<div class="section-label">Research Question</div>',
    unsafe_allow_html=True
)

question = st.text_area(
    "Research Question",
    placeholder=(
        "What would you like to research?\n\n"
        "Example: How is artificial intelligence "
        "changing education in 2026?"
    ),
    height=140,
    label_visibility="collapsed"
)


start = st.button(
    "Start Research  →",
    use_container_width=True
)


# ============================================================
# AGENT NAMES
# ============================================================

agent_names = [
    "Research Planner",
    "Web Researcher",
    "Source Analyst",
    "Fact Checker",
    "Report Writer"
]


# ============================================================
# STATUS
# ============================================================

status_box = st.empty()


def show_status(current_agent, message):

    current_index = agent_names.index(current_agent)

    with status_box.container():

        st.markdown(
            '<div class="section-label">Agent Activity</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="agent-card agent-current">

                <div class="agent-label">
                    ● Currently Working
                </div>

                <div class="agent-title">
                    {current_agent}
                </div>

                <div class="agent-description">
                    {message}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        rows = ""

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

            rows += f"""
            <div class="pipeline-row">

                <div class="dot {dot_class}"></div>

                <div class="pipeline-name">
                    {agent}
                </div>

                <div class="pipeline-status">
                    {status}
                </div>

            </div>
            """

        st.markdown(
            f"""
            <div class="pipeline">
                {rows}
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# RESEARCH
# ============================================================

if start:

    if not question.strip():

        st.warning(
            "Please enter a research question first."
        )

        st.stop()


    # ========================================================
    # API KEY
    # ========================================================

    groq_key = st.secrets.get(
        "GROQ_API_KEY",
        os.environ.get("GROQ_API_KEY")
    )

    if not groq_key:

        st.error(
            "GROQ_API_KEY is missing. "
            "Add it in Streamlit Cloud → Settings → Secrets."
        )

        st.stop()

    os.environ["GROQ_API_KEY"] = groq_key


    # ========================================================
    # 1. PLANNER
    # ========================================================

    show_status(
        "Research Planner",
        "Breaking your question into focused research areas."
    )

    planner = create_planner()

    planning_task = Task(

        description=f"""
        Create a focused research plan for:

        {question}

        Identify:

        1. Main research objectives
        2. Important subtopics
        3. Evidence that should be collected
        4. Questions the final report should answer

        Keep the plan concise and practical.
        """,

        expected_output=(
            "A structured research plan with "
            "objectives, subtopics and evidence requirements."
        ),

        agent=planner
    )

    planner_crew = Crew(
        agents=[planner],
        tasks=[planning_task],
        process=Process.sequential,
        verbose=False
    )

    plan_result = planner_crew.kickoff()

    plan_text = str(plan_result)


    # ========================================================
    # 2. WEB RESEARCHER
    # ========================================================

    show_status(
        "Web Researcher",
        "Searching current web sources and collecting evidence."
    )

    researcher = create_researcher()

    research_task = Task(

        description=f"""
        Research the following question:

        {question}

        Research plan:

        {plan_text}

        You MUST use the Web Research Tool.

        Find relevant and reliable sources.

        For each useful source collect:

        - Title
        - URL
        - Important evidence
        - Relevant facts
        - Publication information if available

        Do not invent sources.
        """,

        expected_output=(
            "A research package containing "
            "source titles, URLs and evidence."
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


    # ========================================================
    # 3. ANALYST
    # ========================================================

    show_status(
        "Source Analyst",
        "Analyzing evidence, patterns and important findings."
    )

    analyst = create_analyst()

    analysis_task = Task(

        description=f"""
        Analyze the collected research.

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
        agents=[analyst],
        tasks=[analysis_task],
        process=Process.sequential,
        verbose=False
    )

    analysis_result = analyst_crew.kickoff()

    analysis_text = str(analysis_result)


    # ========================================================
    # 4. FACT CHECKER
    # ========================================================

    show_status(
        "Fact Checker",
        "Cross-checking important claims against independent sources."
    )

    fact_checker = create_fact_checker()

    fact_task = Task(

        description=f"""
        Fact-check the research.

        Original question:

        {question}

        Research:

        {research_text}

        Analysis:

        {analysis_text}

        You MUST use the Web Research Tool.

        Independently verify important claims.

        Classify claims as:

        SUPPORTED
        PARTIALLY SUPPORTED
        CONFLICTING
        NOT VERIFIED

        Explain each result briefly.

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
        agents=[fact_checker],
        tasks=[fact_task],
        process=Process.sequential,
        verbose=False
    )

    fact_result = fact_crew.kickoff()

    fact_text = str(fact_result)


    # ========================================================
    # 5. REPORT WRITER
    # ========================================================

    show_status(
        "Report Writer",
        "Writing the final evidence-based research report."
    )

    writer = create_report_writer()

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

        Rules:

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
        agents=[writer],
        tasks=[writing_task],
        process=Process.sequential,
        verbose=False
    )

    final_result = writer_crew.kickoff()

    final_report = str(final_result)


    # ========================================================
    # COMPLETE
    # ========================================================

    with status_box.container():

        st.markdown(
            '<div class="section-label">Research Complete</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="agent-card">

                <div class="agent-label">
                    ✓ COMPLETED
                </div>

                <div class="agent-title">
                    Your research is ready.
                </div>

                <div class="agent-description">
                    All five research agents have completed their work.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        rows = ""

        for agent in agent_names:

            rows += f"""
            <div class="pipeline-row">

                <div class="dot dot-done"></div>

                <div class="pipeline-name">
                    {agent}
                </div>

                <div class="pipeline-status">
                    Completed
                </div>

            </div>
            """

        st.markdown(
            f"""
            <div class="pipeline">
                {rows}
            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # REPORT
    # ========================================================

    st.markdown(
        '<div class="report-header">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-label">Final Report</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="report-box">',
        unsafe_allow_html=True
    )

    st.markdown(final_report)

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


    # ========================================================
    # DOWNLOAD
    # ========================================================

    st.download_button(
        "Download Research Report",
        data=final_report,
        file_name="research_report.md",
        mime="text/markdown",
        use_container_width=True
    )
