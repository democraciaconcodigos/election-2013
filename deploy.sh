git checkout gh-pages
git read-tree master:build
git commit -m 'deploy'
git push
git reset --hard
git checkout master -f


