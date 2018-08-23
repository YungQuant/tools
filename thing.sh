git filter-branch --commit-filter '
      if [ "$GIT_AUTHOR_EMAIL" = "*" ];
      then
              GIT_AUTHOR_NAME="yungquant";
              GIT_AUTHOR_EMAIL="theboss723@gmail.com";
              git commit-tree "$@";
      else
              git commit-tree "$@";
      fi' HEAD
