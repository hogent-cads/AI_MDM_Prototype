"""
Common functions and classes for the clean_duplication function.
"""
# pylint: disable=no-name-in-module
from string import punctuation
from unicodedata import combining, category, normalize
from collections import defaultdict
from typing import List, Set, Union, DefaultDict
from itertools import permutations
from math import ceil
import pandas as pd
import dask.dataframe as dd
import dask
from metaphone import doublemetaphone
from rapidfuzz.distance.Levenshtein import distance as LevenshteinDistance
import config as cfg


class FuzzyMatcher:
    """
    Performs clustering methods on data.
    """

    # pylint: disable=too-many-instance-attributes

    clusters: pd.Series
    _df: dd.DataFrame
    _counts: pd.Series
    _df_name: str
    _col: str
    _ngram: int
    _radius: int
    _block_size: int

    def _to_dask(self, df: Union[pd.DataFrame, dd.DataFrame]) -> dd.DataFrame:
        """Convert a dataframe to a dask dataframe."""
        if isinstance(df, dd.DataFrame):
            return df

        df_size = df.memory_usage(deep=True).sum()
        npartitions = ceil(df_size / 128 / 1024 / 1024)  # 128 MB partition size
        return dd.from_pandas(df, npartitions=npartitions)

    def __init__(self, df: Union[pd.DataFrame, dd.DataFrame],
                 col: str, df_name: str, ngram, radius, block_size):
        self.clusters = pd.Series(dtype=object)
        self._df = self._to_dask(df)
        cfg.logger.debug("FuzzyMatcher: __init__: df.head = %s", self._df.head())
        self._counts = pd.Series(dtype=object)
        self._df_name = df_name
        self._col = col
        self._ngram = ngram
        self._radius = radius
        self._block_size = block_size
        self._df[self._col] = self._df[self._col].astype(str)

    def cluster(self, cluster_method: str) -> None:
        """
        Create clusters using the given clustering method.
        """

        if cluster_method == "levenshtein":
            self._nearest_neighbours_cluster()
        else:
            self._key_collision_cluster(cluster_method)

    def _key_collision_cluster(self, cluster_method: str) -> None:
        """
        Create clusters using a key collision method.
        Clusters are a Pandas Series of lists (each list represents a cluster).
        """
        key_funcs = {
            "fingerprint": self._finger_print_key,
            "ngram-fingerprint": self._ngram_finger_print_key,
            "phonetic-fingerprint": self._phonetic_fingerprint_key,
        }
        key_func = key_funcs[cluster_method]
        counts = self._df[self._col].value_counts(sort=False)
        # create dataframe containing unique values
        df = counts.index.to_frame(name=self._col)
        # create a column "key" containing keys created by the given key collision method
        df["key"] = df[self._col].map(key_func)
        # put items with the same key into the same list
        clusters = df.groupby("key")[self._col].apply(list, meta=(self._col, "object"))
        clusters = clusters.loc[clusters.map(len) > 1]
        clusters, self._counts = dask.compute(clusters, counts)

        cfg.logger.debug("FuzzyMatcher: _key_collision_cluster: clusters = %s", clusters)
        # sort by the size of each cluster, so that larger clusters appear first
        self.clusters = clusters.sort_values(
            key=lambda x: x.map(len), ascending=False).reset_index(
            drop=True
        )

    def _nearest_neighbours_cluster(self) -> None:
        """
        Performs nearest neighbour clustering.
        Blocking is used to speed up the process, blocks are obtained where strings in the same
        block share a substring of a given blocking size. Only strings within the same block are
        compared using the levenshtein distance function.

        Method from OpenRefine: https://github.com/OpenRefine/OpenRefine/wiki/Clustering-In-Depth
        and simile-vicino: https://code.google.com/archive/p/simile-vicino/
        """
        blocks: DefaultDict[str, Set[str]] = defaultdict(set)
        counts = self._df[self._col].value_counts(sort=False)
        # create dataframe containing unique values
        df = counts.index.to_frame(name=self._col)
        # put strings in blocks
        populate_blocks = df[self._col].apply(
            self._populate_blocks, args=(blocks, self._block_size), meta=(self._col, "object")
        )
        _, self._counts = dask.compute(populate_blocks, counts)

        # compare strings in the same block and create clusters
        self.clusters = self._get_nearest_neighbour_clusters(blocks, self._radius)

    @staticmethod
    def _populate_blocks(val: str, blocks: DefaultDict[str, Set[str]], block_size: int) -> None:
        """
        Create n gram tokens of the given string and place the string into the block
        for each n gram.
        """
        tokens = _ngram_tokens(val, block_size)
        for token in tokens:
            blocks[token].add(val)

    @staticmethod
    def _get_nearest_neighbour_clusters(
        blocks: DefaultDict[str, Set[str]], radius: int
    ) -> pd.Series:
        """
        Compare every pair of strings in each block and add to cluster if
        their distance is less than the given radius.
        """
        cluster_map: DefaultDict[str, Set[str]] = defaultdict(set)
        for block in blocks.values():
            for center, val in permutations(block, 2):
                if val in cluster_map[center]:
                    continue

                cluster_map[center].add(center)
                dist = LevenshteinDistance(center, val)
                if dist <= radius or radius < 0:
                    cluster_map[center].add(val)

        # remove duplicate clusters and clusters of length 1
        unique_clusters = set(
            frozenset(cluster) for cluster in cluster_map.values() if len(cluster) > 1
        )
        # convert to list of lists
        clusters = [list(cluster) for cluster in unique_clusters]
        # sort by the size of each cluster, so that larger clusters appear first
        return pd.Series(sorted(clusters, key=len, reverse=True))

    @staticmethod
    def _finger_print_key(val: str) -> str:
        """
        Generates a fingerprint key from a given string.

        - remove leading and trailing whitespace
        - convert to lowercase
        - remove punctuation and control characters
        - normalize extended western characters to ASCII
        - split into whitespace separated tokens
        - sort tokens and remove duplicates
        - join tokens back together

        Method taken from OpenRefine:
        https://github.com/OpenRefine/OpenRefine/wiki/Clustering-In-Depth
        """
        val = val.strip()
        val = val.lower()
        val = val.translate(str.maketrans("", "", punctuation))
        # remove control characters
        val = "".join(ch for ch in val if category(ch)[0] != "C")
        val = normalize_non_ascii(val)
        return " ".join(sorted(set(val.split())))

    @staticmethod
    def _phonetic_fingerprint_key(val: str) -> str:
        """
        Generates n-gram fingerprint from the given string.
        Uses the double metaphone algorithm.
        """
        primary, secondary = doublemetaphone(val)
        if primary == secondary:
            secondary = ""
        return f"{primary},{secondary}"

    def _ngram_finger_print_key(self, val: str) -> str:
        """
        Generates n-gram fingerprint from the given string.

        - convert to lowercase
        - remove punctuation, whitespace and control characters
        - normalize extended western characters to ASCII
        - get string n-grams
        - sort n-grams and remove duplicates
        - join sorted n grams back together

        Method taken from OpenRefine:
        https://github.com/OpenRefine/OpenRefine/wiki/Clustering-In-Depth
        """
        return "".join(sorted(set(_ngram_tokens(val, self._ngram))))


def _ngram_tokens(val: str, n: int) -> List[str]:
    """
    Create n-gram tokens from the given string.
    """
    val = val.strip()
    val = val.lower()
    val = " ".join(val.split())
    val = val.translate(str.maketrans("", "", punctuation))
    # remove control characters
    val = "".join(ch for ch in val if category(ch)[0] != "C")
    val = normalize_non_ascii(val)
    return [val[i : i + n] for i in range(len(val) - n + 1)]


def normalize_non_ascii(val: str) -> str:
    """
    Normalize extended western characters to ascii. (remove accents)
    """
    nfkd_form = normalize("NFKD", val)
    return "".join([c for c in nfkd_form if not combining(c)])