import zipfile
import os


BATCH_NUM = os.getenv("BATCH_NUM")


if __name__ == "__main__":
    os.makedirs("output_zip", exist_ok=True)
    output_file = f"output_zip/batch_{BATCH_NUM}.zip"
    input_file = f"output/batch_{BATCH_NUM}.json"
    filename = os.path.basename(input_file)
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(input_file, arcname=filename)
