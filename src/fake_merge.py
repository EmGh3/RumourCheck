import pandas as pd

old_fake = pd.read_csv("../dataset/Fake_processed.csv")
new_fake = pd.read_csv("../dataset/Fake_new.csv")

combined_fake = pd.concat([old_fake, new_fake], ignore_index=True)
combined_fake.to_csv("../dataset/Fake_combined.csv", index=False)
