import streamlit as st
import os

# Initial service charge base value (modifiable)
if "service_base" not in st.session_state:
    st.session_state.service_base = 50
if "show_gp" not in st.session_state:
    st.session_state["show_gp"] = False

# Quote calculation function
def calculate_quote(
    qty, design_paid, packaging_design_paid, branding_paid,
    commercial, packaging, keychain, custom_parts_qty,
    part_sourcing, landing_page, domain_count,
    package_tier, with_profit=True
):
    if qty < 25:
        return 0, 0, "❌ Minimum order quantity is 25."

    # Determine figure discount
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
    if package_tier == "Premium Package":
        discount_rate = 0.10
    if package_tier == "Enterprise Package":
        discount_rate = 0.15

    # Base cost for figures
    base_cost_per_figure = 12.50
    labor_per_figure = 2
    base_cost = (base_cost_per_figure + labor_per_figure) * qty
    base_cost *= (1 - discount_rate)
    figures_total = base_cost * 1.15
    price_per_figure = figures_total / qty if qty else 0

    # Determine add-on discount
    add_on_discount = 0
    if package_tier in ["Pro Package", "Premium Package"]:
        add_on_discount = 0.10
    if package_tier == "Enterprise Package":
        add_on_discount = 0.15

    # Add-on fees
    character_design = 0 if design_paid else 85
    commercial_rights = 0 if package_tier in ["Pro Package", "Premium Package", "Enterprise Package"] else (25 if commercial else 0)
    packaging_design_fee = 0 if packaging_design_paid else (100 if packaging else 0)
    branding_removal_fee = 0 if branding_paid else (85 if packaging else 0)
    ad_package = 500 if package_tier == "Premium Package" else 0
    part_sourcing_fee = 25 if part_sourcing else 0
    custom_parts_cost = custom_parts_qty * qty * 4
    packaging_cost = 0
    if packaging or package_tier in ["Premium Package", "Enterprise Package"]:
        packaging_cost = 2 * qty if keychain else 4.50 * qty
    keychain_cost = 3 * qty if keychain else 0

    # Landing page & domain fees (Premium no longer includes landing page)
    landing_page_fee = 350 if landing_page else 0
    domain_fee = domain_count * 85 if landing_page else 0

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

    # Shipping cost
    weight = (12 if keychain else 15) * qty + 50 + (0 if keychain else 3 * qty)
    if weight <= 100:
        shipping_cost = 12.00
    elif weight <= 250:
        shipping_cost = 14.50
    elif weight <= 500:
        shipping_cost = 18.00
    elif weight <= 1000:
        shipping_cost = 22.00
    elif weight <= 1500:
        shipping_cost = 26.00
    else:
        shipping_cost = 30.00

    # Service charge
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
        figures_total + character_design + commercial_rights + packaging_design_fee +
        branding_removal_fee + ad_package + part_sourcing_fee + custom_parts_cost +
        packaging_cost + keychain_cost + landing_page_fee + domain_fee + shipping_cost + service_charge
    )
    total_cost = base_cost + packaging_cost + shipping_cost + (custom_parts_cost * 0.5)
    profit = final_quote - total_cost

    # Build summary
    title = "### Quote Summary with Profit" if with_profit else "### Quote Summary"
    summary = [
        title,
        f"- Package Selected: {package_tier}",
        f"- Quantity: {qty} MiniKreators",
        f"- Discount on figures: {discount_rate*100:.0f}%,",
        f"- Figures Total (with margin): ${figures_total:.2f}",
        f"- Price per Figure: ${price_per_figure:.2f}",
        f"- Character Design Fee: ${character_design:.2f}",
        f"- Commercial Rights: ${commercial_rights:.2f}",
        f"- Custom Packaging Design Fee: ${packaging_design_fee:.2f}",
        f"- Branding Removal Fee: ${branding_removal_fee:.2f}",
        f"- 2D/3D Ad Package Fee: ${ad_package:.2f}",
        f"- Part Sourcing Fee: ${part_sourcing_fee:.2f}",
        f"- Custom Parts Fee: ${custom_parts_cost:.2f}",
        f"- Packaging Production Cost: ${packaging_cost:.2f}",
        f"- Keychain Production Cost: ${keychain_cost:.2f}",
        f"- Landing Page Fee: ${landing_page_fee:.2f}",
        f"- Domain Registration Fee: ${domain_fee:.2f}",
        f"- Service Charge: ${service_charge:.2f}",
        f"- Estimated Shipping: ${shipping_cost:.2f}",
        f"- **Total: ${final_quote:.2f}**"
    ]
    if with_profit:
        summary.append(f"- **Estimated Profit: ${profit:.2f}**")
    return final_quote, profit, "\n".join(summary)

# Streamlit UI
st.set_page_config(page_title="Create-a-Kreator Quote Calculator", layout="centered")
st.image("creatorslogo-v2-W.png", width=200)
st.title("Create-a-Kreator Quote Calculator")

qty = st.number_input("Quantity of MiniKreators (min 25):", min_value=25, step=1)
design_paid = st.checkbox("Character design already paid (for reorders)")
packaging_design_paid = st.checkbox("Packaging design already paid (for reorders)")
branding_paid = st.checkbox("Branding removal already paid (for reorders)")
shipping_address = st.text_input("Shipping Address:")

st.subheader("Select Package")
package_tier = st.selectbox("Choose a Package:", [
    "Starter Package", "Pro Package", "Premium Package", "Enterprise Package"
])
if package_tier == "Starter Package":
    st.markdown("**Includes:** 25 MiniKreators + Character Design (1 revision incl., +$50 per extra)")
elif package_tier == "Pro Package":
    st.markdown("**Includes:** Starter + Priority Review + 10% off add-ons + Commercial Rights + Part Sourcing")
elif package_tier == "Premium Package":
    st.markdown("**Includes:** Pro + Custom Packaging + 2D/3D Ad + 10% off add-ons")
elif package_tier == "Enterprise Package":
    st.markdown("**Includes:** Premium + Remove Branding + Part Sourcing + 15% off add-ons")

st.subheader("Optional Add-ons")
commercial_disabled = package_tier in ["Pro Package", "Premium Package", "Enterprise Package"]
packaging_disabled = package_tier in ["Premium Package", "Enterprise Package"] or packaging_design_paid
landing_disabled = package_tier in ["Premium Package", "Enterprise Package"]

commercial = st.checkbox("Add Commercial Rights ($25)", disabled=commercial_disabled)
packaging = st.checkbox("Add Custom Packaging ($100)", disabled=packaging_disabled)
branding_removal = st.checkbox("Remove Branding ($85)", disabled=not packaging or branding_paid)
keychain = st.checkbox("Convert to Keychains ($3)")
custom_parts_qty = st.number_input("Custom Parts per Figure ($4 each)", min_value=0)
part_sourcing = st.checkbox("We handle Part Sourcing ($25)")
landing_page = st.checkbox("Custom Landing Page ($350)", disabled=landing_disabled)
if package_tier == "Enterprise Package":
    landing_page = True

domain_count = 0
if landing_page:
    domain_count = st.number_input("Number of Custom Domains ($85 first year)", min_value=0)

col1, col2, col3 = st.columns([1,1,1])
with col1:
    show_quote = st.button("Calculate Quote")
with col2:
    st.link_button("Return to MiniKreators", "https://minikreators.com")
with col3:
    show_gp = st.button("GP-Cal")

if show_quote:
    final_total, profit_amount, quote = calculate_quote(
