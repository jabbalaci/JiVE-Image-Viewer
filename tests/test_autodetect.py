from jive import autodetect as ad


def test_subreddit_url():
    url = "https://www.reddit.com/r/wallpapers/"
    assert ad.detect(url) == (ad.AutoDetectEnum.subreddit_url, "wallpapers")
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
    assert ad.detect("wallpapers") == (ad.AutoDetectEnum.subreddit_name, "wallpapers")


def test_subreddit_r_name():
    assert ad.detect("/r/wallpapers") == (ad.AutoDetectEnum.subreddit_r_name, "wallpapers")
    assert ad.detect("/r/pics") == (ad.AutoDetectEnum.subreddit_r_name, "pics")
    assert ad.detect("/r/Pics") == (ad.AutoDetectEnum.subreddit_r_name, "Pics")

    assert ad.detect("r/wallpapers") == None    # invalid


def test_sequence_url():
    url = "http://www.website.com/[001-030].jpg"
    assert ad.detect(url) == (ad.AutoDetectEnum.sequence_url, )
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
    assert ad.detect(url) != (ad.AutoDetectEnum.sequence_url,)
    assert ad.detect(url) == (ad.AutoDetectEnum.image_url,)
    url = "http://www.website.com/something.jpg"
    assert ad.detect(url) != (ad.AutoDetectEnum.sequence_url, )
    assert ad.detect(url) == (ad.AutoDetectEnum.image_url, )