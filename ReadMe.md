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
docker build -t course-registration-bot:1 .
docker run \
    -e apiBaseUrl=http://127.0.0.1:5000 \
    -d course-registration-bot:1