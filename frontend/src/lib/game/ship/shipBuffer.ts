let shipImgEl: HTMLImageElement | null = null;
let _canvas: HTMLCanvasElement | null = null;
let _imageData: Uint8ClampedArray | null = null;
let _naturalW = 0;
let _naturalH = 0;

function prepareBuffer() {
  if (!shipImgEl) return;
  try {
    _naturalW = shipImgEl.naturalWidth || shipImgEl.width || 0;
    _naturalH = shipImgEl.naturalHeight || shipImgEl.height || 0;
    if (_naturalW > 0 && _naturalH > 0) {
      _canvas = document.createElement('canvas');
      _canvas.width = _naturalW;
      _canvas.height = _naturalH;
      const ctx = _canvas.getContext('2d');
      if (ctx) {
        ctx.clearRect(0,0,_naturalW,_naturalH);
        ctx.drawImage(shipImgEl as HTMLImageElement, 0, 0, _naturalW, _naturalH);
        const id = ctx.getImageData(0,0,_naturalW,_naturalH);
        _imageData = id.data;
      }
    }
  } catch (e) {
    // ignore
  }
}

export function setShipImage(img: HTMLImageElement | null) {
  shipImgEl = img;
  if (!shipImgEl) return;
  if (shipImgEl.complete) prepareBuffer();
  else shipImgEl.addEventListener('load', prepareBuffer, { once: true });
}

export function isShipOpaque(viewportX: number, viewportY: number) {
  if (!shipImgEl || !_imageData || _naturalW <= 0 || _naturalH <= 0) return false;
  try {
    const rect = shipImgEl.getBoundingClientRect();
    if (viewportX < rect.left || viewportX >= rect.right) return false;
    if (viewportY < rect.top || viewportY >= rect.bottom) return false;
    const localX = viewportX - rect.left;
    const localY = viewportY - rect.top;
    const dispW = rect.width;
    const dispH = rect.height;
    let px = Math.floor((localX * _naturalW) / dispW);
    let py = Math.floor((localY * _naturalH) / dispH);
    if (px < 0 || py < 0 || px >= _naturalW || py >= _naturalH) return false;
    const idx = (py * _naturalW + px) * 4 + 3;
    return (_imageData[idx] || 0) > 16;
  } catch (e) {
    return false;
  }
}

export default {
  setShipImage,
  isShipOpaque,
};
