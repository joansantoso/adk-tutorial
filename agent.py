from google.adk.agents import Agent, LlmAgent
import requests
import arxiv

def get_paper_with_keyword(keyword: str, limit: int) -> dict:
    """
    Retrieves a list of paper name that is contain the keyword based on the title of the paper only.

    Args:
        kerword (str): The keyword for the title's paper that want to be searched.
        limit (int): The limit of the list that want to be queried. The recommendation is 10.

    Returns:
        dict: status and the list of paper or error message.
    """
    try:
        search = arxiv.Search(
                query=f'ti:{keyword}',
                max_results=limit
            )
        
        papers = []

        for result in search.results():
            papers.append(result.title)

        return {"status": "success", "list_of_papers": papers}
    
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"An unexpected error occurred: {e}"
        }

def get_paper_abstract(paper_names: str) -> dict:
    """
    Retrieves the user's desired paper abstract.

    Args:
        paper_names (string): The list from name of the paper to get the abstract of the paper.
    Returns:
        dict: status and list of paper title with abstract or error message.
    """
    try: 
        list_of_papers = paper_names.split(",") 
        paper_list = []
        for paper_name in list_of_papers:
            print(paper_name)
            # Define the search query
            search = arxiv.Search(
                query=f'ti:{paper_name}',
                max_results=1
            )

            
            abstract = ""
            title = ""

            # Execute the search
            for result in search.results():
                title = result.title
                abstract = result.summary
                paper_list.append({"title": title, "abstract": abstract})

        return {"status": "success", "list_of_papers": paper_list}

    except requests.exceptions.RequestException as req_err:
        return {
            "status": "error",
            "error_message": f"Request error: {req_err}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"An unexpected error occurred: {e}"
        }
  
summarize_agent = None

summarize_agent = LlmAgent(
    name="summarize_agent",
    model="gemini-2.0-flash",
    instruction=(
        "You are an academic summarization agent. Your task is to analyze the title and abstract of a research paper "
        "to identify and summarize its key contributions and advantages. Focus on highlighting the novel aspects, "
        "methodologies, and the significance of the research within its field."
    ),
    description=(
        "Summarizes the main contributions and advantages of academic papers based on their title and abstract."
    ),
    tools=[]
)

drawback_analysis_agent = None

drawback_analysis_agent = LlmAgent(
    name="drawback_analysis_agent",
    model="gemini-2.0-flash",
    instruction=(
        "You are an academic research assistant specializing in critical analysis. "
        "Given the title and abstract of a research paper, identify and summarize potential drawbacks, limitations, "
        "or areas for improvement. Focus on aspects such as methodological constraints, assumptions made, scope limitations, "
        "and any acknowledged weaknesses. Provide a concise analysis that highlights these points."
    ),
    description=(
        "Analyzes research papers to identify and summarize potential drawbacks and limitations based on the title and abstract."
    ),
    tools=[]
)


root_agent = Agent(
    name="paper_summarization_and_analysis_agent",
    model="gemini-2.0-flash",
    description=(
        "An agent that searches for academic papers by title keyword and orchestrates summarization for drawback analysis that will be inserted to literature review section in the paper journal."
    ),
    instruction=(
        "When provided with a keyword, search for academic papers with titles containing that keyword using 'get_paper_with_keyword' for most recent papers with 10 as limit. If not, then ask about what we want to find."
        "Foreach paper's titles that are retrieved, get the abstract using 'get_paper_abstract' for each title and store it as dictionary. "
        "Give the analysis of potential drawbacks and limitations to the 'drawback_analysis_agent' for each paper abstract that found. "
        "Then, delegate the summarization of the paper's contributions and advantages to the 'summarize_agent' into several paragraphs. "
        "Finally, compile and present the findings to the user."
    ),
    tools=[get_paper_with_keyword, get_paper_abstract],
    sub_agents=[summarize_agent, drawback_analysis_agent]
)
