## 📘 Project Overview

# 🧠 AssetsTracking Agent  
### A Conversational AgenticAI App for Smart Corporate Asset Management  
---
## 📘 Overview  

**AssetsTracking Agent** is a web-based **Agentic AI application** designed to manage and track corporate assets such as laptops, mobile phones, and other hardware equipment.  
This project aims to **simplify audit compliance** and **speed up clearance processes** through an AI-driven conversational interface.  

With this system, corporate users can **interact naturally with an AI agent** to perform asset-related tasks like assigning, returning, and auditing devices — eliminating tedious manual tracking.

---

## 🎯 Objectives  

- Automate asset management and clearance operations.  
- Enable conversational interaction between corporate employees and AI.  
- Reduce manual effort in tracking and auditing hardware.  
- Ensure compliance and transparency during corporate audits.  

---
Follow the steps below to set up and run the backend application.

## 🚀 Steps to Start the Backend App

1. **Navigate to the backend directory**  
   ```bash
   cd /workspace/assets_tracking_agent/backend
   ```

2. **Install the required dependencies**  
   Before running the application, install all necessary Python packages using:  
   ```bash
   pip install -r requirements.txt
   ```

3. **Create Google AI Studio Key**

   Visit https://aistudio.google.com/ using your personal gmail id and create an API Key. If you are a first time user you might have to create a new project in https://console.cloud.google.com/ first , import it here and then create API Key.

4. **Update env with Google AI Studio Key**

   Once the key is created copy the key value and update the below variable in .env file

   GOOGLE_API_KEY=<Use your key>

5. **Run the backend server**  
   Once the dependencies are installed, start the application with:  
   ```bash
   python main.py
   ```

## 🚀 Steps to Start the Frontend App

1. Find the `index.html` file inside the **frontend** directory.

2. **Configure the backend connection**  
   - Ensure that the **backend server** is up and running.  
   - Open the `apiService.js` file (usually located inside the `js` or `services` folder).  
   - Update the **host URL** or **API base URL** to match your backend’s running address.  
     Example:  
     ```js
     const API_CONFIG = {
         baseURL: "<BACKEND_URL>", // Configure the relevant backend url
         headers: {
         "Content-Type": "application/json",
         },
      };
     ```

3. **Start the frontend app**  
   - Right-click on `index.html`.  
   - Choose **"Open with Live Server"** (available in VS Code or similar editors).  
   - The application will automatically open in your default web browser.
