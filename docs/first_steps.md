First steps after installation
==============================

The application can extract images from Imgur albums / galleries,
and from Tumblr posts too. These features only work if you have
the necessary **API keys**.

You can acquire these keys for free.

Once you have the keys, set them as **environment variables**.

Note that the app. will work without these API keys too, but
in that case Imgur and Tumblr links won't be processed. So it
is highly recommended that you get these keys.

Linux
-----

For instance, under Linux, add the following lines
to the end of your `~/.bashrc` file:

    TUMBLR_API_KEY=...

    IMGUR_CLIENT_ID=...
    IMGUR_CLIENT_SECRET=...

Windows
-------

The process is similar. Here is a [short video](https://www.youtube.com/watch?v=bEroNNzqlF4)
that shows you how to set environment variables.

Tip
---

Well, you can also find (lots of) API keys on GitHub too...
Check out this blog post for more info:
https://ubuntuincident.wordpress.com/2013/03/04/find-api-keys-on-github/ .
You can also check out the file `tools/verify_your_api_keys.py`...
