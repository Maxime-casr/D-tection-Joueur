import pandas as pd

from app import lancer_app
from constantes.constantes import DATA_PATH


def main():
    df = pd.read_csv(DATA_PATH)
    lancer_app(df)


if __name__ == "__main__":
    main()
