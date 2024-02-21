import requests, json, random, sys, time

main_url = 'https://letzguess.lu/'
api_url = 'https://api.letzguess.lu/'

cookies = None

session = None

current_round_id = None
auth = None
user_profile = None
answers = None

last_request = None

LOG = False

def load_dict_from_file(filename):
    try:
        with open(filename, 'r') as json_file:
            loaded_dict = json.load(json_file)
        return loaded_dict
    except FileNotFoundError:
        print(f"File '{filename}' not answersfound.")
        return None

def save_dict_to_file(dictionary, filename):
    with open(filename, 'w') as json_file:
        json.dump(dictionary, json_file)

def containing(key):
    global answers
    return key in answers

def getting(key):
    global answers
    return answers.get(key, None)

def setting(key, value):
    print(f'setting: {key} = {value}')
    global answers
    answers[key] = value

def build_header():
    return {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Authorization': auth,
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        #'If-None-Match': 'W/"9b-xbPeGl32iYz0ApGYR68JlSedqDQ"',
    }

def request_get(url):
    # print(f'cooks: {cooks if add_cookies else None}')
    # headers = build_header('GET', url)
    response = session.get(url)
    last_request = response
    if LOG:
        log(response)
    return response

def request_post(url, data=None, json=None):
    # headers = build_header('GET', url)
    # add_cookies=True, 
    # , cookies=cooks if add_cookies else None,
    response = session.post(url, data=data, json=json)
    last_request = response
    if LOG:
        log(response)
    return response

def code(request):
    return request.status_code

def data(request):
    return request.text

def log(response):
    if response == None:
        print(f'--- Response is None')
        return
    print(f'--- {response.url} -> {response.status_code}')
    print(f' |- Headers: {response.request.headers}')
    print(f' |- Cookies: {session.cookies.get_dict()}')
    print(f' |- Body: {response.request.body}')
    print(f' |- Headers: {response.headers}')
    print(f' |- Cookies: {response.cookies.get_dict()}')
    print(f' |- Body: {response.text}')
    print()

def req_game():
    response = request_get(f'{main_url}game')
    return response

def req_refresh():
    response = request_get(f'{api_url}refresh')
    return response

def req_profile():
    response = request_get(f'{api_url}user/profile')
    return response

def to_json(response):
    return response.json()

def update_profile():
    global user_profile

    response = req_profile()
    if code(response) in {200, 340}:
        user_profile = to_json(response)
    elif code(response) == 403:
        update_token()
        #update_profile()

def req_refresh():
    response = request_get(f'{api_url}refresh')
    return response

def req_info():
    response = request_get(f'{api_url}user/challenge/info')
    return response

def update_token():
    global auth, cookies
    response = req_refresh()
    json = to_json(response)
    if code(response) in {200, 340}:
        # auth = f'Bearer {json["accessToken"]}'
        setting('jwt', json["accessToken"])

        cookies = {'jwt': json["accessToken"]}

        session = requests.Session()
        for key, value in cookies.items():
            session.cookies.set(key, value)

    elif code(response) == 403 and json['message'] == 'User not found':
        #req_refresh()
        print('Could not update token')
        pass

def update_info():
    global user_profile
    response = req_info()
    if code(response) in {200, 340}:
        json = to_json(response)
        user_profile = json
    else:
        log(response)

def req_new_round(country):
    response = request_post(f'{api_url}challenge/new-round', json={'country': country})
    return response

def req_latest():
    response = request_get(f'{api_url}challenge/round-active/latest')
    return response

def req_update_round():
    response = request_post(f'{api_url}challenge/update-round', json={'signal': {}})
    return response

def req_round(id):
    response = request_get(f'{api_url}challenge/round/{id}')
    return response

def req_answer(question_id, resp):
    response = request_post(f'{api_url}challenge/answer', json={'question_id': question_id, 'user_response': resp})
    return response

def req_next_question():
    response = request_post(f'{api_url}challenge/next-question')
    return response

def delay(ms):
    print(f'Waiting for {ms}ms')
    time.sleep(ms/1000)

random_error_percent = 28 # / 100%
random_delay_next_question_ms_min = 800
random_delay_next_question_ms_max = 3500
random_delay_new_round_ms_min = 1000
random_delay_new_round_ms_max = 3000
random_delay_answer_ms_min = 800
random_delay_answer_ms_max = 3500

def once():
    global current_round_id, answers
        
    ended = False

    round_count = 5000

    new_round = True
    check_latest = True
    next = False

    while round_count >= 0:
        if new_round:
            if round_count <= 0:
                print('Ran out of rounds')
                return True
            
            update_round = req_update_round()
            if code(update_round) == 403:
                log(update_round)
                print('Error when updating round. 1')
                return False
            json = to_json(update_round)
            if code(update_round) in {410, 404} and json['message'] in {'The round time has expired!', 'No active round found'}:
                
                # Delaying new game creation
                delay(random.randint(random_delay_new_round_ms_min, random_delay_new_round_ms_max))

                new_game = req_new_round('LU')
                json = to_json(new_game)
                if code(new_game) != 201:
                    log(current_round)
                    print('Error when creating new game. 1')
                    return False
                elif json['message'] != "New round created successfully":
                    log(current_round)
                    print('Error when creating new game. 2')
                    return False

                check_latest = True
                print(f'{round_count} ->>> New game created.')
                round_count -= 1
            elif json['message'] == 'Round updated successfully':
                print('No new game created.')

        if check_latest:
            latest = req_latest()
            if code(latest) != 200:
                log(current_round)
                print('Error when getting latest. 1')
                return False
            json = to_json(latest)
            if json['message'] != "Round successfully found":
                log(current_round)
                print('Error when getting latest. 2')
                return False
            
            if not "round" in json:
                log(current_round)
                print('Error when getting latest. 3')
                return False
            round = json['round']
            latest_round_id = round['id']
            current_round_id = latest_round_id

            print(f'Latest round: {latest_round_id}')

            ## probably checking for latest round creation ?
            update_round = req_update_round()
            json = to_json(update_round)
            if code(update_round) == 410 and json['message'] == 'The round time has expired!' or json['message'] == 'No active round found':
                log(current_round)
                print('Error when updating round after latest. 1')
                return False
            elif json['message'] == 'Round updated successfully':
                log(current_round)
                print('Successfully updated round after latest.')
            ## 
            
            check_latest = False

        if next:
            # Delaying next question
            delay(random.randint(random_delay_next_question_ms_min, random_delay_next_question_ms_max))

            next_question = req_next_question()
            json = to_json(next_question)
            if code(next_question) == 404 and json['message'] == "No active round found":
                new_game = True
                continue
            elif code(next_question) == 404 and json['message'] == "Not answered yet":
                next = False
                continue
            elif code(next_question) != 200 and json['message'] != "New question added successfully":
                log(next_question)
                print('Error when getting next question. 1')
                return False
            else:
                print(f'Got next question.')

        current_round = req_round(current_round_id)

        if code(current_round) != 200:
            log(current_round)
            print('Error when getting current round. 1')
            return False
        json = to_json(current_round)
        if json['message'] != "Round successfully found":
            log(current_round)
            print('Error when getting current round. 2')
            return False

        round = json['round']
        if round['ended']:
            new_game = True
            print(f'Round ended. ({current_round_id})')
            continue

        question = round['question']
        # print(f'question: {question}')
        question_id = question['question_id']
        question_text = question['question']
        question_answers = question['responses']

        print(f'Round: {current_round_id}')
        print(f'Question: {question_text} ({question_id})')
        print(f'Possible answers: {question_answers}')

        try_anwser = None
        saved = None

        if containing(question_id):
            if random.randint(0, 101) < random_error_percent:
                try_anwser = random.choice(question_answers.remove(getting(question_id)))
                print(f'Answer found: {try_anwser} but removed')
            else: 
                try_anwser = getting(question_id)
                print(f'Answer found: {try_anwser}')
            saved = True
            # answer = req_answer(found_answer)
            # json_answer = to_json(answer)
        else:
            try_anwser = random.choice(question_answers)
            print(f'No answer found, trying random ({try_anwser})')
            saved = False

        # Delaying answer
        delay(random.randint(random_delay_answer_ms_min, random_delay_answer_ms_max))

        # Sending answer
        answer = req_answer(question_id, try_anwser)
        json_answer = to_json(answer)

        if code(answer) == 404 and json_answer['message'] == "No active round found":
            new_round = True
        elif code(answer) == 200 and json_answer['message'] == "Correct response":
            print(f'Correct answer {try_anwser} ({question_id}) ({"found" if saved else "try/add"})')
            if not saved:
                setting(question_id, try_anwser)
            
            # streak continue
            # return True
            next = True
        elif code(answer) == 400 and json_answer['message'] == "Wrong answer":
            # log(answer)
            print('Wrong answer, correcting')

            correct_round = req_round(current_round_id)
            if code(current_round) != 200:
                log(current_round)
                print('Error when getting correct round. 1')
                return False
            correct_json = to_json(correct_round)
            if json['message'] != "Round successfully found":
                log(current_round)
                print('Error when getting correct round. 2')
                return False
            # log(correct_round)
            
            correct_json_round = correct_json['round']
            correct_question = correct_json_round['question']
            correct_question_id = correct_question['question_id']
            correct_question_text = correct_question['question']
            correct_question_answers = correct_question['responses']
            correct_question_correct_answer = correct_question['correct_response']

            setting(correct_question_id, correct_question_correct_answer)

            print(f'Correct answer {correct_question_correct_answer} ({question_id}) (added)')

            ended = correct_json_round['ended']
            # return True
        elif code(answer) == 400 and json_answer['message'] == 'Question already answered':
            print('Question already answered')
            # current_round_id = int(current_round_id)+1
            check_latest = True
            next = True
            # streak = False

        update_info()
        print(user_profile)

    update_profile()
    return True

if __name__ == '__main__':
    answers = load_dict_from_file('./answers.json')
    auth = getting('auth')
    cookies = {'jwt': getting('jwt')} # auth.replace('Bearer ', '')

    session = requests.Session()
    for key, value in cookies.items():
        session.cookies.set(key, value)
    
    # update_token()
    session.headers = build_header()

    update_profile()

    try :
        if once():
            print('got it')
        else:
            print('nope, error :c')
            log(last_request)
    except KeyboardInterrupt:
        print('Interrupted')

    update_profile()
    print(user_profile)

    save_dict_to_file(answers, './answers.json')
    session.close()
