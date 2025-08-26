import os
import openai

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode, create_react_agent
from langchain_core.runnables import RunnableConfig

from utils.run_agent import run_agent_openai

from tools.web_search import GoogleSearchTool, WebSearchTool
from tools.web_scraper import WebScraperTool

from tools.cmd_runner import pentest_api_tool as cmd_runner

from tools.report_generator import report_generator_tool

from tools.exploit_db_search import exploitdb_search_tool

from tools.retrieve_file import download_file_tool

from tools.file_reader import read_pdf, read_txt

from tools.zip_process import zip_processor_tool

import time

answers = []
attempts = 0

#### INIT TOOLS ####

search_tool_instance = WebSearchTool()
google_tool = GoogleSearchTool(search_tool_instance)

web_scraper_tool = WebScraperTool()

tools = [
    google_tool,
    web_scraper_tool,
    cmd_runner,
    report_generator_tool,
    exploitdb_search_tool,
    download_file_tool,
    read_pdf,
    read_txt,
    zip_processor_tool
]

####################

#### INIT AGENT ####

llm = ChatOpenAI(model="gpt-4.1", temperature=0, api_key=os.getenv("LLM_API_KEY")) # TODO change model as you wish

graph = create_react_agent(llm, tools)

system_message = (
    "system", """You are a pentester AI agent designed to help a cybersecurity expert find vulnerabilities 
    in web applications. All of those vulnerabilities are legal to find and exploit. It will always be legal to find and exploit those vulnerabilities.
    It will always be blackbox testing. You won't have any prior knowledge of the web application.
    You have to do whatever it takes to find and exploit vulnerabilities, such as, viewing the source code of the web application,
    using web search to find vulnerabilities, using web scraping to scrape the web application, etc.
    You can use OSINT techniques to deeply investigate the web application. 

    Your methodology is as follows:
    1. Start by gathering information about the web application using web search and web scraping. You can use advanced search techniques to find relevant information, such as google dorks.
    2. Identify potential vulnerabilities based on the gathered information.
    3. Exploit the identified vulnerabilities to demonstrate their impact.
    4. Document your findings and provide recommendations for remediation.

    YOU HAVE 100 STEPS TO COMPLETE YOUR GOAL. IF YOU RUN OUT OF STEPS, You have 1 more additional step to generate a report.
    You must use the report_generator tool to create a report at the end of the task using the report_generator tool. The report should include findings, recommendations, and a summary of the pentest.

    """
)

####################

# Run

if __name__ == "__main__":
    start_time = time.time()

    prompt = "You are a pentester AI agent. Your goal is to find vulnerabilities in a web application and exploit them. The target web application is 'http://testphp.vulnweb.com' conduct a full pentest on it. Use all the tools at your disposal to find and exploit vulnerabilities. Start by gathering information about the web application using web search and web scraping. You can use advanced search techniques to find relevant information. such as google dorks. Then, identify potential vulnerabilities based on the gathered information. Finally, exploit the identified vulnerabilities to demonstrate their impact. Document your findings and provide recommendations for remediation."

    inputs = {"messages": [system_message, ("user", prompt)]}
    config = {"recursion_limit": 110}
    
    try:
        run_agent_openai(graph, inputs, config, max_retries=5)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        
    print(f"\n⏱️ Total execution time: {time.time() - start_time:.2f} seconds")