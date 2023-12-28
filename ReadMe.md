Plan:
get this running on a website for people - they can update what classes they want
email notifications

Rather than update each class every 5 sec, add entry when data changes
    estimated: 20k students
    each student: 100 actions

Database
SQL
    for each class

Docker commmands:
docker build --platform linux/amd64 -t registration-1 .
docker tag registration-1 ahilio/registration-1
docker push ahilio/registration-1