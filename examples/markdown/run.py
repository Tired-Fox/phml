from phml import HypertextManager

if __name__ == "__main__":
    with HypertextManager.open("src/index.phml") as phml:
        phml.render()
