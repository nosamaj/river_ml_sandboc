import pandas as pd 


#import packington.parquet
df_packington = pd.read_parquet('packington.parquet')
print(df_packington.head())