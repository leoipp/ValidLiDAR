"""
    __    _ ____  ___    ____     _    __      ___ ____  ___  __________  ____
   / /   (_) __ \/   |  / __ \   | |  / /___ _/ (_) __ \/   |/_  __/ __ \/ __ \
  / /   / / / / / /| | / /_/ /   | | / / __ `/ / / / / / /| | / / / / / / /_/ /
 / /___/ / /_/ / ___ |/ _, _/    | |/ / /_/ / / / /_/ / ___ |/ / / /_/ / _, _/
/_____/_/_____/_/  |_/_/ |_|     |___/\__,_/_/_/_____/_/  |_/_/  \____/_/ |_|

* Reformulação de código: https://github.com/Gorgens/valida-als/blob/main/paisagens_sustentaveis/validacaoPaisagens2023.qmd
"""
import os


class LiDARVAL:
    __author__ = "Eric Gorgens"
    __copyright__ = "NA"
    __credits__ = "Leonardo Ippolito"
    __license__ = "GPL"
    __version__ = "1.0.1"
    __maintainer__ = "Leonardo Ippolito"
    __email__ = "leonardo.rodrigues@cenibra.com.br"

    def __init__(self, fusion_folder: str, lastools_folder: str, np_folder: str, valida_folder: str) -> None:
        self.fusion_folder = fusion_folder
        self.lastools_folder = lastools_folder
        self.np_folder = np_folder
        self.valida_folder = valida_folder

    def base_rel(self):
        pipeline_1 = f"{os.path.join(self.fusion_folder, 'Catalog')} /drawtiles /countreturns /density:1,4,8 {os.path.join(self.np_folder, '*.las')} {os.path.join(self.valida_folder, 'Catalog')}"
        pipeline_2 = f"{os.path.join(self.lastools_folder, 'lasinfo')} -cpu64 -i {os.path.join(self.np_folder, '*.las')} -merged -odir {self.valida_folder} -o report.txt -cd -histo gps_time 20"
        os.system(pipeline_1)
        os.system(pipeline_2)
        return

    def return_density(self):
        pipeline = f"{os.path.join(self.fusion_folder, 'ReturnDensity')} /ascii {os.path.join(self.valida_folder, 'density.asc')} 1 {os.path.join(self.np_folder, '*.las')}"
        return os.system(pipeline)

    def dtm(self):
        return

    def dtm_diff(self):
        return

    def chm(self):
        return