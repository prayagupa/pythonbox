matrix = [[0 for m in range(3)] for n in range(3)]

matrix[0][0] = 100
matrix[1][1] = 500

print("matrix[0][0]", matrix)

line_items = []

line_items += [1, 2, 3]
if line_items:
    print("not empty" + str(line_items))
else:
    print("empty")


#function to transform your list into a string
def stringify(v): 
    return "('%s', '%s', %s, %s)" % (v[0], v[1], v[2], v[3])

def to_batch(rows):
    #transform all to string
    vals = map(stringify, rows)

    #glue them together
    batchData = ", ".join(v for v in vals)

    return batchData

## usage
rows = [
        ["samsung tv", "tv", "tvv", "in-grid"],
        ["LG tv", "tv", "tvv", "in-grid"]
        ]

#complete the SQL
sql = "INSERT INTO `table_name`(`column`, `column_1`, `column_2`, `column_3`) \
VALUES %s" % to_batch(rows)

print(sql)


