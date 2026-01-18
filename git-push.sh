#!/bin/bash
TOKEN=$(cat /root/.github_token)
BRANCH=${1:-$(git branch --show-current)}

cd /root/educalims-dev

echo "Push vers GitHub (branche: $BRANCH)..."

CURRENT_URL=$(git remote get-url origin)
git remote set-url origin "https://${TOKEN}@github.com/andypaypow/educalims-django-hostinger.git"
git push origin $BRANCH
git remote set-url origin "$CURRENT_URL"

echo "Push termine!"
