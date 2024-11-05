#!/bin/sh

git filter-branch --env-filter '

OLD_EMAIL="2225107818@qq.com"
NEW_NAME="Meow Stars"
NEW_EMAIL="a2225107818@icloud.com"

if [ "$GIT_COMMITTER_EMAIL" = "$OLD_EMAIL" ]
then
    export GIT_COMMITTER_NAME="$NEW_NAME"
    export GIT_COMMITTER_EMAIL="$NEW_EMAIL"
fi
if [ "$GIT_AUTHOR_EMAIL" = "$OLD_EMAIL" ]
then
    export GIT_AUTHOR_NAME="$NEW_NAME"
    export GIT_AUTHOR_EMAIL="$NEW_EMAIL"
fi
' HEAD ^origin/${branch}

