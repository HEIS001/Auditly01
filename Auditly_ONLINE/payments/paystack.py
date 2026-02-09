import os, requests
PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET_KEY")

def initialize_payment(email, amount):
    url = "https://api.paystack.co/transaction/initialize"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET}"}
    data = {"email": email, "amount": amount*100}
    res = requests.post(url,json=data,headers=headers)
    return res.json()
