import os
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import logging
from functools import partial

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def convert_feather_to_csv(file_path, base_dir, target_dir):
    try:
        df = pd.read_feather(f"{base_dir}/{file_path}")
        csv_file_path = f"{target_dir}/{file_path.replace('.feather', '.csv')}"
        df.to_csv(csv_file_path, index=False)
        return csv_file_path
    except Exception as e:
        logger.error(f"Error converting {file_path}: {e}")
        return None


def main():
    base_dir = "1min_2024-12-01_2025-04-22"
    target_dir = "okx_csv_data"
    os.makedirs(target_dir, exist_ok=True)

    feather_files = [f for f in os.listdir(base_dir) if f.endswith(".feather")]
    _fun = partial(convert_feather_to_csv, base_dir=base_dir, target_dir=target_dir)

    logger.info("start converting feather files to csv......")
    converted_files = []
    with tqdm(total=len(feather_files)) as p_bar:
        with ProcessPoolExecutor() as executor:
            for result in executor.map(_fun, feather_files):
                if result:
                    converted_files.append(result)
                p_bar.update()

    logger.info("end of converting feather files to csv.\n")
    return converted_files


if __name__ == "__main__":
    main()