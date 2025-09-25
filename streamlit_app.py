import streamlit as st

def calculate_scottish_tax(salary):
    """
    Calculates the Scottish income tax for the 2025-2026 tax year.

    Args:
        salary (float): The annual gross salary.

    Returns:
        tuple: A tuple containing the total tax due and a dictionary
               with the tax breakdown by band.
    """
    
    # Define the tax bands and rates for 2025-2026
    tax_bands = [
        (15397, 0.19),  # Starter rate: £12,571 - £15,397
        (27491, 0.20),  # Basic rate: £15,398 - £27,491
        (43662, 0.21),  # Intermediate rate: £27,492 - £43,662
        (75000, 0.42),  # Higher rate: £43,663 - £75,000
        (125140, 0.45) # Advanced rate: £75,001 - £125,140
    ]
    top_rate = 0.48 # Top rate: Above £125,140

    # Calculate the personal allowance. It's reduced by £1 for every £2 over £100,000
    if salary > 125140:
        personal_allowance = 0
    elif salary > 100000:
        personal_allowance = 12570 - ((salary - 100000) / 2)
    else:
        personal_allowance = 12570

    taxable_income = salary - personal_allowance
    total_tax = 0.0
    tax_breakdown = {}
    
    previous_band_limit = 0
    
    # Calculate tax for each band
    for band_limit, rate in tax_bands:
        if taxable_income > previous_band_limit:
            # The amount of income in the current band
            taxable_in_band = min(taxable_income, band_limit) - previous_band_limit
            tax_for_band = taxable_in_band * rate
            total_tax += tax_for_band
            tax_breakdown[f"£{previous_band_limit+1:,} - £{band_limit:,}"] = f"£{taxable_in_band:,.2f} @ {int(rate*100)}% = £{tax_for_band:,.2f}"
            previous_band_limit = band_limit
        else:
            break

    # Calculate tax for the top rate band
    if taxable_income > previous_band_limit:
        taxable_in_top_band = taxable_income - previous_band_limit
        tax_for_top_band = taxable_in_top_band * top_rate
        total_tax += tax_for_top_band
        tax_breakdown[f"Above £{previous_band_limit:,}"] = f"£{taxable_in_top_band:,.2f} @ {int(top_rate*100)}% = £{tax_for_top_band:,.2f}"
        
    return total_tax, tax_breakdown

# Streamlit App
st.title("Scottish Income Tax Calculator (2025-2026)")
st.write("Enter your annual salary to calculate your estimated Scottish income tax.")

# Get salary input from the user
salary = st.number_input("Annual Salary (£)", min_value=0.0, step=1000.0)

# Button to trigger the calculation
if st.button("Calculate Tax"):
    if salary == 0:
        st.warning("Please enter a salary to calculate the tax.")
    else:
        total_tax_due, breakdown = calculate_scottish_tax(salary)
        
        # Display the results
        st.header("Tax Calculation Summary")
        st.write(f"**Annual Salary:** £{salary:,.2f}")

        # Personal Allowance Calculation based on salary
        personal_allowance = 12570
        if salary > 100000 and salary <= 125140:
            personal_allowance = 12570 - ((salary - 100000) / 2)
        elif salary > 125140:
            personal_allowance = 0

        st.write(f"**Personal Allowance:** £{personal_allowance:,.2f}")
        st.write(f"**Taxable Income:** £{salary - personal_allowance:,.2f}")
        
        st.subheader("Breakdown by Tax Band")
        for band, details in breakdown.items():
            st.write(f"**Band {band}:** {details}")

        st.markdown("---")
        st.success(f"**Total Scottish Income Tax due:** £{total_tax_due:,.2f}")
        st.info(f"**Take-home pay (pre-NI):** £{salary - total_tax_due:,.2f}")
