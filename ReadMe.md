Plan:
get this running on a website for people - they can update what classes they want
email notifications

Docker commmands:
docker build --platform linux/amd64 -t registration-1 .
docker tag registration-1 ahilio/registration-1
docker push ahilio/registration-1