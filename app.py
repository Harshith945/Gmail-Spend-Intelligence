import streamlit as st
import pandas as pd

from gmail_service import (
    get_auth_url,
    get_gmail_service,
    get_messages,
    get_message_details,
    extract_email_body,
    is_financial_email,
)

from extractor import extract_transaction

from analytics import (
    create_dataframe,
    total_spending,
    spending_by_category,
    spending_by_merchant,
    spending_over_time,
    identify_recurring_transactions,
    recurring_monthly_estimate,
)

from insights import (
    generate_spending_insights,
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Gmail Spend Intelligence",
    page_icon="💳",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("💳 Gmail Spend Intelligence")

st.write(
    "Turn your Gmail transaction emails into "
    "structured spending insights using AI."
)


# =========================================================
# SESSION STATE
# =========================================================

if "gmail_service" not in st.session_state:
    st.session_state.gmail_service = None

if "auth_state" not in st.session_state:
    st.session_state.auth_state = None

if "auth_url" not in st.session_state:
    st.session_state.auth_url = None

if "all_messages" not in st.session_state:
    st.session_state.all_messages = []

if "financial_emails" not in st.session_state:
    st.session_state.financial_emails = []

if "transactions" not in st.session_state:
    st.session_state.transactions = []


# =========================================================
# GOOGLE OAUTH CALLBACK
# =========================================================

if (
    "code" in st.query_params
    and st.session_state.gmail_service is None
):

    code = st.query_params["code"]

    try:

        service = get_gmail_service(
            code,
            st.session_state.auth_state
        )

        st.session_state.gmail_service = service
        st.session_state.auth_url = None

        st.query_params.clear()

        st.rerun()

    except Exception as e:

        st.error("Gmail authentication failed.")
        st.exception(e)


# =========================================================
# CONNECT GMAIL
# =========================================================

if st.session_state.gmail_service is None:

    st.header("🔐 Connect Gmail")

    st.write(
        "Connect your Gmail account using secure "
        "read-only access."
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.session_state.auth_url is None:

            if st.button(
                "🔐 Connect Gmail",
                type="primary"
            ):

                try:

                    auth_url, state = get_auth_url()

                    st.session_state.auth_url = auth_url
                    st.session_state.auth_state = state

                    st.rerun()

                except Exception as e:

                    st.error(
                        "Could not start Gmail authentication."
                    )

                    st.exception(e)

        else:

            st.write(
                "Click below to continue with Google."
            )

            st.link_button(
                "Continue with Google →",
                st.session_state.auth_url
            )

    with col2:

        st.subheader("🔒 Read-Only Access")

        st.write("✅ Read emails")
        st.write("✅ Analyze transaction emails")
        st.write("✅ Extract spending information")
        st.write("❌ Cannot send emails")
        st.write("❌ Cannot modify or delete emails")


# =========================================================
# CONNECTED
# =========================================================

else:

    st.success("✅ Gmail Connected")

    st.write(
        "Your Gmail account is connected with "
        "read-only access."
    )


    # =====================================================
    # FETCH EMAILS
    # =====================================================

    st.header("📥 Fetch Gmail Emails")

    max_results = st.slider(
        "Number of emails",
        min_value=5,
        max_value=100,
        value=20,
        step=5
    )

    if st.button(
        "📥 Fetch Emails",
        type="primary"
    ):

        try:

            with st.spinner(
                "Fetching emails..."
            ):

                messages = get_messages(
                    st.session_state.gmail_service,
                    max_results
                )

            st.session_state.all_messages = messages

            st.success(
                f"Fetched {len(messages)} emails."
            )

        except Exception as e:

            st.error(
                "Failed to fetch emails."
            )

            st.exception(e)


    # =====================================================
    # FINANCIAL EMAIL DETECTION
    # =====================================================

    if st.session_state.all_messages:

        st.header("🔎 Financial Email Detection")

        if st.button(
            "🔎 Detect Financial Emails"
        ):

            financial_emails = []

            progress = st.progress(0)

            total_messages = len(
                st.session_state.all_messages
            )

            for index, message in enumerate(
                st.session_state.all_messages
            ):

                try:

                    message_id = message["id"]

                    details = get_message_details(
                        st.session_state.gmail_service,
                        message_id
                    )

                    payload = details.get(
                        "payload",
                        {}
                    )

                    headers = payload.get(
                        "headers",
                        []
                    )

                    subject = ""
                    sender = ""
                    email_date = ""

                    for header in headers:

                        name = header.get(
                            "name",
                            ""
                        ).lower()

                        value = header.get(
                            "value",
                            ""
                        )

                        if name == "subject":

                            subject = value

                        elif name == "from":

                            sender = value

                        elif name == "date":

                            email_date = value


                    body = extract_email_body(
                        payload
                    )

                    if is_financial_email(
                        subject,
                        sender,
                        body
                    ):

                        financial_emails.append(
                            {
                                "id": message_id,
                                "subject": subject,
                                "sender": sender,
                                "date": email_date,
                                "body": body
                            }
                        )

                except Exception as e:

                    st.warning(
                        f"Could not process email: {e}"
                    )

                progress.progress(
                    (index + 1) / total_messages
                )

            st.session_state.financial_emails = (
                financial_emails
            )

            st.success(
                f"💰 Financial Emails Found: "
                f"{len(financial_emails)}"
            )


    # =====================================================
    # SHOW FINANCIAL EMAILS
    # =====================================================

    if st.session_state.financial_emails:

        st.header("💳 Financial Emails")

        for email in st.session_state.financial_emails:

            subject = email["subject"]

            if not subject:
                subject = "No Subject"

            with st.expander(
                f"📧 {subject}"
            ):

                st.write(
                    f"**From:** {email['sender']}"
                )

                st.write(
                    f"**Date:** {email['date']}"
                )

                st.write(
                    email["body"][:3000]
                )


    # =====================================================
    # AI TRANSACTION EXTRACTION
    # =====================================================

    if st.session_state.financial_emails:

        st.header("🤖 AI Transaction Extraction")

        st.write(
            "Groq converts unstructured email content "
            "into validated transaction data."
        )

        if st.button(
            "🤖 Extract Transactions"
        ):

            transactions = []

            progress = st.progress(0)

            total_emails = len(
                st.session_state.financial_emails
            )

            for index, email in enumerate(
                st.session_state.financial_emails
            ):

                try:

                    transaction = extract_transaction(
                        subject=email["subject"],
                        sender=email["sender"],
                        date=email["date"],
                        body=email["body"]
                    )

                    if transaction.is_transaction:

                        transactions.append(
                            transaction.model_dump()
                        )

                except Exception as e:

                    st.error(
                        f"Extraction failed: "
                        f"{email['subject']}"
                    )

                    st.code(
                        str(e)
                    )

                progress.progress(
                    (index + 1) / total_emails
                )

            st.session_state.transactions = (
                transactions
            )

            if transactions:

                st.success(
                    f"✅ Extracted "
                    f"{len(transactions)} transactions."
                )

            else:

                st.warning(
                    "No valid transactions were extracted."
                )


    # =====================================================
    # SPENDING ANALYTICS
    # =====================================================

    if st.session_state.transactions:

        st.divider()

        st.header("📊 Spending Intelligence")

        # -------------------------------------------------
        # CREATE DATAFRAME
        # -------------------------------------------------

        df = create_dataframe(
            st.session_state.transactions
        )


        # -------------------------------------------------
        # CALCULATIONS
        # -------------------------------------------------

        total = total_spending(df)

        category_data = spending_by_category(df)

        merchant_data = spending_by_merchant(df)

        time_data = spending_over_time(df)


        # =================================================
        # MAIN METRICS
        # =================================================

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Transactions",
                len(df)
            )

        with col2:

            st.metric(
                "Total Spending",
                f"₹{total:,.2f}"
            )

        with col3:

            st.metric(
                "Categories",
                df["category"].nunique()
            )


        # =================================================
        # CATEGORY ANALYSIS
        # =================================================

        st.subheader(
            "📂 Highest-Spend Categories"
        )

        if not category_data.empty:

            st.dataframe(
                category_data,
                use_container_width=True,
                hide_index=True
            )

            st.bar_chart(
                category_data.set_index(
                    "category"
                )
            )

        else:

            st.info(
                "No category data available."
            )


        # =================================================
        # MERCHANT ANALYSIS
        # =================================================

        st.subheader(
            "🏪 Highest-Spend Merchants"
        )

        if not merchant_data.empty:

            st.dataframe(
                merchant_data,
                use_container_width=True,
                hide_index=True
            )

            st.bar_chart(
                merchant_data.set_index(
                    "merchant"
                )
            )

        else:

            st.info(
                "No merchant data available."
            )


        # =================================================
        # SPENDING OVER TIME
        # =================================================

        st.subheader(
            "📅 Spending Over Time"
        )

        if not time_data.empty:

            st.line_chart(
                time_data.set_index(
                    "month"
                )
            )

            st.dataframe(
                time_data,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "Not enough date information "
                "to show spending over time."
            )


        # =================================================
        # TRANSACTION DATA
        # =================================================

        st.subheader(
            "💳 Transaction Data"
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


        # =================================================
        # TRANSACTION DETAILS
        # =================================================

        st.subheader(
            "🔍 Transaction Details"
        )

        for transaction in (
            st.session_state.transactions
        ):

            merchant = transaction.get(
                "merchant",
                "Unknown"
            )

            amount = transaction.get(
                "amount",
                0
            )

            currency = transaction.get(
                "currency",
                "INR"
            )

            category = transaction.get(
                "category",
                "Other"
            )

            transaction_type = transaction.get(
                "transaction_type",
                ""
            )

            transaction_date = transaction.get(
                "transaction_date",
                ""
            )

            with st.expander(
                f"{merchant} - "
                f"{currency} {amount}"
            ):

                st.write(
                    f"**Merchant:** {merchant}"
                )

                st.write(
                    f"**Amount:** "
                    f"{currency} {amount}"
                )

                st.write(
                    f"**Category:** {category}"
                )

                st.write(
                    f"**Type:** {transaction_type}"
                )

                st.write(
                    f"**Date:** {transaction_date}"
                )


        # =================================================
        # RECURRING TRANSACTIONS
        # =================================================

        st.divider()

        st.header("🔄 Recurring Transactions")

        st.write(
            "Identify subscriptions and repeated payments "
            "based on merchant, amount, and transaction frequency."
        )


        # -------------------------------------------------
        # IDENTIFY RECURRING TRANSACTIONS
        # -------------------------------------------------

        recurring_data = identify_recurring_transactions(
            df
        )


        if not recurring_data.empty:

            # -------------------------------------------------
            # RECURRING METRICS
            # -------------------------------------------------

            monthly_estimate = (
                recurring_monthly_estimate(
                    recurring_data
                )
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Recurring Payments",
                    len(recurring_data)
                )

            with col2:

                st.metric(
                    "Estimated Monthly Recurring",
                    f"₹{monthly_estimate:,.2f}"
                )

            with col3:

                st.metric(
                    "Recurring Merchants",
                    recurring_data[
                        "merchant"
                    ].nunique()
                )


            # -------------------------------------------------
            # RECURRING TRANSACTION TABLE
            # -------------------------------------------------

            st.subheader(
                "🔄 Detected Recurring Payments"
            )

            display_recurring = recurring_data.copy()

            display_recurring[
                "last_transaction"
            ] = pd.to_datetime(
                display_recurring[
                    "last_transaction"
                ]
            ).dt.strftime(
                "%Y-%m-%d"
            )

            st.dataframe(
                display_recurring,
                use_container_width=True,
                hide_index=True
            )


            # -------------------------------------------------
            # RECURRING PAYMENT DETAILS
            # -------------------------------------------------

            st.subheader(
                "📋 Recurring Payment Details"
            )

            for _, row in recurring_data.iterrows():

                merchant = row["merchant"]

                amount = row["amount"]

                frequency = row["frequency"]

                occurrences = row["occurrences"]

                interval = row[
                    "average_interval_days"
                ]

                last_transaction = row[
                    "last_transaction"
                ]

                with st.expander(
                    f"🔄 {merchant} — ₹{amount:,.2f}"
                ):

                    st.write(
                        f"**Merchant:** {merchant}"
                    )

                    st.write(
                        f"**Amount:** ₹{amount:,.2f}"
                    )

                    st.write(
                        f"**Frequency:** {frequency}"
                    )

                    st.write(
                        f"**Occurrences:** {occurrences}"
                    )

                    st.write(
                        f"**Average interval:** "
                        f"{interval} days"
                    )

                    st.write(
                        f"**Last transaction:** "
                        f"{last_transaction.strftime('%Y-%m-%d')}"
                    )

        else:

            st.info(
                "🔎 No recurring transactions detected yet."
            )

            st.write(
                "Recurring payments require at least "
                "two transactions from the same merchant "
                "with similar amounts."
            )


        # =================================================
        # AI SPENDING INSIGHTS
        # =================================================

        st.divider()

        st.header("🤖 AI Spending Insights")

        st.write(
            "Get intelligent insights and recommendations "
            "from your spending patterns."
        )


        # -------------------------------------------------
        # GENERATE INSIGHTS
        # -------------------------------------------------

        insights = generate_spending_insights(
            df,
            recurring_data
        )


        # -------------------------------------------------
        # DISPLAY INSIGHTS
        # -------------------------------------------------

        if insights:

            for insight in insights:

                st.info(
                    f"💡 {insight}"
                )

        else:

            st.info(
                "Not enough transaction data "
                "to generate insights."
            )