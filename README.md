# Linear Algebra Tutor Agent (Friedberg Edition)

An LLM-based tutor agent specialized in Friedberg, S. H., Insel, A. J., & Spence, L. E. (2002). Linear algebra (4th ed.). Pearson.

This agent is powered by **Google Gemini 2.5 Pro**.

## Features

-   **Strict Source Adherence:** Answers are grounded strictly in the provided textbook definitions and theorems.
-   **Thinking Process Display:** Shows the agent's internal reasoning, search strategy, and theorem retrieval process before answering.
-   **Hallucination Defense:** Rejects out-of-scope topics (e.g., politics, history) and hypothetical definitions not found in the text.
-   **LaTeX Support:** Renders complex mathematical notation beautifully.

## Tech Stack

-   **Frontend/Backend:** Streamlit
-   **Model:** Google Gemini 2.5 Pro
-   **Orchestration:** Python with Google GenAI SDK

## How to Run Locally

1.  Clone the repository.

2.  Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3.  Replace the API Key placeholder in `.streamlit/secrets.toml`:

    ```toml
    GEMINI_API_KEY = "replace-this-by-gemini-api-key"
    ```

4.  Run the app in shell:

    ```bash
    streamlit run app.py
    ```

## Note

This agent uses a specific PDF as its knowledge base. Ensure `linear-algebra-4ed.pdf` is present in the root directory.
