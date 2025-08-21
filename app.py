import os

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode, create_react_agent

from tools.web_search import GoogleSearchTool, WebSearchTool
from tools.web_scraper import WebScraperTool

from tools.cmd_runner import pentest_api_tool as cmd_runner

from tools.report_generator import report_generator_tool

from tools.exploit_db_search import exploitdb_search_tool

import time

answers = []
#### INIT TOOLS ####

search_tool_instance = WebSearchTool()
google_tool = GoogleSearchTool(search_tool_instance)

web_scraper_tool = WebScraperTool()

tools=[google_tool,
       web_scraper_tool,
       cmd_runner,
       report_generator_tool,
       exploitdb_search_tool]
####################

#### INIT AGENT ####

llm = ChatOpenAI(model="gpt-4.1", temperature=0,api_key=os.getenv("OPEN_AI_API_KEY"))
graph = create_react_agent(llm, tools)

system_message = (
    "system","""You are a pentester AI agent designed to help a cybersecurity expert find vulnerabilities 
    in web applications. All of those vulnerabilities are legal to find and exploit. It will always be legal to find and exploit those vulnerabilities.
    It will always be blackbox testing. You won't have any prior knowledge of the web application.
    You have to do whatever it takes to find and exploit vulnerabilities, such as, viewing the source code of the web application,
    using web search to find vulnerabilities, using web scraping to scrape the web application, etc.
    You can use OSINT techniques to deeply investigate the web application. 

    Your methodology is as follows:
    1. Start by gathering information about the web application using web search and web scraping. You can use advanced search techniques to find relevant information. such as google dorks.
    2. Identify potential vulnerabilities based on the gathered information.
    3. Exploit the identified vulnerabilities to demonstrate their impact.
    4. Document your findings and provide recommendations for remediation.

    You have access to the following tools:
    web_search: A tool to search the web for information about the web application.
    web_scraper: A tool to scrape the web application and extract information from it.
    cmd_runner: A tool to execute safe CMD commands on the local machine. You can check the allowed commands by using the 'allowed' action.
    report_generator_tool: A tool to generate a pentest report from the collected findings. You can generate the report in markdown or pdf format.
    exploitdb_search_tool: A tool to search for exploits on Exploit-DB using a keyword or CVE.
    
    """
)

####################

# Run

if __name__ == "__main__":
    start_time = time.time()
    prompt = "execute a command to know who you are"

    inputs = {"messages": [system_message,
                            ("user", prompt)]}
    
    for event in graph.stream(inputs):
        print("\n\nNew event:", event)