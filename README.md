    SPA application: Comments

- Backend is implemented on Django REST framework
- Frontend is implemented on Vue.js

    User capabilities:

- registration
- login
- logout
- publishing posts
- publishing comments to posts

   Features of the functionality:

- registration with validation and captcha
- processing of photos and files
- auto tags for the form of publication of a post and comment
- filtering of posts

    To run on a local repository:

  Clone the repository:
# git clone https://github.com/olexiygolovko/spa_talk_back.git
# cd spa_talk_back

  Creating a virtual environment:
- python -m venv venv

  Activating the virtual environment
  For Windows:
- venv\Scripts\activate
  For Linux/Mac:
- source venv/bin/activate

  Installing dependencies:
- pip install -r requirements.txt

  Create .env file
  Create .env file in the root of the project and add the necessary variables:
- SECRET_KEY=your_secret_key
- DATABASE_NAME=your_db_name
- DATABASE_USER=your_db_user
- DATABASE_PASSWORD=your_db_password

  Applying Migrations
- python makemigrations
- python manage.py migrate

  Launching the development server
- python manage.py runserver

  Setting up the frontend (Vue.js)

  Frontend directory:
- cd frontend

  Installing dependencies:
- npm install

  Launching the development server:
- npm run dev

  Setting up a PostgreSQL database:
- Install PostgreSQL
- Create a database
- Specify connection parameters in the .env file

  The backend should be accessible at: http://127.0.0.1:8000
  The frontend should be accessible at: http://localhost:5173