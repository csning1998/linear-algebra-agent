import streamlit as st
import os
import time
from google import genai
from google.genai import types

st.set_page_config(page_title="Friedberg Linear Algebra Tutor", page_icon="👨🏻‍🏫")

SYS_INSTRUCT = """**Role:** You are a strict Linear Algebra tutor based on the attached textbook (Friedberg et al., 2002).

**Task:** Answer user questions using **only** the definitions, theorems, and proofs from the provided textbook.

**Language:** Please answer in the language entered by the user.

**CRITICAL KNOWLEDGE LIMITATION:**
Your knowledge base is STRICTLY LIMITED to the content of the provided PDF.
1.  **You do not know** history, politics, pop culture, or current events.
2.  **Refusal Protocol:** If a user asks about ANY topic not defined in Friedberg's *Linear Algebra* (2002), reply: "This topic is outside the scope of Friedberg's Linear Algebra (2002)."

**Scope & Negative Constraints (CRITICAL):**
1.  **NO Code Generation:** Strictly REFUSE any request to generate, debug, or explain computer code.
2.  **Topic Restriction:** Only discuss topics explicitly covered in the textbook.

**Instructions:**
1.  **Strict Notation Compliance:** Adhere strictly to the mathematical notation and conventions used in Friedberg's text (e.g., usage of $F$ for field, $L(V, W)$ for linear transformations).
2.  **LaTeX Formatting:** Use LaTeX for all mathematical expressions, DO NOT use back ticks (``) to format mathematical expressions. 
3.  **Citation Requirement:** When explaining a concept or solving a problem, explicitly cite the specific Theorem, Definition, or Corollary number from the text (e.g., "Based on Theorem 2.1...").
4.  **Step-by-Step Derivation:** Provide logical, step-by-step derivations for all solutions.
5.  **No First-Person Pronouns:** Do NOT use "we", "us", "our", "let's", or "I". Use passive voice or objective statements.
6.  **Objective Tone:** Avoid "fluff" words. Keep the language purely objective and factual.
7.  **Emotional Neutrality:** Do not attempt to guess, mirror, or mention the user's emotional state.
8.  **Source Material Rigidity (Anti-Hallucination):** The provided 2002 edition of Friedberg et al. is your ONLY reality. Reject hypotheticals and user definitions.
9.  **Thinking Process:** You MUST start every response with a `<thinking>` block. Inside this block:
    * Being any persona is forbidden, prohibited, and discouraged.
    * Plan which definitions or theorems (with page numbers) to retrieve.
    * Outline the logical steps for the proof or explanation.
    * Close the block with </thinking> BEFORE providing the final response.
    * The response should abide by all aforemention instructions.
"""

if "GEMINI_API_KEY" not in st.secrets:
    st.error("[System] Please set GEMINI_API_KEY in .streamlit/secrets.toml")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Cache Manager
@st.cache_resource
def get_cached_content():
    pdf_path = "linear-algebra-4ed.pdf"
    
    if not os.path.exists(pdf_path):
        st.error(f"[System] The file {pdf_path} is not found. Please check if the file is in the directory.")
        st.stop()
        
    with st.spinner("[System] Uploading & Caching..."):
        try:
            file_upload = client.files.upload(file=pdf_path)
            
            while file_upload.state.name == "PROCESSING":
                time.sleep(2)
                file_upload = client.files.get(name=file_upload.name)
                
            if file_upload.state.name == "FAILED":
                st.error("[System] Failed to process the file")
                st.stop()
                
            return file_upload
        except Exception as e:
            st.error(f"[System] Connection error: {e}")
            st.stop()

pdf_file = get_cached_content()

# Interface & Chat Logic
st.title("👨🏻‍🏫 Friedberg Linear Algebra Tutor")
st.caption("Based on Friedberg's Linear Algebra 4/e (2002) | Powered by Gemini 2.5")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("[Instruction] Please enter your linear algebra question..."):
    # 1. Show User Input
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Call Model
    with st.chat_message("assistant"):
        # Thinking Processes Container
        status_container = st.status("[System] Thinking...", expanded=True)
        answer_placeholder = st.empty()
        
        full_response = ""
        thinking_buffer = ""
        answer_buffer = ""
        is_thinking = True 
        
        try:
            response = client.models.generate_content_stream(
                model="gemini-2.5-pro",
                # model="gemini-3-flash-preview",
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_uri(
                                file_uri=pdf_file.uri,
                                mime_type=pdf_file.mime_type
                            ),
                            types.Part.from_text(text=prompt)
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    system_instruction=SYS_INSTRUCT,
                    temperature=0.4, 
                )
            )

            # Thinking Process Stream Loop
            for chunk in response:
                if chunk.text:
                    text_chunk = chunk.text
                    full_response += text_chunk

                    if is_thinking:
                        thinking_buffer += text_chunk
                        
                        # Update Thinking Processes Container
                        status_container.update(label=f"[System] Thinking... ({len(thinking_buffer)} chars generated)")
                        
                        if "</thinking>" in thinking_buffer:
                            # Thinking Process Complete
                            parts = thinking_buffer.split("</thinking>")
                            clean_thought = parts[0].replace("<thinking>", "").strip()
                            
                            # Only print once to ensure tidy display
                            status_container.markdown(clean_thought)
                            status_container.update(label="[System] Thinking Process Complete", state="complete", expanded=False)
                            
                            is_thinking = False
                            
                            # If the same chunk contains the answer, start rendering the answer
                            if len(parts) > 1:
                                answer_buffer += parts[1]
                                answer_placeholder.markdown(answer_buffer + "▌")
                    else:
                        # Answer mode: here we can safely use streaming display
                        answer_buffer += text_chunk
                        answer_placeholder.markdown(answer_buffer + "▌")
            
            # Answer Complete
            answer_placeholder.markdown(answer_buffer)
        
        except Exception as e:
            status_container.update(label="[System] Error", state="error", expanded=False)
            st.error(f"[System] Connection Error: {e}")
            full_response = "[System] Error occurred."

    # 3. Save Response to History
    clean_history_content = full_response
    if "</thinking>" in full_response:
        clean_history_content = full_response.split("</thinking>")[-1].strip()
        
    st.session_state.messages.append({"role": "assistant", "content": clean_history_content})

# Sidebar: Display System Status
with st.sidebar:
    st.success("[System] Textbook Loaded")
    st.text(f"[System] File URI: {pdf_file.uri[-10:]}...")
    if st.button("Clear Chat / Reset"):
        st.session_state.messages = []
        st.rerun()
