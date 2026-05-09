"""Script para gerar ícones PNG do PWA. Execute uma vez após instalar os requirements."""
import struct
import zlib
import os

def create_png(width, height, color=(13, 110, 253)):
    """Cria um PNG sólido com a cor informada."""
    def pack_chunk(name, data):
        chunk = name + data
        crc = zlib.crc32(chunk) & 0xFFFFFFFF
        return struct.pack('>I', len(data)) + chunk + struct.pack('>I', crc)

    signature = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr = pack_chunk(b'IHDR', ihdr_data)

    raw_rows = b''
    for _ in range(height):
        row = b'\x00' + bytes(color) * width
        raw_rows += row
    compressed = zlib.compress(raw_rows)
    idat = pack_chunk(b'IDAT', compressed)
    iend = pack_chunk(b'IEND', b'')

    return signature + ihdr + idat + iend


def draw_text_d(size):
    """Para icons maiores, tenta usar Pillow para um ícone mais bonito."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGBA', (size, size), (13, 110, 253, 255))
        draw = ImageDraw.Draw(img)
        # Letra D centralizada
        try:
            font = ImageFont.truetype("arialbd.ttf", int(size * 0.6))
        except Exception:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), 'D', font=font)
        x = (size - (bbox[2] - bbox[0])) // 2 - bbox[0]
        y = (size - (bbox[3] - bbox[1])) // 2 - bbox[1]
        draw.text((x, y), 'D', fill=(255, 255, 255, 255), font=font)
        return img
    except ImportError:
        return None


if __name__ == '__main__':
    icons_dir = os.path.join('app', 'static', 'icons')
    os.makedirs(icons_dir, exist_ok=True)

    for size in [192, 512]:
        path = os.path.join(icons_dir, f'icon-{size}.png')
        img = draw_text_d(size)
        if img:
            img.save(path)
            print(f'Criado (Pillow): {path}')
        else:
            with open(path, 'wb') as f:
                f.write(create_png(size, size))
            print(f'Criado (fallback simples): {path}')

    print('Ícones gerados com sucesso!')
