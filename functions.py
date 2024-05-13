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
    health_info: str = Field(description="If included in the message: User's any health information from the message.")
    allergies: str = Field(description="If included in the message: User's allergies.")
    intolerances: str = Field(description="If included in the message: User's food intolerances.")
    exclude: str = Field(description="If included in the message: Which foods to exclude from the diet.")
    add: str = Field(description="If included in the message: Which foods to add to your diet.")


class Indication(BaseModel):
    indication_index: int = Field(description="Index of similar indications.")
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
        "You are a specialist in processing requests from a user who describes information about himself for the "
        "purpose of assigning him a therapeutic diet."
        "But there are cases when the user's message is incorrect or contains false information, so first check "
        "whether the user's message is an adequate description of information about: "
        "the user's health problems, his allergies, intolerances, "
        "wishes, what to exclude and what to add, type of diet and other restrictions. "
        "If the user's message is inadequate, contains many grammatical, lexical, "
        "semantic errors, errors in medical terms, non-existent medical terms or invented made-up diseases, "
        "humorous diseases then fill all fields as None."
        f"If the user's message is correct, extract the relevant information from the message. User message: '{user_message}'"
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

    # Handling an invalid user request
    if parsed_output['health_info'] == 'None' or parsed_output['health_info'] is None:
        raise Exception("❗❗❗ Sorry, please write your request again. Please do it right ❗❗❗")

    return parsed_output


def get_indication_info(user_info: UserInfo, indications_list: List[tuple], model: ChatOpenAI) -> Indication:
    query = (
        f"'List of medical indications': {indications_list}. "
        "You are a specialist in determining the appropriateness of user information and available medical indications."
        f"Write the diet number that best describes and corresponds to the user’s health indications, keep in mind "
        f"that some lines are similar, but you should choose the one that is as similar in meaning as possible: user_info ='{user_info['health_info']}'. "
        "If you did not find an exact match in the 'List of medical indications', then return indication_index None."
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
        f"User is currently located in the country {'Ukraine'}. Please indicate prices for food products in {'UAH'}."
    )

    if user_info['exclude'] or user_info['add']:
        query += (f"Please note as additional conditions from the client that the menu should not contain products "
                  f"such as: {user_info['exclude']}, but on the contrary, be sure to add products: {user_info['add']}. ")

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
    indication_index = int(indication_info['indication_index'])
    if indication_index is not None:
        temp = diet_data_list_en[indication_index].copy()
        if 'indications' in temp:
            temp.pop('indications')
        if 'purpose' in temp:
            temp.pop('purpose')
        if 'eating_regime' in temp:
            temp.pop('eating_regime')
    else:
        temp = user_info.copy()
        temp['diet_name'] = f"General diet for '{user_info['health_info']}'"
    diet_options = get_diet_options(temp, user_info, model_4)
    if language == "Ukrainian ***:red[beta]***":
        translated_diet_options = translate_dict(diet_options)
        return translated_diet_options
    else:
        return diet_options


if __name__ == "__main__":
    # Positive example:
    # Hi there! I've been diagnosed with esophagitis and gastritis. Can you assist me in creating a suitable diet plan? I'm allergic to peanuts and soy. Also, I don't like onions, but I do like apples, keep that in mind.
    # Negative example:
    # Hiya, I've been diagnosed with flibberjabberitis and gobbledygookitis. Can you help me create a diet plan? I'm allergic to marshmallows and moon cheese.
    user_message = ("Hi there! I've been diagnosed with esophagitis and gastritis. Can you assist me in creating a "
                    "suitable diet plan? I'm allergic to peanuts and soy. Also, I don't like onions, but I do like "
                    "apples, keep that in mind.")
    # Call the main function
    user_info = main(user_message, st.secrets["OPENAI_API_KEY"])
    print(user_info)
