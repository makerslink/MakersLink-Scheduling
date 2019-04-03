# MakersLink-Scheduling
Project to develop a system to schecdule and book opening times at MakersLink

Rough roadmap:
1. Notification to email/slack
2. CSV-export?

To deploy:
First on your local machine:
# Pull including current tags
git pull
# Make sure to get tags
git fetch --tags
# Look at old tags
git tag
# Invent a new version number
git tag $VERSION_NUM
# Push tag to github
git push origin $VERSION_NUM
# Build docker image locally
sudo docker build -t makerslink_scheduling .
# Save docker image
sudo docker save -o ./MakersLink-Scheduling-$VERSION_NUM.tar makerslink_scheduling:latest
# Change owner to your self
sudo chown me:me ./MakersLink-Scheduling-$VERSION_NUM.tar
# Push image to server
sudo scp MakersLink-Scheduling-$VERSION_NUM.tar somebody@somewhere:/a/dir

Then on the server:
# Load docker image
sudo docker load -i MakersLink-Scheduling-$VERSION_NUM.tar
# Start with this command (on our server this is in the start_scheduling script).
sudo docker run -dt -e "DJANGO_SECRET=$SUPER_DUPER_SECRET" -e "SCHEDULING_PASS=$DIFFERENT_SECRET" --name scheduling --restart unless-stopped  -v /somewhere/db:/scheduling/makerslink/makerslink/db -v /somewhere/pks:/scheduling/pks -p 8000:8000 makerslink_scheduling
