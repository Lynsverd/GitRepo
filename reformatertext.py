with open('output.txt', 'r', encoding='utf-8') as file:
    for line in file:
        parts = line.strip().split('\t')
        if len(parts) == 2:
            image, answer = parts
            print(f"{{ image: '{answer}', answer: '{image.lower()}' }},")
