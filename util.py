from enum import Enum

AlignmentColours = {
        "Good": 0x00FF00,
        "Neutral": 0x888888,
        "Evil": 0xFF0000,
        "Ball": 0xFFFFFF,
        "Traveller": 0xFFFF00
        }



def levenshtein_distance(s, t):
    m, n = len(s), len(t)
    d = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        d[i][0] = i
    
    for j in range(n + 1):
        d[0][j] = j
    
    for j in range(1, n + 1):
        for i in range(1, m + 1):
            if s[i - 1] == t[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = min(d[i - 1][j], d[i][j - 1], d[i - 1][j - 1]) + 1
    
    return d[m][n]


def find_most_similar_string(string, string_array):
    closest_string = None
    closest_distance = float('inf')
    
    for candidate_string in string_array:
        distance = levenshtein_distance(string, candidate_string)
        if distance < closest_distance:
            closest_distance = distance
            closest_string = candidate_string
    
    return closest_string
