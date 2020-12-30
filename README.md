### Auto Albums (RIP 2020-2020)
The purpose of this project ~~is~~ _was_ to maintain derivative Google Photos albums programmatically. In particular, I _want to_ create a dynamic album of the N most recent photos from one album to populate another.

Why? Dad wants an album of "recent" baby photos (out of the big album where we dump pictures) for his Google Nest Hub and I needed an excuse to play with the Google APIs.

Why not tho? _Because Google Photos's API doesn't let you do anything with existing media items and I don't want to reupload media files_

## How to "run"

By _"run"_ here, I mean: create a configuration file and then do nothing with it.

(Instructions adapted from [Photos-Upload](https://github.com/shraiysh/Photos-Upload) thanks)
...but there's no point in following them :shrug:

1. Create and download a `client_secret.json` from Google
 - Go to the [Google API Console](https://console.developers.google.com/apis/).
 - From the menu bar, select a project or create a new project.
 - To open the Google API Library, from the Navigation menu, select APIs & Services > Library.
 - Search for "Google Photos Library API". Select the correct result and click Enable.
 - Under Credentials for your project, create "OAuth Client ID" for **Desktop apps** and open the newly created credentials link
 - Download JSON as `client_secret.json` somewhere useful

```bash
$ python3 -m autoalbum.configurator
$ python3 -m autoalbum
$ python3 -m autoalbum autoalbum.behavior.n_most_recent # Use some defaults
$ python3 -m autoalbum autoalbum.behavior.n_most_recent -n 10 # Most explicit
$ python3 -m autoalbum --help # if you want help
```

## Features
1. Interactive CLI configurator utility (run this first)
2. Dynamic module loading for easy breezy extensibility
3. An overengineered architecture for something I could have solved in a single, 100-line script
4. Does not actually do anything

## Future features
1. **Come back to this when/if the Photos API does [what I need it to](https://issuetracker.google.com/issues/132274769)**
2. More behaviors?

## Contributions
Suggestions and contributions are always welcome. Please open an issue or submit a PR.
Contribution by Google Photos to enable their API is also welcome.
