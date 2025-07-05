
    import streamlit as st
    import os
    import urllib.parse
    from typing import Optional

    # Try importing OpenAI; if unavailable, show notice
    try:
        from openai import OpenAI
    except ImportError:
        OpenAI = None

    st.set_page_config(page_title="AI Architect • Sequence Diagram Generator")

    st.title("🛠️ Software Architect AI Agent")
    st.markdown(
        """Enter any **system or feature description** below.  
        The agent will think through the logic and generate **sequence‑diagram.org** code for you.""")

    # Sidebar controls
    backend = st.sidebar.selectbox(
        "LLM backend",
        ["OpenAI Chat (recommended ‑ needs key)", "Heuristic Fallback (dummy)"]
    )

    if backend.startswith("OpenAI"):
        openai_key = st.sidebar.text_input(
            "OpenAI API Key",
            type="password",
            help="Create a free account at https://platform.openai.com — pay‑as‑you‑go; first $5 credit is usually free."
        )
    else:
        openai_key = None

    system_description = st.text_area(
        "📋 System / Feature description",
        height=220,
        placeholder="e.g. Create a user login flow with email + password + OTP verification"
    )

    show_reasoning = st.checkbox("Show agent reasoning (extra API cost)")

    # Helper: call OpenAI
    def call_openai(prompt: str, api_key: str, model: str = "gpt-3.5-turbo") -> str:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()

    # Generate button
    if st.button("🚀 Generate Diagram"):
        if not system_description.strip():
            st.warning("Please enter a system description.")
            st.stop()

        if backend.startswith("OpenAI") and not openai_key:
            st.error("Please supply your OpenAI API key in the sidebar.")
            st.stop()

        reasoning = ""
        diagram_code = ""

        if backend.startswith("OpenAI"):
            # 1️⃣ optionally get reasoning
            if show_reasoning:
                reasoning_prompt = f"""You are a senior software architect.
Provide a concise step‑by‑step reasoning outline for how you'd design the system described below. Limit to ~10 bullet points.

SYSTEM DESCRIPTION:
{system_description}"""
                reasoning = call_openai(reasoning_prompt, openai_key)

            # 2️⃣ get diagram code
            diagram_prompt = f"""You are a senior software architect. Think through the system below and then output ONLY the final sequence diagram code using the textual syntax supported by https://www.sequencediagram.org. Do **not** add any commentary before or after the diagram.

SYSTEM DESCRIPTION:
{system_description}"""
            diagram_code = call_openai(diagram_prompt, openai_key)

        else:
            diagram_code = "Caller->System: TODO\nSystem->Caller: Not implemented"
            reasoning = "(Heuristic fallback selected; no LLM used.)"

        # Display results
        if show_reasoning and reasoning:
            with st.expander("🧠 Agent reasoning"):
                st.markdown(reasoning)

        st.subheader("📄 Sequence Diagram Code")
        st.code(diagram_code, language="text")

        # Convenience download
        st.download_button(
            "Download diagram code",
            diagram_code,
            file_name="sequence_diagram.txt",
            mime="text/plain"
        )

        # Attempt to build quick link (simple URL‑encode; may fail for long diagrams)
        encoded = urllib.parse.quote_plus(diagram_code)
        seq_url = f"https://sequencediagram.org/index.html?initialData={encoded}"
        st.markdown(f"[🔗 Open in SequenceDiagram.org]({seq_url})")
