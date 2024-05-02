"""
    __    _ ____  ___    ____     _    __      ___ ____  ___  __________  ____
   / /   (_) __ \/   |  / __ \   | |  / /___ _/ (_) __ \/   |/_  __/ __ \/ __ \
  / /   / / / / / /| | / /_/ /   | | / / __ `/ / / / / / /| | / / / / / / /_/ /
 / /___/ / /_/ / ___ |/ _, _/    | |/ / /_/ / / / /_/ / ___ |/ / / /_/ / _, _/
/_____/_/_____/_/  |_/_/ |_|     |___/\__,_/_/_/_____/_/  |_/_/  \____/_/ |_|

* Reformulação de código: https://github.com/Gorgens/valida-als/blob/main/paisagens_sustentaveis/validacaoPaisagens2023.qmd
"""
import os
import glob
import rasterio
import subprocess
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject
import numpy as np
import matplotlib.pyplot as plt


class LiDARVAL:
    __author__ = "Leonardo Ippolito"
    __copyright__ = "NA"
    __credits__ = "Eric Gorgens"
    __license__ = "GPL"
    __version__ = "1.0.1"
    __maintainer__ = "Leonardo Ippolito"
    __email__ = "leonardo.rodrigues@cenibra.com.br"

    def __init__(self, fusion_folder: str, lastools_folder: str, np_folder: str, valida_folder: str) -> None:
        self.fusion_folder = fusion_folder
        self.lastools_folder = lastools_folder
        self.np_folder = np_folder
        self.valida_folder = valida_folder

    def base_rel(self, nome):
        print(os.path.join(self.np_folder, '*.las'))
        pipeline_1 = f"{os.path.join(self.fusion_folder, 'Catalog')} /drawtiles /countreturns /density:1,5,10 {os.path.join(self.np_folder, '*.las')} {os.path.join(self.valida_folder, f'{nome}_Catalog')}"
        pipeline_2 = f"{os.path.join(self.lastools_folder, 'lasinfo')} -cpu64 -i {os.path.join(self.np_folder, '*.las')} -merged -odir {self.valida_folder} -o {nome}_report.txt -cd -histo gps_time 20"
        os.system(pipeline_1)
        os.system(pipeline_2)
        return

    def return_density(self):
        pipeline = f"{os.path.join(self.fusion_folder, 'ReturnDensity')} /ascii {os.path.join(self.valida_folder, 'density.asc')} 1 {os.path.join(self.np_folder, '*.las')}"
        return os.system(pipeline)

    def dtm(self):
        pipeline_1 = f"{os.path.join(self.fusion_folder, 'GroundFilter')} {os.path.join(self.valida_folder, 'ground.las')} 8 {os.path.join(self.np_folder, '*.las')}"
        pipeline_2 = f"{os.path.join(self.fusion_folder, 'GridSurfaceCreate')} {os.path.join(self.valida_folder, 'mdtCriado.dtm')} 1 m m 0 0 0 0 {os.path.join(self.valida_folder, 'ground.las')}"
        pipeline_3 = f"{os.path.join(self.fusion_folder, 'DTM2ASCII')} {os.path.join(self.valida_folder, 'mdtCriado.dtm')} {os.path.join(self.valida_folder, 'mdtCriado.asc')}"
        os.system(pipeline_1)
        os.system(pipeline_2)
        os.system(pipeline_3)
        return

    @staticmethod
    def open_raster(path, expected_crs=None):
        with rasterio.open(path) as src:
            data = src.read(1, masked=True)
            meta = src.meta.copy()  # Make a copy of the metadata

            # Update CRS in the metadata if it's missing
            if src.crs is None:
                if expected_crs is None:
                    raise ValueError(f"No CRS found in raster {path} and no expected CRS provided.")
                else:
                    meta['crs'] = expected_crs  # Set the expected CRS in the metadata

            return data, meta, src.bounds

    def dtm_diff(self, dtm_entregue: str):
        dtm_calculado, meta_calculado, bounds_calculado = self.open_raster(os.path.join(self.valida_folder,"mdtCriado.asc"),'EPSG:4326')

        # Define the reference raster
        dtm_entregue, meta_entregue, bounds_entregue = self.open_raster(dtm_entregue, meta_calculado['crs'])

        # Calculate new transform and dimensions for alignment using actual bounds
        transform, width, height = calculate_default_transform(
            meta_entregue['crs'], meta_calculado['crs'], meta_entregue['width'], meta_entregue['height'],
            *bounds_entregue)

        dtm_entregue_resampled = np.empty(shape=(height, width), dtype=np.float32)

        # Resample dtm_entregue to match dtm_calculado
        reproject(
            source=dtm_entregue,
            destination=dtm_entregue_resampled,
            src_transform=meta_entregue['transform'],
            src_crs=meta_entregue['crs'],
            dst_transform=transform,
            dst_crs=meta_calculado['crs'],
            resampling=Resampling.nearest
        )

        # Resample dtm_calculado for consistent comparison
        dtm_calculado_resampled = np.empty(shape=(height, width), dtype=np.float32)
        reproject(
            source=dtm_calculado,
            destination=dtm_calculado_resampled,
            src_transform=meta_calculado['transform'],
            src_crs=meta_calculado['crs'],
            dst_transform=transform,
            dst_crs=meta_calculado['crs'],
            resampling=Resampling.nearest
        )

        # Calculate the difference and plot histogram
        difference = dtm_entregue_resampled - dtm_calculado_resampled
        plt.hist(difference.ravel(), bins=50, alpha=0.75)
        plt.title('Histogram of Differences')
        plt.xlabel('Value Difference')
        plt.ylabel('Frequency')
        return plt.show()

    def chm(self):
        files = glob.glob(os.path.join(self.np_folder, '*.las'))
        print(files)
        for filename in files:
            pipeline = f"{os.path.join(self.fusion_folder, 'GridMetrics')} /nointensity /nocsv /raster:max /ascii {os.path.join(self.valida_folder, 'mdtCriado.dtm')} 10 1 {os.path.join(self.valida_folder, os.path.splitext(os.path.basename(filename))[0] + '.asc')} {os.path.join(self.np_folder, os.path.basename(filename))}"
            process = subprocess.run(pipeline, shell=True)
            print("Command executed:", pipeline)
            print("Return code:", process.returncode)

        return
