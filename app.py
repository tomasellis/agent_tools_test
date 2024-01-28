#!/usr/bin/env python
import requests
import uvicorn

from typing import List, Tuple, Union, Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langserve import add_routes
from langchain.tools import BaseTool, StructuredTool, tool
from langchain.schema.output_parser import StrOutputParser

from langchain.schema.runnable import RunnableLambda, RunnableParallel
from langserve.schema import CustomUserType
from langchain.chains import LLMChain
from fastapi.responses import RedirectResponse

#ENV
import os

WEATHER_API_KEY = os.environ['WEATHER_API_KEY']

loader = WebBaseLoader(["https://tomasellis.dev/about", "https://tomasellis.dev/projects"])
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(docs)
embeddings = OpenAIEmbeddings()
vector = FAISS.from_documents(documents, embeddings)
retriever = vector.as_retriever()

retriever_tool = create_retriever_tool(
    retriever,
    "tomas_info",
    "Search for information about Tomas. For any questions about Tomas, you must use this tool!",
)

@tool
def weather(city: str) -> any:
    """Get weather for a city"""
    
    try:
        url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city}&days=1&aqi=no&alerts=no"
        response = requests.post(url)
        data = response.json()

        return f"""{data["location"]["name"]} in {data["location"]["country"]}
        currently has a temperature of {data["current"]["temp_c"]} Celcius or {data["current"]["temp_f"]} Fahrenheit,
        with a max of {data["forecast"]["forecastday"][0]["day"]["maxtemp_c"]} C° / {data["forecast"]["forecastday"][0]["day"]["maxtemp_f"]}
        F° and min of {data["forecast"]["forecastday"][0]["day"]["mintemp_c"]} C° / {data["forecast"]["forecastday"][0]["day"]["mintemp_f"]} F°.
        It feels like {data["current"]["feelslike_c"]} Celcius or {data["current"]["feelslike_f"]} Fahrenheit.
        It is {data["current"]["condition"]["text"]} outside. Wind is moving at {data["current"]["wind_mph"]} Mph or {data["current"]["wind_kph"]} Km/h.
        """
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error in Weather, code: {err.response.status_code}. Error: {err.response.text}")
        return(err.response.text)
    except Exception as e:
        print(f"Unexpected error in WEATHER with {city} param: {str(e)}")
        return f"Unexpected error in WEATHER with {city} param: {str(e)}"
@tool
def sum(int1: int, int2:int) -> int:
    """Sums two numbers and returns a number"""
    return int1 + int2


@tool
async def draw(image_desc: str) -> any:
    """Draws an image from a prompt and returns the image url"""

    try:
        from langchain.prompts import PromptTemplate
        from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
        from langchain_openai import OpenAI
        
        llm = OpenAI(temperature=0.9)
        prompt = PromptTemplate(
            input_variables=["image_desc"],
            template="Generate a simple prompt of less than 1000 characters to generate an image based on the following description: {image_desc}, cartoon, joyful, sky, high quality, focused on sky",
        )

        chain = LLMChain(llm=llm, prompt=prompt)
        image_url = DallEAPIWrapper().run(chain.run(image_desc))
        return f"Here's the image url: {image_url} pass it fully to the user, don't cut it, leave the query params intact. Just pass the whole thing forward."
    
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error in DRAW, code: {err.response.status_code}. Error: {err.response.text}")
        return(err.response.text)
    except Exception as e:
        print(f"Unexpected error in DRAW with {image_desc} param: {str(e)}")
        return f"Unexpected error in DRAW with {image_desc} param: {str(e)}"
    
tools = [retriever_tool, weather, sum, draw]

#Proper agent
prompt = hub.pull("hwchase17/openai-functions-agent")
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

app = FastAPI(
  title="Agent Testing",
  version="1.0",
  description="A simple API server using LangChain's Runnable interfaces for testing OpenAI Agents",
)

class ChatHistory(CustomUserType):
    chat_history: List[Union[HumanMessage, AIMessage]] = Field(
        ...,
        examples=[[("human input", "ai response")]],
        extra={"widget": {"type": "chat", "input": "question", "output": "answer"}},
    )
    question: str


def _format_to_messages(input: ChatHistory) -> List[BaseMessage]:
    """Format the input to a list of messages."""
    history = input.chat_history
    user_input = input.question
    messages = history
    print("history", history)
    print("question", user_input)
    #messages.append(HumanMessage(content=user_input))
    return {"chat_history":messages, "input": user_input}

def parse_actions(agent_actions: any):
    return {"answer": AIMessage(content=agent_actions["output"])}

class Response(BaseModel):
    output: AIMessage

chat_model = (RunnableLambda(_format_to_messages) | agent_executor | RunnableLambda(parse_actions))

add_routes(
    app,
    chat_model.with_types(input_type=ChatHistory, output_type=Response),
    config_keys=["configurable"],
    path="/agent"
)

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return f"""
    <html>
        <head>
            <title>Agent Testing</title>
        </head>
        <body>
            <a href="{str(request.url)}agent/playground">Go here for testing!</a>
        </body>
    </html>
    """

@app.get("/agent", response_class=HTMLResponse)
def root(request: Request):
    return f"""
    <html>
        <head>
            <title>Agent Testing</title>
        </head>
        <body>
            <a href="{str(request.url)}/playground">Go here for testing!</a>
        </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)