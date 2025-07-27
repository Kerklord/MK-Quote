import streamlit as st
import os

# Initial service charge base value (modifiable)
if "service_base" not in st.session_state:
    st.session_state.service_base = 50

if "show_gp" not in st.session_state:
    st.session_state["show_gp"] = False

if "show_admin" not in st.session_state:
    st.session_state["show_admin"] = False

# Quote calculation function
def calculate_quote(
    qty, design_paid, packaging_design_paid, branding_paid,
    commercial, packaging, keychain, custom_parts_qty,
    part_sourcing, landing_page, domain_count,
    package_tier, with_profit=True
):
    if qty < 25:
        return 0, 0, "❌ Minimum order quantity is 25."

    # Determine quantity discount on figures
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

    # Package figure discounts
    if package_tier == "Premium Package":
        discount_rate = 0.10
    if package_tier == "Enterprise Package":
        discount_rate = 0.15

    # Base costs for figures
    base_cost_per_figure = 12.50
    labor_per_figure = 2
    base_cost = (base_cost_per_figure + labor_per_figure) * qty
    base_cost *= (1 - discount_rate)
    total_with_margin = base_cost * 1.15

    # Initialize add-on discount factor
    add_on_discount = 0.0
    if package_tier == "Pro Package":
        add_on_discount = 0.10
    if package_tier == "Premium Package":
        add_on_discount = 0.10
    if package_tier == "Enterprise Package":
        add_on_discount = 0.15

    # Add-on fees
    character_design = 0 if design_paid else 85
    commercial_rights = 25 if commercial else 0
    packaging_design_fee = 100 if packaging and not packaging_design_paid else 0
    branding_removal_fee = 85 if packaging and not branding_paid else 0
    ad_package = 500 if package_tier == "Premium Package" else 0
    part_sourcing_fee = 25 if part_sourcing else 0
    custom_parts_cost = custom_parts_qty * qty * 4
    packaging_cost = 0
    if packaging or package_tier in ["Premium Package", "Enterprise Package"]:
        packaging_cost = 2 * qty if keychain else 4.50 * qty
    keychain_cost = 3 * qty if keychain else 0
    landing_page_fee = 350 if (landing_page or package_tier in ["Premium Package", "Enterprise Package"]) else 0
    domain_fee = domain_count * 85 if landing_page or package_tier in ["Premium Package", "Enterprise Package"] else 0

    # Apply add-on discounts
    if add_on_discount > 0:
        commercial_rights *= (1 - add_on_discount)
        packaging_design_fee *= (1 - add_on_discount)
        branding_removal_fee *= (1 - add_on_discount)
        ad_package *= (1 - add_on_discount)
        part_sourcing_fee *= (1 - add_on_discount)
        custom_parts_cost *= (1 - add_on_discount)
        packaging_cost *= (1 - add_on_discount)
        keychain_cost *= (1 - add_on_discount)
        landing_page_fee *= (1 - add_on_discount)
        domain_fee *= (1 - add_on_discount)

    # Shipping cost estimate based on weight
    base_weight = (12 if keychain else 15) * qty + 50 + (3 * qty if not keychain else 0)
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
    shipping_cost = estimate_shipping(base_weight)

    # Service charge: base rate, +15% if qty>=75, plus modifiers
    service_charge = 0
    if qty >= 25:
        service_charge = st.session_state.service_base
        if qty >= 75:
            service_charge *= 1.15
        if packaging:
            service_charge *= 1.05
        if landing_page:
            service_charge *= 1.05
        if part_sourcing:
            service_charge *= 1.03

    # Final quote and profit
    final_quote = (
        total_with_margin + character_design + commercial_rights + packaging_design_fee +
        branding_removal_fee + ad_package + part_sourcing_fee + custom_parts_cost +
        packaging_cost + keychain_cost + landing_page_fee + domain_fee + shipping_cost + service_charge
    )
    total_cost = base_cost + packaging_cost + shipping_cost + (custom_parts_cost * 0.5)
    profit = final_quote - total_cost

    # Build quote summary
    title = "### Quote Summary with Profit" if with_profit else "### Quote Summary"
    quote_summary = (
        f"{title}\n"
        f"- Package Selected: {package_tier}\n"
        f"- Quantity: {qty} MiniKreators\n"
        f"- Discount on figures: {discount_rate*100:.0f}%\n"
        f"- Character Design Fee: ${character_design:.2f}\n"
        f"- Commercial Rights: ${commercial_rights:.2f}\n"
        f"- Custom Packaging Design Fee: ${packaging_design_fee:.2f}\n"
        f"- Branding Removal Fee: ${branding_removal_fee:.2f}\n"
        f"- 2D/3D Ad Package Fee: ${ad_package:.2f}\n"
        f"- Part Sourcing Fee: ${part_sourcing_fee:.2f}\n"
        f"- Custom Parts Fee: ${custom_parts_cost:.2f}\n"
        f"- Packaging Production Cost: ${packaging_cost:.2f}\n"
        f"- Keychain Production Cost: ${keychain_cost:.2f}\n"
        f"- Landing Page Fee: ${landing_page_fee:.2f}\n"
        f"- Domain Registration Fee: ${domain_fee:.2f}\n"
        f"- Service Charge: ${service_charge:.2f}\n"
        f"- Estimated Shipping: ${shipping_cost:.2f}\n"
        f"- **Total: ${final_quote:.2f}**"
    )
    if with_profit:
        quote_summary += f"\n- **Estimated Profit: ${profit:.2f}**"
    return final_quote, profit, quote_summary

# Streamlit App UI
st.set_page_config(page_title="Create-a-Kreator Quote Calculator", layout="centered")
st.image("creatorslogo-v2-W.png", width=200)
st.title("Create-a-Kreator Quote Calculator")

qty = st.number_input("Quantity of MiniKreators (min 25):", min_value=25, step=1)
design_paid = st.checkbox("Character design already paid (for reorders)")
packaging_design_paid = st.checkbox("Packaging design already paid (for reorders)")
branding_paid = st.checkbox("Branding removal already paid (for reorders)")
shipping_address = st.text_input("Shipping Address:")

st.subheader("Select Package")
package_tier = st.selectbox(
    "Choose a Package:",
    ["Starter Package", "Pro Package", "Premium Package", "Enterprise Package"]
)
if package_tier == "Starter Package":
    st.markdown("**Includes:** 25 MiniKreators + Character Design (1 revision included, +$50 per additional revision)")
elif package_tier == "Pro Package":
    st.markdown("**Includes:** Starter Package + Priority Review + 10% off Add-ons + Commercial Rights + We Handle Part Sourcing")
elif package_tier == "Premium Package":
    st.markdown("**Includes:** Pro Package + Custom Packaging + 2D/3D Ad Package + Custom Landing Page + 10% off add-ons")
elif package_tier == "Enterprise Package":
    st.markdown("**Includes:** Everything from Premium Package + Remove Branding + We Handle Part Sourcing + 15% off add-ons")

st.subheader("Optional Add-ons")
commercial_disabled = package_tier in ["Pro Package", "Premium Package", "Enterprise Package"]
packaging_disabled = package_tier in ["Premium Package", "Enterprise Package"] or packaging_design_paid
landing_disabled = package_tier == "Enterprise Package"

commercial = st.checkbox("Add Commercial Rights ($25 per design)", disabled=commercial_disabled)
packaging = st.checkbox("Add Custom Packaging ($100 per design)", disabled=packaging_disabled)
if packaging:
    branding_removal = st.checkbox("Remove MiniKreator Branding ($85)", disabled=branding_paid)
else:
    branding_removal = False
keychain = st.checkbox("Convert to Keychains ($3 per figure)")
custom_parts_qty = st.number_input("Number of Custom Parts per Figure ($4 each)", min_value=0, step=1)
part_sourcing = st.checkbox("MiniKreators will handle Part Sourcing ($25)")
landing_page = st.checkbox(
    "Custom Landing Page (shopqzr.com/minikreators/yourname) ($350)",
    disabled=landing_disabled
)
if package_tier == "Enterprise Package":
    landing_page = True
# Domain count input
if landing_page:
    domain_count = st.number_input(
        "Number of Custom Domains ($85 per domain for first year, $55/year after)",
        min_value=0,
        step=1
    )
else:
    domain_count = 0

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    show_quote = st.button("Calculate Quote")
with col2:
    st.link_button("Return to MiniKreators", "https://minikreators.com")
with col3:
    show_gp_prompt = st.button("GP-Cal")

if show_quote:
    final_total, profit_amount, quote = calculate_quote(
        qty, design_paid, packaging_design_paid, branding_paid,
        commercial, packaging, keychain, custom_parts_qty,
        part_sourcing, landing_page, domain_count,
        package_tier, with_profit=False
    )
    st.markdown(quote)
    st.markdown(
        "⚠️ **Disclaimer:** This quote is not 100% accurate as it is an estimate. "
        "For a more accurate quote please go to https://shopqzr.com/create-a-kreator"
    )

if show_gp_prompt:
    st.session_state["show_gp"] = True
if st.session_state.get("show_gp"):
    pw = st.text_input("Enter password:", type="password", key="gp_pw")
    if pw == "5150":
        final_total, profit_amount, quote = calculate_quote(
            qty, design_paid, packaging_design_paid, branding_paid,
            commercial, packaging, keychain, custom_parts_qty,
            part_sourcing, landing_page, domain_count,
            package_tier, with_profit=True
        )
        st.markdown(quote)
        st.markdown(
            "⚠️ **Disclaimer:** This quote is not 100% accurate as it is an estimate. "
            "For a more accurate quote please go to https://shopqzr.com/create-a-kreator"
        )
        st.session_state["show_gp"] = False
    elif pw == "5051":
        new_service_charge = st.number_input(
            "Enter new Service Charge base value:",
            min_value=0,
            value=st.session_state.service_base,
            step=1,
            key="sc_input"
        )
        if st.button("Update Service Charge"):
            st.session_state.service_base = new_service_charge
            st.success(f"Service charge base updated to ${new_service_charge:.2f}")
            st.session_state["show_gp"] = False
    elif pw:
        st.error("Incorrect password.")

st.markdown(
    "\n---\n<center>Qazer Inc. © 2025 All Rights Reserved.</center>",
    unsafe_allow_html=True
)
