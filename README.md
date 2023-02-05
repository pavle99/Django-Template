# Django-Template

## Description

This is a template for Django projects with customized auth and users CRUD. The project is dockerized and uses postgresql as the database so it needs minimal adjustments to be used in production. The project is also configured to use gmail as the email backend so you can use it to send emails to users.

## Features

For auth, you have the following functionalities you can find in the `account` app:
- Register
- Login
- Refresh token
- Get current user
- Change password
- Forgot password
- Set password

I have setup CORS headers for the APIs so that you can access them from the frontend. You can change the allowed origins with the `CORS_ALLOWED_ORIGINS` variable.

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

I have also added Swagger documentation for the APIs. You can access it at `http://localhost:9000/docs/` after running the project.

## Development

### Development via Docker

To run the project locally, you need to have `docker` and `docker-compose` installed on your machine. Before starting the docker containers, you need to provide the EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in the `.env.dev` file and switch to smtp email backend in the `settings.py` file.

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

**NOTE**: When adding new apps, you need to add them `docker-entrypoint.sh` file in the `makemigrations` command so that the migrations are applied on each start of the docker containers since the migrations folder of each app is initially empty. You can find the following line in the `docker-entrypoint.sh` file:
```bash
python manage.py makemigrations account users [new_app_names]
```

[//]: # (every time the docker compose starts it will give migrations)
On each start of the docker containers, the migrations are applied. If you want to apply migrations manually, you can run the following commands:
```bash
docker-compose -f docker-compose.yml exec web python manage.py makemigrations [app_names]
docker-compose -f docker-compose.yml exec web python manage.py migrate --noinput
```

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

## Testing

I have already added the complete test cases suit for the `account` and `users` apps with 100% coverage. You can run the tests by entering the following command:
```bash
python manage.py test [app_names]
coverage run manage.py test [app_names]
```

To get the coverage report, you can run the following command:
```bash
coverage report
```

To get the coverage report in html format, you can run the following command:
```bash
coverage html
```
And then open the `index.html` file in the `htmlcov` folder.