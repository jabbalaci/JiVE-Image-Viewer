from jive import autodetect as ad


def test_subreddit_url():
    url = "https://www.reddit.com/r/wallpapers/"
    res = ad.detect(url)
    assert res == (ad.AutoDetectEnum.subreddit_url, "wallpapers")
    assert isinstance(res, tuple)

    url = "https://www.reddit.com/r/wallpapers"
    assert ad.detect(url) == (ad.AutoDetectEnum.subreddit_url, "wallpapers")
    url = "http://www.reddit.com/r/wallpapers/"
    assert ad.detect(url) == (ad.AutoDetectEnum.subreddit_url, "wallpapers")
    url = "http://www.reddit.com/r/wallpapers"
    assert ad.detect(url) == (ad.AutoDetectEnum.subreddit_url, "wallpapers")
    url = "http://reddit.com/r/wallpapers/"
    assert ad.detect(url) == (ad.AutoDetectEnum.subreddit_url, "wallpapers")
    url = "http://reddit.com/r/wallpapers"
    assert ad.detect(url) == (ad.AutoDetectEnum.subreddit_url, "wallpapers")
    url = "http://old.reddit.com/r/wallpapers"
    assert ad.detect(url) == (ad.AutoDetectEnum.subreddit_url, "wallpapers")
    url = "http://old.reddit.com/r/wallpapers/"
    assert ad.detect(url) == (ad.AutoDetectEnum.subreddit_url, "wallpapers")
    url = "https://old.reddit.com/r/wallpapers"
    assert ad.detect(url) == (ad.AutoDetectEnum.subreddit_url, "wallpapers")
    url = "https://old.reddit.com/r/wallpapers/"
    assert ad.detect(url) == (ad.AutoDetectEnum.subreddit_url, "wallpapers")


def test_subreddit_name():
    res = ad.detect("wallpapers")
    assert res == (ad.AutoDetectEnum.subreddit_name, "wallpapers")
    assert isinstance(res, tuple)


def test_subreddit_r_name():
    res = ad.detect("/r/wallpapers")
    assert res == (ad.AutoDetectEnum.subreddit_r_name, "wallpapers")
    assert isinstance(res, tuple)

    assert ad.detect("/r/pics") == (ad.AutoDetectEnum.subreddit_r_name, "pics")
    assert ad.detect("/r/Pics") == (ad.AutoDetectEnum.subreddit_r_name, "Pics")

    assert ad.detect("r/wallpapers") == None    # invalid


def test_sequence_url():
    url = "http://www.website.com/[001-030].jpg"
    res = ad.detect(url)
    assert res == (ad.AutoDetectEnum.sequence_url, )
    assert isinstance(res, tuple)

    url = "http://www.website.com/[1-10].jpg"
    assert ad.detect(url) == (ad.AutoDetectEnum.sequence_url,)

    url = "http://www.website.com/[001-].jpg"
    assert ad.detect(url) != (ad.AutoDetectEnum.sequence_url,)
    assert ad.detect(url) == (ad.AutoDetectEnum.image_url,)
    url = "http://www.website.com/[-030].jpg"
    assert ad.detect(url) != (ad.AutoDetectEnum.sequence_url,)
    assert ad.detect(url) == (ad.AutoDetectEnum.image_url,)
    url = "http://www.website.com/[-].jpg"
    assert ad.detect(url) != (ad.AutoDetectEnum.sequence_url,)
    assert ad.detect(url) == (ad.AutoDetectEnum.image_url,)
    url = "http://www.website.com/something[2-5]/[1-10].jpg"
    assert ad.detect(url) == (ad.AutoDetectEnum.sequence_url,)
    url = "http://www.website.com/something.jpg"
    assert ad.detect(url) != (ad.AutoDetectEnum.sequence_url, )
    assert ad.detect(url) == (ad.AutoDetectEnum.image_url, )


def test_tumblr_post():
    url = "https://different-landscapes.tumblr.com/post/174158537319"
    res = ad.detect(url)
    assert res == (ad.AutoDetectEnum.tumblr_post, )
    assert isinstance(res, tuple)


def test_imgur_album():
    url = "https://imgur.com/a/9p0gCyv"
    res = ad.detect(url)
    assert res == (ad.AutoDetectEnum.imgur_album, )
    assert isinstance(res, tuple)

    url = "https://imgur.com/gallery/9p0gCyv"
    assert ad.detect(url) == (ad.AutoDetectEnum.imgur_album, )


def test_imgur_html_page_with_embedded_image():
    url = "https://imgur.com/k489QN8"
    res = ad.detect(url)
    assert res == (ad.AutoDetectEnum.imgur_html_page_with_embedded_image, "https://imgur.com/k489QN8.jpg")
    assert isinstance(res, tuple)