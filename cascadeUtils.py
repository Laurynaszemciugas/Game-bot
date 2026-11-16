import os

def generate_negative_file():
    with open("neg.txt", "w") as f:
        for filename in os.listdir("Negative"):
            f.write('Negative/'+filename+'\n')