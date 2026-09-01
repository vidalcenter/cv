import easyocr
import os
import numpy as np
from PIL import Image

reader = easyocr.Reader(['pt', 'en'], gpu=False)
img_dir = r'c:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\meu_site\aulas\bioengenharia_de_solos\aulas\aula01_formacao_solos\img'

for fname in sorted(os.listdir(img_dir)):
    if fname.endswith('.png'):
        print(f'\n===== {fname} =====')
        img = Image.open(os.path.join(img_dir, fname))
        img_np = np.array(img)
        results = reader.readtext(img_np, detail=0)
        for line in results:
            print(line)



