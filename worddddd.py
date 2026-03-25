from wordcloud import WordCloud
import matplotlib.pyplot as plt

words = {
    'sweet': 18, 'roasted': 16, 'fresh': 14, 'earthy': 12, 'fruity': 11,
    'nutty': 10, 'smoky': 9, 'meaty': 9, 'bitter': 8, 'tropical': 8,
    'citrusy': 7, 'greasy': 7, 'caramelized': 7, 'ripe': 7, 'woody': 6,
    'floral': 6, 'sour': 6, 'leathery': 5, 'cheese': 5, 'bacon': 5,
    'strong': 5, 'burnt': 4, 'fatty': 4, 'deep': 4, 'spicy': 4,
    'onion': 4, 'grassy': 3, 'beefiness': 3, 'bread': 3, 'pleasant': 3,
    'warm': 3, 'ripeness': 3, 'musky': 2, 'rubbery': 2, 'soil': 2,
    'chocolate': 2, 'artificial': 2, 'vinegar': 2, 'peel': 2,
}

palette = ['#D95F3B', '#E07A6A', '#E8A96A', '#E8C96A', '#7DBF7D',
           '#5FADA6', '#6B9FC4', '#7B8FCC', '#9B7FBF']

def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    idx = list(words.keys()).index(word) % len(palette)
    hex_color = palette[idx]
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return f'rgb({r},{g},{b})'

wc = WordCloud(
    width=1200,
    height=600,
    background_color='white',
    prefer_horizontal=1.0,
    relative_scaling=0.6,
    min_font_size=12,
    max_font_size=120,
    colormap=None,
    color_func=color_func,
    collocations=False,
).generate_from_frequencies(words)

plt.figure(figsize=(10, 6))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.tight_layout(pad=0)
plt.savefig('wordcloud.png', dpi=300, bbox_inches='tight')
plt.savefig('wordcloud.pdf', dpi=300, bbox_inches='tight')
plt.show()
print("Saved: wordcloud_smellai.png")