"""Refresh ShowingReel social kit with the NEW logo: reusable logomark, profile pics, FB banners."""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont
os.chdir("C:/OpenMontage/projects/video-service-business")
OUT="brand-social/out"; os.makedirs(OUT,exist_ok=True)
NAVY=(13,27,42); CORAL=(255,107,74); CORAL_D=(214,74,40); CORAL_L=(255,140,108); WHITE=(255,255,255); DARK=(150,44,20); MUT=(178,190,202)
ARCH="samples-pt/fonts/ArchivoBlack.ttf"; SEGSB="C:/Windows/Fonts/seguisb.ttf"
HOUSE=[(16,52),(16,28.8),(13.6,28.8),(32,13.6),(50.4,28.8),(48,28.8),(48,52)]
TRI=[(25.6,33.9),(25.6,48.3),(41,41.1)]
def F(p,s): return ImageFont.truetype(p,s)

def render_logo(size, frac=0.82, mode="squircle", shadow=True, gloss=True):
    SS=4; P=size*SS; RAD=int(0.225*P)
    g=Image.new("RGB",(P,P)); px=g.load()
    for y in range(P):
        for x in range(P):
            t=(x+y)/(2*P-2); px[x,y]=tuple(int(CORAL_L[i]+(CORAL_D[i]-CORAL_L[i])*t) for i in range(3))
    def sqm():
        m=Image.new("L",(P,P),0); ImageDraw.Draw(m).rounded_rectangle([0,0,P,P],RAD,fill=255); return m
    if mode=="squircle": g.putalpha(sqm()); tile=g.convert("RGBA"); clip=sqm()
    else: tile=g.convert("RGBA"); clip=Image.new("L",(P,P),255)
    if gloss:
        s=Image.new("L",(P,P),0); ImageDraw.Draw(s).ellipse([-P*0.3,-P*0.75,P*1.3,P*0.55],fill=40)
        s=ImageChops.multiply(s,clip); ov=Image.new("RGBA",(P,P),(255,255,255,0)); ov.putalpha(s); tile=Image.alpha_composite(tile,ov)
    ms=int(P*frac); off=(P-ms)//2; k=ms/64.0; NY=1.6  # optical vertical centering
    hm=Image.new("L",(P,P),0); d=ImageDraw.Draw(hm)
    d.polygon([(x*k+off,(y-NY)*k+off) for x,y in HOUSE],fill=255); d.polygon([(x*k+off,(y-NY)*k+off) for x,y in TRI],fill=0)
    if shadow:
        sh=hm.filter(ImageFilter.GaussianBlur(P*0.012)); sh=ImageChops.offset(sh,int(P*0.012),int(P*0.016))
        sh=ImageChops.multiply(sh,clip); sl=Image.new("RGBA",(P,P),DARK+(0,)); sl.putalpha(sh.point(lambda v:int(v*0.5))); tile=Image.alpha_composite(tile,sl)
    mk=Image.new("RGBA",(P,P),WHITE+(0,)); mk.putalpha(hm); tile.alpha_composite(mk)
    return tile.resize((size,size),Image.LANCZOS)

# reusable transparent squircle logomark (no shadow, for pasting on cards)
render_logo(512, mode="squircle", shadow=False, gloss=True).save(f"{OUT}/logomark_sq.png")
print("logomark_sq.png")

# profile pic (FB + IG): coral logo, circle-safe
render_logo(1080, frac=0.90, mode="square", shadow=True, gloss=True).convert("RGB").save(f"{OUT}/pfp_logo.png")
print("pfp_logo.png")

def navy_bg(W,H):
    im=Image.new("RGB",(W,H)); px=im.load()
    for y in range(H):
        for x in range(W):
            t=(x/ W*0.5 + y/H*0.5)
            px[x,y]=(int(10+(20-10)*t), int(22+(44-22)*t), int(34+(60-34)*t))
    # coral glow top-right
    glow=Image.new("L",(W,H),0); ImageDraw.Draw(glow).ellipse([W-560,-260,W+180,300],fill=60)
    glow=glow.filter(ImageFilter.GaussianBlur(80)); cl=Image.new("RGB",(W,H),CORAL)
    return Image.composite(cl,im,glow.point(lambda v:int(v*0.5)))

def fb_cover(tagline,name):
    W,H=1640,624; im=navy_bg(W,H).convert("RGBA"); d=ImageDraw.Draw(im)
    logo=render_logo(150, shadow=True, gloss=True)
    wf=F(ARCH,92); w1=d.textbbox((0,0),"Showing",font=wf)[2]; w2=d.textbbox((0,0),"Reel",font=wf)[2]
    gap=30; total=150+gap+w1+w2; x0=(W-total)//2; ly=190
    im.alpha_composite(logo,(x0, ly-8))
    tx=x0+150+gap; ty=ly+30
    d.text((tx,ty),"Showing",font=wf,fill=WHITE); d.text((tx+w1,ty),"Reel",font=wf,fill=CORAL)
    tf=F(SEGSB,36); tw=d.textbbox((0,0),tagline,font=tf)[2]; d.text(((W-tw)//2,ly+210),tagline,font=tf,fill=MUT)
    d.rectangle([0,H-8,W,H],fill=CORAL_D)
    im.convert("RGB").save(f"{OUT}/{name}.png"); print(name)

fb_cover("Your listing photos, turned into a scroll-stopping video ad.","fb_cover_en")
fb_cover("As suas fotos de imóvel num anúncio em vídeo que prende.","fb_cover_pt")
print("DONE")
