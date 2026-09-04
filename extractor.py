import os
import json

from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel


# ==================================================
# LOAD ENVIRONMENT VARIABLES
# ==================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not found in the .env file."
    )


# ==================================================
# GROQ CLIENT
# ==================================================

client = Groq(
    api_key=GROQ_API_KEY
)


# ==================================================
# PYDANTIC TRANSACTION MODEL
# ==================================================

class Transaction(BaseModel):

    is_transaction: bool
    merchant: str
    amount: float
    currency: str
    category: str
    transaction_type: str
    transaction_date: str


# ==================================================
# TRANSACTION JSON SCHEMA
# ==================================================

TRANSACTION_SCHEMA = {

    "type": "object",

    "properties": {

        "is_transaction": {
            "type": "boolean"
        },

        "merchant": {
            "type": "string"
        },

        "amount": {
            "type": "number"
        },

        "currency": {
            "type": "string"
        },

        "category": {
            "type": "string"
        },

        "transaction_type": {
            "type": "string"
        },

        "transaction_date": {
            "type": "string"
        }

    },

    "required": [
        "is_transaction",
        "merchant",
        "amount",
        "currency",
        "category",
        "transaction_type",
        "transaction_date"
    ],

    "additionalProperties": False
}


# ==================================================
# EXTRACT TRANSACTION
# ==================================================

def extract_transaction(
    subject,
    sender,
    date,
    body
):

    prompt = f"""
You are a financial transaction extraction system.

Analyze the following Gmail email.

Determine whether it represents an actual financial
transaction.

EMAIL SUBJECT:
{subject}

EMAIL SENDER:
{sender}

EMAIL DATE:
{date}

EMAIL BODY:
{body}


EXTRACTION RULES:

1. Set is_transaction to true only if the email
   represents an actual financial activity such as:

   - Payment
   - Purchase
   - Subscription
   - Bill
   - Refund
   - Cashback
   - Charge
   - Debit


2. Do NOT treat promotional emails, advertisements,
   newsletters, job alerts, or general notifications
   as transactions.


3. Never invent an amount.

4. If an actual transaction amount is present,
   extract it accurately.


5. Convert Indian Rupee symbols such as ₹ and Rs
   into currency "INR".


6. Use the merchant/company that actually received
   or issued the payment.

   Example:

   Swiggy payment → merchant = "Swiggy"

7. Choose a suitable category such as:

   Food
   Shopping
   Travel
   Entertainment
   Utilities
   Subscription
   Healthcare
   Education
   Electronics
   Other


8. Choose a suitable transaction type such as:

   Payment
   Purchase
   Subscription
   Refund
   Bill
   Cashback
   Charge


9. If a transaction date is explicitly mentioned,
   use that date.


10. If the transaction date is not explicitly
    mentioned, use the email date.


11. For an email that is NOT an actual transaction,
    return:

    is_transaction = false
    merchant = ""
    amount = 0
    currency = ""
    category = ""
    transaction_type = ""
    transaction_date = ""


12. Return only the structured JSON response.
"""


    # ==================================================
    # GROQ API CALL
    # ==================================================

    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0,

        reasoning_format="hidden",

        response_format={
            "type": "json_schema",

            "json_schema": {

                "name": "transaction_extraction",

                "strict": True,

                "schema": TRANSACTION_SCHEMA
            }
        }
    )


    # ==================================================
    # GET GROQ RESPONSE
    # ==================================================

    content = response.choices[0].message.content

    if not content:
        raise ValueError(
            "Groq returned an empty response."
        )


    # ==================================================
    # PARSE JSON
    # ==================================================

    try:

        data = json.loads(content)

    except json.JSONDecodeError as e:

        raise ValueError(
            f"Could not parse Groq response as JSON.\n"
            f"Response: {content}"
        ) from e


    # ==================================================
    # PYDANTIC VALIDATION
    # ==================================================

    try:

        transaction = Transaction.model_validate(
            data
        )

    except Exception as e:

        raise ValueError(
            f"Transaction validation failed.\n"
            f"Data returned by Groq: {data}\n"
            f"Error: {e}"
        ) from e


    return transaction