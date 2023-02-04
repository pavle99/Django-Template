# Django-Template

## Description

This is a template for Django projects with customized auth and users CRUD. 
For auth, you have the following functionalities you can find in the `account` app:
 <!-- make list -->
- Register
- Login
- Refresh token
- Get current user
- Change password
- Forgot password
- Set password

For users CRUD, you have the following functionalities you can find in the `users` app:
- List all users
- Create user
- Get user by id
- Update user
- Delete user
- Upload avatar

On **update user**, you receive avatar as a base64 string, so you can display it in the frontend and on **upload avatar**, you receive the avatar image. If frontend requires avatar to always be in base64, you can use the `get_avatar_base64` method in the `users` serializers to get the avatar as a base64 string.

I have also added a `utils` app that contains the following functionalities:

- Send email when user forgot password or when user is created using the `set_password.html` template. You need to provide the `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` in the `docker-compose.yml` file and switch to smtp email backend in the `settings.py` file if you want to test the email functionality using gmail. You can get EMAIL_HOST_PASSWORD from [here](https://myaccount.google.com/apppasswords).
- File to base64 and base64 to file conversion. You can use it to convert the avatar image to base64 and vice versa.

## Development

### Development via Docker

To run the project locally, you need to have `docker` and `docker-compose` installed on your machine. Before starting the docker containers, you need to provide the EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in the `docker-compose.yml` file and switch to smtp email backend in the `settings.py` file.

Now, you can run the following commands:
```bash
docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml up -d
```

After running the above commands, you can access the project at `http://localhost:9000/` and the admin panel at `http://localhost:9000/admin/`. You can login to the admin panel using the following credentials:
```bash
username: admin
password: admin
```

The default database in dockerized development is **postgresql**.

### Development via Virtual Environment

First, you need to create a virtual environment and activate it:
```bash
python -m venv venv
venv\Scripts\activate # for windows
source venv/bin/activate # for linux
```

Then, you need to install the requirements:
```bash
pip install -r requirements.txt
```

Next, apply the migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

Optionally, you can create a superuser by entering the following command and following the instructions:
```bash
python manage.py createsuperuser
```

Finally, you can run the project:
```bash
python manage.py runserver 9000
```

The default database in venv development is **sqlite3**.