# SPA application: Comments

- Backend is implemented on Django REST framework
- Frontend is implemented on Vue.js

## User capabilities:

- registration
- login
- logout
- publishing posts
- publishing comments to posts

## Features of the functionality:

- registration with validation and captcha
- processing of photos and files
- auto tags for the form of publication of a post and comment
- filtering of posts

## To run on a local repository:

### 1. Clone the repository:
```bash
git clone https://github.com/olexiygolovko/spa_talk_back.git
```
### 2. Creating a virtual environment:
```bash
python -m venv venv
```
### 3. Activating the virtual environment
### For Windows:
```bash
venv\Scripts\activate
```
### For Linux/Mac:
```bash
source venv/bin/activate
```

### 4. Installing dependencies:
```bash
pip install -r requirements.txt
```
### 5. Create .env file
### Create .env file in the root of the project and add the necessary variables:
- SECRET_KEY=your_secret_key
- DATABASE_NAME=your_db_name
- DATABASE_USER=your_db_user
- DATABASE_PASSWORD=your_db_password

### 6. Applying Migrations
```bash
cd spa_talk_back
```
```bash
python makemigrations
```
```bash
python manage.py migrate
```
### 7. Launching the development server
```bash
pythnon manage.py createsuperuser
```
### 8. Launching the development server
```bash
python manage.py runserver
```
### 9. Setting up the frontend (Vue.js)
### Frontend directory:
```bash
cd frontend
```
### 10. Installing dependencies:
```bash
npm install
```

### 11. Launching the development server:
```bash
npm run dev
```

## 12. Setting up a PostgreSQL database:
### Install PostgreSQL
### Create a database
### Specify connection parameters in the .env file

### The backend should be accessible at: http://127.0.0.1:8000
### The frontend should be accessible at: http://localhost:5173
