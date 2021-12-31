gianna_results = 'data/manual_results/oldcsv/coordinates.gc.20210625.csv'
benoit_results = 'data/manual_results/oldcsv/coordinates-benoit-2021-06-25.csv'
parker_results = 'data/manual_results/oldcsv/coordinates-parker-2021-06-25-11_06_30.csv'

gcsv = read_csv(gianna_results)
bcsv = read_csv(benoit_results)
pcsv = read_csv(parker_results)

gx = gcsv.field2
gy = gcsv.field3
gcr = [[gx],[gy]]

bx = bcsv.field2
by = bcsv.field3
bcr = [[bx],[by]]

px = pcsv.field2
py = pcsv.field3
pcr = [[px],[py]]

gcr[*,0] = abs(gcr[*,0]-18)
gcr[*,1] = abs(gcr[*,1]-32)

bcr[*,0] = abs(bcr[*,0]-18)
bcr[*,1] = abs(bcr[*,1]-32)

pcr[*,0] = abs(pcr[*,0]-18)
pcr[*,1] = abs(pcr[*,1]-32)

gcr = [[gcsv.field1],[gcr]]
bcr = [[bcsv.field1],[bcr]]
pcr = [[pcsv.field1],[pcr]]

write_csv,'data/manual_results/gianna_results.csv',transpose(gcr)
write_csv,'data/manual_results/benoit_results.csv',transpose(bcr)
write_csv,'data/manual_results/parker_results.csv',transpose(pcr)

end