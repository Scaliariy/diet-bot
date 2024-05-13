import streamlit as st
from openai import AuthenticationError
from functions import main
from pdf_generator import generate_pdf
import time

# Title and language selection
st.title('🍉🤖 Diet Bot')
language = st.radio("Select the language of your request and response:", ["English", "Ukrainian ***:red[beta]***"])

# Sidebar for OpenAI API key input
st.sidebar.write("**Disclaimer**⚠️ \n\n"
                 "*This bot generates diets based "
                 "on the information you provide. We are not professional "
                 "dietitians or doctors, and we are not responsible for the "
                 "accuracy or effectiveness of the diets provided. "
                 "Users are solely responsible for their health and "
                 "the decisions they make based on the bot's recommendations. "
                 "If you have any doubts or questions about your diet or health, "
                 "consult a qualified professional. By using our bot, you agree to these terms.*")
disclaimer = st.sidebar.checkbox("I have read and agree to the terms of the disclaimer.")
if disclaimer:
    openai_api_key = st.sidebar.text_input('OpenAI API Key', type='password')

# Initialization result
if 'result' not in st.session_state:
    st.session_state['result'] = ''


# Function to generate response
def generate_response(input_text, api_key, language):
    with st.spinner('Wait about 1.5 minutes...'):
        st.session_state['result'] = main(input_text, api_key, language)


# Main content
st.write(
    'Please describe your health problems, allergies, intolerances '
    'in free form, so that the AI can create the correct individual diet for you. '
    'Please use the correct terms to generate the diet correctly.'
)

# Form for user input
with st.form('my_form'):
    text = st.text_area('Enter your request:',
                        placeholder='Example: Hello, I have a cold, please help me create a dietary menu for me. Please note that I am allergic to tree nuts and peanuts. I also have lactose intolerance.')
    submitted = st.form_submit_button('Submit')

    try:
        # Warning for missing OpenAI API key
        if not openai_api_key.startswith('sk-'):
            st.warning('Please enter your OpenAI API key!', icon='⚠')

        # Process submitted form
        if submitted and openai_api_key.startswith('sk-'):
            if text:
                try:
                    generate_response(text, openai_api_key, language)
                except AuthenticationError:
                    st.error('Please enter correct OpenAI API key!', icon='⚠')
            else:
                st.info('Please enter your request.', icon='⚠')
    except NameError:
        st.error('Please read and accept the disclaimer.', icon='⚠')

# Display result if available
if st.session_state['result']:
    st.write("**Created daily diet options:**")
    result = st.session_state['result']
    for i, menu in enumerate(result['menus']):
        # Create tab for each menu option
        with st.expander(f"**Menu {i + 1}**"):
            st.write(f"***:red[Total Price]: {menu['total_price']} {menu['currency']}***")
            for meal in menu['meals']:
                st.subheader(f"{meal['description']}")
                for dish in meal['dishes']:
                    st.write(f"**:violet[Name]: {dish['name']}**")
                    st.write(f"**:orange[Ingredients]:** {', '.join(dish['ingredients'])}")
                    st.write(f"**:blue[Cooking Instructions]:** {dish['cooking_instructions']}")
                    st.write(f"**:green[Price]:** {dish['price']} {menu['currency']}")
                # Generate PDF button
            if st.button(f"Generate PDF for Menu {i + 1}", key=f"generate-pdf-menu_{i + 1}"):
                with st.spinner('Generating PDF...'):
                    time.sleep(1)
                    generate_pdf(menu, f"diet_plan_{i + 1}.pdf")
                st.success(f"Generated diet_plan_{i + 1}.pdf!")
                with open(f"diet_plan_{i + 1}.pdf", "rb") as f:
                    st.download_button(f"Download pdf for Menu {i + 1}", f, f"diet_plan_{i + 1}.pdf",
                                       key=f"download-pdf-menu_{i + 1}")

