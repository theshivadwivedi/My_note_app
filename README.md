# 📝 My Note App

A simple and secure **FastAPI-based Note Management Application** with **Google Authentication** and **MongoDB** integration — deployed live on Render.

🌐 **Live Demo:** [https://my-note-app-0k8c.onrender.com](https://my-note-app-0k8c.onrender.com)

---

## 🚀 Overview

**My Note App** allows users to securely sign up, log in (manually or via Google OAuth), and manage personal notes online.  
It is built using **FastAPI**, with **MongoDB** as the database and **Authlib** for Google login integration.  
The app is production-ready and deployed using **Render**.

---

## ⚙️ Features

✅ User Signup and Login (via Email or Google OAuth)  
✅ Create, Edit, Delete Notes  
✅ Secure Authentication with JWT Tokens  
✅ MongoDB Backend for Data Storage  
✅ Environment Variables for Secrets (.env)  
✅ Deployed and Auto-Scalable on Render  
✅ Built with Modern FastAPI + Uvicorn Stack  

---

## 🧩 Tech Stack

| Component | Technology |
|------------|-------------|
| **Backend** | FastAPI |
| **Auth** | Google OAuth (Authlib) |
| **Database** | MongoDB |
| **Server** | Uvicorn |
| **Deployment** | Render |
| **Environment** | Python 3.11+ |

---

## 🧠 Project Structure

my_note_app/
├── index.py # Entry point for FastAPI app
├── routes/
│ ├── auth.py # Handles signup/login
│ ├── google_auth.py # Google OAuth routes
├── models/
│ └── user.py # User schema
├── templates/ # Optional (if frontend added later)
├── .env # Environment variables (local use)
├── requirements.txt # Dependencies
└── README.md
