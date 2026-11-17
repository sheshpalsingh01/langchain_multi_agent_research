import os
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.tools.tools import scrape_url, websearch_tool
from dotenv import load_dotenv

load_dotenv()
# LLM

llm = ChatOpenAI(model="gpt-4o-mini", timeout=45, max_retries=0)


# First Agent
def build_search_agent():
    return create_agent(
        model =llm,
        tools=[websearch_tool],
    )
    
# Second agent : reader agent

def reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url],
        system_prompt=(
            "You are a source reader. Select one relevant URL from the supplied "
            "search results and call scrape_url exactly once. Never invent a URL. "
            "If no URL is available, explain that no source could be read."
        ),
    )


# 3rd agent

writer_prompt =ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])


writter_chain = writer_prompt|llm|StrOutputParser()


#critic_chain 

critic_prompt = ChatPromptTemplate.from_messages([
     ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()