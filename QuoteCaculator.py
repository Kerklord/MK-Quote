import streamlit as st
import os

def calculate_quote(qty, design_paid, packaging_design_paid, branding_paid, commercial, packaging, keychain, custom_parts_qty, discount_addons, part_sourcing, package_tier, with_profit=True):
    if qty < 25:
        return 0, 0, "❌ Minimum order quantity is 25."

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
    total_with_margin = base_cost * 1.15

    character_design = 0 if design_paid else 85
    commercial_rights = 0
    packaging_design_fee = 0 if packaging_design_paid else 100 if packaging else 0
    branding_removal_fee = 0 if branding_paid else 85
    packaging_cost = 0
    keychain_cost = 0
    ad_package = 0
    part_sourcing_fee = 25 if part_sourcing else 0
    custom_parts_cost = custom_parts_qty * qty * 4
    custom_parts_profit = custom_parts_cost * 0.5
    branding_removal_profit = 85 if not branding_paid else 0

    if package_tier == "Pro Package":
        commercial_rights = 25 * 0.9
        discount_addons = True
    elif package_tier == "Premium Package":
        commercial_rights = 25 * 0.9
        packaging_design_fee = 0 if packaging_design_paid else 100 * 0.9
        ad_package = 500 * 0.9
        discount_addons = True
    else:
        commercial_rights = 25 if commercial else 0
        ad_package = 0

    if packaging or package_tier == "Premium Package":
        if keychain:
            packaging_cost = 2 * qty
        else:
            per_package_cost = 4.50
            if qty > 75:
                per_package_cost *= 0.97
            packaging_cost = per_package_cost * qty

    if keychain:
        keychain_cost = 3 * qty

    base_weight = 15 * qty
    if keychain:
        base_weight = 12 * qty
    else:
        base_weight += 3 * qty
    total_weight = base_weight + 50

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

    final_quote = total_with_margin + character_design + commercial_rights + packaging_design_fee + branding_removal_fee + packaging_cost + keychain_cost + ad_package + part_sourcing_fee + custom_parts_cost + shipping_cost
    total_cost = base_cost + packaging_cost + shipping_cost + (custom_parts_cost * 0.5)
    profit = final_quote - total_cost + branding_removal_profit

    title = "### Quote Summary with Profit" if with_profit else "### Quote Summary"
    quote_summary = (f"{title}\n"
                     f"- Package Selected: {package_tier}\n"
                     f"- Quantity: {qty} MiniKreators\n"
                     f"- Discount on figures: {discount_rate*100:.0f}%\n"
                     f"- Character Design Fee: ${character_design:.2f}\n"
                     f"- Commercial Rights: ${commercial_rights:.2f}\n"
                     f"- Custom Packaging Design Fee: ${packaging_design_fee:.2f}\n"
                     f"- Branding Removal Fee: ${branding_removal_fee:.2f}\n"
                     f"- Custom Packaging Production: ${packaging_cost:.2f}\n"
                     f"- Keychains: ${keychain_cost:.2f}\n"
                     f"- Custom Parts: ${custom_parts_cost:.2f}\n"
                     f"- Ad Package (Premium only): ${ad_package:.2f}\n"
                     f"- Part Sourcing: ${part_sourcing_fee:.2f}\n"
                     f"- Estimated Shipping: ${shipping_cost:.2f}\n"
                     f"- **Total: ${final_quote:.2f}**")

    if with_profit:
        quote_summary += f"\n- **Estimated Profit: ${profit:.2f}**"

    return final_quote, profit, quote_summary

st.set_page_config(page_title="MiniKreators Quote Calculator", layout="centered")
st.image("creatorslogo-v2-W.png", width=200)
st.title("MiniKreators Quote Calculator")

qty = st.number_input("Quantity of MiniKreators (min 25):", min_value=25, step=1)
design_paid = st.checkbox("Character design already paid (for reorders)")
packaging_design_paid = st.checkbox("Packaging design already paid (for reorders)")
branding_paid = st.checkbox("Branding removal already paid (for reorders)")
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
packaging_disabled = package_tier == "Premium Package" or packaging_design_paid

commercial = st.checkbox("Add Commercial Rights ($25 per design)", disabled=commercial_disabled)
packaging = st.checkbox("Add Custom Packaging ($100 per design)", disabled=packaging_disabled)
branding_removal = st.checkbox("Remove MiniKreator Branding ($85)", disabled=branding_paid)
keychain = st.checkbox("Convert to Keychains ($3 per figure)")
custom_parts_qty = st.number_input("Number of Custom Parts per Figure ($4 each)", min_value=0, step=1)
part_sourcing = st.checkbox("MiniKreators will handle Part Sourcing ($25)")
discount_addons = st.checkbox("Apply 10% discount on all add-ons (Pro/Premium only)", value=(package_tier != "Starter Package"), disabled=True)

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    show_quote = st.button("Calculate Quote")
with col2:
    st.link_button("Return to MiniKreators", "https://minikreators.com")
with col3:
    show_gp_prompt = st.button("GP-Cal")

if show_quote:
    final_total, profit_amount, quote = calculate_quote(qty, design_paid, packaging_design_paid, branding_paid, commercial, packaging, keychain, custom_parts_qty, discount_addons, part_sourcing, package_tier, with_profit=False)
    st.markdown(quote)

if show_gp_prompt:
    st.session_state["show_gp"] = True

if st.session_state.get("show_gp"):
    pw = st.text_input("Enter password to view GP-Cal results:", type="password", key="gp_pw")
    if pw and st.button("Submit Password"):
        if pw == "5150":
            final_total, profit_amount, quote = calculate_quote(qty, design_paid, packaging_design_paid, branding_paid, commercial, packaging, keychain, custom_parts_qty, discount_addons, part_sourcing, package_tier, with_profit=True)
            st.markdown(quote)
            st.session_state["show_gp"] = False
        else:
            st.error("Incorrect password.")
            st.session_state["show_gp"] = False

st.markdown("\n---\n<center>Qazer Inc. © 2025 All Rights Reserved.</center>", unsafe_allow_html=True)
