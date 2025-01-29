import streamlit as st
import time
import requests
import dspy
from dspy.signatures.signature import signature_to_template
import streamlit.components.v1 as components

st.set_page_config(
    page_title="riNgo",
    page_icon="🍎",
    layout="centered",
    initial_sidebar_state='collapsed'
)

# mapping the labels of the image to its corresponding names to search for it in the database
label_to_food_item = {
    0: 'Apple Pie',
    1: 'Baby Back Ribs',
    2: 'Baklava',
    3: 'Beef Carpaccio',
    4: 'Beef Tartare',
    5: 'Beet Salad',
    6: 'Beignets',
    7: 'Bibimbap',
    8: 'Bread Pudding',
    9: 'Breakfast Burrito',
    10: 'Bruschetta',
    11: 'Caesar Salad',
    12: 'Cannoli',
    13: 'Caprese Salad',
    14: 'Carrot Cake',
    15: 'Ceviche',
    16: 'Cheesecake',
    17: 'Cheese Plate',
    18: 'Chicken Curry',
    19: 'Chicken Quesadilla',
    20: 'Chicken Wings',
    21: 'Chocolate Cake',
    22: 'Chocolate Mousse',
    23: 'Churros',
    24: 'Clam Chowder',
    25: 'Club Sandwich',
    26: 'Crab Cakes',
    27: 'Crème Brûlée',
    28: 'Croque Madame',
    29: 'Cupcakes',
    30: 'Deviled Eggs',
    31: 'Donuts',
    32: 'Dumplings',
    33: 'Edamame',
    34: 'Eggs Benedict',
    35: 'Escargots',
    36: 'Falafel',
    37: 'Filet Mignon',
    38: 'Fish and Chips',
    39: 'Foie Gras',
    40: 'French Fries',
    41: 'French Onion Soup',
    42: 'French Toast',
    43: 'Fried Calamari',
    44: 'Fried Rice',
    45: 'Frozen Yogurt',
    46: 'Garlic Bread',
    47: 'Gnocchi',
    48: 'Greek Salad',
    49: 'Grilled Cheese Sandwich',
    50: 'Grilled Salmon',
    51: 'Guacamole',
    52: 'Gyoza',
    53: 'Hamburger',
    54: 'Hot and Sour Soup',
    55: 'Hot Dog',
    56: 'Huevos Rancheros',
    57: 'Hummus',
    58: 'Ice Cream',
    59: 'Lasagna',
    60: 'Lobster Bisque',
    61: 'Lobster Roll Sandwich',
    62: 'Macaroni and Cheese',
    63: 'Macarons',
    64: 'Miso Soup',
    65: 'Mussels',
    66: 'Nachos',
    67: 'Omelette',
    68: 'Onion Rings',
    69: 'Oysters',
    70: 'Pad Thai',
    71: 'Paella',
    72: 'Pancakes',
    73: 'Panna Cotta',
    74: 'Peking Duck',
    75: 'Pho',
    76: 'Pizza',
    77: 'Pork Chop',
    78: 'Poutine',
    79: 'Prime Rib',
    80: 'Pulled Pork Sandwich',
    81: 'Ramen',
    82: 'Ravioli',
    83: 'Red Velvet Cake',
    84: 'Risotto',
    85: 'Samosa',
    86: 'Sashimi',
    87: 'Scallops',
    88: 'Seaweed Salad',
    89: 'Shrimp and Grits',
    90: 'Spaghetti Bolognese',
    91: 'Spaghetti Carbonara',
    92: 'Spring Rolls',
    93: 'Steak',
    94: 'Strawberry Shortcake',
    95: 'Sushi',
    96: 'Tacos',
    97: 'Takoyaki',
    98: 'Tiramisu',
    99: 'Tuna Tartare',
    100: 'Waffles'
}
food101 = []
for food in label_to_food_item.values():
    food101.append(food.lower())

def search_fact_from_database(food: str):
    '''search for existing food in database'''

    # searcing for it if it exist in the database retreive it
    food_name = food # food detected from resnet

    api_key = '2bqySjf9bBLfiqW3MEslAQccsF7hs3aGzhJ50hd2'

    search_url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={food_name}"
    search_response = requests.get(search_url)
    search_data = search_response.json()


    if search_data['foods']:
        fdc_id = search_data['foods'][0]['fdcId']

        # Retrieve nutritional information using the fdcId
        nutrient_url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}?format=full&api_key={api_key}"
        nutrient_response = requests.get(nutrient_url)
        nutrition_info = nutrient_response.json()
        show_fact(nutrition_info = nutrition_info)
    
def show_fact(nutrition_info): 
    '''adjust the nutrition fact in a list for display'''

    #extracting real Fact from database
    facts = []
    for i in range(len(nutrition_info['foodNutrients'])):
        facts.extend((nutrition_info['foodNutrients'][i]['nutrient']['name'],nutrition_info['foodNutrients'][i]['amount'],nutrition_info['foodNutrients'][i]['nutrient']['unitName']) if nutrition_info['foodNutrients'][i]['amount'] > 1 and nutrition_info['foodNutrients'][i]['nutrient']['unitName'] in ['g', 'kcal'] else '')

    fact_labels = facts[::3]
    fact_value = facts[1::3]
    fact_unit = facts[2::3]

    facts = []

    for i in range(len(fact_unit)):
        facts.append((fact_labels[i], fact_value[i], fact_unit[i]))

    facts.append(("Serving Size",nutrition_info['servingSize'], nutrition_info['servingSizeUnit']))    
    return facts

#dspy signaure (task)
class NutritionFact(dspy.Signature):
    """Generate full nutrition values for given food labels and serving portions."""
    
    food_labels: str = dspy.InputField()
    serving_size: str = dspy.InputField(desc='Default serving size is 45 grams to 75 grams if it is not specified')
    estimated_nutrition: list[str] = dspy.InputField(desc=f'''If the list is not empty, then it has estimations of the nutrition facts,
                                                    generate a more precise estimation by calculating the avarage of the nutritions in the list
                                                    or find features to predict a better nutrition estimation.''')
    nutrition_fact: str = dspy.OutputField(desc='''Do not copy the same estimation in estimated_nutrition, generate a new nutrition consest of more precise values.
                                        Write the final answer as:
                                        Nutrition Facts:
                                        Calories: type the estimation here, unit: kcal
                                        Total Carbohydrates: type the estimation here, unit: g
                                        Total Fat: type the estimation here, unit: g
                                        Total Sugars: type the estimation here, unit: g
                                        Fibers: type the estimation here, unit: g''')

class CoT(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought(NutritionFact)

    def forward(self, food_labels: str, serving_size: str = '45g to 75g', estimated_nutrition: list[str] = []):
        return self.prog(food_labels = food_labels, serving_size = serving_size, estimated_nutrition = ' '.join(estimated_nutrition)) 
    
c = CoT() #dspy object to deal with llms

st.logo(
    './riNgo_logo.png',
    size='large',
)


with st.sidebar:
    st.write('Navigation')
    Mode = st.selectbox("Mode:", ("T1D Super Warrior", "HealthBuster"))
    pages_mode2 = {
    "Home":"Home",
    "Calculate Nutrition":"Calculate Nutrition",
    }
    if Mode == "HealthBuster":
        page = st.sidebar.radio("Go to", list(pages_mode2.keys()))
    pages_mode1 = {
    "Home":"Home",
    "Calculate Nutrition":"Calculate Nutrition",
    "Calculate Carb Ratio I:C":"",
    "Calculate Bolus Amount":"",
    "Calculate A1c":"",
    "Calculate Insulin Sensitivity Factor":"",
    "Calculate Avarage Blood Glucose": "",
    "Calculate Correction Amount":"",
    }
    if Mode == "T1D Super Warrior":
        page = st.sidebar.radio("Go to", list(pages_mode1.keys()))

#-----------------------------------
if page == "Home":
    st.write('# riNgo 🍎')
    st.subheader('', divider='red')
    st.write('**🍎 Your AI Nutrition Guide 🍎** \n\n **allows you to monitor your diet at any time and from any location!**')
    st.write('*Simply take a quick photo of your meal and await the Nutrition results!*')
    st.subheader('', divider='red')
    st.write("Welcome to **riNgo**—your AI-powered dietary companion \n\nthat makes healthy eating effortless. Simply snap a photo of your plate, and let our state-of-the-art AI models analyze the image to provide you with detailed nutrition facts in an instant. Whether you're counting calories, carbs, or just curious about what’s on your plate,\n\n **riNgo** has got you covered. Plus, with its intuitive tracking features, you can easily keep an eye on your food consumption and make informed choices for a healthier lifestyle.\n\n Eat smart, live well, and let riNgo guide you every step of the way! 🍽️📱✨Enjoy the journey to a healthier you!")
    st.subheader('', divider='red')
    st.write("This App is mainly made for T1D patients and their health care providers")
#-----------------------------------
if page == "Health AI Assisstant":
    pass
#-----------------------------------
if page == 'Calculate Nutrition':
    
    st.subheader('', divider="blue")

    st.write('# Upload a photo of your dish')

    photo = st.file_uploader(label="Upload Here", type=["jpg", "jpeg", "png"]) #later on enable accept_multiple_file = True -> return list of files

    #resnet   
    #load once in session i think use cache_data not resource check notes
    def query(image: str):
        '''load resnet-model, post the image and return the response'''
        
        API_URL = "https://api-inference.huggingface.co/models/microsoft/resnet-50"
        headers = {f"Authorization": "Bearer "+ open('secret.txt').read()}

        response = requests.post(API_URL, headers=headers, data=image)
        return response.json()

    if photo:
        st.image(photo)

        # line 
        st.subheader('', divider="blue")

        #calling resnet
        image_label = query(photo.read())
        
        try:
            time.sleep(15) #waiting for resnet response
            # extracting the high scores only 
            food_component_resnet = []
            for i in range(len(image_label)):
                if image_label[i]['score'] > 0.1:
                    food_component_resnet.append(image_label[i]['label'])   
        except:
            time.sleep(30)
            # extracting the high scores only 
            food_component_resnet = []
            for i in range(len(image_label)):
                if image_label[i]['score'] > 0.1:
                    food_component_resnet.append(image_label[i]['label'])
        
        # write food on screen
        st.write("**Your delicious dish has these ingredients:**")
        st.write(f"{food_component_resnet}")
        
        # check if food label in food101 return fact from database else return model
        facts = []
        end_flag = False
        for food in food101:
            if food in food_component_resnet[0].lower():
                facts = search_fact_from_database(food)
                end_flag = True
        
        if end_flag:
            # line
            st.subheader('', divider="blue")
            # end of displaying facts function
        else:    
            # line
            st.subheader('', divider="blue")
            
            st.write("**If you have more ingredients in you dish that is not shown in the list above, Please provide them here**")
            prompt_extend = st.text_input("additional ingredients")
        
            st.write("**What is the number of servings you are having ?**")
            servings = st.text_input("servings")
            try:
                with st.status("Downloading AI data..."):
                    st.write("Searching for data...")
                    dspy.Assert
                    time.sleep(30)
                    #set model1
                    llm_model =dspy.LM('openai/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B', api_key=open('secret.txt').read(), max_tokens=2000, temperature=0.4, api_base='https://api-inference.huggingface.co/v1/')
                    dspy.settings.configure(lm=llm_model)
                    nutrition_tamplet = signature_to_template(NutritionFact)
                    dspy.settings.lm = llm_model
                    #generate fact1
                    fact1 = c.forward(food_labels=' '.join(food_component_resnet) + prompt_extend, serving_size=servings)
                    fact1 = str(fact1)
                    
                    st.write("Did you know that The Small Intestine is Not So **Small!** Despite its name, the small intestine is 8about 6 meters*!")
                    st.write("Detecting Ingredients..")
                    
                    time.sleep(50)
                    #set model2 (final model)
                    llm_model = dspy.LM('openai/deepseek-ai/DeepSeek-V3', api_key=open('secret.txt').read(), max_tokens=2000, temperature=0.4, api_base='https://huggingface.co/api/inference-proxy/together')
                    dspy.settings.configure(lm=llm_model)
                    nutrition_tamplet = signature_to_template(NutritionFact)
                    dspy.settings.lm = llm_model
                    #generate fact2
                    fact2 = c.forward(food_labels=' '.join(food_component_resnet) + prompt_extend, serving_size=servings, estimated_nutrition=[fact1])
                    fact2 = str(fact2)
                    
                    st.write("Taste Bud Trivia: Did you know that the average human has about **10,000** taste buds!")
                    st.write("Displaying Nutritions...")
                    time.sleep(15)


                show = st.button("Show Nutritions")
                final_fact = fact2[fact2.rindex('Nutrition'):len(fact2)-1]
                if show:
                    with st.container(border=True): #container
                        st.write(final_fact)
            
            except Exception as e:
                st.write("try again", e)
            
#----------------------------------------
if page == "Calculate Carb Ratio I:C":
    therapy = st.selectbox("Therapy", ("Pen Injections", "Pump Therapy"))
    if therapy == "Pen Injections":
        carb_intake = 500
        daily_insulin_unit = st.number_input("daily insulin unit")
        if daily_insulin_unit !=0 :
            icr = carb_intake / daily_insulin_unit
            st.write(f'1 unit of insulin per {icr:.2f} grams of carb')

    if therapy == "Pump Therapy":
        carb_intake = st.number_input("avarage carb intake")
        daily_insulin_unit = st.number_input("daily insulin unit")
        if daily_insulin_unit !=0 :    
            icr = carb_intake / daily_insulin_unit
            st.write(f'1 unit of insulin per {icr:.2f} grams of carb')
#----------------------------------------
if page == "Calculate Bolus Amount":
    icr = 0
    bolus = 0
    therapy = st.selectbox("Therapy", ("Pen Injections", "Pump Therapy"))
    if therapy == "Pen Injections":
        carb_intake = 500
        daily_insulin_unit = st.number_input("daily insulin unit")
        if daily_insulin_unit !=0 :
            icr = carb_intake / daily_insulin_unit
            st.write(f'1 unit of insulin per {icr:.2f} grams of carb')

    if therapy == "Pump Therapy":
        carb_intake = st.number_input("avarage carb intake")
        daily_insulin_unit = st.number_input("daily insulin unit")
        if daily_insulin_unit !=0 :    
            icr = carb_intake / daily_insulin_unit
            st.write(f'1 unit of insulin per {icr:.2f} grams of carb')
    carb_in_meal = st.number_input("carbs in meal")
    if icr !=0:
        bolus = carb_in_meal/icr
    st.write(f"Bolus Amount: {bolus:.2f} units")   
#----------------------------------------
if page == "Calculate A1c":
    st.write("You have to know your avarage blood glucose to calculate A1c")
    avg_bg = st.number_input("avarage blood glucose")
    a1c = (avg_bg + 46.7) / 28.7
    st.write(f"A1c = {a1c:.1f} \n\nNormal Range: below 6.00")
#----------------------------------------
if page == "Calculate Insulin Sensitivity Factor":
    isf = 0
    daily_insulin_unit = st.number_input("daily insulin unit")
    if daily_insulin_unit !=0 :
        isf = 1700 / daily_insulin_unit
    st.write(f"Insulin Sensitivity Factor: {isf:.2f}")    
#----------------------------------------
if page == "Calculate Correction Amount": 
    isf = 0
    correction_unit = 0
    daily_insulin_unit = st.number_input("daily insulin unit")
    if daily_insulin_unit !=0 :
        isf = 1700 / daily_insulin_unit  
    current_bg = st.number_input("youe current blood glucose")
    if isf != 0:
        correction_unit = (current_bg - 180) / isf
    st.write(f"Correction Amount: {correction_unit:.2f} units")    
#----------------------------------------
if page == "Calculate Avarage Blood Glucose":
    st.write(f"You should know your A1c to calculate your avarage blood glucose")
    a1c = st.number_input("your A1c")
    avg_bg = a1c * 28.7 - 46.7
    st.write(f"Avarage Blood Glucose: {avg_bg:.2f}")
