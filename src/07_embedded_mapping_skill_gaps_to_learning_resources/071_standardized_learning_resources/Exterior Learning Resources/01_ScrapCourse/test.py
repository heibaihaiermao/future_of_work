
import pandas as pd

df = pd.read_csv("Cate_3_learningResources 1.csv")

print(df.tail(20))
print(df[df.iloc[:,0].astype(str).str.contains("RShiny", na=False)])
