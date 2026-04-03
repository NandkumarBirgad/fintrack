# 🚀 FinTrack--Finance Tracking System

FinTrack is a modern, scalable **finance management system** designed to
help users efficiently track, analyze, and manage their financial data.\
It consists of a powerful **Flask (Python) REST API backend** and a
visually rich **React (Vite) frontend**.

------------------------------------------------------------------------

## 💎 Key Features

### 💰 Financial Records Management

-   Manage **income and expense transactions**
-   Fields: amount, type, category, date, notes\
-   Full **CRUD operations**\
-   Advanced filtering:
    -   By type (income / expense)
    -   By category
    -   By date range

------------------------------------------------------------------------

### 🔐 Role-Based Access Control (RBAC)

-   **Admin** → Full access (CRUD + user management + analytics)\
-   **Analyst** → View transactions + analytics\
-   **Viewer** → Read-only access

👉 Authentication using **JWT**

------------------------------------------------------------------------

### 📊 Advanced Analytics

-   Total Income, Expenses, Balance\
-   Monthly cash flow\
-   Category-wise breakdown

------------------------------------------------------------------------

### ⚙️ Backend Architecture

-   Flask with MVC + Service Layer\
-   Routes, Services, Schemas, Models separation

------------------------------------------------------------------------

### ✅ Validation & Error Handling

-   Marshmallow validation\
-   Proper HTTP codes (422, 404)\
-   JSON error responses

------------------------------------------------------------------------

### 🎨 Frontend

-   React + Vite\
-   Glassmorphism UI\
-   Charts using Recharts\
-   JWT authentication

------------------------------------------------------------------------

## 🚀 Setup Instructions

### Backend

``` bash
cd fintrack
cd backend
pip install -r requirements.txt
python run.py
```

### Frontend

``` bash
cd fintrack
cd frontend
npm install
npm run dev
```

------------------------------------------------------------------------

## 🧪 Testing

``` bash
python test_api.py
```

------------------------------------------------------------------------

## 🔑 Demo Users

  Role      Email                  Password
  --------- ---------------------- -------------
  Admin     admin@fintrack.com     Admin@123
  Analyst   analyst@fintrack.com   Analyst@123
  Viewer    viewer@fintrack.com    Viewer@123

------------------------------------------------------------------------

## 💥 Summary

**FinTrack is a full-stack, role-based finance management system with
secure APIs and insightful analytics.**
