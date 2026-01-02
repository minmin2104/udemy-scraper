import json


def count_null(json_data):
    none_list = [d for d in json_data if d is None]
    return len(none_list)


def get_link(path):
    with open(path, "r") as f:
        data = json.load(f)
    return data


def get_failed_link(batch_num, result_path):
    batch_link = f"batches/batch_{batch_num:02}.json"
    expected_url = get_link(batch_link)
    with open(result_path, "r") as f:
        data = json.load(f)
    actual_url = [d["url"] for d in data if d]
    for link in expected_url:
        if link not in actual_url:
            print(link)


if __name__ == "__main__":
    filename = "batch_00.json"
    with open(filename, "r") as f:
        data = json.load(f)
    print(count_null(data))
    get_failed_link(0, "batch_00.json")
