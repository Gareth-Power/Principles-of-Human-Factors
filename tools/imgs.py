import sys,glob,os
from PIL import Image
src,out,prev=sys.argv[1:4]
for f in sorted(glob.glob(src+'/*')):
    n=os.path.splitext(os.path.basename(f))[0]
    im=Image.open(f); w,h=im.size
    if w>1400: im=im.resize((1400,round(h*1400/w)),Image.LANCZOS)
    alpha = im.mode in ('RGBA','LA','P')
    if im.mode=='P': im=im.convert('RGBA')
    im.save(f'{out}/{n}.webp','WEBP',quality=82,method=6)
    p=im.convert('RGBA'); bg=Image.new('RGB',p.size,(255,255,255)); bg.paste(p,mask=p.split()[3]); bg.thumbnail((640,640)); bg.save(f'{prev}/{n}.jpg',quality=70)
    print(n,(w,h),im.size,alpha,os.path.getsize(f'{out}/{n}.webp')//1024,'KB')
