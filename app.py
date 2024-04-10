from flask import Flask, render_template, request, redirect, url_for
import requests
import random
import re

def get_access_token(client_id, grant_type, username, password, scope):
    token_url = 'https://cosylab.iiitd.edu.in/api/auth/realms/bootadmin/protocol/openid-connect/token'

    token_data = {
        'client_id': client_id,
        'grant_type': grant_type,
        'username': username,
        'password': password,
        'scope': scope
    }

    try:
        response = requests.post(token_url, data=token_data)
        response.raise_for_status()
        return response.json().get('access_token')

    except requests.exceptions.RequestException as e:
        print(f"Error obtaining access token: {str(e)}")
        return None

def access_api_with_token(api_endpoint, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(api_endpoint, headers=headers)
        response.raise_for_status()
    
        return response.json()


    except requests.exceptions.RequestException as e:
        print(f"Error accessing API: {str(e)}")


app = Flask(__name__)

# First page with a button to redirect to the second page
@app.route('/')
def index():
    return render_template('index.html')

# Second page with a form to select multiple options
@app.route('/second_page', methods=['GET', 'POST'])
def second_page():
    if request.method == 'POST':
        selected_options = request.form.getlist('options')
        print(type(selected_options),selected_options)
        return redirect(url_for('next_page', options=selected_options))
    return render_template('second_page.html')

# Third page to display the selected options
@app.route('/next_page/<options>')
def next_page(options):
    selected_options = (options)
    client_id = 'app-ims'
    grant_type = 'password'
    username = 'forkit-hackathon'
    password = 'forkitiiitdelhi'
    scope = 'openid'

    dict = {"Sadness":['Lavendar','Bergamot'],"Anger":['Chamomile','Rose'],"Fear":['Clary','Epazote'],"Disgust":['Peppermint','Lemon'],"Happy":['Chocolate']}

    # Use regular expression to extract list elements
    pattern = r"\[([^\]]*)\]"
    match = re.search(pattern, selected_options)
    if match:
        # Get the content inside the square brackets
        content_inside_brackets = match.group(1)
        # Split the content to get individual elements
        global my_list
        my_list = [element.strip("' ") for element in content_inside_brackets.split(',')]
        # Now, my_list is a Python list
        print("lolo",my_list[0])
    else:
        print("No match found.")
        print('selected options : ',selected_options[0])
     
    for i in range (len(my_list)):
        choice = dict[my_list[i]]
        entity_name = random.choice(choice)
        print(entity_name)
        api_endpoint1 = f'https://cosylab.iiitd.edu.in/api/entity/getentities?name={entity_name}'
        access_token = get_access_token(client_id, grant_type, username, password, scope)

        entity1 = []
        if access_token:
            # Access API with obtained token
            entity1.append(access_api_with_token(api_endpoint1, access_token))
        else:
            print("Authentication failed.")
        entity_id = entity1[0][0]['entity_id']
        api_endpoint2 = f'https://cosylab.iiitd.edu.in/api/foodPairingAnalysis/{entity_id}'

        if access_token:
            # Access API with obtained token
            edi = access_api_with_token(api_endpoint2, access_token)
            cat = []
            for i in range(len(edi['similar_entities'])):
                if edi['similar_entities'][i]["category"] in ['Herb','Seed','Flower']:
                    cat.append(edi['similar_entities'][i]["entity_name"])

        else:
            print("Authentication failed.")
        #print(cat)
            print(selected_options)

        return render_template('next_page.html' , selected_options=random.sample(cat,5))

if __name__ == '__main__':
    app.run(debug=True)