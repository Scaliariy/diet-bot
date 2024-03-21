import streamlit as st
from openai import AuthenticationError
from functions import main
from pdf_generator import generate_pdf
import time

st.title('🍉🤖 Diet Bot')

language = st.radio(
    "Select the language of your request and response:",
    ["English", "Ukrainian ***:red[beta]***"])

openai_api_key = st.sidebar.text_input('OpenAI API Key', type='password')

# Initialization result
if 'result' not in st.session_state:
    st.session_state['result'] = ''


def generate_response(input_text, api_key, language):
    with st.spinner('Wait for it...'):
        # result = main(input_text, api_key, language)
        result = {'menus':
                      [{'meals': [{'meal_number': 1,
                                   'description': 'Breakfast',
                                   'dishes': [{'name': 'Oatmeal porridge',
                                               'ingredients': ['Water', 'Oats', 'Salt', 'Honey'],
                                               'cooking_instructions': 'Boil water, add oats and salt, simmer until cooked, serve with honey.',
                                               'price': 30}],
                                   'total_price': 30},
                                  {'meal_number': 2,
                                   'description': 'Second Breakfast',
                                   'dishes': [{'name': 'Buckwheat soup',
                                               'ingredients': ['Water', 'Buckwheat', 'Carrots', 'Potatoes', 'Salt'],
                                               'cooking_instructions': 'Boil water, add buckwheat, diced carrots, and potatoes, season with salt, cook until vegetables are tender.',
                                               'price': 45}],
                                   'total_price': 45},
                                  {'meal_number': 3,
                                   'description': 'Lunch',
                                   'dishes': [{'name': 'Boiled chicken breast',
                                               'ingredients': ['Chicken breast', 'Salt', 'Bay leaves'],
                                               'cooking_instructions': 'Boil chicken breast in water with salt and bay leaves until fully cooked.',
                                               'price': 60},
                                              {'name': 'Mashed potatoes',
                                               'ingredients': ['Potatoes', 'Salt', 'Olive oil'],
                                               'cooking_instructions': 'Boil potatoes until tender, mash with olive oil and salt.',
                                               'price': 35}],
                                   'total_price': 95},
                                  {'meal_number': 4,
                                   'description': 'Afternoon Snack',
                                   'dishes': [{'name': 'Fruit jelly',
                                               'ingredients': ['Water', 'Apple juice', 'Gelatin'],
                                               'cooking_instructions': 'Dissolve gelatin in water, add apple juice, refrigerate until set.',
                                               'price': 25}],
                                   'total_price': 25},
                                  {'meal_number': 5,
                                   'description': 'Dinner',
                                   'dishes': [{'name': 'Vegetable stew',
                                               'ingredients': ['Carrots',
                                                               'Potatoes',
                                                               'Zucchini',
                                                               'Onions',
                                                               'Salt',
                                                               'Olive oil'],
                                               'cooking_instructions': 'Sauté onions in olive oil, add diced vegetables, season with salt, and simmer until tender.',
                                               'price': 50}],
                                   'total_price': 50}],
                        'meals_number': 5,
                        'total_price': 245,
                        'currency': 'UAH'},
                       {'meals': [{'meal_number': 1,
                                   'description': 'Breakfast',
                                   'dishes': [{'name': 'Rice porridge',
                                               'ingredients': ['Water', 'Rice', 'Salt', 'Maple syrup'],
                                               'cooking_instructions': 'Boil water, add rice and salt, simmer until cooked, serve with maple syrup.',
                                               'price': 30}],
                                   'total_price': 30},
                                  {'meal_number': 2,
                                   'description': 'Second Breakfast',
                                   'dishes': [{'name': 'Vegetable broth',
                                               'ingredients': ['Water', 'Carrots', 'Celery', 'Potatoes', 'Salt'],
                                               'cooking_instructions': 'Boil water, add diced vegetables, season with salt, cook until vegetables are tender.',
                                               'price': 40}],
                                   'total_price': 40},
                                  {'meal_number': 3,
                                   'description': 'Lunch',
                                   'dishes': [{'name': 'Boiled turkey fillet',
                                               'ingredients': ['Turkey fillet', 'Salt', 'Bay leaves'],
                                               'cooking_instructions': 'Boil turkey fillet in water with salt and bay leaves until fully cooked.',
                                               'price': 65},
                                              {'name': 'Quinoa salad',
                                               'ingredients': ['Quinoa',
                                                               'Cucumbers',
                                                               'Tomatoes',
                                                               'Lemon juice',
                                                               'Olive oil',
                                                               'Salt'],
                                               'cooking_instructions': 'Cook quinoa as per instructions, mix with diced cucumbers and tomatoes, dress with lemon juice, olive oil, and salt.',
                                               'price': 40}],
                                   'total_price': 105},
                                  {'meal_number': 4,
                                   'description': 'Afternoon Snack',
                                   'dishes': [{'name': 'Carrot sticks with hummus',
                                               'ingredients': ['Carrots',
                                                               'Chickpeas',
                                                               'Tahini',
                                                               'Lemon juice',
                                                               'Garlic',
                                                               'Salt'],
                                               'cooking_instructions': 'Cut carrots into sticks. Blend chickpeas, tahini, lemon juice, garlic, and salt to make hummus.',
                                               'price': 35}],
                                   'total_price': 35},
                                  {'meal_number': 5,
                                   'description': 'Dinner',
                                   'dishes': [{'name': 'Baked cod',
                                               'ingredients': ['Cod fillets',
                                                               'Lemon juice',
                                                               'Olive oil',
                                                               'Salt',
                                                               'Pepper'],
                                               'cooking_instructions': 'Marinate cod in lemon juice, olive oil, salt, and pepper, bake until cooked through.',
                                               'price': 70}],
                                   'total_price': 70}],
                        'meals_number': 5,
                        'total_price': 280,
                        'currency': 'UAH'},
                       {'meals': [{'meal_number': 1,
                                   'description': 'Breakfast',
                                   'dishes': [{'name': 'Barley porridge',
                                               'ingredients': ['Water', 'Barley', 'Salt', 'Agave syrup'],
                                               'cooking_instructions': 'Boil water, add barley and salt, simmer until cooked, serve with agave syrup.',
                                               'price': 25}],
                                   'total_price': 25},
                                  {'meal_number': 2,
                                   'description': 'Second Breakfast',
                                   'dishes': [{'name': 'Pumpkin soup',
                                               'ingredients': ['Pumpkin', 'Water', 'Salt', 'Onion', 'Olive oil'],
                                               'cooking_instructions': 'Sauté onion in olive oil, add diced pumpkin and water, season with salt, cook until pumpkin is tender, blend until smooth.',
                                               'price': 45}],
                                   'total_price': 45},
                                  {'meal_number': 3,
                                   'description': 'Lunch',
                                   'dishes': [{'name': 'Boiled beef',
                                               'ingredients': ['Beef', 'Salt', 'Bay leaves'],
                                               'cooking_instructions': 'Boil beef in water with salt and bay leaves until fully cooked.',
                                               'price': 70},
                                              {'name': 'Steamed vegetables',
                                               'ingredients': ['Broccoli', 'Carrots', 'Salt'],
                                               'cooking_instructions': 'Steam broccoli and carrots until tender, season with salt.',
                                               'price': 30}],
                                   'total_price': 100},
                                  {'meal_number': 4,
                                   'description': 'Afternoon Snack',
                                   'dishes': [{'name': 'Apple slices with peanut-free almond butter substitute',
                                               'ingredients': ['Apples', 'Sunflower seed butter'],
                                               'cooking_instructions': 'Slice apples and serve with sunflower seed butter.',
                                               'price': 30}],
                                   'total_price': 30},
                                  {'meal_number': 5,
                                   'description': 'Dinner',
                                   'dishes': [{'name': 'Grilled chicken',
                                               'ingredients': ['Chicken breast', 'Olive oil', 'Salt', 'Herbs'],
                                               'cooking_instructions': 'Marinate chicken breast in olive oil, salt, and herbs, grill until fully cooked.',
                                               'price': 55}],
                                   'total_price': 55}],
                        'meals_number': 5,
                        'total_price': 255,
                        'currency': 'UAH'}]}
        st.session_state['result'] = result
        time.sleep(2)


st.write(
    'Please describe your health problems, allergies, intolerances '
    'in free form, so that the AI can create the correct individual diet for you. '
    'Please use the correct terms to generate the diet correctly.')
with st.form('my_form'):
    text = st.text_area('Enter your request:',
                        placeholder='Example: Hello, I have a cold, please help me create a dietary menu for me. Please note that I am allergic to tree nuts and peanuts. I also have lactose intolerance.')
    submitted = st.form_submit_button('Submit')
    if not openai_api_key.startswith('sk-'):
        st.warning('Please enter your OpenAI API key!', icon='⚠')
    if submitted and openai_api_key.startswith('sk-'):
        if text:
            try:
                generate_response(text, openai_api_key, language)
            except AuthenticationError:
                st.error('Please enter correct OpenAI API key!', icon='⚠')
        else:
            st.info('Please enter your request.', icon='⚠')

if st.session_state['result']:
    result = st.session_state['result']
    # Create tabs
    tabs = [f"Menu {i + 1}" for i in range(len(result['menus']))]

    # Iterate over each menu option
    for i, menu in enumerate(result['menus']):
        with st.expander(tabs[i]):
            st.write(f"Total Price: {menu['total_price']} {menu['currency']}")
            for meal in menu['meals']:
                st.subheader(f"Meal {meal['meal_number']}: {meal['description']}")
                for dish in meal['dishes']:
                    st.write(f"Name: {dish['name']}")
                    st.write(f"Ingredients: {', '.join(dish['ingredients'])}")
                    st.write(f"Price: {dish['price']} {menu['currency']}")
                    st.write(f"Cooking Instructions: {dish['cooking_instructions']}")
            # Generate PDF button
            if st.button("Generate PDF", key=f"generate-pdf-diet_plan_{i + 1}"):
                with st.spinner('Generating PDF...'):
                    time.sleep(1)
                    generate_pdf(menu, f"diet_plan_{i + 1}.pdf")
                st.success(f"Generated diet_plan_{i + 1}.pdf!")
                with open(f"diet_plan_{i + 1}.pdf", "rb") as f:
                    st.download_button("Download pdf", f, f"diet_plan_{i + 1}.pdf",
                                       key=f"download-pdf-diet_plan_{i + 1}")

    st.write(result)
