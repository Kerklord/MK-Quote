import streamlit as st
import os

def calculate_quote(qty, design_paid, commercial, packaging, keychain, discount_addons, package_tier):
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

    # Add-ons from selections or package
    character_design = 0 if design_paid else 85
    commercial_rights = 0
    packaging_cost = 0
    keychain_cost = 0
    ad_package = 0

    if package_tier == "Pro Package":
        commercial_rights = 25 * 0.9
        packaging_cost = 25 * 0.9 if packaging else 0
        keychain_cost = 3 * qty * 0.9 if keychain else 0
        discount_addons = True
    elif package_tier == "Premium Package":
        commercial_rights = 25 * 0.9
        packaging_cost = 100 * 0.9
        keychain_cost = 3 * qty * 0.9 if keychain else 0
        ad_package = 500 * 0.9
        discount_addons = True
    else:  # Starter
        commercial_rights = 25 if commercial else 0
        packaging_cost = 100 if packaging else 0
        keychain_cost = 3 * qty if keychain else 0

    # Shipping weight estimate (in grams)
    base_weight = 15 * qty
    if keychain:
        base_weight = 12 * qty
    else:
        base_weight += 3 * qty
    box_weight = 50
    total_weight = base_weight + box_weight

    def estimate_shipping(weight):
        if weight <= 100:
            return 12.00
        elif weight <= 250:
            return 14.50
        elif weight <= 500:
            return 18.00
        elif weight <= 1000:
            return 22.00
        elif weight <= 1500:
            return 26.00
        else:
            return 30.00

    shipping_cost = estimate_shipping(total_weight)

    final_quote = total_with_margin + character_design + commercial_rights + packaging_cost + keychain_cost + ad_package + shipping_cost

    return (f"### Quote Summary\n"
            f"- Package Selected: {package_tier}\n"
            f"- Quantity: {qty} MiniKreators\n"
            f"- Discount on figures: {discount_rate*100:.0f}%\n"
            f"- Character Design Fee: ${character_design:.2f}\n"
            f"- Commercial Rights: ${commercial_rights:.2f}\n"
            f"- Custom Packaging: ${packaging_cost:.2f}\n"
            f"- Keychains: ${keychain_cost:.2f}\n"
            f"- Ad Package (Premium only): ${ad_package:.2f}\n"
            f"- Estimated Shipping: ${shipping_cost:.2f}\n"
            f"- **Total: ${final_quote:.2f}**")

# Streamlit UI
st.set_page_config(page_title="MiniKreators Quote Calculator", layout="centered")
st.image("creatorslogo-v2-W.png", width=200)
st.title("MiniKreators Quote Calculator")

qty = st.number_input("Quantity of MiniKreators (min 25):", min_value=25, step=1)
design_paid = st.checkbox("Character design already paid (for reorders)")
shipping_address = st.text_input("Shipping Address:")

st.subheader("Select Package")
package_tier = st.selectbox("Choose a Package:", ["Starter Package", "Pro Package", "Premium Package"])

if package_tier == "Starter Package":
    st.markdown("**Includes:** 25 MiniKreators + Character Design (1 revision included, +$50 per additional revision)")
elif package_tier == "Pro Package":
    st.markdown("**Includes:** Starter Package + Priority Review + 10% off Add-ons + Commercial Rights")
elif package_tier == "Premium Package":
    st.markdown("**Includes:** Pro Package + Custom Packaging + 2D/3D Ad Package (10% off) + Social Media Showcase")

st.subheader("Optional Add-ons")
commercial_disabled = package_tier in ["Pro Package", "Premium Package"]
packaging_disabled = package_tier == "Premium Package"

commercial = st.checkbox("Add Commercial Rights ($25 per design)", disabled=commercial_disabled)
packaging = st.checkbox("Add Custom Packaging ($100 per design)", disabled=packaging_disabled)
keychain = st.checkbox("Convert to Keychains ($3 per figure)")
discount_addons = st.checkbox("Apply 10% discount on all add-ons (Pro/Premium only)", value=(package_tier != "Starter Package"), disabled=True)

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Calculate Quote"):
        quote = calculate_quote(qty, design_paid, commercial, packaging, keychain, discount_addons, package_tier)
        st.markdown(quote)
with col2:
    st.link_button("Return to MiniKreators", "https://minikretors.com")

st.markdown("\n---\n<center>Qazer Inc. © 2025 All Rights Reserved.</center>", unsafe_allow_html=True)
