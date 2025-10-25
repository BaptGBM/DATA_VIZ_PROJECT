import pandas as pd
import io

def load_data(path):
    # Ouvre le fichier en ignorant les caractères problématiques
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    df = pd.read_csv(io.StringIO(content), low_memory=False)
    return df