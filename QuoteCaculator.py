import streamlit as st
import os

# Initialize session state
if "service_base" not in st.session_state:
    st.session_state.service_base = 50
if "show_gp" not in st.session_state:
    st.session_state["show_gp"] = False

# Calculation function
def calculate_quote(qty, design_paid, packaging_design_paid, branding_paid,
                    commercial, packaging, keychain, custom_parts_qty,
                    part_sourcing, landing_page, domain_count,
                    package_tier, with_profit=True):
    # Minimum check
    if qty < 25:
        return 0, 0, "❌ Minimum order quantity is 25."

    # Figure discount rates
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
    # Package-specific figure discounts
    if package_tier == "Premium Package":
        discount_rate = 0.10
    if package_tier == "Enterprise Package":
        discount_rate = 0.15

    # Base cost per figure + labor
    base_unit = 12.50 + 2
    base_cost = base_unit * qty * (1 - discount_rate)
    figures_total = base_cost * 1.15
    unit_price = figures_total / qty if qty else 0

    # Add-on discount factors
    add_on_discount = 0
    if package_tier in ["Pro Package", "Premium Package"]:
        add_on_discount = 0.10
    if package_tier == "Enterprise Package":
        add_on_discount = 0.15

    # Add-on fees
    char_design_fee = 0 if design_paid else 85
    comm_rights = 0 if package_tier in ["Pro Package", "Premium Package", "Enterprise Package"] else (25 if commercial else 0)
    packaging_design_fee = 0 if packaging_design_paid else (100 if packaging else 0)
    branding_fee = 0 if branding_paid else (85 if packaging else 0)
    ad_fee = 500 if package_tier == "Premium Package" else 0
    sourcing_fee = 25 if part_sourcing else 0
    custom_parts_fee = custom_parts_qty * 4 * qty
    pack_prod_cost = 2 * qty if packaging and keychain else (4.50 * qty if packaging else 0)
    keychain_cost = 3 * qty if keychain else 0
    lp_fee = 350 if landing_page else 0
    dom_fee = domain_count * 85 if landing_page else 0

    # Apply add-on discounts
    if add_on_discount > 0:
        comm_rights *= (1 - add_on_discount)
        packaging_design_fee *= (1 - add_on_discount)
        branding_fee *= (1 - add_on_discount)
        ad_fee *= (1 - add_on_discount)
        sourcing_fee *= (1 - add_on_discount)
        custom_parts_fee *= (1 - add_on_discount)
        pack_prod_cost *= (1 - add_on_discount)
        keychain_cost *= (1 - add_on_discount)
        lp_fee *= (1 - add_on_discount)
        dom_fee *= (1 - add_on_discount)

    # Shipping estimate
    weight = (12 if keychain else 15) * qty + 50 + (0 if keychain else 3 * qty)
    if weight <= 100:
        ship_cost = 12
    elif weight <= 250:
        ship_cost = 14.5
    elif weight <= 500:
        ship_cost = 18
    elif weight <= 1000:
        ship_cost = 22
    elif weight <= 1500:
        ship_cost = 26
    else:
        ship_cost = 30

    # Service charge
    svc = 0
    if qty >= 25:
        svc = st.session_state.service_base
        if qty >= 75:
            svc *= 1.15
        if packaging:
            svc *= 1.05
        if landing_page:
            svc *= 1.05
        if part_sourcing:
            svc *= 1.03

    # Final totals
    final = (figures_total + char_design_fee + comm_rights + packaging_design_fee + branding_fee +
             ad_fee + sourcing_fee + custom_parts_fee + pack_prod_cost + keychain_cost + lp_fee + dom_fee + ship_cost + svc)
    cost_basis = base_cost + pack_prod_cost + ship_cost + (custom_parts_fee * 0.5)
    profit = final - cost_basis

    # Build summary text
    title = "### Quote Summary with Profit" if with_profit else "### Quote Summary"
    summary = [
        title,
        f"- Package: {package_tier}",
        f"- Quantity: {qty}",
        f"- Figure Discount: {discount_rate*100:.0f}%",        
        f"- Figures Total: ${figures_total:.2f} (Unit: {unit_price:.2f} per fig)",
        f"- Character Design: ${char_design_fee:.2f}",
        f"- Commercial Rights: ${comm_rights:.2f}",
        f"- Packaging Design: ${packaging_design_fee:.2f}",
        f"- Branding Removal: ${branding_fee:.2f}",
        f"- 2D/3D Ad: ${ad_fee:.2f}",
        f"- Part Sourcing: ${sourcing_fee:.2f}",
        f"- Custom Parts: ${custom_parts_fee:.2f}",
        f"- Packaging Prod: ${pack_prod_cost:.2f}",
        f"- Keychains: ${keychain_cost:.2f}",
        f"- Landing Page: ${lp_fee:.2f}",
        f"- Domains: ${dom_fee:.2f}",
        f"- Shipping: ${ship_cost:.2f}",
        f"- Service Charge: ${svc:.2f}",
        f"- **Total: ${final:.2f}**"
    ]
    if with_profit:
        summary.append(f"- **Profit: ${profit:.2f}**")
    return final, profit, "
".join(summary)

# Streamlit App UI
st.set_page_config(page_title="Create-a-Kreator Quote Calculator", layout="centered")
st.image("creatorslogo-v2-W.png", width=200)
st.title("Create-a-Kreator Quote Calculator")

# Inputs
qty = st.number_input("Quantity of MiniKreators (min 25):", min_value=25)
design_paid = st.checkbox("Character design paid")
packaging_design_paid = st.checkbox("Packaging design paid")
branding_paid = st.checkbox("Branding removal paid")
shipping_address = st.text_input("Shipping Address")

# Package selection
st.subheader("Select Package")
package_tier = st.selectbox("Package", ["Starter Package", "Pro Package", "Premium Package", "Enterprise Package"])
if package_tier == "Starter Package":
    st.markdown("Includes: 25 figures + Character Design")
elif package_tier == "Pro Package":
    st.markdown("Includes: Starter + Priority Review + 10% off add-ons + Commercial Rights + Part Sourcing")
elif package_tier == "Premium Package":
    st.markdown("Includes: Pro + Custom Packaging + 2D/3D Ad + 10% off add-ons")
elif package_tier == "Enterprise Package":
    st.markdown("Includes: Premium + Remove Branding + Part Sourcing + 15% off add-ons")

# Add-ons
st.subheader("Add-ons")
com_disabled = package_tier in ["Pro Package", "Premium Package", "Enterprise Package"]
pack_disabled = (package_tier == "Premium Package") or packaging_design_paid
landing_disabled = (package_tier == "Enterprise Package")

commercial = st.checkbox("Commercial Rights ($25)", disabled=com_disabled)
packaging = st.checkbox("Custom Packaging ($100)", disabled=pack_disabled)
branding_removal = st.checkbox("Remove Branding ($85)", disabled=not packaging or branding_paid)
keychain = st.checkbox("Convert to Keychains ($3)")
custom_parts_qty = st.number_input("Custom Parts per Figure ($4)", min_value=0)
part_sourcing = st.checkbox("We handle Part Sourcing ($25)")
landing_page = st.checkbox("Custom Landing Page ($350)", disabled=landing_disabled)
if package_tier == "Enterprise Package":
    landing_page = True

# Domain count
domain_count = 0
if landing_page:
    domain_count = st.number_input("Custom Domains ($85 each)", min_value=0)

# Actions
col1, col2, col3 = st.columns(3)
with col1:
    show_quote = st.button("Calculate Quote")
with col2:
    st.link_button("Return to MiniKreators", "https://minikreators.com")
with col3:
    show_gp = st.button("GP-Cal")

# Display quote
if show_quote:
    total, profit, text = calculate_quote(qty, design_paid, packaging_design_paid, branding_paid,
                                          commercial, packaging, keychain, custom_parts_qty,
                                          part_sourcing, landing_page, domain_count,
                                          package_tier, with_profit=False)
    st.markdown(text)
    st.markdown("⚠️ Disclaimer: Estimate only. For accurate quote, visit https://shopqzr.com/create-a-kreator")

# GP-Cal section
if show_gp:
    st.session_state["show_gp"] = True
if st.session_state["show_gp"]:
    pw = st.text_input("Password", type="password")
    if pw == "5150":
        _, _, text = calculate_quote(qty, design_paid, packaging_design_paid, branding_paid,
                                     commercial, packaging, keychain, custom_parts_qty,
                                     part_sourcing, landing_page, domain_count,
                                     package_tier, with_profit=True)
        st.markdown(text)
        st.markdown("⚠️ Disclaimer: Estimate only. For accurate quote, visit https://shopqzr.com/create-a-kreator")
        st.session_state["show_gp"] = False
    elif pw == "5051":
        new_base = st.number_input("New Service Charge Base", value=st.session_state.service_base)
        if st.button("Update Service Charge"):
            st.session_state.service_base = new_base
            st.success(f"Service base updated to ${new_base}")
            st.session_state["show_gp"] = False
    elif pw:
        st.error("Incorrect password")

# Footer
st.markdown(
    "---\n<center>Qazer Inc. © 2025 All Rights Reserved.</center>",
    unsafe_allow_html=True
)
