from typing import List, Dict, Optional
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.output_parsers import OutputFixingParser
from langchain.schema import OutputParserException
import googletrans
import diets
import streamlit as st


# Define your models
class UserInfo(BaseModel):
    health_problems: str = Field(
        description="If included in the message: User's health problems and any information from the message.")
    allergies: str = Field(description="If included in the message: User's allergies.")
    intolerances: str = Field(description="If included in the message: User's food intolerances.")
    exclude: str = Field(description="If included in the message: What to exclude from the diet.")
    add: str = Field(description="If included in the message: What to add from the diet.")
    calories: str = Field(default=2400,
                          description="If included in the message: Any calorie information. Default is 2400.")
    type_of_diet: str = Field(description="If included in the message: Any information about the desired type of diet.")
    meals_number: str = Field(default=3,
                              description="If included in the message: Any information number of meals per day. Default is 3.")
    other_restrictions: str = Field(
        description="If included in the message: Any information about religious, cultural, or ethical dietary restrictions.")


class Indication(BaseModel):
    indeication_index: int = Field(description="Index of similar indications.")
    explanation: str = Field(description="Why you think so?")


class Dish(BaseModel):
    name: str = Field(description="Name of the dish")
    ingredients: List[str] = Field(description="List of ingredients for the dish")
    cooking_instructions: str = Field(description="Cooking instructions for the dish")
    price: float = Field(description="Approximate price of the dish")


class Meal(BaseModel):
    meal_number: int = Field(description="Number of the meal")
    description: str = Field(description="Description of the meal")
    dishes: List[Dish] = Field(description="List of dishes for the meal")
    total_price: float = Field(description="Total approximate price of the meal")


class DailyMenu(BaseModel):
    meals: List[Meal] = Field(description="List of meals for the day")
    meals_number: Optional[int] = Field(description="Number of meals for the day")
    total_price: float = Field(description="Total approximate price of all meals for the day")
    currency: str = Field(description="Local currency")


class DailyMenuList(BaseModel):
    menus: List[DailyMenu] = Field(description="List of daily menu options")


# Define your functions
def get_model(api_key, model) -> ChatOpenAI:
    return ChatOpenAI(openai_api_key=api_key, model=model, temperature=0)


def get_user_info(user_message: str, model: ChatOpenAI) -> UserInfo:
    query = (
        f"Extract information about the user's health problems, his allergies, intolerances, "
        f"wishes what exclude, wishes what add, calorie information, type of diet and other_restrictions from the message: {user_message}."
    )
    parser = JsonOutputParser(pydantic_object=UserInfo)
    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | model
    output = chain.invoke({"query": query})
    try:
        parsed_output = parser.parse(output.content)
    except OutputParserException as e:
        fix_parser = OutputFixingParser.from_llm(parser=parser, llm=model)
        parsed_output = fix_parser.parse(output.content)
    return parsed_output


def get_indication_info(user_info: UserInfo, indications_list: List[tuple], model: ChatOpenAI) -> Indication:
    query = (
        f"'List of medical indications': {indications_list}. "
        f"Please write the index of the medical indication that corresponds to the information about the health of the user: '{user_info['health_problems']}'. "
        "If user_info contains rubbish not related to medicine or you did not find an exact match in the 'List of medical indications', then indicate the index 99."
    )
    parser = JsonOutputParser(pydantic_object=Indication)
    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | model
    output = chain.invoke({"query": query})
    try:
        parsed_output = parser.parse(output.content)
    except OutputParserException as e:
        fix_parser = OutputFixingParser.from_llm(parser=parser, llm=model)
        parsed_output = fix_parser.parse(output.content)
    return parsed_output


def get_diet_options(temp: Dict, user_info: UserInfo, model: ChatOpenAI) -> DailyMenuList:
    query = (
        f"{temp} \n"
        "You are a dietary cook, your work is very important, so do it responsibly and carefully, "
        "do not invent non-existent dishes and follow dietary recommendations. "
        f"Taking into account the dietary recommendations of '{temp['diet_name']}', "
        f"create for me a list of {3} balanced daily menu options. "
        f"Each daily menu on your list should consist of {5} meals."
        f"Each daily menu dish on your list should not contain products that may cause allergies: '{user_info['allergies']}' and intolerances: '{user_info['intolerances']}'."
        "User is currently located in the country Ukraine. Please indicate prices for food products in UAH."
    )
    parser = JsonOutputParser(pydantic_object=DailyMenuList)
    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | model
    output = chain.invoke({"query": query})
    try:
        parsed_output = parser.parse(output.content)
    except OutputParserException as e:
        fix_parser = OutputFixingParser.from_llm(parser=parser, llm=model)
        parsed_output = fix_parser.parse(output.content)
    return parsed_output


def translate_text(text: str, dest_language: str = 'uk') -> str:
    translator = googletrans.Translator()
    result = translator.translate(text, dest=dest_language)
    return result.text


def translate_dict(data: dict, dest_language: str = 'uk') -> dict:
    if isinstance(data, dict):
        return {k: translate_dict(v, dest_language) for k, v in data.items()}
    elif isinstance(data, list):
        return [translate_dict(item, dest_language) for item in data]
    elif isinstance(data, str):
        return translate_text(data, dest_language)
    else:
        return data


def main(user_message, api_key, language):
    # Main code
    model_3_5 = get_model(api_key, "gpt-3.5-turbo-0125")
    model_4 = get_model(api_key, "gpt-4-0125-preview")
    diet_data_list = diets.get_diet_data_list()
    diet_data_list_en = diets.get_diet_data_list_en()
    user_info = get_user_info(user_message, model_3_5)
    indications_list = [(i, diet['indications']) for i, diet in enumerate(diet_data_list_en)]
    indications_list.append((99, "If it doesn't exactly match any other."))
    indication_info = get_indication_info(user_info, indications_list, model_3_5)
    indeication_index = int(indication_info['indeication_index'])
    temp = diet_data_list[indeication_index].copy()
    # temp.pop('diet_name')
    temp.pop('indications')
    temp.pop('purpose')
    temp.pop('eating_regime')
    diet_options = get_diet_options(temp, user_info, model_4)
    if language == "Ukrainian ***:red[beta]***":
        translated_diet_options = translate_dict(diet_options)
        return translated_diet_options
    else:
        return diet_options


if __name__ == "__main__":
    # Hello, I have a cold, please help me create a dietary menu for me. Please note that I am allergic to tree nuts and peanuts. I also have lactose intolerance.
    user_message = ("Hello, I have a cold, please help me create a dietary menu for me. "
                    "Please note that I am allergic to tree nuts and peanuts. "
                    "I also have lactose intolerance.")
    # Call the main function
    user_info = main(user_message, st.secrets["OPENAI_API_KEY"])
    print(user_info)
