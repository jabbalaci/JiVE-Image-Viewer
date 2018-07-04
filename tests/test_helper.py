from jive import helper as h


def test_fold_urls():
    lst = ["node1", "node2", "node3"]
    res = h.fold_urls(lst)
    assert res == "node[1-3]"

    lst = ["node01", "node02", "node03"]
    res = h.fold_urls(lst)
    assert res == "node[01-03]"

    lst = ["http://www.website.com/005.jpg", "http://www.website.com/006.jpg", "http://www.website.com/007.jpg"]
    res = h.fold_urls(lst)
    assert res == "http://www.website.com/[005-007].jpg"


def test_unfold_sequence_url():
    text = "node[1-3]"
    res = h.unfold_sequence_url(text)
    assert res == ["node1", "node2", "node3"]

    text = "node[01-03]"
    res = h.unfold_sequence_url(text)
    assert res == ["node01", "node02", "node03"]