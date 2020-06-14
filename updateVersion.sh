# ./updateVersion.sh [major/feature/bug] https://github.com/makerslink/MakersLink-Scheduling

##########################
#
# VARIABLES
#
##########################

# Branch to use for new releases
wantedBranch="master"

# Regex to find versionnumber
regex="v([0-9]+).([0-9]+).([0-9]+)"

# Variables to hold versioning
major=0
minor=0
patch=0

##########################
#
# SCRIPT
#
##########################

# Check script was started correctly
if [ "$#" -ne 2 ]; then
    echo "usage: ./updateVersion.sh [major/feature/bug] [repository]"
    exit -1
fi
case $1 in
    major|feature|bug) ;;
    *) echo "usage: ./updateVersion.sh [major/feature/bug] [repository]"; exit -1 ;;
esac

# Fetch only latest tag before anything else:
latestVersion=$(git ls-remote --tags $2 | sort -t '/' -k 3 -V | tail -n1 | awk -F"/" '{print $3}')
# Make sure version matches our regex and break down the version number into it's components
if [[ $latestVersion =~ $regex ]]; then
    major="${BASH_REMATCH[1]}"
    minor="${BASH_REMATCH[2]}"
    patch="${BASH_REMATCH[3]}"
else
    echo "Invalid version-number format in repo, exiting script!"
    exit -1
fi

##########################
#
# NEW VERSION
#
##########################

echo "Deploying a new version assumes branch=\"$wantedBranch\" and will pull from remote repository before pushing a new tag."
read -p "Do you wish to continue?(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Exiting script!"
    exit 0
fi

# Get the current branch in use
currentBranch=$(git branch | grep \* | cut -d ' ' -f2)
# Make sure git command did not fail (this also works to make sure we have a .git directory)
if [ $? -ne 0 ]; then
    echo "Could not fetch current branch (\"git branch\" failed). Exiting script!"
    exit 1
fi

# Check if we are on correct branch
if [[ $wantedBranch != $currentBranch ]]; then
    echo "Wrong branch checked out, you are on \"$currentBranch\" and should be on \"$wantedBranch\". Exiting script!"
    exit -1
fi

# Pull latest
if ! git pull --quiet
then
    echo "Failed to pull from remote, exiting script!"
    exit -1
fi

# Get new version number
# check paramater to see which number to increment
if [[ "$1" == "major" ]]; then
    major=$(echo $major+1 | bc)
    minor=0
    patch=0
elif [[ "$1" == "feature" ]]; then
    minor=$(echo $minor + 1 | bc)
    patch=0
elif [[ "$1" == "bug" ]]; then
    patch=$(echo $patch + 1 | bc)
fi

#Combine new version into variable
newVersion="v${major}.${minor}.${patch}"

# Check that new version is what we wanted
echo "Current version is $latestVersion, new version will be $newVersion"
read -p "Do you wish to continue?(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Exiting script!"
    exit 0
fi

# Create new tag
git tag $newVersion
# Push to origin with new version/tag
git push origin $newVersion

