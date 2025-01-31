from langchain_community.chat_models.yandex import ChatYandexGPT
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_core.messages import HumanMessage
import json
import os

from config import *

# Initialize YandexGPT LLM
model_uri = "gpt://b1gm60ickcj6d4fhev3m/yandexgpt"
llm = ChatYandexGPT(api_key=YAGPT_API_KEY, model_uri=model_uri, temperature=0.2)

# Initialize Tavily Search Tool
tavilySearchAPIWrapper = TavilySearchAPIWrapper(tavily_api_key=TAVILY_API_KEY)
tavily_search = TavilySearchResults(api_wrapper=tavilySearchAPIWrapper)


# Step 1: Fetch information using Tavily Search
def search_information(question):
    search_results = tavily_search.run(question)
    return search_results  # Contains retrieved web results


# Step 2: Ask the LLM if the question has answer choices
def check_if_has_answers(question):
    prompt = f"""
    Определи, содержит ли данный вопрос пронумерованный список вариантов ответов.
    Вопрос:
    {question}
    Если нет вариантов, или нет предлагаемых ответов, или нет списка вариантов ответов, ответь "Нет".
    Также, если вопрос очень странный, непонятный или после строки "Вопрос:" ничего нет, то также ответь "Нет".
    Если в вопросе есть варианты ответов (например, "1.", "2.", "3."), ответь "Да".
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    return "Да" in response.content  # Return True if LLM detects answer choices


# Step 3: Generate final response
def generate_answer(question, search_results, query_id):
    # Let the LLM decide if the question has answer choices
    if not check_if_has_answers(question):
        # Return the specified JSON response when no answer choices are detected
        return {
            "id": query_id,
            "answer": None,
            "reasoning": "Не было представлено вариантов ответа",
            "sources": []
        }

    # If the question contains choices, generate an answer normally
    prompt_template = """
    Вопрос:
    {question}

    Найденная информация:
    {search_results}

    Ответь в следующем формате (в одну строку!):
    {{
      "answer": <номер ответа [только число]>,
      "reasoning": "<причина твоего ответа>. (сайт, с которого была взята информация, но не ссылка!!). Ответ составлен с помощью YandexGPT.",
      "sources": ["<ссылка1>", "<ссылка2>", "<ссылка3>"]
    }}

    Важно:
    - Укажи не более 3 (можешь меньше) ссылок в поле "sources".
    - Если ссылок меньше 3, укажи только те, которые наиболее релевантны.
    - Убедись, что ссылки являются корректными и релевантными к вопросу.
    """

    response = llm.invoke([HumanMessage(content=prompt_template.format(
        question=question,
        search_results=search_results
    ))])

    try:
        # Parse the response as JSON
        response_data = json.loads(response.content)

        # Validate the response structure
        if not all(key in response_data for key in ["answer", "reasoning", "sources"]):
            raise ValueError("Response is missing required keys")

        # Add the query ID to the response
        response_data["id"] = query_id

        return response_data
    except json.JSONDecodeError:
        raise ValueError(f"AI model returned invalid JSON: {response.content}")
    except Exception as e:
        raise ValueError(f"Unexpected error while parsing response: {str(e)}")

