with open("scripts/f1.txt", "r", encoding="utf-8") as f1:
    d1 = f1.readlines()
    
with open("scripts/f2.txt", "r", encoding="utf-8") as f2:
    d2 = f2.readlines()
    
for l1, l2 in zip(d1, d2):
    if l1 != l2:
        print(l1)
        print(l2)
        print("\n\n")    
    