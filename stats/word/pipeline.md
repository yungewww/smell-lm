Task1 + Task2 -> CSV

统计所有词，保留频率>2的
用人工筛选出其中跟气味相关的词
再手动把这些词归入5个类别

categories = {
    "Sweet":        ["sweet", "caramelized", "syrupy", "chocolate", "cinnamon", "fruity", "berry", "tropical", "ripe"],
    "Savory":       ["savory", "meaty", "umami", "greasy", "fatty", "buttery", "cheesy", "yeasty"],
    "Sour":         ["sour", "tart", "vinegary", "citrus", "citrusy", "bitter"],
    "Burnt/Smoked": ["roasted", "smoky", "smoked", "charred", "roasty", "burnt", "toasted", "grilled"],
    "Fresh":        ["fresh", "crisp", "refreshing", "floral", "flower", "fragrant", "mint", "leafy",
                     "grassy", "spice", "earthy", "wood", "musky", "nutty"]
}

