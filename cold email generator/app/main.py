import streamlit as st
import urllib.parse
import asyncio
import os
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from streamlit.components.v1 import html

from chains import Chain
from portfolio import Portfolio
from utils import clean_text as text_cleaner

# Disable tokenizer parallelism to prevent warnings in LLM environments
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# --- Playwright Helpers ---

# Asynchronously fetch page HTML using Playwright (for JS-heavy pages)
async def fetch_html_async(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=120000, wait_until="domcontentloaded")
            await asyncio.sleep(3)  # Wait for JS to settle
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(5)  # Wait for content to hydrate
            content = await page.inner_text('body')
        finally:
            await browser.close()
        return content

# Synchronous wrapper around the async Playwright function
def fetch_html_sync(url):
    return asyncio.run(fetch_html_async(url))

# --- Retry for LLM Calls ---

# Try calling LLM to extract job info with basic retry logic
def try_extract_jobs(llm, text, retries=2):
    for attempt in range(retries):
        try:
            jobs = llm.extract_jobs(text)
            if jobs:
                return jobs
        except Exception as e:
            print(f"⚠️ LLM parsing failed on attempt {attempt+1}: {e}")
    return []

# --- HTML Parsing Helpers ---

# Extract job-relevant sections (Qualifications/Responsibilities)
def extract_relevant_sections(soup):
    sections = soup.find_all("section") + soup.find_all("div")
    candidates = []
    for section in sections:
        if section and section.get_text():
            if re.search(r"(Qualifications|Requirements|Experience|Responsibilities)", section.get_text(), re.IGNORECASE):
                candidates.append(section.get_text(separator="\n"))
    return "\n".join(candidates)

# Try to extract number of years of experience mentioned
def extract_experience_years(text):
    patterns = [
        r"(\d+)\+?\s*(?:years?|yrs?)\s+of\s+[\w\s]+experience"
        r"(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:.*?\s)?experience",
        r"minimum\s+of\s+(\d+)\+?\s*(?:years?|yrs?)",
        r"(?:typically|around|approximately)?\s*(\d+)\+?\s*(?:years?|yrs?)\b",
        r"experience.*?(\d+)\+?\s*(?:years?|yrs?)",
        r"(\d+)\+?\s*(?:years?|yrs?)\s+technical",
        r"(\d+)\+?\s*(?:years?|yrs?)\s+in\s+.*",
    ]
    found_years = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        found_years.extend([int(m) for m in matches if m.isdigit()])
    return f"{max(found_years)} years" if found_years else "Not specified"

# Summarize job description using LLM with retries
def summarize_job_description(llm, text, max_retries=2):
    for attempt in range(max_retries):
        try:
            return llm.summarize(text)
        except Exception as e:
            print(f"⚠️ Summarization failed (attempt {attempt+1}): {e}")
    return "Summary not available due to an error."

# --- Main Streamlit App UI ---

def create_streamlit_app(llm, user_portfolio, clean_fn):
    st.set_page_config(layout="wide", page_title="AI Business Outreach", page_icon="📧")
    st.title("📧 AI Business Outreach")

    # --- URL Input Section ---
    url_input = st.text_input("Enter a URL:", value="")

    if url_input:
        st.session_state["last_url"] = url_input
        if st.button("Submit"):
            st.session_state["submit_triggered"] = True

        # Proceed if submit clicked and URL retained in session
        if st.session_state.get("submit_triggered") and st.session_state.get("last_url"):
            url_input = st.session_state["last_url"]
        try:
            raw_html = fetch_html_sync(url_input)
            soup = BeautifulSoup(raw_html, "html.parser")
            full_text = "\n".join(soup.stripped_strings)
            cleaned_text = clean_fn(full_text)

            # Try to extract relevant section and years of experience
            relevant_sections = extract_relevant_sections(soup)
            experience = extract_experience_years(relevant_sections or full_text)

            user_portfolio.load_portfolio()  # Load portfolio if not loaded yet

            jobs = try_extract_jobs(llm, cleaned_text)
            if not jobs:
                st.warning("⚠️ Could not extract job info. Please try again.")
                return

            # Iterate through each detected job
            for job in jobs:
                role = job.get("role", "Unknown Role")
                skills = job.get("skills", [])

                job["url"] = url_input
                job["experience"] = experience

                # Display job header info
                st.markdown(f"**🔎 Job Title:** <span style='color:green'>{role}</span>", unsafe_allow_html=True)
                st.markdown(f"**🧠 Experience Required:** {experience}")
                st.markdown(f"**🛠️ Expected Skills:** {skills}")

                # Show summarized description
                with st.spinner("Summarizing job description..."):
                    summary = summarize_job_description(llm, cleaned_text)
                    st.markdown(f"📝 Job Summary: \n{summary}")

                if not skills:
                    st.warning(f"⚠️ No skills found for job: {role}. Portfolio links may be missing.")

                job_key = f"{role}_{url_input}"

                # Tone selection
                tone = st.selectbox(
                    "✏️ Choose Email Tone:",
                    ["Formal", "Friendly", "Concise", "Technical"],
                    key=f"tone_{job_key}"
                )

                # Query portfolio for matching examples
                raw_links = user_portfolio.query_links(skills)
                links = [link["links"] for link in raw_links if "links" in link]

                if not links:
                    st.warning(f"⚠️ No strong match, but including job '{role}' due to partial skill overlap.")

                # Email generation keying and regeneration logic
                regen_key = f"regen_triggered_{job_key}"
                stored_tone_key = f"stored_tone_{job_key}"
                email_key = f"email_{job_key}"

                previous_tone = st.session_state.get(stored_tone_key)
                tone_changed = previous_tone != tone

                if st.button("✨ Regenerate", key=f"regen_button_{job_key}"):
                    st.session_state[regen_key] = True

                if tone_changed or st.session_state.get(regen_key) or email_key not in st.session_state:
                    st.session_state[email_key] = llm.write_mail(job, links, url_input, tone=tone)
                    st.session_state[stored_tone_key] = tone
                    st.session_state[regen_key] = False

                email = st.session_state[email_key]

                # Extract subject and email body
                subject_line_match = re.search(r"(?i)^subject\s*:\s*(.*)", email)
                if subject_line_match:
                    subject = subject_line_match.group(1).strip()
                    email_body = re.sub(r"(?i)^subject\s*:.*\n?", "", email, count=1).strip()
                else:
                    subject = f"Business Opportunity - {role}"
                    email_body = email.strip()

                # Display the final generated email
                st.markdown(f"#### ✉️ Generated Email for {role}")
                st.markdown(email.replace("\n", "  \n"))

                # --- Email Sharing Buttons (Gmail, Outlook, Copy) ---
                def generate_mail_links(subject, body):
                    encoded_subject = urllib.parse.quote(subject)
                    encoded_body = urllib.parse.quote(body)
                    gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&to=&su={encoded_subject}&body={encoded_body}&tf=1"
                    outlook_url = f"https://outlook.office.com/mail/deeplink/compose?subject={encoded_subject}&body={encoded_body}"
                    return gmail_url, outlook_url

                gmail_link, outlook_link = generate_mail_links(subject, email_body)

                # Email sharing buttons with hosted icons
                gmail_icon_url = "https://img.icons8.com/?size=100&id=P7UIlhbpWzZm&format=png&color=000000"
                copy_icon_url = "https://img.icons8.com/material-outlined/24/copy.png"
                outlook_icon_url = "https://img.icons8.com/color/48/microsoft-outlook-2019.png"

                html(f"""
                <div style="text-align: center; margin-top: 24px; font-family: Arial, Helvetica, sans-serif;">
                    <span style="display: inline-block; margin: 0 18px;">
                        <a href="{gmail_link}" target="_blank" style="text-decoration: none;">
                            <img src="{gmail_icon_url}" width="20" style="vertical-align: middle; margin-right: 6px;" />
                            <span style="vertical-align: middle; color: white; font-weight: 600;">Open in Gmail</span>
                        </a>
                    </span>

                    <span style="display: inline-block; margin: 0 18px;">
                        <button onclick="copyEmail()" style="
                            padding: 6px 12px;
                            font-size: 15px;
                            border-radius: 6px;
                            background-color: #444;
                            color: white;
                            border: none;
                            cursor: pointer;
                            font-family: Arial, Helvetica, sans-serif;
                            font-weight: 600;">
                            <img src="{copy_icon_url}" width="16" style="vertical-align: middle; margin-right: 6px;" />
                            Copy Email
                        </button>
                        <textarea id="emailBody" style="position: absolute; left: -9999px;">{email_body}</textarea>
                    </span>

                    <span style="display: inline-block; margin: 0 18px;">
                        <a href="{outlook_link}" target="_blank" style="text-decoration: none;">
                            <img src="{outlook_icon_url}" width="20" style="vertical-align: middle; margin-right: 6px;" />
                            <span style="vertical-align: middle; color: white; font-weight: 600;">Open in Outlook</span>
                        </a>
                    </span>
                </div>

                <script>
                function copyEmail() {{
                    var textarea = document.getElementById("emailBody");
                    textarea.select();
                    document.execCommand("copy");
                    alert("📋 Email copied to clipboard!");
                }}
                </script>
                """, height=150)

        except Exception as e:
            st.error(f"An error occurred: {e}")

# --- App Entry Point ---
if __name__ == "__main__":
    chain = Chain(prompt_mode="robust")  # Robust prompt includes skill/role enforcement
    portfolio = Portfolio()              # Portfolio with tech-link mappings
    create_streamlit_app(chain, portfolio, text_cleaner)