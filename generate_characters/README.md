# Using GAP to calculate symmetric group characters

Character tables are computed with [GAP](https://www.gap-system.org/) (the Graphs, Algorithms, and Programming computer algebra system). We used GAP version 4.11.1.

You can install GAP on your computer by following the [installation instructions](https://www.gap-system.org/Download/index.html).

Then, in this directory, run:

```bash
./generate_characters.sh
```

Files `s2.csv`, `s3.csv`, ... will be created, as well as a table `symmetric_group_conjugacy_classes.csv` with additional information about the rows and columns.

The contents of `s3.csv` look like this:

| |1+1+1|2+1|3|
|-|-----|---|-|
|1+1+1|1|2|1|
|2+1|-1|0|1|
|3|1|-1|1|
