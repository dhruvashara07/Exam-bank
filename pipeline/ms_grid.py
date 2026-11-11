"""Quick check picture of OUR mark-scheme tables (what students get): python3 pipeline/ms_grid.py out.png <qid> ..."""
import sys,os; sys.path.insert(0,'/home/claude/exam-bank/pipeline'); os.chdir('/home/claude/exam-bank')
import store, review_assets as ra
from PIL import Image, ImageDraw
ids=sys.argv[2:]; out=sys.argv[1]
ims=[]
for q in ids:
    sv=store.review_svgs(q,'/tmp/rtmp'); im=ra.svg_img(sv['ms'],60)
    c=Image.new('RGB',(im.width,im.height+14),'white'); c.paste(im,(0,14)); ImageDraw.Draw(c).text((2,1),q[5:],fill=(200,0,0)); ims.append(c)
cols=3; W=max(i.width for i in ims)
rows=[ims[i:i+cols] for i in range(0,len(ims),cols)]
H=sum(max(i.height for i in r)+6 for r in rows)
g=Image.new('RGB',(W*cols+12,H),(200,200,200)); y=0
for r in rows:
    for k,i in enumerate(r): g.paste(i,(k*(W+6),y))
    y+=max(i.height for i in r)+6
g.save(out); print(g.size)
