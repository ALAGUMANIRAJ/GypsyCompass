# 🧭 GypsyCompass — AI-Powered Travel Recommendation System

> **"You have the money, we have the map."**
> An intelligent travel destination recommender built with Django REST Framework + React.js

---

## 🚀 Quick Start

### 1. Setup Backend (Django)
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 2. Setup Frontend (React)
```bash
cd frontend
npm install
npm start
```

Visit: **http://localhost:3000** 🌐

---

## 🔑 Configuration (.env)

1. **Gemini API Key**: Get one from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. **Secret Key**: Generate a long random string for Django security.
3. **Database URL**: For production (Supabase).

---

## 🏗️ Project Structure

```
GypsyCompass/
├── .env                          # 🔑 Environment variables
├── manage.py                     # Django management
├── gypsycompass_backend/
│   ├── settings.py               # Django settings
│   └── urls.py                   # Main URL routing
├── recommendations/
│   ├── ai_service.py             # 🤖 Gemini AI integration
│   ├── models.py                 # Database models
│   ├── views.py                  # API endpoints
│   └── urls.py                   # API URL routing
└── frontend/src/
    ├── App.js                    # React Router setup
    ├── api.js                    # API service module
    ├── index.css                 # Complete design system
```

---

## 📋 Features

### 🏠 Home Page
- Beautiful hero section with landscape photography
- How-it-works section
- Destination preview cards
- Contact section with form

### 🗺️ Trip Planner (9 Steps)
1. **Your Name** — Personalized experience
2. **Budget + Currency** — Multi-currency support
3. **Solo or Group** — Experience tailoring
4. **Travel Scope** — Domestic or International
5. **Number of Days** — Duration planning
6. **Food & Accommodation** — Preferences
7. **Departure Location** — AI-powered autocomplete
8. **Travel Medium** — Transport selection
9. **Destination Style** — 20+ thematic categories

### 🎯 Results Page
- AI-driven destination suggestions
- Categorization based on budget
- Detailed summaries for each choice

### 📍 Destination Details
- Tourist spots and entry fees
- Local food recommendations
- Transportation costs and options
- Complete travel tips and emergency info

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12 + Django 5 + Django REST Framework |
| AI | Google Gemini 1.5 Flash |
| Frontend | React 18 + JavaScript |
| Database | PostgreSQL (Supabase) |
| Hosting | Render (Backend) + Vercel (Frontend) |

---

## 🤝 Contributing

Made with ❤️ for explorers who have money but need direction!
