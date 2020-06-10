Example usage:
```
$ python process.py --txt-file MC34_1h.txt --wells wells.csv > result.csv
```

I would recommend parsing individual txt files separately and appending to the CSV file like here:
```
$ python process.py --txt-file MC34_3h.txt --wells wells.csv >> result.csv
```
