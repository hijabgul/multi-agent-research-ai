import re
from io import BytesIO

import streamlit as st
from ddgs import DDGS
from crewai import Crew, Task
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
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
}

.hero-title {
    font-size: 48px;
    font-weight: 800;
    color: #ffffff;
    margin-top: 5px;
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

    <div class="hero-title">
        Research Intelligently.
    </div>

    <div class="hero-subtitle">
        Ask a research question and let a team of specialized AI agents
        plan, search, analyze, verify, and write a detailed research report.
    </div>
</div>
""")


# ============================================================
# WEB SEARCH
# ============================================================

def search_web(query, max_results=5):

    query = query.strip()

    if not query:
        return "No search query was provided."

    try:

        results = DDGS().text(
            query,
            max_results=max_results
        )

        if not results:
            return f"No results found for: {query}"

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
{summary[:600]}
""".strip()
            )

        return "\n\n".join(output)

    except Exception as e:

        return f"Search failed for '{query}': {str(e)}"


# ============================================================
# MULTIPLE SEARCHES
# ============================================================

def conduct_research(question, plan):

    searches = [
        question,
        question + " research study evidence",
        question + " benefits advantages",
        question + " challenges limitations risks",
        question + " statistics recent studies",
        question + " academic research 2023 2024 2025"
    ]

    all_results = []

    for query in searches:

        result = search_web(
            query,
            max_results=5
        )

        all_results.append(
            f"""
SEARCH QUERY:
{query}

{result}
"""
        )

    return "\n\n".join(all_results)


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


def show_agent_activity(
    current_agent=None,
    completed_agents=None
):

    if completed_agents is None:
        completed_agents = []

    st.html("""
    <div class="section-title">
        Agent Activity
    </div>
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
            <div class="agent-card">
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
# RUN AGENT
# ============================================================

def run_single_agent(agent, task_description):

    task = Task(
        description=task_description,
        expected_output=(
            "Produce detailed but focused research content. "
            "Use only the supplied evidence. "
            "Do not invent facts or sources."
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
# PDF
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

    story = []

    story.append(
        Paragraph(
            "ResearchAI Research Report",
            title_style
        )
    )

    story.append(Spacer(1, 20))

    for line in report_text.split("\n"):

        line = line.strip()

        if not line:
            story.append(Spacer(1, 6))
            continue

        clean_line = re.sub(
            r"[#*_`]",
            "",
            line
        )

        if clean_line.startswith(
            (
                "Introduction",
                "Key Findings",
                "Analysis",
                "Verified Evidence",
                "Discussion",
                "Limitations",
                "Conclusion",
                "Sources"
            )
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
<div class="section-title">
    Research Question
</div>
""")

question = st.text_area(
    "Research Question",
    placeholder=(
        "Example: What are the benefits, challenges, "
        "and ethical concerns of artificial intelligence in education?"
    ),
    height=130,
    label_visibility="collapsed"
)

analyze = st.button(
    "🔎 Analyze Research Question",
    use_container_width=True
)


# ============================================================
# MAIN
# ============================================================

if analyze:

    if not question.strip():

        st.warning(
            "Please enter a research question first."
        )

        st.stop()

    completed = []

    status_placeholder = st.empty()
    activity_placeholder = st.empty()

    with activity_placeholder.container():

        show_agent_activity()


    # ========================================================
    # 1. PLANNER
    # ========================================================

    try:

        with status_placeholder.container():
            st.info("Research question received")

        with activity_placeholder.container():

            show_agent_activity(
                current_agent="Research Planner",
                completed_agents=completed
            )

        planner = create_planner()

        plan_prompt = f"""
Research Question:

{question}

Create a detailed research plan.

Identify the major areas that should be investigated.

The plan should include:

1. Definition and background
2. Major applications or uses
3. Benefits
4. Challenges and limitations
5. Risks or ethical concerns
6. Evidence and statistics that should be verified
7. Recent research
8. Important opposing or alternative perspectives
9. Questions that require fact checking

Keep the plan organized and practical.
"""

        plan = run_single_agent(
            planner,
            plan_prompt
        )

        completed.append(
            "Research Planner"
        )

    except Exception as e:

        st.error(
            f"Research Planner failed: {str(e)}"
        )

        st.stop()


    # ========================================================
    # 2. WEB RESEARCH
    # ========================================================

    try:

        with status_placeholder.container():
            st.info(
                "Searching current web sources"
            )

        with activity_placeholder.container():

            show_agent_activity(
                current_agent="Web Researcher",
                completed_agents=completed
            )

        web_results = conduct_research(
            question,
            plan
        )

        researcher = create_researcher()

        research_prompt = f"""
Research Question:

{question}

Research Plan:

{plan[:5000]}

WEB SEARCH RESULTS:

{web_results[:14000]}

You are now responsible for producing a substantial research evidence summary.

Analyze the web search results carefully.

Cover:

1. Background
2. Definitions
3. Major applications
4. Benefits
5. Challenges
6. Risks
7. Ethical considerations
8. Statistics or quantitative evidence
9. Recent research
10. Different perspectives
11. Important findings
12. Source URLs

For every important claim, use the supplied sources.

Do not invent facts.

If evidence is missing, explicitly say that the evidence is limited.

Produce a detailed evidence summary, not a short paragraph.
"""

        research_findings = run_single_agent(
            researcher,
            research_prompt
        )

        completed.append(
            "Web Researcher"
        )

    except Exception as e:

        st.error(
            f"Web Researcher failed: {str(e)}"
        )

        st.stop()


    # ========================================================
    # 3. ANALYST
    # ========================================================

    try:

        with status_placeholder.container():
            st.info(
                "Extracting and analyzing evidence"
            )

        with activity_placeholder.container():

            show_agent_activity(
                current_agent="Source Analyst",
                completed_agents=completed
            )

        analyst = create_analyst()

        analysis_prompt = f"""
Research Question:

{question}

Research Plan:

{plan[:3500]}

WEB RESEARCH FINDINGS:

{research_findings[:10000]}

Analyze the evidence in depth.

Identify:

1. Strongly supported findings
2. Findings supported by multiple sources
3. Claims supported by only one source
4. Conflicting information
5. Important statistics
6. Benefits supported by evidence
7. Challenges supported by evidence
8. Risks and ethical concerns
9. Research gaps
10. Claims requiring additional verification
11. Important source URLs

Separate established evidence from claims that remain uncertain.

Do not invent information.

Produce a detailed analytical summary.
"""

        analysis = run_single_agent(
            analyst,
            analysis_prompt
        )

        completed.append(
            "Source Analyst"
        )

    except Exception as e:

        st.error(
            f"Source Analyst failed: {str(e)}"
        )

        st.stop()


    # ========================================================
    # 4. FACT CHECKER
    # ========================================================

    try:

        with status_placeholder.container():
            st.info(
                "Cross-checking important claims"
            )

        with activity_placeholder.container():

            show_agent_activity(
                current_agent="Fact Checker",
                completed_agents=completed
            )

        independent_sources = conduct_research(
            question,
            plan
        )

        fact_checker = create_fact_checker()

        fact_check_prompt = f"""
Research Question:

{question}

RESEARCH FINDINGS:

{research_findings[:7000]}

SOURCE ANALYSIS:

{analysis[:7000]}

INDEPENDENT WEB SEARCH RESULTS:

{independent_sources[:9000]}

Fact-check the important claims.

For each major claim:

1. State the claim.
2. Determine whether the supplied evidence supports it.
3. Identify supporting sources.
4. Identify contradictions if present.
5. Mention uncertainty where appropriate.
6. Identify statistics that appear supported.
7. Identify claims that should NOT be presented as established facts.

Do not invent information.

Do not perform another web search.

Produce a detailed fact-checking summary.
"""

        fact_check = run_single_agent(
            fact_checker,
            fact_check_prompt
        )

        completed.append(
            "Fact Checker"
        )

    except Exception as e:

        st.error(
            f"Fact Checker failed: {str(e)}"
        )

        st.stop()


    # ========================================================
    # 5. REPORT WRITER
    # ========================================================

    try:

        with status_placeholder.container():
            st.info(
                "AI is analyzing and writing the final report"
            )

        with activity_placeholder.container():

            show_agent_activity(
                current_agent="Research Report Writer",
                completed_agents=completed
            )

        writer = create_report_writer()

        report_prompt = f"""
Write a detailed professional research report about:

{question}

RESEARCH PLAN:

{plan[:3500]}

WEB RESEARCH:

{research_findings[:9000]}

SOURCE ANALYSIS:

{analysis[:8000]}

FACT CHECK:

{fact_check[:8000]}

Write a substantial report.

Use this structure:

# Research Report

## Introduction

Explain the topic, background, and why it matters.

## Background

Provide definitions, context, and development of the topic.

## Major Applications

Explain the important uses and applications.

## Key Benefits

Explain the benefits and support each important claim with evidence.

## Challenges and Limitations

Explain limitations, practical difficulties, and weaknesses.

## Risks and Ethical Considerations

Discuss relevant risks, ethical concerns, bias, privacy, security,
fairness, or other concerns when supported by the evidence.

## Evidence and Research Findings

Include important statistics, studies, findings, and concrete evidence
available in the supplied research.

## Different Perspectives

Present significant differing perspectives when supported by the evidence.

## Research Gaps

Explain what remains uncertain or insufficiently studied.

## Conclusion

Give a balanced summary of the evidence.

## Sources

List the important source titles and URLs used in the research.

IMPORTANT RULES:

- Write a detailed report.
- Do not make the report artificially short.
- Use paragraphs as well as bullet points where appropriate.
- Do not invent statistics.
- Do not invent studies.
- Do not invent URLs.
- Do not claim something is proven when the supplied evidence does not establish it.
- Distinguish evidence from interpretation.
- Use the supplied research rather than adding unsupported information.
- Include specific evidence wherever available.
"""

        final_report = run_single_agent(
            writer,
            report_prompt
        )

        completed.append(
            "Research Report Writer"
        )

    except Exception as e:

        st.error(
            f"Research Report Writer failed: {str(e)}"
        )

        st.stop()


    # ========================================================
    # COMPLETE
    # ========================================================

    with status_placeholder.container():

        st.success(
            "Research completed successfully"
        )

    with activity_placeholder.container():

        show_agent_activity(
            completed_agents=completed
        )


    # ========================================================
    # FINAL REPORT
    # ========================================================

    st.html("""
    <div class="section-title">
        Final Research Report
    </div>
    """)

    st.markdown(
        final_report
    )


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
            "Web Searches",
            "12"
        )

    with col3:

        st.metric(
            "Research Status",
            "Completed"
        )


    # ========================================================
    # PDF
    # ========================================================

    pdf_file = create_pdf(
        final_report
    )

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
