Command-line arguments
======================

Currently, only one command-line argument can be passed to JiVE,
which can be a local file, a local folder, or a URL (a subreddit's URL,
an Imgur album's URL, a Tumblr post's URL, etc.), or a subreddit's name.
JiVE will try to auto-detect this parameter.

Examples
--------

normal launch without any parameter
```
$ jive
```

open images in the current folder
```
$ jive .
```

open a given image
```
$ jive folder/image.png
```

open a folder that contains images
```
$ jive folder/
```

open an image by its URL
```
$ jive https://i.imgur.com/k489QN8.jpg
```

open an Imgur album / gallery
```
* jive https://imgur.com/gallery/9p0gCyv
* jive https://imgur.com/a/uAFvn
```

open a Tumblr post
```
$ jive https://different-landscapes.tumblr.com/post/174158537319
```

open a subreddit
```
$ jive https://www.reddit.com/r/EarthPorn/
$ jive earthporn
```

open a sequence URL (Warning! NSFW example!)
```
$ jive "https://content9.erosberry.com/digitaldesire.com/6003/[00-03].jpg"
```

Notice that the argument is between quotes because of the square brackets.
