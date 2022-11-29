from phml.builder import p
from phml.utils import inspect

if __name__ == "__main__":
    node = p("""<!-- Some Comment
multiline -->
""")
    print(node.stringify(2))
    # with open("file_1.txt", "r") as file_1:
    #     data_1 = file_1.readlines()
    
    # with open("file_2.txt", "r") as file_2:
    #     data_2 = file_2.readlines()
    
    # count = 0
    # for L1, L2 in zip(data_1, data_2):
    #     if L1 != L2:
    #         print(L1)
    #         print(L2)
    #         print("\n\n")
    #         count += 1
            
    # print(f"{count} total different lines")
    