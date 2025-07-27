import streamlit as st

def calculate_quote(qty, design_paid, commercial, packaging, keychain, discount_addons):
    if qty < 25:
        return "❌ Minimum order quantity is 25."

    # Determine discount rate
    if qty >= 100:
        discount_rate = 0.06
    elif qty >= 75:
        discount_rate = 0.05
    elif qty >= 50:
        discount_rate = 0.04
    elif qty >= 35:
        discount_rate = 0.03
    elif qty >= 30:
        discount_rate = 0.02
    else:
        discount_rate = 0

    base_cost_per_figure = 12.50
    labor_per_figure = 2
    base_cost = (base_cost_per_figure + labor_per_figure) * qty
    base_cost *= (1 - discount_rate)
    total_with_margin = base_cost * 1.15  # 15% markup

    # Add-ons
    character_design = 0 if design_paid else 85
    commercial_rights = 25 if commercial else 0
    packaging_cost = 100 if packaging else 0
    keychain_cost = 3 * qty if keychain else 0

    # Discounts for add-ons
    if discount_addons:
        commercial_rights *= 0.9
        packaging_cost *= 0.9
        keychain_cost *= 0.9

    final_quote = total_with_margin + character_design + commercial_rights + packaging_cost + keychain_cost

    return (f"### Quote Summary\n"
            f"- Quantity: {qty} MiniKreators\n"
            f"- Discount on figures: {discount_rate*100:.0f}%\n"
            f"- Character Design Fee: ${character_design:.2f}\n"
            f"- Commercial Rights: ${commercial_rights:.2f}\n"
            f"- Custom Packaging: ${packaging_cost:.2f}\n"
            f"- Keychains: ${keychain_cost:.2f}\n"
            f"- **Total (before shipping): ${final_quote:.2f}**\n"
            f"- Shipping is calculated based on your address.")

# Streamlit UI
st.set_page_config(page_title="MiniKreators Quote Calculator", layout="centered")
st.title("MiniKreators Quote Calculator")

qty = st.number_input("Quantity of MiniKreators (min 25):", min_value=25, step=1)
design_paid = st.checkbox("Character design already paid (for reorders)")
shipping_address = st.text_input("Shipping Address:")

st.subheader("Optional Add-ons")
commercial = st.checkbox("Add Commercial Rights ($25 per design)")
packaging = st.checkbox("Add Custom Packaging ($100 per design)")
keychain = st.checkbox("Convert to Keychains ($3 per figure)")
discount_addons = st.checkbox("Apply 10% discount on all add-ons (Pro/Premium only)")

if st.button("Calculate Quote"):
    quote = calculate_quote(qty, design_paid, commercial, packaging, keychain, discount_addons)
    st.markdown(quote)
