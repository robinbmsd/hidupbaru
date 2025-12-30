# Import statement that is needed by the application
import os
import requests
# import uvicorn
from requests.auth import HTTPBasicAuth
from datetime import datetime
from fastapi import FastAPI, status
from pydantic import BaseModel
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from fastapi.responses import JSONResponse

# Data needed for the API URL, and login credential to acess the biller side  
API_URL = "http://horven-api.sumpahpalapa.com/api/v3/inquiry/bpjs_ketenagakerjaan"
USERNAME = "ii" #os.environ["ALTERRA_USERNAME"]
PASSWORD = "pp" #os.environ["ALTERRA_PWD_DEV"]

# Function to be use for decrypting a token send from mobile to prove its allowed to call the api
def decrypt_Auth(ciphertext_hex, nonce_hex, tag_hex, execMode):
    if execMode == "DEV":
        hex_key = os.environ["HEX_KEY"] 
    else:
        hex_key = ""

    key = bytes.fromhex(hex_key)
    ciphertext = bytes.fromhex(ciphertext_hex)
    nonce = bytes.fromhex(nonce_hex)
    tag = bytes.fromhex(tag_hex)

    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(nonce, tag),
        backend=default_backend()
    ).decryptor()

    try:
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    except Exception as e:
        print(e)
        return False
    
    return plaintext.decode("utf-8")


# Function to record the log end of an action
def record_log(params, status_code, resptext, resp, billerHitTime, billerRespTime, startTime, endTime):
    return True


app = FastAPI()

# Container holding data and behaviour will be used for request
class BPJSTKInquiry(BaseModel):
    inquiry_id : str
    customer_id : str
    product_code : str
    payment_period : str
    authorization: str
    authorizationNonce: str
    authorizationTag: str



#  POST endpoint
@app.post("/inquiryBillBPJSTK")
def inquiryBillBPJSTK(params: BPJSTKInquiry):               # Function to start inquiry bill
    api_start = str(datetime.now())                          # function to check the time when the api post started

# Verify that the request came from an authorized client uses the function of def decrypt_Auth(ciphertext_hex, nonce_hex, tag_hex, execMode):
    try:
        decrypted_inquiry_id = decrypt_Auth(params.authorization, params.authorizationNonce, params.authorizationTag, "DEV")
    except Exception as e:
        resp = {"status": "03A", "message": "Wrong cryptographic parameters"} #If the cryptographic data can be decrypted at all
        record_log(str(params), None, None, resp, None, None, api_start, str(datetime.now()))
        return JSONResponse(content=resp, status_code=status.HTTP_401_UNAUTHORIZED)
    
    # Check if the decrypted value is correct
    if decrypted_inquiry_id != params.inquiry_id:
        resp = {"status": "03B", "message": "Unauthorized"}
        record_log(str(params), None, None, resp, None, None, api_start, str(datetime.now()))
        return JSONResponse(content=resp, status_code=status.HTTP_401_UNAUTHORIZED)
    
    # Data payload send from the mobile api to this fastapi
    payload ={
        "customer_id": params.customer_id,
        "product_code": params.product_code,
        "payment_period": params.payment_period
    }

    # SEND REQUEST TO BILLER
    # Start timer for sending the request to the biller 
    start_hit_time = datetime.now()

    # using proxies since server need specific http
    try:
        proxies = {
            "http": "http://34.56.189.54:3128",
            "https": "http://34.56.189.54:3128",
        }
        # Send http post request to the biller , Response = -> is saving the biler reponse
        response = requests.post(
            API_URL,
            json=payload,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            timeout=20,
            proxies=proxies,
        )
    # Return message if the post does happen to timeout
    except requests.Timeout:
        resp = {"status": "05", "amount": 0, "message": "Timeout from biller"}
        timeout_time = datetime.now()
        record_log(str(params), 408, None, resp, str(start_hit_time), str(timeout_time), api_start, str(timeout_time))
        return JSONResponse(content=resp, status_code=status.HTTP_408_REQUEST_TIMEOUT)
    
    # Return message if the post cant connect to the biller / server didnt reply correctly
    except requests.exceptions.ProxyError:
        resp = {"status": "06", "amount": 0, "message": "Proxy error when connecting to biller"}
        proxy_error_time = datetime.now()
        record_log(str(params), None, None, resp, str(start_hit_time), str(proxy_error_time), api_start, str(proxy_error_time))
        return JSONResponse(content=resp, status_code=status.HTTP_502_BAD_GATEWAY)
    
    # Return message if an error did occur on the server
    except Exception as e:
        resp = {"status": "99", "amount": 0, "message": "Unknown error when connecting to biller"}
        error_time = datetime.now()
        record_log(str(params), None, str(e), resp, str(start_hit_time), str(error_time), api_start, str(error_time))
        return JSONResponse(content=resp, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # End timer of the request done being processed
    end_hit_time = datetime.now()

    # Return message if the response code that was received isnt 200
    if response.status_code != 200:
        resp = {"status": "01", "amount": 0, "message": "problem in connecting to biller"}
        record_log(str(params), response.status_code, response.text, resp, str(start_hit_time), str(end_hit_time), api_start, str(datetime.now()))
        return JSONResponse(content=resp, status_code=status.HTTP_400_BAD_REQUEST)
    
    #Return data showing the amount and customer name
    amt_to_be_paid = int(response.json().get("price"))
    customer_name = response.json().get("data", {}).get("account", {}).get("name")
    reference_number = response.json().get("reference_number")
    resp = {
        "status": "00", 
        "message": "inquiry successful",
        "amount": amt_to_be_paid,
        "customer Name": customer_name,
        "reference number" : reference_number
        }
    api_End = datetime.now()
    record_log(str(params), response.status_code, response.text, resp, str(start_hit_time), str(end_hit_time), api_start, api_End)
    return JSONResponse(content=resp, status_code=status.HTTP_200_OK)


# To run the internal api testing
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
