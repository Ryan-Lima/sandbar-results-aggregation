# Sandbar Results Aggregation

This is a repository to facilitate the sharing of scripts/workflows/sql 
that performs analysis/aggregation of results from the GCMRC's sandbar database.

## Development/Build/Deploy

### Development

There are 3 types of branches we care about:

1. **Master** - Always working. Only administrators can push to it.
2. **dev** - Integration branch. Most of the testing happens here. 
3. **dev_FEATURENAME** - feature branches. In general these should be local only. Exceptions can be made for backup purposes but the ***parent repos should never contain a reference to a feature branch.***

* **Code commits** happen on feature branches
* **Hotfixes** can happen anywhere but most likely on dev.
* `dev` will be pushed to `master` for a product launch.  

#### How to create a new feature?

The following is a standard workflow for `checkout->branch->work->rebase->Push` workflow. It seems 
like a lot of steps but after a few iterations it will make a lot of sense and should become second nature.

1. **Checkout**: Check out the latest `dev`
2. **Branch**: Create a local feature branch `dev-featurename`. Please **do not push this branch**. It will make rebasing harder later.
3. **Work**: Make as many commits as you need to finish the feature.
4. Test your feature thoroughly. 
5. **Rebase**: `dev` may have advanced in the time you took to create your feature so you need to **rebase** before you can merge with it. 
    1. **Checkout** `dev` and **pull** so your local is up to date
    2. **Checkout** `dev-featurename` and **rebase** on top of local `dev`. Fix any conflicts or problems.
    3. **Checkout** `dev` again and **merge** with `dev-featurename`. Merge should be smooth without any commits. If you get a commit. Rollback the merge commit and start over.
6. **Push**: Push `dev` up to master.


## Dependencies
