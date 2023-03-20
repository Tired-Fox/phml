if __name__ == "__main__":
    from phml import inspect, PHML

    phml = PHML()

    phml.load("sandbox/sample.phml")
    print(inspect(phml.ast))
    print(phml.render())
