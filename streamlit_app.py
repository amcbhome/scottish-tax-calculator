import streamlit as st

# A dictionary to store tax rates and bands for different tax years.
# This makes it easy to update for new tax years.
tax_data = {
    "2025-2026": {
        "personal_allowance": 12570,
        "allowance_threshold": 100000,
        "tax_bands": [
            (15397, 0.19),  # Starter rate: £12,571 - £15,397
            (27491, 0.20),  # Basic rate: £15,398 - £27,491
            (43662, 0.21),  # Intermediate rate: £27,492 - £43,662
            (75000, 0.42),  # Higher rate: £43,663 - £75,000
            (125140, 0.45) # Advanced rate: £75,001 - £125,140
        ],
        "top_rate": 0.48,
    }
    # Add new tax years here as they are announced
    # Example:
    # "2026-2027": { ... }
}

def calculate_scottish_tax(salary, tax_year_data):
    """
    Calculates the Scottish income tax for a specified tax year.

    Args:
        salary (float): The annual gross salary.
        tax_year_data (dict): A dictionary containing the tax rates and bands for a specific year.

    Returns:
        tuple: A tuple containing the total tax due and a dictionary
               with the tax breakdown by band.
    """
    personal_allowance = tax_year_data["personal_allowance"]
    allowance_threshold = tax_year_data["allowance_threshold"]
    tax_bands = tax_year_data["tax_bands"]
    top_rate = tax_year_data["top_rate"]

    # Calculate the personal allowance.
    if salary > 125140:
        personal_allowance = 0
    elif salary > allowance_threshold:
        personal_allowance = personal_allowance - ((salary - allowance_threshold) / 2)
    
    taxable_income = salary - personal_allowance
    total_tax = 0.0
    tax_breakdown = {}
    
    # Correctly initialize the previous band limit to the personal allowance
    previous_band_limit = personal_allowance
    
    # The first band's lower limit is the personal allowance
    first_tax_band_limit = tax_bands[0][0]
    first_tax_rate = tax_bands[0][1]
    
    if taxable_income > 0:
        taxable_in_first_band = min(taxable_income, first_tax_band_limit - personal_allowance)
        tax_for_first_band = taxable_in_first_band * first_tax_rate
        total_tax += tax_for_first_band
        tax_breakdown[f"£{personal_allowance + 1:,} - £{first_tax_band_limit:,}"] = f"£{taxable_in_first_band:,.2f} @ {int(first_tax_rate*100)}% = £{tax_for_first_band:,.2f}"

    # Calculate tax for the remaining bands
    previous_band_limit = first_tax_band_limit
    
    for band_limit, rate in tax_bands[1:]:
        if taxable_income > previous_band_limit - personal_allowance:
            # The amount of income in the current band
            taxable_in_band = min(taxable_income, band_limit - personal_allowance) - (previous_band_limit - personal_allowance)
            tax_for_band = taxable_in_band * rate
            total_tax += tax_for_band
            tax_breakdown[f"£{previous_band_limit+1:,} - £{band_limit:,}"] = f"£{taxable_in_band:,.2f} @ {int(rate*100)}% = £{tax_for_band:,.2f}"
            previous_band_limit = band_limit
        else:
            break

    # Calculate tax for the top rate band
    if taxable_income > previous_band_limit - personal_allowance:
        taxable_in_top_band = taxable_income - (previous_band_limit - personal_allowance)
        tax_for_top_band = taxable_in_top_band * top_rate
        total_tax += tax_for_top_band
        tax_breakdown[f"Above £{previous_band_limit:,}"] = f"£{taxable_in_top_band:,.2f} @ {int(top_rate*100)}% = £{tax_for_top_band:,.2f}"
        
    return total_tax, tax_breakdown

# Streamlit App
st.title("Scottish Income Tax Calculator")
st.write("Calculate your estimated Scottish income tax for various tax years.")

# User selects the tax year
tax_year = st.selectbox("Select Tax Year", list(tax_data.keys()))

# Get salary input from the user
salary = st.number_input("Annual Salary (£)", min_value=0.0, step=1000.0)

# Button to trigger the calculation
if st.button("Calculate Tax"):
    if salary == 0:
        st.warning("Please enter a salary to calculate the tax.")
    else:
        selected_tax_data = tax_data[tax_year]
        total_tax_due, breakdown = calculate_scottish_tax(salary, selected_tax_data)
        
        st.header(f"Tax Calculation Summary for {tax_year}")
        st.write(f"**Annual Salary:** £{salary:,.2f}")

        personal_allowance = selected_tax_data["personal_allowance"]
        if salary > selected_tax_data["allowance_threshold"] and salary <= 125140:
            personal_allowance = personal_allowance - ((salary - selected_tax_data["allowance_threshold"]) / 2)
        elif salary > 125140:
            personal_allowance = 0

        st.write(f"**Personal Allowance:** £{personal_allowance:,.2f}")
        st.write(f"**Taxable Income:** £{salary - personal_allowance:,.2f}")
        
        st.subheader("Breakdown by Tax Band")
        if breakdown:
            for band, details in breakdown.items():
                st.write(f"**Band {band}:** {details}")
        else:
            st.write("No tax due.")

        st.markdown("---")
        st.success(f"**Total Scottish Income Tax due:** £{total_tax_due:,.2f}")
        st.info(f"**Take-home pay (pre-NI):** £{salary - total_tax_due:,.2f}")
