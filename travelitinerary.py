import streamlit as st
from datetime import datetime
import subprocess
import yagmail
from notion_client import Client
import uuid
import os

# Function to call local Ollama model
def get_text_ollama(prompt):
    try:
        result = subprocess.run(
            ['ollama', 'run', 'mistral'],
            input=prompt.encode('utf-8'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=300
        )
        return result.stdout.decode('utf-8')
    except subprocess.TimeoutExpired:
        return "⚠️ Ollama took too long to respond. Try again with fewer days or interests."
    except Exception as e:
        return f"❌ Error using Ollama: {e}"


def send_email_yagmail(to_email, subject, body):
    sender_email = st.secrets["email"]["sender"]
    app_password = st.secrets["email"]["app_password"]
    print("Email function called with:", to_email, subject)
    try:
        yag = yagmail.SMTP(user=sender_email, password=app_password)
        yag.send(to=to_email, subject=subject, contents=body)
        print("✅ Email sent successfully.")
        return True
    except Exception as e:
        print("❌ Error sending email:", e)
        return f"Failed to send email: {e}"


def save_itinerary_to_notion_page(itinerary_text, title="Travel Itinerary"):
    try:
        notion = Client(auth=st.secrets["notion"]["token"])
        parent_page_id = st.secrets["notion"]["parent_page_id"]
        
        # Split into chunks of max 2000 characters for Notion limits
        max_len = 2000
        chunks = [itinerary_text[i:i+max_len] for i in range(0, len(itinerary_text), max_len)]

        # Create a new child page
        response = notion.pages.create(
            parent={"page_id": parent_page_id},
            properties={
                "title": [
                    {
                        "text": {
                            "content": f"{title} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                        }
                    }
                ]
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": chunk}}]
                    }
                } for chunk in chunks
            ]
        )
        return True
    except Exception as e:
        return f"❌ Failed to save to Notion: {e}"


# App title and description
st.set_page_config(page_title="Travel Itinerary Generator", page_icon="✈️", layout="centered")
st.markdown("<h1 style='text-align: center;'>✈️ Travel Itinerary Generator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Plan your trip with an AI-powered itinerary based on your interests, travel style, and budget!</p>", unsafe_allow_html=True)
st.markdown("---")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/201/201623.png", width=100)
    st.markdown("**Travel Itinerary App**")
    st.markdown("Powered by 🧠 Ollama + Notion + Email")

# Form Section
with st.form("trip_form"):
    st.subheader("📝 Trip Details")

    col1, col2 = st.columns(2)
    with col1:
        email = st.text_input("📧 Your Email")
        destination = st.text_input("📍 Destination")
        budget = st.selectbox("💰 Budget", ['500$-1000$', '1000$-2000$', '2000$+'])
    with col2:
        travel_style = st.selectbox("🧳 Travel Style", [
            'Budget-Friendly', 'Luxury Travel', 'Family-Friendly', 'Solo Travel', 'Group Travel'
        ])
        start_date = st.date_input("📅 Start Date")
        end_date = st.date_input("📅 End Date")

    interests = st.multiselect("🎯 Interests", [
        'Adventure (Hiking, Sports, Outdoor Activities)',
        'Food & Dining',
        'Culture & History',
        'Shopping & Markets',
        'Relaxation (Beaches, Spas)',
        'Nightlife & Entertainment'
    ])
    
    submitted = st.form_submit_button("✨ Generate Itinerary")

# Generate itinerary
# After form submission and itinerary generation
if submitted:
    if end_date <= start_date:
        st.error("🚫 End date must come after start date.")
    elif not destination or not interests:
        st.warning("⚠️ Please fill in all the required fields.")
    else:
        trip_days = (end_date - start_date).days
        interests_text = ', '.join(interests)

        main_prompt = (
            f"Create a short and fun {trip_days}-day travel itinerary for a trip to {destination}. "
            f"User interests: {interests_text}. Travel style: {travel_style}, budget: {budget}. "
            f"Include daily places to visit, local transport tips, a rough daily budget, and average weather based on past years."
        )

        with st.spinner("🧠 Generating itinerary using your local AI model..."):
            itinerary = get_text_ollama(main_prompt)
            st.session_state.itinerary = itinerary
            st.session_state.email_sent = False  # reset email flag

        st.success("✅ Here's your custom travel itinerary:")
        st.markdown(st.session_state.itinerary)
        
        save_result = save_itinerary_to_notion_page(
        itinerary_text=itinerary,
        title=f"Itinerary for {email} - {destination}"
        )
        if save_result == True:
            st.success("📥 Saved Itinerary to database")
        else:
            st.error(save_result)


# Only show email sending section after form submission
if "itinerary" in st.session_state and not st.session_state.email_sent:
    with st.expander("📧 Send itinerary to your email"):
        email_sent_button = st.button("📤 Send Itinerary")

        if email_sent_button:
            result = send_email_yagmail(
                to_email=email,
                subject="Your AI-Powered Travel Itinerary",
                body=st.session_state.itinerary
            )
            if result == True:
                st.success("✅ Itinerary sent to your email!")
                st.session_state.email_sent = True  # flag to avoid multiple sends
            else:
                st.error(result)

# If the email has already been sent, show a confirmation
if "itinerary" in st.session_state and st.session_state.email_sent:
    st.info("✅ Itinerary has already been sent to your email!")