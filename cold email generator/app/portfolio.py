import pandas as pd
import chromadb
import uuid

class Portfolio:
    def __init__(self, file_path="app/resource/company_portfolio.csv"):
        # Initialize the Portfolio class with file path and ChromaDB setup
        self.file_path = file_path
        self.data = pd.read_csv(file_path)  # Load portfolio CSV into DataFrame
        self.chroma_client = chromadb.PersistentClient('vectorstore')  # Initialize ChromaDB persistent client
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")  # Get or create collection

    def load_portfolio(self):
        # Load portfolio into vector store if collection is empty
        if not self.collection.count():
            for _, row in self.data.iterrows():
                techstack = str(row["Techstack"])  # Ensure tech stack is string
                link = str(row["Links"])  # Ensure link is string

                # Add document to ChromaDB with metadata
                self.collection.add(
                    documents=[techstack],
                    metadatas=[{"links": link}],  # Metadata must be list of dicts
                    ids=[str(uuid.uuid4())]  # Unique ID for each document
                )

    def query_links(self, skills):
        # Return early if no skills provided
        if not skills:
            print("⚠️ Warning: No skills found for job, skipping portfolio query.")
            return []

        # Normalize incoming skills (e.g., 'Python ' → 'python')
        normalized_skills = set(s.lower().strip() for s in skills)

        matched_links = []

        # Check each row of the portfolio for skill overlap
        for _, row in self.data.iterrows():
            # Normalize skills listed in the portfolio
            portfolio_skills = [s.lower().strip() for s in row["Techstack"].split(",")]

            # If any overlap, include the corresponding link
            if normalized_skills.intersection(portfolio_skills):
                matched_links.append({"links": row["Links"]})

        return matched_links