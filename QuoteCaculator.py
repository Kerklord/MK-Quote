import streamlit as st
import os

# Initial service charge base value (modifiable)
if "service_base" not in st.session_state:
    st.session_state.service_base = 50

if "show_gp" not in st.session_state:
    st.session_state["show_gp"] = False

if "show_admin" not in st.session_state:
    st.session_state["show_admin"] = False

def calculate_quote(qty, design_paid, packaging_design_paid, branding_paid, commercial, packaging, keychain, custom_parts_qty, discount_addons, part_sourcing, landing_page, domain_count, package_tier, with_profit=True):
    if qty < 25:
        return 0, 0, "❌ Minimum order quantity is 25."

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
    branding_removal_profit = 85 if not branding_paid else 0

    landing_page_fee = 350 if landing_page else 0
    domain_fee = domain_count * 85 if landing_page else 0
    domain_profit = domain_count * 85 * 0.6 if landing_page else 0

    if package_tier == "Pro Package":
        commercial_rights = 25 * 0.9
        part_sourcing_fee = 25
        discount_addons = True
    elif package_tier == "Premium Package":
        commercial_rights = 25 * 0.9
        packaging_design_fee = 0 if packaging_design_paid else 100 * 0.9
        ad_package = 500 * 0.9
        landing_page_fee = 350
        discount_addons = True
    elif package_tier == "Enterprise Package":
        commercial_rights = 0
        packaging_design_fee = 0
        branding_removal_fee = 0
        ad_package = 0
        landing_page_fee = 350
        part_sourcing_fee = 25
        discount_addons = True
        discount_rate += 0.15  # Enterprise Pack has 15% off all addons featured
    else:
        commercial_rights = 25 if commercial else 0
        ad_package = 0

    if packaging or package_tier in ["Premium Package", "Enterprise Package"]:
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

    # Service charge: base for 25+, increase 15% at 75+
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

    final_quote = total_with_margin + character_design + commercial_rights + packaging_design_fee + branding_removal_fee + packaging_cost + keychain_cost + ad_package + part_sourcing_fee + custom_parts_cost + landing_page_fee + domain_fee + shipping_cost + service_charge
    total_cost = base_cost + packaging_cost + shipping_cost + (custom_parts_cost * 0.5)
    profit = final_quote - total_cost + branding_removal_profit + domain_profit + landing_page_fee

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
                     f"- Ad Package: ${ad_package:.2f}\n"
                     f"- Part Sourcing: ${part_sourcing_fee:.2f}\n"
                     f"- Custom Landing Page: ${landing_page_fee:.2f}\n"
                     f"- Domain Registration: ${domain_fee:.2f}\n"
                     f"- Service Charge: ${service_charge:.2f}\n"
                     f"- Estimated Shipping: ${shipping_cost:.2f}\n"
                     f"- **Total: ${final_quote:.2f}**")

    if with_profit:
        quote_summary += f"\n- **Estimated Profit: ${profit:.2f}**"

    return final_quote, profit, quote_summary
