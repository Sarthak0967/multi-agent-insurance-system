import streamlit as st
import requests
import os 

BASE_URL = os.environ.get("BACKEND_URL", "http://insurance-api-service/api")

st.set_page_config(
    page_title="Multi-Agent Insurance System",
    layout="wide"
)

st.title("🧠 Multi-Agent Insurance System")

# =====================================
# Sidebar Navigation
# =====================================

menu = st.sidebar.radio(
    "Navigation",
    ["Health Check", "Research Policy", "Compare Policies"]
)

# =====================================
# Health Check
# =====================================

if menu == "Health Check":

    st.header("🔍 System Health Status")

    if st.button("Check System Health"):

        response = requests.get(f"{BASE_URL}/system/health")

        if response.status_code == 200:
            st.success("System is Running")
            st.json(response.json())
        else:
            st.error("Backend not responding")


# =====================================
# Research Policy
# =====================================

elif menu == "Research Policy":

    st.header("📘 Research Insurance Policy")

    try:
        policies_response = requests.get(f"{BASE_URL}/policies")
        policies = policies_response.json()
    except:
        policies = []

    selected_policy = st.selectbox(
        "Select Policy",
        policies if policies else ["No policies available"]
    )

    if st.button("Research Policy"):

        if not selected_policy:
            st.warning("Please select a policy")
        else:
            with st.spinner("Researching policy..."):

                response = requests.post(
                    f"{BASE_URL}/research",
                    json={"policy_name": selected_policy}
                )

                if response.status_code == 200:
                    data = response.json()

                    st.success("Research Completed")

                    st.subheader("📄 Policy Overview")

                    st.write("### 📝 Simple Explanation")
                    st.write(data.get("simple_explanation", "N/A"))

                    st.write("### 👤 Who Should Buy It")
                    for item in data.get("who_should_buy", []):
                        st.write("•", item)

                    st.write("### 🚫 Who Should Avoid It")
                    for item in data.get("who_should_avoid", []):
                        st.write("•", item)

                    st.write("### ⭐ Key Takeaways")
                    for item in data.get("key_takeaways", []):
                        st.write("•", item)

                else:
                    st.error("Error occurred")
                    st.json(response.json())


# =====================================
# Compare Policies
# =====================================

elif menu == "Compare Policies":

    st.header("⚖ Compare Two Insurance Policies")

    try:
        policies_response = requests.get(f"{BASE_URL}/policies")
        policies = policies_response.json()
    except:
        policies = []

    col1, col2 = st.columns(2)

    with col1:
        policy_a = st.selectbox("Select Policy A", policies)

    with col2:
        policy_b = st.selectbox("Select Policy B", policies)

    if st.button("Compare Policies"):

        if policy_a == policy_b:
            st.warning("Please select two different policies")
        else:
            with st.spinner("Comparing policies..."):

                response = requests.post(
                    f"{BASE_URL}/compare",
                    json={
                        "policy_a": policy_a,
                        "policy_b": policy_b
                    }
                )

                if response.status_code == 200:
                    data = response.json()

                    st.success("Comparison Completed")

                    # ✅ Recommendation Section
                    st.subheader("📌 Recommendation")
                    st.write(data.get("recommendation", "N/A"))

                    # ✅ Detailed Comparison
                    st.subheader("📊 Detailed Comparison")

                    comparison = data.get("comparison", {})

                    if comparison:
                        for key, value in comparison.items():
                            title = key.replace("_", " ").title()
                            st.markdown(f"### {title}")
                            st.write(value)
                    else:
                        st.write("No comparison data available")

                else:
                    st.error("Error occurred")
                    st.json(response.json())