from speedict  import Rdict, Options

path = str("./test_dict")

# create a Rdict with default options at `path`
db = Rdict(path)

# storing numbers
db[1.0] = 1
db[1] = 1.0
db["huge integer"] = 2343546543243564534233536434567543
db["good"] = True
db["bad"] = False
db["bytes"] = b"bytes"
db["this is a list"] = [1, 2, 3]
db["store a dict"] = {0: 1}

# for example numpy array
import numpy as np
import pandas as pd
db[b"numpy"] = np.array([1, 2, 3])
db["a table"] = pd.DataFrame({"a": [1, 2], "b": [2, 1]})

# close Rdict
db.close()

# reopen Rdict from disk
db = Rdict(path)
assert db[1.0] == 1
assert db[1] == 1.0
assert db["huge integer"] == 2343546543243564534233536434567543
assert db["good"] == True
assert db["bad"] == False
assert db["bytes"] == b"bytes"
assert db["this is a list"] == [1, 2, 3]
assert db["store a dict"] == {0: 1}
assert np.all(db[b"numpy"] == np.array([1, 2, 3]))
assert np.all(db["a table"] == pd.DataFrame({"a": [1, 2], "b": [2, 1]}))

# iterate through all elements
for k, v in db.items():
    print(f"{k} -> {v}")

# batch get:
print(db[["good", "bad", 1.0]])
# [True, False, 1]

# delete Rdict from dict
db.close()
Rdict.destroy(path)