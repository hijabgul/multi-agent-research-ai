import re
from io import BytesIO

import streamlit as st
from ddgs import DDGS
from crewai import Crew, Task
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER

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
    page_icon="🔎",
    layout="wide"
)


# ============================================================
# CSS
# ============================================================

st.html("""
<style>

    .stApp {
        background: #080808;
        color: #f5f5f5;
    }

    [data-testid="stSidebar"] {
        background: #0d0d0d;
        border-right: 1px solid #292929;
    }

    [data-testid="stSidebar"] * {
        color: #eeeeee;
    }

    .brand {
        font-size: 28px;
        font-weight: 800;
        color: #d4af37;
        margin-bottom: 5px;
    }

    .brand-sub {
        color: #888888;
        font-size: 13px;
        margin-bottom: 30px;
    }

    .sidebar-card {
        background: #151515;
        border: 1px solid #292929;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
    }

    .sidebar-title {
        color: #d4af37;
        font-weight: 700;
        font-size: 14px;
        margin-bottom: 7px;
    }

    .sidebar-text {
        color: #aaaaaa;
        font-size: 13px;
        line-height: 1.5;
    }

    .hero {
        padding: 20px 0 10px 0;
    }

    .hero-small {
        color: #d4af37;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .hero-title {
        font-size: 48px;
        font-weight: 800;
        color: #ffffff;
        margin-top: 5px;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        color: #999999;
        font-size: 17px;
        max-width: 760px;
        line-height: 1.6;
    }

    .section-title {
        color: #ffffff;
        font-size: 21px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 10px;
    }

    .agent-card {
        background: #121212;
        border: 1px solid #292929;
        border-radius: 12px;
        padding: 13px 16px;
        margin-bottom: 9px;
    }

    .agent-active {
        background: #18150b;
        border: 1px solid #d4af37;
    }

    .agent-completed {
        background: #101510;
        border: 1px solid #365936;
    }

    .agent-waiting {
        background: #121212;
        border: 1px solid #292929;
    }

    .agent-name {
        color: #ffffff;
        font-weight: 700;
        font-size: 15px;
    }

    .agent-status {
        color: #999999;
        font-size: 12px;
        margin-top: 4px;
    }

    .gold {
        color: #d4af37;
    }

    .success-text {
        color: #75b975;
    }

    .footer {
        text-align: center;
        color: #666666;
        font-size: 12px;
        margin-top: 50px;
        padding: 20px;
        border-top: 1px solid #222222;
    }

    div.stButton > button {
        background: #d4af37;
        color: #000000;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        min-height: 45px;
    }

    div.stButton > button:hover {
        background: #e5c354;
        color: #000000;
    }

    textarea {
        background-color: #111111 !important;
        color: #ffffff !important;
    }

</style>
""")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.html("""
    <div class="brand">ResearchAI</div>
    <div class="brand-sub">Multi-Agent Research Assistant</div>
    """)

    st.html("""
    <div class="sidebar-card">
        <div class="sidebar-title">🌐 Web Research Tool</div>
        <div class="sidebar-text">
            DuckDuckGo Search<br>
            <span style="color:#75b975;">● Connected</span>
        </div>
    </div>
    """)

    st.html("""
    <div class="sidebar-card">
        <div class="sidebar-title">AI PIPELINE</div>
        <div class="sidebar-text">
            Research Planner<br>
            Web Researcher<br>
            Source Analyst<br>
            Fact Checker<br>
            Research Report Writer
        </div>
    </div>
    """)

    st.html("""
    <div class="sidebar-card">
        <div class="sidebar-title">TECHNOLOGY</div>
        <div class="sidebar-text">
            CrewAI<br>
            Groq<br>
            DuckDuckGo<br>
            Streamlit
        </div>
    </div>
    """)


# ============================================================
# HERO
# ============================================================

st.html("""
<div class="hero">
    <div class="hero-small">MULTI-AGENT RESEARCH</div>
    <div class="hero-title">Research Intelligently.</div>
    <div class="hero-subtitle">
        Ask a research question and let a team of specialized AI agents
        plan, search, analyze, verify, and write your research report.
    </div>
</div>
""")


# ============================================================
# WEB SEARCH FUNCTION
# ============================================================

def search_web(query, max_results=3):

    query = query.strip()

    if not query:
        return "No search query was provided."

    try:

        results = DDGS().text(
            query,
            max_results=max_results
        )

        if not results:
            return f"No web results found for: {query}"

        output = []

        for number, result in enumerate(results, start=1):

            title = result.get("title", "Untitled")
            url = result.get("href", "")
            summary = result.get("body", "")

            output.append(
                f"""
SOURCE {number}

Title:
{title}

URL:
{url}

Summary:
{summary[:400]}
""".strip()
            )

        return "\n\n".join(output)

    except Exception as e:

        return f"Web search failed: {str(e)}"


# ============================================================
# AGENT STATUS
# ============================================================

agent_names = [
    "Research Planner",
    "Web Researcher",
    "Source Analyst",
    "Fact Checker",
    "Research Report Writer"
]


def show_agent_activity(current_agent=None, completed_agents=None):

    if completed_agents is None:
        completed_agents = []

    st.html("""
    <div class="section-title">Agent Activity</div>
    """)

    html = ""

    for agent in agent_names:

        if agent in completed_agents:

            html += f"""
            <div class="agent-card agent-completed">
                <div class="agent-name">
                    ✓ {agent}
                </div>
                <div class="agent-status success-text">
                    Completed
                </div>
            </div>
            """

        elif agent == current_agent:

            html += f"""
            <div class="agent-card agent-active">
                <div class="agent-name">
                    ● {agent}
                </div>
                <div class="agent-status gold">
                    Working...
                </div>
            </div>
            """

        else:

            html += f"""
            <div class="agent-card agent-waiting">
                <div class="agent-name">
                    ○ {agent}
                </div>
                <div class="agent-status">
                    Waiting
                </div>
            </div>
            """

    st.html(html)


# ============================================================
# CREW AGENT RUNNER
# ============================================================

def run_single_agent(agent, task_description):

    task = Task(
        description=task_description,
        expected_output=(
            "Return concise, useful research information. "
            "Do not invent facts. Use only the information provided "
            "in the task and clearly identify sources when available."
        ),
        agent=agent
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=False
    )

    result = crew.kickoff()

    if result is None:
        raise Exception("The agent returned no response.")

    output = str(result).strip()

    if not output:
        raise Exception("The agent returned an empty response.")

    return output


# ============================================================
# PDF GENERATOR
# ============================================================

def create_pdf(report_text):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    body_style = styles["BodyText"]
    body_style.leading = 16
    body_style.spaceAfter = 8

    heading_style = styles["Heading2"]
    heading_style.spaceBefore = 12
    heading_style.spaceAfter = 8

    story = []

    story.append(
        Paragraph(
            "ResearchAI Research Report",
            title_style
        )
    )

    story.append(Spacer(1, 20))

    lines = report_text.split("\n")

    for line in lines:

        line = line.strip()

        if not line:
            story.append(Spacer(1, 6))
            continue

        clean_line = re.sub(
            r"[#*_`]",
            "",
            line
        )

        if (
            clean_line.upper().startswith("INTRODUCTION")
            or clean_line.upper().startswith("CONCLUSION")
            or clean_line.upper().startswith("SOURCES")
            or clean_line.upper().startswith("KEY FINDINGS")
            or clean_line.upper().startswith("ANALYSIS")
        ):
            story.append(
                Paragraph(
                    clean_line,
                    heading_style
                )
            )
        else:
            story.append(
                Paragraph(
                    clean_line,
                    body_style
                )
            )

    document.build(story)

    buffer.seek(0)

    return buffer


# ============================================================
# INPUT
# ============================================================

st.html("""
<div class="section-title">Research Question</div>
""")

question = st.text_area(
    "Enter your research question",
    placeholder=(
        "Example: What are the benefits and challenges "
        "of artificial intelligence in education?"
    ),
    height=130,
    label_visibility="collapsed"
)


# ============================================================
# ANALYZE BUTTON
# ============================================================

analyze = st.button(
    "🔎 Analyze Research Question",
    use_container_width=True
)


# ============================================================
# MAIN PIPELINE
# ============================================================

if analyze:

    if not question.strip():

        st.warning("Please enter a research question first.")

        st.stop()

    completed = []

    status_placeholder = st.empty()

    activity_placeholder = st.empty()

    with activity_placeholder.container():

        show_agent_activity()

    # --------------------------------------------------------
    # 1. RESEARCH PLANNER
    # --------------------------------------------------------

    try:

        with status_placeholder.container():

            st.info("Research question received")

        with activity_placeholder.container():

            show_agent_activity(
                current_agent="Research Planner",
                completed_agents=completed
            )

        planner = create_planner()

        planning_prompt = f"""
Research Question:

{question}

Create a short research plan for this question.

Identify:
1. The main topics that need investigation.
2. Important facts that should be verified.
3. What types of sources should be searched.

Keep the plan concise.
"""

        plan = run_single_agent(
            planner,
            planning_prompt
        )

        completed.append("Research Planner")

    except Exception as e:

        st.error(f"Research Planner failed: {str(e)}")

        st.stop()


    # --------------------------------------------------------
    # 2. WEB SEARCH
    # --------------------------------------------------------

    try:

        with status_placeholder.container():

            st.info("Searching current web sources")

        with activity_placeholder.container():

            show_agent_activity(
                current_agent="Web Researcher",
                completed_agents=completed
            )

        # Search based on the original question
        web_results = search_web(
            question,
            max_results=3
        )

        # Also search the main topics from the plan
        plan_search = search_web(
            question + " latest research study evidence",
            max_results=3
        )

        combined_sources = (
            web_results
            + "\n\n"
            + plan_search
        )

        researcher = create_researcher()

        researcher_prompt = f"""
Research Question:

{question}

Research Plan:

{plan[:3500]}

Web Search Results:

{combined_sources[:5000]}

Analyze these search results.

Return:
- the most relevant facts
- important evidence
- source titles
- source URLs

Do not invent information.
Do not perform another web search.
Keep the response concise.
"""

        research_findings = run_single_agent(
            researcher,
            researcher_prompt
        )

        completed.append("Web Researcher")

    except Exception as e:

        st.error(f"Web Researcher failed: {str(e)}")

        st.stop()


    # --------------------------------------------------------
    # 3. SOURCE ANALYST
    # --------------------------------------------------------

    try:

        with status_placeholder.container():

            st.info("Extracting and analyzing evidence")

        with activity_placeholder.container():

            show_agent_activity(
                current_agent="Source Analyst",
                completed_agents=completed
            )

        analyst = create_analyst()

        analyst_prompt = f"""
Research Question:

{question}

Research Plan:

{plan[:2500]}

Web Research Findings:

{research_findings[:5000]}

Analyze the findings.

Identify:
1. Strong evidence.
2. Important facts.
3. Claims that require verification.
4. Weak or unclear information.
5. The most useful sources.

Do not add unsupported facts.
Keep the analysis concise.
"""

        analysis = run_single_agent(
            analyst,
            analyst_prompt
        )

        completed.append("Source Analyst")

    except Exception as e:

        st.error(f"Source Analyst failed: {str(e)}")

        st.stop()


    # --------------------------------------------------------
    # 4. FACT CHECKER
    # --------------------------------------------------------

    try:

        with status_placeholder.container():

            st.info("Cross-checking important claims")

        with activity_placeholder.container():

            show_agent_activity(
                current_agent="Fact Checker",
                completed_agents=completed
            )

        # Direct web search instead of CrewAI tool calling
        fact_check_sources = search_web(
            question + " evidence facts study verification",
            max_results=3
        )

        fact_checker = create_fact_checker()

        fact_check_prompt = f"""
Research Question:

{question}

Research Findings:

{research_findings[:4000]}

Source Analysis:

{analysis[:4000]}

Independent Web Sources:

{fact_check_sources[:3500]}

Fact-check the important claims.

For each important claim:
- State whether it appears supported.
- Identify supporting evidence.
- Mention uncertainty when evidence is insufficient.
- Include source URLs where available.

Do not invent facts.
Do not perform another web search.
Keep the response concise.
"""

        fact_check = run_single_agent(
            fact_checker,
            fact_check_prompt
        )

        completed.append("Fact Checker")

    except Exception as e:

        st.error(f"Fact Checker failed: {str(e)}")

        st.stop()


    # --------------------------------------------------------
    # 5. REPORT WRITER
    # --------------------------------------------------------

    try:

        with status_placeholder.container():

            st.info("AI is analyzing and writing the final report")

        with activity_placeholder.container():

            show_agent_activity(
                current_agent="Research Report Writer",
                completed_agents=completed
            )

        writer = create_report_writer()

        report_prompt = f"""
Write a professional research report about:

{question}

Research Plan:
{plan[:2000]}

Web Research:
{research_findings[:4000]}

Source Analysis:
{analysis[:3500]}

Fact Check:
{fact_check[:4000]}

Create the final report using this structure:

# Research Report

## Introduction

## Key Findings

## Analysis

## Verified Evidence

## Conclusion

## Sources

Rules:
- Use only the evidence provided.
- Do not invent statistics, studies, dates, or facts.
- Clearly communicate uncertainty.
- Include important source URLs.
- Keep the report clear and professional.
"""

        final_report = run_single_agent(
            writer,
            report_prompt
        )

        completed.append("Research Report Writer")

    except Exception as e:

        st.error(f"Research Report Writer failed: {str(e)}")

        st.stop()


    # --------------------------------------------------------
    # COMPLETED
    # --------------------------------------------------------

    with status_placeholder.container():

        st.success("Research completed successfully")

    with activity_placeholder.container():

        show_agent_activity(
            completed_agents=completed
        )


    # ========================================================
    # RESULTS
    # ========================================================

    st.html("""
    <div class="section-title">Final Research Report</div>
    """)

    st.markdown(final_report)


    # ========================================================
    # METRICS
    # ========================================================

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "AI Agents",
            "5"
        )

    with col2:
        st.metric(
            "Web Sources",
            "6"
        )

    with col3:
        st.metric(
            "Research Status",
            "Completed"
        )


    # ========================================================
    # PDF
    # ========================================================

    pdf_file = create_pdf(final_report)

    st.download_button(
        label="📄 Download Research Report as PDF",
        data=pdf_file,
        file_name="research_report.pdf",
        mime="application/pdf",
        use_container_width=True
    )


# ============================================================
# FOOTER
# ============================================================

st.html("""
<div class="footer">
    ResearchAI • Multi-Agent Research Assistant
</div>
""")
