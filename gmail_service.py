import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import base64


# --------------------------------------------------
# GOOGLE GMAIL CONFIGURATION
# --------------------------------------------------

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly"
]


# --------------------------------------------------
# GOOGLE OAUTH CONFIGURATION
# --------------------------------------------------

def get_google_client_config():

    return {
        "web": {
            "client_id": st.secrets["GOOGLE_CLIENT_ID"],
            "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": (
                "https://www.googleapis.com/oauth2/v1/certs"
            ),
            "redirect_uris": [
                st.secrets["REDIRECT_URI"]
            ]
        }
    }


# --------------------------------------------------
# GET REDIRECT URI
# --------------------------------------------------

def get_redirect_uri():

    return st.secrets["REDIRECT_URI"]


# --------------------------------------------------
# CREATE GOOGLE AUTHORIZATION URL
# --------------------------------------------------

def get_auth_url():

    flow = Flow.from_client_config(
        get_google_client_config(),
        scopes=SCOPES,
        redirect_uri=get_redirect_uri()
    )

    # Generate PKCE verifier
    code_verifier = (
        base64.urlsafe_b64encode(
            __import__("secrets").token_bytes(32)
        )
        .decode("utf-8")
        .rstrip("=")
    )

    st.session_state.oauth_code_verifier = code_verifier

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        code_challenge_method="S256",
        code_verifier=code_verifier
    )

    return authorization_url, state


# --------------------------------------------------
# CREATE GMAIL SERVICE
# --------------------------------------------------

def get_gmail_service(code, state):

    code_verifier = st.session_state.get(
        "oauth_code_verifier"
    )

    if not code_verifier:

        raise Exception(
            "OAuth code verifier is missing. "
            "Please click Connect Gmail again."
        )

    flow = Flow.from_client_config(
        get_google_client_config(),
        scopes=SCOPES,
        state=state,
        redirect_uri=get_redirect_uri()
    )

    flow.fetch_token(
        code=code,
        code_verifier=code_verifier
    )

    credentials = flow.credentials

    service = build(
        "gmail",
        "v1",
        credentials=credentials
    )

    # Remove verifier after successful authentication
    st.session_state.oauth_code_verifier = None

    return service


# --------------------------------------------------
# GET EMAIL LIST
# --------------------------------------------------

def get_messages(
    service,
    max_results=20
):

    response = (
        service.users()
        .messages()
        .list(
            userId="me",
            maxResults=max_results
        )
        .execute()
    )

    return response.get(
        "messages",
        []
    )


# --------------------------------------------------
# GET COMPLETE EMAIL
# --------------------------------------------------

def get_message_details(
    service,
    message_id
):

    response = (
        service.users()
        .messages()
        .get(
            userId="me",
            id=message_id,
            format="full"
        )
        .execute()
    )

    return response


# --------------------------------------------------
# DECODE EMAIL BODY
# --------------------------------------------------

def decode_body(data):

    if not data:
        return ""

    try:

        decoded = base64.urlsafe_b64decode(
            data
        )

        return decoded.decode(
            "utf-8",
            errors="ignore"
        )

    except Exception:

        return ""


# --------------------------------------------------
# EXTRACT EMAIL BODY
# --------------------------------------------------

def extract_email_body(payload):

    body_data = (
        payload
        .get("body", {})
        .get("data")
    )

    if body_data:

        return decode_body(
            body_data
        )

    parts = payload.get(
        "parts",
        []
    )

    # Look for text/plain
    for part in parts:

        mime_type = part.get(
            "mimeType",
            ""
        )

        if mime_type == "text/plain":

            data = (
                part
                .get("body", {})
                .get("data")
            )

            if data:

                return decode_body(
                    data
                )

    # Search nested parts
    for part in parts:

        if "parts" in part:

            nested_body = extract_email_body(
                part
            )

            if nested_body:

                return nested_body

    return ""


# --------------------------------------------------
# FINANCIAL KEYWORDS
# --------------------------------------------------

FINANCIAL_KEYWORDS = [

    "payment",
    "paid",
    "purchase",
    "order",
    "receipt",
    "invoice",
    "transaction",
    "subscription",
    "bill",
    "refund",
    "cashback",
    "debit",
    "charged",
    "amount",
    "spent",
    "emi",
    "upi",
    "bank",
    "credit"
]


# --------------------------------------------------
# FINANCIAL CONTEXT
# --------------------------------------------------

FINANCIAL_CONTEXT_KEYWORDS = [

    "rs",
    "inr",
    "₹",
    "usd",
    "$",
    "total",
    "price",
    "cost",
    "payment",
    "transaction",
    "charged",
    "debit",
    "paid",
    "purchase",
    "order total",
    "amount",
    "merchant",
    "invoice",
    "refund",
    "subscription"
]


# --------------------------------------------------
# EXCLUSION KEYWORDS
# --------------------------------------------------

EXCLUSION_KEYWORDS = [

    "job openings",
    "job alert",
    "jobs for you",
    "career",
    "hiring",
    "recruitment",
    "newsletter",
    "weekly update",
    "valued member",
    "community",
    "welcome",
    "unsubscribe",
    "linkedin",
    "job opportunity",
    "career opportunity"
]


# --------------------------------------------------
# FINANCIAL EMAIL DETECTION
# --------------------------------------------------

def is_financial_email(
    subject,
    sender,
    body
):

    subject_text = (
        subject or ""
    ).lower()

    sender_text = (
        sender or ""
    ).lower()

    body_text = (
        body or ""
    ).lower()

    full_text = (
        subject_text
        + " "
        + sender_text
        + " "
        + body_text
    )

    # Remove obvious non-financial emails
    for keyword in EXCLUSION_KEYWORDS:

        if keyword in full_text:

            return False

    # Check financial keyword
    financial_match = False

    for keyword in FINANCIAL_KEYWORDS:

        if keyword in full_text:

            financial_match = True

            break

    if not financial_match:

        return False

    # Check financial context
    context_match = False

    for keyword in FINANCIAL_CONTEXT_KEYWORDS:

        if keyword in full_text:

            context_match = True

            break

    if context_match:

        return True

    return False
