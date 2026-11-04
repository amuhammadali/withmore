import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
from PIL import Image, ImageOps, ImageFilter

human_path = '/var/www/withmore/uploads/tryon/tryon_c9577d3b562866de.jpeg'
garm_path = '/var/www/withmore/uploads/tryon/garm_15.jpg'
out_path = '/var/www/withmore/uploads/tryon/pillow_lion_result.jpg'

# 1. Human photo
human = ImageOps.exif_transpose(Image.open(human_path)).convert('RGBA')
hw, hh = human.size
target_w = 768
target_h = int(hh * (target_w / hw))
human = human.resize((target_w, target_h), Image.Resampling.LANCZOS)

# 2. Garment
garm = Image.open(garm_path).convert('RGBA')
gw, gh = garm.size
suit_w = int(target_w * 0.78)
suit_h = int(gh * (suit_w / gw))
suit = garm.resize((suit_w, suit_h), Image.Resampling.LANCZOS)

# 3. Composite
pos_x = (target_w - suit_w) // 2
pos_y = int(target_h * 0.32)

comp = Image.new('RGBA', (target_w, target_h), (255, 255, 255, 0))
comp.paste(human, (0, 0))

r, g, b, a = suit.split()
a = a.filter(ImageFilter.GaussianBlur(radius=1.2))
suit = Image.merge('RGBA', (r, g, b, a))
comp.paste(suit, (pos_x, pos_y), suit)

comp.convert('RGB').save(out_path, 'JPEG', quality=92)
print('Pillow composition saved successfully! Size:', out_path)
"""

stdin, stdout, stderr = ssh.exec_command(f'/var/www/withmore/.venv/bin/python3 -c "{remote}"')
print(stdout.read().decode())
print(stderr.read().decode())
ssh.close()

