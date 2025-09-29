import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

# Load environment variables from .env file (e.g., GROQ_API_KEY)
load_dotenv()

class Chain:
    def __init__(self, prompt_mode="default"):
        # Set prompt mode: 'default' or 'robust'
        self.prompt_mode = prompt_mode
        # Initialize LLM (Groq with LLaMA 3.1 model)
        self.llm = ChatGroq(temperature=0.8, model="llama-3.1-8b-instant")
        self.chat_model = self.llm  # Used for summarization as well

    def extract_jobs(self, cleaned_text):
        # Use robust or default prompt based on mode
        if self.prompt_mode == "robust":
            prompt_text = """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from a job posting page. Extract only one job and return it in this exact JSON format:

            {{
              "role": "...",
              "experience": "...",
              "skills": ["...", "..."],
              "description": "Summarize the job responsibilities in 4–6 sentences, covering the core responsibilities, the purpose of the role, and the team or product this role supports."
            }}

            - Always extract a `role`, even if it needs to be inferred.
            - `skills` must include technical tools, languages, or platforms, especially those mentioned in Qualifications or Responsibilities.
            - If a field is missing, leave it as an empty string or empty list, but DO NOT omit the key.
            Output clean, **valid JSON** only.
            """
        else:
            prompt_text = """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from a job posting page. Extract only the job that is clearly described on this page.
            Your job is to extract the job posting and return it in JSON format containing the following keys: `role`, `experience`, `skills`, and `description`.
            Extract a JSON array of distinct skill names and tools mentioned in the job description.  
            Ignore full sentences or descriptions. Only output skill/tool names as strings.
            Only return the valid JSON.
            Do not assume multiple jobs exist.
            ### VALID JSON (NO PREAMBLE):
            """

        # Create prompt and pass it to the LLM chain
        prompt_extract = PromptTemplate.from_template(prompt_text)
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})

        try:
            # Attempt to parse JSON output
            json_parser = JsonOutputParser()
            parsed = json_parser.parse(res.content)
            return parsed if isinstance(parsed, list) else [parsed]
        except Exception as e:
            # Handle JSON parsing failures gracefully
            st.warning(f"⚠️ Skipping a chunk due to parsing error: {e}")
            print("⚠️ Parsing failed due to size or formatting.")
            raise OutputParserException("Context too big. Unable to parse jobs.")

    def summarize(self, text, max_words=60):
        # Create summarization prompt (e.g., for job preview)
        prompt_template = ChatPromptTemplate.from_template(
            """
            ### CONTEXT:
            {text}

            ### INSTRUCTION:
            Summarize the job description above in under {max_words} words.
            Focus on the core responsibilities and the overall goal of the role.
            Output only the summary. Do not prefix it with 'Summary:' or any other label.
            """
        )
        # Run summarization chain
        chain_summary = prompt_template | self.chat_model
        result = chain_summary.invoke({"text": text.strip(), "max_words": max_words})
        return result.content.strip()

    def write_mail(self, job, links, job_url=None, tone="Formal"):
        # Create the prompt for cold outreach email
        prompt_email = PromptTemplate.from_template(
            """
               ### JOB DESCRIPTION:
               {job_description}
    
               ### JOB LINK:
               {job_url}
    
               ### INSTRUCTION:
               You are Karthik Mohan, a business development executive at Tata Consultancy Services. Tata Consultancy Services (TCS) is an AI & Software Consulting company that helps global enterprises build secure, scalable, and intelligent systems across domains.
    
               Your job is to write a personalized cold email to the client regarding the job mentioned above. Highlight how TCS can support the technical goals of the position through our proven capabilities.
    
               Focus on:
               - How our engineering teams, domain experts, and cross-functional consultants align with the technical demands of the role.
               - Specific types of projects we’ve delivered in areas like cloud platforms, scalable architectures, DevOps, cybersecurity, and AI.
               - Relevant accomplishments that demonstrate the value we bring to similar roles/teams.
    
               Reference **up to 4 most relevant portfolio links** from the list provided in {link_list}. Do not present them as a bullet list — weave them naturally into the explanation.
    
               Include the job link explicitly in the email body.
    
               End the email with this signature, each on a new line:
               Karthik Mohan  
               Business Development Executive  
               Tata Consultancy Services
    
               Avoid generic phrases or long intros. Do not include any job requirements or candidate qualifications.
               Do not add any preamble before the email starts.
    
               ### EMAIL (NO PREAMBLE):
               """
        )
        # Run email generation chain
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({
            "job_description": job.get("description", ""),
            "link_list": links,
            "job_url": job_url or "Not Provided",
            "tone": tone
        })
        return res.content

# Debug/test entry point
if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))  # Print GROQ API Key to confirm environment setup