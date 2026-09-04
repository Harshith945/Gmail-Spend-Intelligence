import pandas as pd


def create_dataframe(transactions):
    """
    Convert transaction list into a DataFrame.
    """

    df = pd.DataFrame(transactions)

    if df.empty:
        return df

    # Convert amount to number
    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    )

    # Convert date to datetime
    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"],
        errors="coerce"
    )

    return df


def total_spending(df):
    """
    Calculate total spending.
    """

    if df.empty:
        return 0

    return df["amount"].sum()


def spending_by_category(df):
    """
    Calculate spending for each category.
    """

    if df.empty:
        return pd.DataFrame()

    result = (
        df.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    return result


def spending_by_merchant(df):
    """
    Calculate spending for each merchant.
    """

    if df.empty:
        return pd.DataFrame()

    result = (
        df.groupby("merchant")["amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    return result


def spending_over_time(df):
    """
    Calculate spending month by month.
    """

    if df.empty:
        return pd.DataFrame()

    valid_dates = df.dropna(
        subset=["transaction_date"]
    ).copy()

    if valid_dates.empty:
        return pd.DataFrame()

    valid_dates["month"] = (
        valid_dates["transaction_date"]
        .dt.to_period("M")
        .astype(str)
    )

    result = (
        valid_dates.groupby("month")["amount"]
        .sum()
        .reset_index()
        .sort_values("month")
    )

    return result


# =========================================================
# RECURRING TRANSACTION ANALYSIS
# =========================================================

def identify_recurring_transactions(
    df,
    min_occurrences=2,
    date_tolerance_days=7
):
    """
    Identify potentially recurring transactions.

    A transaction is considered recurring when:
    - The same merchant appears multiple times
    - The amount is approximately the same
    - The transactions occur on different dates
    """

    if df.empty:
        return pd.DataFrame()

    required_columns = [
        "merchant",
        "amount",
        "transaction_date"
    ]

    for column in required_columns:

        if column not in df.columns:
            return pd.DataFrame()

    working_df = df.dropna(
        subset=[
            "merchant",
            "amount",
            "transaction_date"
        ]
    ).copy()

    if working_df.empty:
        return pd.DataFrame()

    working_df = working_df.sort_values(
        "transaction_date"
    )

    recurring_groups = []

    # Group by merchant
    for merchant, group in working_df.groupby(
        "merchant"
    ):

        if len(group) < min_occurrences:
            continue

        group = group.sort_values(
            "transaction_date"
        )

        # Compare transactions with similar amounts
        for amount, amount_group in group.groupby(
            "amount"
        ):

            if len(amount_group) < min_occurrences:
                continue

            dates = list(
                amount_group[
                    "transaction_date"
                ]
            )

            if len(dates) < min_occurrences:
                continue

            intervals = []

            for i in range(1, len(dates)):

                difference = (
                    dates[i] - dates[i - 1]
                ).days

                intervals.append(
                    difference
                )

            if not intervals:
                continue

            average_interval = (
                sum(intervals)
                / len(intervals)
            )

            # Determine frequency
            if 25 <= average_interval <= 35:

                frequency = "Monthly"

            elif 80 <= average_interval <= 100:

                frequency = "Quarterly"

            elif 350 <= average_interval <= 380:

                frequency = "Yearly"

            elif 6 <= average_interval <= 8:

                frequency = "Weekly"

            else:

                frequency = "Other"

            # Only consider reasonably consistent intervals
            consistent_intervals = [
                interval
                for interval in intervals
                if abs(
                    interval - average_interval
                ) <= date_tolerance_days
            ]

            if len(consistent_intervals) >= 1:

                recurring_groups.append(
                    {
                        "merchant": merchant,
                        "amount": amount,
                        "occurrences": len(
                            amount_group
                        ),
                        "average_interval_days": round(
                            average_interval,
                            1
                        ),
                        "frequency": frequency,
                        "last_transaction": dates[-1]
                    }
                )

    if not recurring_groups:
        return pd.DataFrame()

    result = pd.DataFrame(
        recurring_groups
    )

    result = result.sort_values(
        "amount",
        ascending=False
    )

    return result.reset_index(
        drop=True
    )


def recurring_monthly_estimate(
    recurring_df
):
    """
    Estimate monthly recurring spending.
    """

    if recurring_df.empty:
        return 0

    total = 0

    for _, row in recurring_df.iterrows():

        amount = row["amount"]
        frequency = row["frequency"]

        if frequency == "Weekly":

            monthly_amount = (
                amount * 52 / 12
            )

        elif frequency == "Monthly":

            monthly_amount = amount

        elif frequency == "Quarterly":

            monthly_amount = (
                amount / 3
            )

        elif frequency == "Yearly":

            monthly_amount = (
                amount / 12
            )

        else:

            monthly_amount = 0

        total += monthly_amount

    return total