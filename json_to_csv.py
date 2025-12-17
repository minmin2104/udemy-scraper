import os
import pandas as pd


if __name__ == '__main__':
    filepath = './output/scrap_course_metadata.json'
    df = pd.read_json(filepath)

    output_dir = 'sheets/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    df.to_csv(f'{output_dir}/udemy_course.csv')
