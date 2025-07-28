import streamlit as st

# Initialize session state
if "service_base" not in st.session_state:
    st.session_state.service_base = 50
if "show_gp" not in st.session_state:
    st.session_state["show_gp"] = False

# Calculation function
def calculate_quote(
    qty, design_paid, packaging_design_paid, branding_paid,
    commercial, packaging, packaging_design, keychain,
    custom_parts_qty, custom_part_creation, part_sourcing,
    landing_page, domain_count, package_tier, with_profit=True
):
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
        discount_rate = 0.0
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
    add_on_discount = 0.0
    if package_tier in ["Pro Package", "Premium Package"]:
        add_on_discount = 0.10
    if package_tier == "Enterprise Package":
        add_on_discount = 0.15

    # Add-on fees
    char_design_fee = 0 if design_paid else 85
    commercial_rights = 0 if package_tier in ["Pro Package", "Premium Package", "Enterprise Package"] else (25 if commercial else 0)
    packaging_design_fee = 0 if packaging_design_paid else (100 if packaging_design else 0)
    branding_fee = 0 if branding_paid else (85 if packaging_design else 0)
    ad_fee = 500 if package_tier == "Premium Package" else 0
    sourcing_fee = 25 if part_sourcing else 0
    custom_parts_fee = custom_parts_qty * 4 * qty
    creation_fee = 150 if custom_part_creation else 0
    packaging_cost = (2 * qty if packaging and keychain else (4.50 * qty if packaging else 0))
    keychain_cost = 3 * qty if keychain else 0
    lp_fee = 350 if landing_page else 0
    dom_fee = domain_count * 85 if domain_count else 0

    # Apply add-on discounts
    if add_on_discount > 0:
        for attr in ["commercial_rights","packaging_design_fee","branding_fee", 
                     "ad_fee","sourcing_fee","custom_parts_fee",
                     "packaging_cost","keychain_cost","lp_fee","dom_fee"]:
            val = locals()[attr]
            locals()[attr] = val * (1 - add_on_discount)
    
    # Shipping estimate
    weight = ((12 if keychain else 15) * qty) + 50 + (0 if keychain else 3 * qty)
    if weight <= 100:
        ship_cost = 12.0
    elif weight <= 250:
        ship_cost = 14.5
    elif weight <= 500:
        ship_cost = 18.0
    elif weight <= 1000:
        ship_cost = 22.0
    elif weight <= 1500:
        ship_cost = 26.0
    else:
        ship_cost = 30.0

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
    final = (figures_total + char_design_fee + commercial_rights + packaging_design_fee +
             branding_fee + ad_fee + sourcing_fee + custom_parts_fee + creation_fee +
             packaging_cost + keychain_cost + lp_fee + dom_fee + ship_cost + svc)
    cost_basis = base_cost + packaging_cost + ship_cost + (custom_parts_fee * 0.5)
    profit = final - cost_basis

    # Build summary
    title = "### Quote Summary with Profit" if with_profit else "### Quote Summary"
    lines = [title,
             f"- Package: {package_tier}",
             f"- Quantity: {qty}",
             f"- Figure Discount: {discount_rate*100:.0f}%",  
             f"- Figures Total: ${figures_total:.2f}",
             f"- Unit Price per Figure: ${unit_price:.2f}"]
    if not design_paid: lines.append(f"- Character Design: ${char_design_fee:.2f}")
    if commercial_rights: lines.append(f"- Commercial Rights: ${commercial_rights:.2f}")
    if packaging_design_fee: lines.append(f"- Packaging Design: ${packaging_design_fee:.2f}")
    if branding_fee: lines.append(f"- Branding Removal: ${branding_fee:.2f}")
    if ad_fee: lines.append(f"- 2D/3D Ad Package: ${ad_fee:.2f}")
    if part_sourcing: lines.append(f"- Part Sourcing: ${sourcing_fee:.2f}")
    if custom_parts_qty>0: lines.append(f"- Custom Parts ({custom_parts_qty} ea): ${custom_parts_fee:.2f}")
    if custom_part_creation: lines.append(f"- Custom Part Creation: ${creation_fee:.2f}")
    if packaging: lines.append(f"- Packaging Production: ${packaging_cost:.2f}")
    if keychain: lines.append(f"- Keychains: ${keychain_cost:.2f}")
    if landing_page: lines.append(f"- Landing Page: ${lp_fee:.2f}")
    if domain_count>0: lines.append(f"- Domains: ${dom_fee:.2f}")
    lines.append(f"- Shipping: ${ship_cost:.2f}")
    lines.append(f"- Service Charge: ${svc:.2f}")
    lines.append(f"- **Total: ${final:.2f}**")
    if with_profit:
        lines.append(f"- **Profit: ${profit:.2f}**")
    return final, profit, "\n".join(lines)

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
package_tier = st.selectbox("Package", ["Starter Package","Pro Package","Premium Package","Enterprise Package"])
if package_tier=="Starter Package":
    st.markdown("Includes: 25 figures + Character Design")
elif package_tier=="Pro Package":
    st.markdown("Includes: Starter + Priority Review + 10% off add-ons + Commercial Rights + Part Sourcing")
elif package_tier=="Premium Package":
    st.markdown("Includes: Pro + Custom Packaging + 2D/3D Ad + 10% off add-ons")
elif package_tier=="Enterprise Package":
    st.markdown("Includes: Premium + Remove Branding + Part Sourcing + 15% off add-ons")

# Add-ons
st.subheader("Add-ons")
com_disabled = package_tier in ["Pro Package","Premium Package","Enterprise Package"]
pack_disabled = (package_tier=="Premium Package") or packaging_design_paid
landing_disabled = (package_tier=="Enterprise Package")

commercial = st.checkbox("Commercial Rights ($25)", disabled=com_disabled)
packaging_design = st.checkbox("Custom Packaging ($100)", disabled=pack_disabled)
branding_removal = st.checkbox("Remove Branding ($85)", disabled=not packaging_design or branding_paid)
keychain = st.checkbox("Convert to Keychains ($3)")
custom_parts_qty = st.number_input("Custom Parts per Figure ($4)", min_value=0)
custom_part_creation = st.checkbox("Create Custom Part ($150)")
part_sourcing = st.checkbox("We handle Part Sourcing ($25)")
landing_page = st.checkbox("Custom Landing Page ($350)", disabled=landing_disabled)
if package_tier=="Enterprise Package": landing_page=True

domain_count = st.number_input("Custom Domains ($85 each)", min_value=0)

# Actions
col1,col2,col3=st.columns(3)
with col1:
    show_quote = st.button("Calculate Quote")
with col2:
    show_custom = st.button("Custom Part Quote")
with col3:
    st.link_button("Return to MiniKreators","https://minikreators.com")
show_gp = col3.button("GP-Cal")

# Display custom part quote
if show_custom:
    _,_,raw=calculate_quote(qty,design_paid,packaging_design_paid,branding_paid,
                             commercial,packaging_design,keychain,custom_parts_qty,
                             custom_part_creation,part_sourcing,
                             landing_page,domain_count,package_tier,False)
    # parse lines
    lines=raw.split("\n")
    # filter only custom part related
    cp_lines=[l for l in lines if any(tag in l for tag in ["Custom Parts","Custom Part Creation","Shipping","Service Charge","Commercial Rights"])
             or l.startswith("###")]
    st.markdown("\n".join(cp_lines))

# Display full quote
if show_quote:
    total,profit,text=calculate_quote(qty,design_paid,packaging_design_paid,branding_paid,
                                     commercial,packaging_design,keychain,custom_parts_qty,
                                     custom_part_creation,part_sourcing,
                                     landing_page,domain_count,package_tier,False)
    st.markdown(text)
    st.markdown("⚠️ Disclaimer: Estimate only. For accurate quote, visit https://shopqzr.com/create-a-kreator")

# GP-Cal section
if show_gp:
    st.session_state["show_gp"]=True
if st.session_state.get("show_gp"):
    pw=st.text_input("Password",type="password")
    if pw=="5150":
        _,_,text=calculate_quote(qty,design_paid,packaging_design_paid,branding_paid,
                                 commercial,packaging_design,keychain,custom_parts_qty,
                                 custom_part_creation,part_sourcing,
                                 landing_page,domain_count,package_tier,True)
        st.markdown(text)
        st.markdown("⚠️ Disclaimer: Estimate only. For accurate quote, visit https://shopqzr.com/create-a-kreator")
        st.session_state["show_gp"]=False
    elif pw=="5051":
        new_base=st.number_input("Service Charge Base",value=st.session_state.service_base)
        if st.button("Update Service Charge"):
            st.session_state.service_base=new_base
            st.success(f"Service base updated to ${new_base}")
            st.session_state["show_gp"]=False
    elif pw:
        st.error("Incorrect password")

# Footer
st.markdown("---\n<center>Qazer Inc. © 2025 All Rights Reserved.</center>",unsafe_allow_html=True)
