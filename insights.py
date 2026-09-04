import pandas as pd


# =========================================================
# AI SPENDING INSIGHTS
# =========================================================

def generate_spending_insights(
    df,
    recurring_df=None
):
    """
    Generate useful spending insights from transaction data.
    """

    insights = []

    if df.empty:
        return insights

    # Make sure amount is numeric
    df = df.copy()

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["amount"]
    )

    if df.empty:
        return insights

    # =====================================================
    # 1. TOTAL SPENDING
    # =====================================================

    total = df["amount"].sum()

    insights.append(
        f"Your total spending is ₹{total:,.2f}."
    )

    # =====================================================
    # 2. HIGHEST SPENDING CATEGORY
    # =====================================================

    if "category" in df.columns:

        category_spending = (
            df.groupby("category")["amount"]
            .sum()
            .sort_values(ascending=False)
        )

        if not category_spending.empty:

            top_category = category_spending.index[0]
            top_category_amount = category_spending.iloc[0]

            percentage = (
                top_category_amount / total
            ) * 100

            insights.append(
                f"Your highest spending category is "
                f"{top_category}, with ₹{top_category_amount:,.2f} "
                f"({percentage:.1f}% of total spending)."
            )

    # =====================================================
    # 3. HIGHEST SPENDING MERCHANT
    # =====================================================

    if "merchant" in df.columns:

        merchant_spending = (
            df.groupby("merchant")["amount"]
            .sum()
            .sort_values(ascending=False)
        )

        if not merchant_spending.empty:

            top_merchant = merchant_spending.index[0]
            top_merchant_amount = merchant_spending.iloc[0]

            insights.append(
                f"Your highest spending merchant is "
                f"{top_merchant}, with total spending of "
                f"₹{top_merchant_amount:,.2f}."
            )

    # =====================================================
    # 4. LARGE TRANSACTIONS
    # =====================================================

    average_amount = df["amount"].mean()

    large_transactions = df[
        df["amount"] > average_amount * 2
    ]

    if not large_transactions.empty:

        largest = large_transactions.sort_values(
            "amount",
            ascending=False
        ).iloc[0]

        insights.append(
            f"You have a high-value transaction of "
            f"₹{largest['amount']:,.2f} at "
            f"{largest['merchant']}."
        )

    # =====================================================
    # 5. RECURRING PAYMENTS
    # =====================================================

    if recurring_df is not None:

        if not recurring_df.empty:

            recurring_count = len(recurring_df)

            insights.append(
                f"You have {recurring_count} recurring "
                f"payment(s) that may contribute to your "
                f"regular monthly expenses."
            )

    # =====================================================
    # 6. SPENDING RECOMMENDATION
    # =====================================================

    if "category" in df.columns:

        category_spending = (
            df.groupby("category")["amount"]
            .sum()
            .sort_values(ascending=False)
        )

        if not category_spending.empty:

            top_category = category_spending.index[0]

            insights.append(
                f"Consider reviewing your spending in the "
                f"{top_category} category to identify "
                f"possible savings."
            )

    return insights