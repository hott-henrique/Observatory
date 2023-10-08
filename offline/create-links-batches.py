import argparse
import os
import random
import zipfile


def generate_links_file(out_file: str):
    with open(out_file, mode="w") as f:
        for i in range(499897):
            print(f"https://www.google.com/search?q={i}", file=f)

def main(file: str,
         generate_test=False,
         n_batches: int=2):
    if generate_test:
        generate_links_file(file)

    with open(file, mode="r") as f:
        links = f.readlines()

    random.shuffle(links)

    links_per_batch = int(len(links) / n_batches)
    missing = len(links) - (links_per_batch * n_batches)

    with zipfile.ZipFile("batches.zip", mode="w") as z:
        for i in range(n_batches):
            batch_file_name = f"batch{i}-links.txt"

            with open(batch_file_name, mode="w") as f:
                start = i * links_per_batch
                end = (i + 1) * links_per_batch

                if i == n_batches - 1:
                    end = end + missing

                batch_links = links[start: end]

                print(*batch_links, end='', file=f)

            z.write(batch_file_name)

            os.remove(batch_file_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--generate-test", action="store_true", default=False)
    parser.add_argument("--file", type=str, default="links.txt", required=False)
    parser.add_argument("--n", type=int, default=2, required=False)

    args = parser.parse_args()

    main(generate_test=args.generate_test,
         file=args.file,
         n_batches=args.n)

