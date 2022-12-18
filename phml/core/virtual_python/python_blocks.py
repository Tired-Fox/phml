from re import sub


if __name__ == "__main__":
    mlb = MultiLineBlock(
        '''\
    {
        for name in names:
            yield """
            <li>{name}</li>
            """
    }    \
'''
    )

    print(mlb)
