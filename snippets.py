insert_after = 0
for dep in getfullargspec( meer ).args:
    index = deps.index( dep )
    if index > insert_after:
        insert_after = index
else:
    deps.insert( insert_after + 1, meer.__name__  )

print( deps )
