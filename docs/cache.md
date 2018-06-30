[dev] cache
===========

JiVE has a cache that you can enable / disable in the preferences file.
The cache is a folder in the file system with a maximized size. When
you open an online image, it goes in the cache too. When you open this
image again, JiVE will check if it's in the cache. If it's there, then
the image is not downloaded again.

The cache works as a FIFO list (queue). New images are stored at the end. If the
cache's size gets too big, old images are removed until the cache's size
goes below the specified threshold.

JiVE can also do preloading. It means that when you open an image, the next
image is preloaded and kept in memory. When you go to the next image, it'll
appear very quickly. The previous image is also preloaded, thus browsing
forward and backward should be a smooth experience.

At any moment, maximum three images are kept in memory (previous, current, next).
