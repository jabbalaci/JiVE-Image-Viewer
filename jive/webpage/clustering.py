"""
blog post:
https://pythonadventures.wordpress.com/2013/11/08/extracting-relevant-images-from-xxx-galleries-using-text-clustering/
"""

from pprint import pprint
from typing import Dict, List

from jive import helper

DISTANCE = 10


class Cluster:
    """
    Clustering a list of (sorted!) strings.

    I use it for clustering URLs. After extracting all the links (or images)
    from a web page, I use this class to group together similar URLs. It also
    identifies the largest cluster.
    """
    def __init__(self) -> None:
        self.clusters: Dict[str, Dict] = {'clusters': {}}
 
    def clustering(self, elems, distance: int = DISTANCE) -> None:
        """
        Clusterize the input elements.

        Input: list of words (e.g. list of URLs). It MUST be sorted!

        Process: build a dictionary where keys are cluster IDs (int) and
                 values are lists (elements in the given cluster)
        """
        clusters: Dict = {}
        cid = 0

        for i, line in enumerate(elems):
            if i == 0:
                clusters[cid] = []
                clusters[cid].append(line)
            else:
                last = clusters[cid][-1]
                if helper.lev_dist(last, line) <= distance:
                    clusters[cid].append(line)
                else:
                    cid += 1
                    clusters[cid] = []
                    clusters[cid].append(line)
        #
        self.clusters['clusters'] = clusters
        self.clusters['clusters']['largest'] = self.get_largest_cluster()
        self.clusters['clusters']['number_of_clusters'] = cid + 1

    def get_largest_cluster(self) -> List[str]:
        clusters = self.clusters['clusters']

        maxi_k = -1
        maxi_v = -1
        first = True

        for k, v in clusters.items():
            if first:
                maxi_k = k
                maxi_v = len(v)
                first = False
            else:
                if len(v) > maxi_v:
                    maxi_v = len(v)
                    maxi_k = k
        #
        result: List[str] = clusters[maxi_k] if maxi_k != -1 else []
        return result

    def show(self) -> None:
        pprint(self.clusters)


# def get_clusters(elems):
#     elems = sorted(elems)
#     cl = Cluster()
#     cl.clustering(elems)
#     result = cl.clusters['clusters']
#     pprint(result)
#     return result
