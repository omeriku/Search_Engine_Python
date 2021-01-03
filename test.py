# import math
#
# vec1 = [0, 1, 8]
# vec2 = [5, 0, 2]
# vec3 = [2, 2.5, 20]
# query = [1, 2, 10]

import math

vec1 = [7, 0.2]
vec2 = [4, 25]
vec3 = [18.5, 10.5]
query = [9, 5.4]
matrix = {"d1": vec1, "d2": vec2, "d3":  vec3}
d3 = {}
d2 = {}
print("2D")
for vec in matrix:
    mone = 0
    mechane_vec = 0
    mechane_query = 0
    for i, num in enumerate(matrix[vec]):
        mone += query[i] * num
        mechane_vec += pow(num, 2)
        mechane_query += pow(query[i], 2)
    mechane_total = math.sqrt(mechane_vec) * math.sqrt(mechane_query)

    print("cos similarity q and", vec, ": ", mone/mechane_total)

print()
print("3D")


vec1 = [0, 1, 8]
vec2 = [5, 0, 2]
vec3 = [2, 2.5, 20]
query = [1, 2, 10]
matrix = {"d1": vec1, "d2": vec2, "d3":  vec3}

for vec in matrix:
    mone = 0
    mechane_vec = 0
    mechane_query = 0
    for i, num in enumerate(matrix[vec]):
        mone += query[i] * num
        mechane_vec += pow(num, 2)
        mechane_query += pow(query[i], 2)
    mechane_total = math.sqrt(mechane_vec) * math.sqrt(mechane_query)

    print("cos similarity q and", vec, ": ", mone/mechane_total)




# for vec in matrix:
#     for doc in matrix:
#         if vec == doc:
#             continue
#         distance = 0
#         for i, num in enumerate(matrix[vec]):
#             distance += pow(matrix[vec][i] - matrix[doc][i], 2)
#         distance = math.sqrt(distance)
#         # print("The distance between", vec, "and", doc, "is:", distance)
#         key = vec + " " + doc
#         d2[key] = distance

# vec1 = [0, 1, 8]
# vec2 = [5, 0, 2]
# vec3 = [2, 2.5, 20]
# query = [1, 2, 10]
# matrix = {"d1": vec1, "d2": vec2, "d3":  vec3, "q": query}
#
# for vec in matrix:
#     for doc in matrix:
#         if vec == doc:
#             continue
#         distance = 0
#         for i, num in enumerate(matrix[vec]):
#             distance += pow(matrix[vec][i] - matrix[doc][i], 2)
#         distance = math.sqrt(distance)
#         # print("The distance between", vec, "and", doc, "is:", distance)
#         key = vec + " " + doc
#         d3[key] = distance
#
# for i, num in enumerate(d2):
#     print("2D/3D",num ,"Ratio is :", d2[num]/d3[num] )