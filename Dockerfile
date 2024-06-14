# We Use an official Python runtime as a parent image
FROM python:3.12

# create test_auth_api directory
RUN mkdir /test_auth_api

# make test_auth_api the working directory
WORKDIR /test_auth_api

# copy whole project from current directory to test_auth_api directory.
copy . .

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# run this command to install all dependencies
RUN pip install -r requirements.txt

# port to run the app
EXPOSE 8000

# start server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]