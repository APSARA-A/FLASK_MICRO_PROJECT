def odd_index(text):
    result=" "
    for i in range(len(text)):
        if i % 2 ==0:
            result += text[i]
    return result


text=input("enter a string")
print("string after removing odd indexed characters:",odd_index(text))
