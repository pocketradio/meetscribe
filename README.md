# Meetscribe

Meetscribe is an agent-driven meeting transcript processing system that generates summaries, extracts action items, and drafts follow-up emails with human decision control and resumable execution.

## Setup

### 1. Clone the repository

```
git clone <repo-url>
cd meetscribe
```

### 2. Install dependencies

```
uv sync
```

### 3. Configure AWS credentials

```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=your_region
```

### 4. Run the application

```
streamlit run streamlit_app.py
```

### Alternative Model Configuration ( without aws bedrock )

If you do not have access to AWS Bedrock, modify the model initialization inside `crew.py` to use another model provider.
