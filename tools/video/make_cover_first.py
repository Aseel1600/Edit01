"""make_cover_first.py — give a WTMG reel a strong auto-cover (frame 0) for FB/IG.

Generates a branded dark-ledger cover still (dimmed hero + gold price + subject +
burn twist-teaser + wordmark) and prepends it as a short freeze, padding the audio
with matching silence so A/V stay in sync. Run with the Python311 exe (needs Pillow).

Usage:
  make_cover_first.py --reel <in.mp4> --hero <hero.png/jpg> --price "$300" \
    --subject "one pair of glasses" --twist "the frame? ~$8" --out <out.mp4> [--hold 0.5]
"""
import argparse, subprocess, os
from PIL import Image, ImageDraw, ImageFont

INK=(245,241,232); GOLD=(217,164,65); BURN=(228,87,73); MUTED=(139,148,156)
BOLD=[r"C:/Windows/Fonts/arialbd.ttf"]; REG=[r"C:/Windows/Fonts/arial.ttf"]

def font(paths, size):
    for p in paths:
        try: return ImageFont.truetype(p, size)
        except Exception: pass
    return ImageFont.load_default()

def make_cover(hero, price, subject, twist, out_png):
    S=2; W,H=1080*S,1920*S
    img=Image.new("RGB",(W,H),(11,14,19)); d=ImageDraw.Draw(img)
    for y in range(H):
        t=y/H; d.line([(0,y),(W,y)], fill=(int(16*(1-t)+10*t),int(21*(1-t)+13*t),int(28*(1-t)+18*t)))
    if hero and os.path.exists(hero):
        hi=Image.open(hero).convert("RGB")
        r=max(W/hi.width,H/hi.height); nw,nh=int(hi.width*r),int(hi.height*r)
        hi=hi.resize((nw,nh),Image.LANCZOS).crop(((nw-W)//2,(nh-H)//2,(nw-W)//2+W,(nh-H)//2+H))
        img=Image.blend(img,hi,0.42)
        ov=Image.new("L",(W,H),0); od=ImageDraw.Draw(ov)
        for y in range(H):
            a=int(150*(1-y/(H*0.30))) if y<H*0.30 else (int(185*((y-H*0.58)/(H*0.42))) if y>H*0.58 else 55)
            od.line([(0,y),(W,y)], fill=max(0,min(255,a)))
        img=Image.composite(Image.new("RGB",(W,H),(8,11,16)),img,ov)
    d=ImageDraw.Draw(img)
    def ctext(text,fnt,fill,y,ls=0):
        if ls:
            ws=[d.textlength(c,font=fnt) for c in text]; tot=sum(ws)+ls*(len(text)-1); x=W/2-tot/2
            for c,w in zip(text,ws): d.text((x,y),c,font=fnt,fill=fill); x+=w+ls
        else:
            w=d.textlength(text,font=fnt); d.text((W/2-w/2,y),text,font=fnt,fill=fill)
    ctext("WHERE THE MONEY GOES", font(BOLD,26*S), GOLD, 120*S, ls=8*S)
    ctext(price, font(BOLD,230*S), GOLD, 660*S)
    ctext(subject, font(REG,52*S), INK, 950*S)
    ctext(twist, font(BOLD,64*S), BURN, 1090*S)
    ctext("@themoneysplit", font(REG,30*S), MUTED, H-118*S)
    img.resize((1080,1920), Image.LANCZOS).save(out_png)

def prepend(cover_png, reel, out, hold):
    vf=(f"[0:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p[cv];"
        f"[1:v]setsar=1,fps=30,format=yuv420p[rv];[cv][rv]concat=n=2:v=1:a=0[v];"
        f"anullsrc=channel_layout=stereo:sample_rate=48000:d={hold}[sil];[sil][1:a]concat=n=2:v=0:a=1[a]")
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-loop","1","-t",str(hold),"-i",cover_png,
        "-i",reel,"-filter_complex",vf,"-map","[v]","-map","[a]","-c:v","libx264","-preset","medium","-crf","18",
        "-pix_fmt","yuv420p","-r","30","-c:a","aac","-b:a","192k",out], check=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--reel",required=True); ap.add_argument("--hero",default="")
    ap.add_argument("--price",required=True); ap.add_argument("--subject",required=True)
    ap.add_argument("--twist",required=True); ap.add_argument("--out",required=True)
    ap.add_argument("--hold",type=float,default=0.5); ap.add_argument("--cover-out",default="")
    a=ap.parse_args()
    cov=a.cover_out or (os.path.splitext(a.out)[0]+"_cover.png")
    make_cover(a.hero,a.price,a.subject,a.twist,cov)
    prepend(cov,a.reel,a.out,a.hold)
    print("cover:",cov,"| out:",a.out)
