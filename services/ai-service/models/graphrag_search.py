from pydantic import BaseModel, Field
import asyncio

class GlobalSearchResult(BaseModel):
    query: str = Field(description="The query used to search the LLM model")
    response: str = Field(description="The response from the LLM model")
    reports: str = Field(description="The reports used in the context for the LLM responses")
    llm_calls: int = Field(description="The number of LLM calls")
    prompt_tokens: int = Field(description="The number of LLM tokens used in the prompt")
    
    def display(self):
        print(f"############# QUERY ############# \n {self.query} \n \n")

        print(f"############# RESPONSE ############# \n {self.response} \n \n")

        # inspect the data used to build the context for the LLM responses
        print(f"############# REPORTS USED IN CONTEXT ############# \n {self.reports} \n \n")

        # inspect number of LLM calls and tokens
        print(f"LLM calls: {self.llm_calls}. LLM tokens: {self.prompt_tokens}")

class LocalSearchResult(BaseModel):
    query: str = Field(description="The query used to search the LLM model")
    response: str = Field(description="The response from the LLM model")
    reports: str = Field(description="The reports used in the context for the LLM responses")
    llm_calls: int = Field(description="The number of LLM calls")
    prompt_tokens: int = Field(description="The number of LLM tokens used in the prompt")
    
    def display(self):
        print(f"############# QUERY ############# \n {self.query} \n \n")

        print(f"############# RESPONSE ############# \n {self.response} \n \n")

        # inspect the data used to build the context for the LLM responses
        print(f"############# REPORTS USED IN CONTEXT ############# \n {self.reports} \n \n")

        # inspect number of LLM calls and tokens
        print(f"LLM calls: {self.llm_calls}. LLM tokens: {self.prompt_tokens}")