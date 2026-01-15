IDs = range(4616)

with open("params.txt", "w") as f:
    for idx in IDs:
        f.write(f"{idx} \n")


batch_size = 1000  # <= cluster limit

with open("params.txt") as f:
    lines = f.readlines()

for i, start in enumerate(range(0, len(lines), batch_size)):
    with open(f"params_batch_{i}.txt", "w") as f_out:
        f_out.writelines(lines[start : start + batch_size])
