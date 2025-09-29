import re

# Skill synonyms mapping for normalization
SKILL_SYNONYMS = {
    # Programming Languages
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "py": "Python",
    "python3": "Python",
    "java": "Java",
    "c#": "C#",
    "csharp": "C#",
    "c++": "C++",
    "cpp": "C++",
    "go": "Go",
    "golang": "Go",
    "rb": "Ruby",
    "ruby": "Ruby",
    "php": "PHP",
    "swift": "Swift",
    "kotlin": "Kotlin",
    "scala": "Scala",
    "perl": "Perl",
    "rust": "Rust",
    "r": "R",
    "matlab": "MATLAB",

    # Cloud Platforms
    "aws": "Amazon Web Services",
    "amazon web services": "Amazon Web Services",
    "azure": "Microsoft Azure",
    "gcp": "Google Cloud Platform",
    "google cloud": "Google Cloud Platform",
    "oci": "Oracle Cloud Infrastructure",

    # Containers and Orchestration
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "docker": "Docker",
    "containerization": "Docker",

    # Databases
    "sql": "SQL",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "oracle": "Oracle",
    "sqlite": "SQLite",
    "cassandra": "Cassandra",
    "dynamodb": "DynamoDB",
    "hdfs": "Hadoop Distributed File System",
    "hive": "Hive",
    "elasticsearch": "Elasticsearch",

    # Big Data / Data Engineering
    "spark": "Apache Spark",
    "hadoop": "Hadoop",
    "flink": "Apache Flink",
    "kafka": "Apache Kafka",
    "airflow": "Apache Airflow",

    # DevOps / CI-CD
    "ci/cd": "Continuous Integration / Continuous Deployment",
    "ci": "Continuous Integration",
    "cd": "Continuous Deployment",
    "jenkins": "Jenkins",
    "circleci": "CircleCI",
    "travis": "Travis CI",
    "gitlab ci": "GitLab CI",
    "github actions": "GitHub Actions",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "puppet": "Puppet",
    "chef": "Chef",

    # Web / Frontend Frameworks
    "react": "React",
    "reactjs": "React",
    "angular": "Angular",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "ember": "Ember.js",
    "jquery": "jQuery",
    "bootstrap": "Bootstrap",

    # Backend Frameworks
    "node": "Node.js",
    "node.js": "Node.js",
    "express": "Express.js",
    "django": "Django",
    "flask": "Flask",
    "spring": "Spring Boot",
    "laravel": "Laravel",
    "rails": "Ruby on Rails",

    # Data Science / ML / AI
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "nlp": "Natural Language Processing",
    "natural language processing": "Natural Language Processing",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "scikit-learn": "Scikit-Learn",
    "keras": "Keras",
    "opencv": "OpenCV",

    # BI / Visualization
    "tableau": "Tableau",
    "power bi": "Power BI",
    "qlik": "Qlik",
    "lookml": "LookML",
    "d3": "D3.js",
    "matplotlib": "Matplotlib",
    "seaborn": "Seaborn",

    # Agile / Methodologies
    "scrum": "Agile Scrum",
    "kanban": "Agile Kanban",
    "agile": "Agile",
    "waterfall": "Waterfall",

    # APIs / Protocols
    "rest api": "REST API",
    "restful": "REST API",
    "graphql": "GraphQL",
    "soap": "SOAP",

    # Miscellaneous Tools & Concepts
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "jira": "Jira",
    "confluence": "Confluence",
    "docker-compose": "Docker Compose",
    "microservices": "Microservices",
    "oauth": "OAuth",
    "jwt": "JWT",
    "mvc": "MVC",
    "oop": "Object-Oriented Programming",
    "functional programming": "Functional Programming",

    # Mobile Development
    "ios": "iOS",
    "android": "Android",
    "flutter": "Flutter",
    "react native": "React Native",
    "xamarin": "Xamarin",

    # Testing
    "jest": "Jest",
    "mocha": "Mocha",
    "selenium": "Selenium",
    "cypress": "Cypress",
    "junit": "JUnit",

    # Security
    "ssl": "SSL",
    "tls": "TLS",
    "penetration testing": "Penetration Testing",
    "vulnerability assessment": "Vulnerability Assessment",
}

# Normalize skill name to its canonical form using SKILL_SYNONYMS mapping
def normalize_skill(skill: str) -> str:
    skill_clean = skill.strip().lower()  # Clean and lowercase input
    return SKILL_SYNONYMS.get(skill_clean, skill.title())  # Return normalized or title-cased input

# Clean raw text by removing unwanted characters and formatting
def clean_text(text: str) -> str:
    # Remove any HTML tags
    text = re.sub(r'<[^>]*?>', '', text)
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    # Remove non-alphanumeric characters (but keep spaces)
    text = re.sub(r'[^a-zA-Z0-9 ]+', '', text)
    # Normalize multiple spaces to a single space
    text = re.sub(r'\s+', ' ', text)
    # Trim whitespace from both ends
    return text.strip()