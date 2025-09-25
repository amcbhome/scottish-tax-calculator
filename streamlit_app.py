import streamlit as st

# A dictionary to store tax rates and bands for different tax years.
tax_data = {
    "2025-2026": {
        "personal_allowance": 12570,
        "allowance_threshold": 100000,
        "tax_bands": [
            (15397, 0.19),  # Starter rate
            (27491, 0.20),  # Basic rate
            (43662, 0.21),  # Intermediate rate
            (75000, 0.42),  # Higher rate
            (125140, 0.45) # Advanced rate
        ],
        "top_rate": 0.48,
    }
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

    # Calculate the effective personal allowance.
    effective_personal_allowance = personal_allowance
    if salary > 125140:
        effective_personal_allowance = 0
    elif salary > allowance_threshold:
        effective_personal_allowance = personal_allowance - ((salary - allowance_threshold) / 2)
    
    taxable_income = max(0, salary - effective_personal_allowance)
    total_tax = 0.0
    tax_breakdown = {}
    
    # Correctly handle the progressive tax bands
    previous_band_limit = 0
    
    for band_limit, rate in tax_bands:
        if taxable_income > previous_band_limit:
            # The amount of income in the current band is the minimum of
            # the remaining taxable income or the width of the band.
            band_width = band_limit - previous_band_limit
            taxable_in_band = min(taxable_income - previous_band_limit, band_width)
            
            tax_for_band = round(taxable_in_band * rate, 2)
            total_tax += tax_for_band
            tax_breakdown[f"£{previous_band_limit + effective_personal_allowance + 1:,} - £{band_limit + effective_personal_allowance:,}"] = f"£{taxable_in_band:,.2f} @ {int(rate*100)}% = £{tax_for_band:,.2f}"
            
            previous_band_limit = band_limit
        else:
            break

    # Calculate tax for the top rate band
    if taxable_income > previous_band_limit:
        taxable_in_top_band = taxable_income - previous_band_limit
        tax_for_top_band = round(taxable_in_top_band * top_rate, 2)
        total_tax += tax_for_top_band
        tax_breakdown[f"Above £{previous_band_limit + effective_personal_allowance:,}"] = f"£{taxable_in_top_band:,.2f} @ {int(top_rate*100)}% = £{tax_for_top_band:,.2f}"
        
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

        effective_personal_allowance = selected_tax_data["personal_allowance"]
        if salary > selected_tax_data["allowance_threshold"] and salary <= 125140:
            effective_personal_allowance = effective_personal_allowance - ((salary - selected_tax_data["allowance_threshold"]) / 2)
        elif salary > 125140:
            effective_personal_allowance = 0

        st.write(f"**Personal Allowance:** £{effective_personal_allowance:,.2f}")
        st.write(f"**Taxable Income:** £{max(0, salary - effective_personal_allowance):,.2f}")
        
        st.subheader("Breakdown by Tax Band")
        if breakdown:
            for band, details in breakdown.items():
                st.write(f"**Band {band}:** {details}")
        else:
            st.write("No tax due.")

        st.markdown("---")
        st.success(f"**Total Scottish Income Tax due:** £{total_tax_due:,.2f}")
        st.info(f"**Take-home pay (pre-NI):** £{salary - total_tax_due:,.2f}")
