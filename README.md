✈️ AI-Powered Travel Itinerary Generator

This is a Streamlit web app that helps users create personalized travel itineraries using an AI model (via Ollama), and then emails the itinerary and saves it to Notion automatically!

🚀 Features

- ✅ Generate a custom travel itinerary based on:
  - Destination
  - Budget
  - Travel style
  - Interests
  - Dates
- 📅 Save each itinerary to the admin's Notion
- 📧 Send the itinerary to the user’s email
- 🧠 Uses local AI (Ollama + Mistral model) for quick, cost-free text generation

📦 Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/mateisalajan/travel-itinerary-app.git
   cd travel-itinerary-app
   ```

2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your `secrets.toml` file under `.streamlit/` directory:

   ```toml
   # .streamlit/secrets.toml

   [email]
   sender = "your_email@gmail.com"
   app_password = "your_email_app_password"

   [notion]
   token = "your_notion_integration_token"
   parent_page_id = "your_notion_page_id"
   ```

4. Run the app:

   ```bash
   streamlit run app.py
   ```

📌 Notes

- You must have [Ollama](https://ollama.com/) and the `mistral` model installed locally.
- Notion integration must be correctly set up and shared with the integration.
- App is optimized for deployment on Streamlit Community Cloud.



🚰 Future Improvements

- 🌐 Google Maps API to fetch top places based on interests
- 📱 Mobile responsive design
- 🌍 Multi-language support

