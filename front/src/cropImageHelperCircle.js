export default async function getCroppedImgCircle(imageSrc, croppedAreaPixels) {
    return new Promise((resolve, reject) => {
      const image = new Image();
      image.src = imageSrc;
  
      image.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
  
        // Define o tamanho do canvas com base no menor lado do recorte (para manter o círculo)
        const size = Math.min(croppedAreaPixels.width, croppedAreaPixels.height);
        canvas.width = size;
        canvas.height = size;
  
        // Centraliza o recorte para um círculo
        const centerX = croppedAreaPixels.x + croppedAreaPixels.width / 2;
        const centerY = croppedAreaPixels.y + croppedAreaPixels.height / 2;
  
        // Ajusta as coordenadas para desenhar a imagem no canvas circular
        ctx.beginPath();
        ctx.arc(size / 2, size / 2, size / 2, 0, Math.PI * 2, true);
        ctx.clip();
  
        ctx.drawImage(
          image,
          centerX - size / 2,
          centerY - size / 2,
          size,
          size,
          0,
          0,
          size,
          size
        );
  
        canvas.toBlob(
          (blob) => {
            if (!blob) {
              reject(new Error('Erro ao criar blob da imagem.'));
              return;
            }
            resolve(blob);
          },
          'image/jpeg',
          0.9 // Qualidade da compressão (0.9 = alta qualidade)
        );
      };
  
      image.onerror = () => {
        reject(new Error('Erro ao carregar a imagem.'));
      };
    });
  }
  