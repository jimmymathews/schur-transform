# Using GAP to calculate symmetric group characters

Character tables are computed with [GAP](https://www.gap-system.org/) (the Groups, Algorithms, and Programming computer algebra system). We used GAP version 4.11.1.

You can install GAP on your computer by following the [installation instructions](https://www.gap-system.org/Download/index.html). Ensure `gap` is on the path, or else modify `generate_characters.sh` accordingly.

Then, in this directory, run:

```bash
./generate_characters.sh
```

Files `s2.csv`, `s3.csv`, ... will be created, as well as a table `symmetric_group_conjugacy_classes.csv` with additional information about the rows and columns.

The contents of `s3.csv` look like this:

| |1+1+1|2+1|3|
|-|-----|---|-|
|1+1+1|1|1|1|
|2+1|2|0|-1|
|3|1|-1|1|

Each row provides the values of one irreducible character function. Care was taken to ensure that these rows are appropriately labelled by integer partitions. The desire to ensure this was one reason that we opted to use GAP directly rather than the SageMath wrapper around GAP. (See [discussion](https://math.stackexchange.com/questions/2348878/labels-for-irreducible-symmetric-group-characters).)

The contents of `symmetric_group_conjugacy_classes.csv` look like this:

|Symmetric group|Partition|Conjugacy class size|
|---------------|---------|--------------------|
|S2|1+1|1|
|S2|2|1|
|S3|1+1+1|1|
|S3|2+1|3|
|S3|3|2|
|S4|1+1+1+1|1|
|S4|2+1+1|6|
|S4|2+2|3|
|S4|3+1|8|
|S4|4|6|
|S5|1+1+1+1+1|1|
|S5|2+1+1+1|10|
|S5|2+2+1|15|
|S5|3+1+1|20|
|S5|3+2|20|
|S5|4+1|30|
|S5|5|24|
|S6|1+1+1+1+1+1|1|
|S6|2+1+1+1+1|15|
|S6|2+2+1+1|45|
|S6|2+2+2|15|
|S6|3+1+1+1|40|
|S6|3+2+1|120|
|S6|3+3|40|
|S6|4+1+1|90|
|S6|4+2|90|
|S6|5+1|144|
|S6|6|120|
|...|...|...|