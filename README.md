💰 Smart Finance Hub

Smart Finance Hub is a stylish, multi-page financial management application built with Streamlit. It leverages machine learning for expense prediction and Google's Gemini AI for personalized financial coaching, providing a comprehensive toolkit for modern personal finance.

✨ Key Features

🔐 Secure Multi-Page Dashboard: A clean, authenticated environment for managing your finances.

📊 Visual Analytics: Interactive spending breakdowns by category and historical trend analysis using Plotly.

📈 Smart Expense Prediction: Integrated Linear Regression model that forecasts tomorrow's spending based on historical habits.

🤖 AI Financial Assistant: Powered by Gemini, providing actionable insights and budget planning advice.

📥 Flexible Data Export: One-click downloads for your expense database in CSV and Excel formats.

🎨 Premium UI: Custom CSS styling with a focus on whitespace, rounded corners, and a modern aesthetic.

🚀 Getting Started

Prerequisites

Python 3.9 or higher

A GitHub account (for deployment)

Local Installation

Clone the repository:

git clone [https://github.com/yourusername/smart-finance-hub.git](https://github.com/yourusername/smart-finance-hub.git)
cd smart-finance-hub


Install dependencies:

pip install -r requirements.txt


Run the application:

streamlit run app.py


🛠️ Configuration & Secrets

To enable the AI Financial Assistant, you need to configure your Gemini API key in Streamlit's secrets:

Create a .streamlit/secrets.toml file locally.

Add your key:

GEMINI_API_KEY = "YOUR_API_KEY_HERE"


📦 Deployment

This app is optimized for Streamlit Cloud:

Push your code to GitHub.

Connect your repo to Streamlit Cloud.

Add your GEMINI_API_KEY in the Streamlit Cloud dashboard under Settings > Secrets.

📝 Roadmap

[ ] Firebase/Firestore integration for persistent cross-session storage.

[ ] OCR for receipt scanning.

[ ] Export to PDF report generation.

[ ] Multi-currency support.

📄 License

Distributed under the MIT License. See LICENSE for more information.

<p align="center">
Built with ❤️ for better financial futures.
</p>
