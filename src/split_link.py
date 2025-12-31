import json
import os


def write_to_json(path, payload):
    with open(path, "w") as f:
        json.dump(payload, f, indent=4)


if __name__ == "__main__":
    data = []
    with open("all_courses_link.json", "r") as f:
        data = json.load(f)
    acc = []
    counter = 0
    batch = 0
    output_dir = "batches"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    for link in data:
        acc.append(link)
        counter += 1
        if counter >= 4000:
            output_filename = f"{output_dir}/batch_{batch:02}.json"
            write_to_json(output_filename, acc)
            acc = []
            counter = 0
            batch += 1
