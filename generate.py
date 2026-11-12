#!/usr/bin/env python3
"""Generates terminal.svg for the @APIGranter GitHub profile.
Pulls the latest entries from CISA's Known Exploited Vulnerabilities (KEV) catalog
for the falling-CVE rain and the bottom threat-feed ticker. Stdlib only.
Usage: python generate.py [--static] [--kev path/to/local.json] > terminal.svg"""
import sys, html, random, json, urllib.request, datetime
FEEDS=["https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
       "https://raw.githubusercontent.com/cisagov/kev-data/develop/known_exploited_vulnerabilities.json"]
def load_kev():
    if "--kev" in sys.argv:
        return json.load(open(sys.argv[sys.argv.index("--kev")+1],encoding="utf-8"))
    for u in FEEDS:
        try:
            req=urllib.request.Request(u,headers={"User-Agent":"APIGranter-profile-banner"})
            return json.load(urllib.request.urlopen(req,timeout=30))
        except Exception as e:
            print(f"feed failed: {u}: {e}",file=sys.stderr)
    sys.exit("could not reach any KEV feed; leaving existing SVG untouched")
kev=load_kev()
vulns=sorted(kev["vulnerabilities"],key=lambda v:(v["dateAdded"],v["cveID"]),reverse=True)
latest=vulns[:10]
synced=kev.get("dateReleased","")[:10] or datetime.date.today().isoformat()
random.seed(synced)
static="--static" in sys.argv
banner=[' █████╗ ██████╗ ██╗ ██████╗ ██████╗  █████╗ ███╗   ██╗████████╗███████╗██████╗', '██╔══██╗██╔══██╗██║██╔════╝ ██╔══██╗██╔══██╗████╗  ██║╚══██╔══╝██╔════╝██╔══██╗', '███████║██████╔╝██║██║  ███╗██████╔╝███████║██╔██╗ ██║   ██║   █████╗  ██████╔╝', '██╔══██║██╔═══╝ ██║██║   ██║██╔══██╗██╔══██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗', '██║  ██║██║     ██║╚██████╔╝██║  ██║██║  ██║██║ ╚████║   ██║   ███████╗██║  ██║', '╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝']
W=860; X0=24; CW=8.4; FS=14; BCW=7.8; BFS=13; BLH=13.4
FONT="'SFMono-Regular',Consolas,'Liberation Mono',Menlo,'DejaVu Sans Mono',monospace"
PROMPT="APIGranter@kali:~$ "
out=[]; defs=[]; cid=[0]
esc=lambda s: html.escape(s,quote=True)
def show(t): return '' if static else f'<set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>'
def op(): return '' if static else ' opacity="0"'
def reveal_clip(x,y,n,t,speed,h=22):
    cid[0]+=1; c=f'c{cid[0]}'; w=n*CW
    if static: defs.append(f'<clipPath id="{c}"><rect x="{x}" y="{y-16}" width="{w+2}" height="{h}"/></clipPath>')
    else:
        vals=';'.join(f'{i*CW:.1f}' for i in range(n+1))
        defs.append(f'<clipPath id="{c}"><rect x="{x}" y="{y-16}" width="0" height="{h}"><animate attributeName="width" values="{vals}" calcMode="discrete" begin="{t:.2f}s" dur="{n*speed:.2f}s" fill="freeze"/></rect></clipPath>')
    return c
PR=lambda y: f'<text x="{X0}" y="{y}" textLength="{len(PROMPT)*CW}"><tspan class="u">APIGranter@kali</tspan><tspan class="d">:</tspan><tspan class="h">~</tspan><tspan class="d">$ </tspan></text>'
def typed(y,text,t,speed=0.055):
    x=X0+len(PROMPT)*CW
    c=reveal_clip(x,y,len(text),t,speed)
    out.append(f'<g{op()}>{show(t-0.25)}{PR(y)}</g>')
    out.append(f'<text x="{x}" y="{y}" class="w" textLength="{len(text)*CW}" clip-path="url(#{c})">{esc(text)}</text>')
    return t+len(text)*speed
def parts_svg(y,parts,x=X0):
    s=''
    for txt,cls in parts:
        s+=f'<text x="{x:.1f}" y="{y}" class="{cls}" textLength="{len(txt)*CW:.1f}">{esc(txt)}</text>'; x+=len(txt)*CW
    return s,x
def line(y,parts,t):
    s,_=parts_svg(y,parts); out.append(f'<g{op()}>{show(t)}{s}</g>')

# ---------- timeline ----------
t=0.6
t=typed(60,'./access --user APIGranter',t)+0.2
# handshake progress bar
y=86
bar=24
s,xb=parts_svg(y,[('[','d'),('*','y'),('] ','d'),('handshake ','d')])
out.append(f'<g{op()}>{show(t)}{s}<text x="{xb:.1f}" y="{y}" class="d" textLength="{bar*CW}">{"░"*bar}</text></g>')
c=reveal_clip(xb,y,bar,t+0.15,0.035)
out.append(f'<text x="{xb:.1f}" y="{y}" class="g" textLength="{bar*CW}" clip-path="url(#{c})">{"█"*bar}</text>')
t+=0.15+bar*0.035
s2,_=parts_svg(y,[(' 100%','g')],xb+bar*CW)
out.append(f'<g{op()}>{show(t)}{s2}</g>')
t+=0.25; y+=24
# ACCESS GRANTED flash
s,xe=parts_svg(y,[('[','d'),('+','g'),('] ','d')])
ag='ACCESS GRANTED'
blink='' if static else f'<animate attributeName="opacity" values="1;0;1;0;1;0;1" dur="0.7s" begin="{t:.2f}s" fill="freeze"/>'
out.append(f'<g{op()}>{show(t)}{s}<g filter="url(#glow)">{blink}<rect x="{xe-3:.1f}" y="{y-14}" width="{len(ag)*CW+6:.1f}" height="19" rx="2" class="agbg"/><text x="{xe:.1f}" y="{y}" class="ag" textLength="{len(ag)*CW}">{ag}</text></g></g>')
t+=0.9
# banner with glitch + shimmer
by=y+34
def blines(cls,extra=''):
    return ''.join(f'<text x="{X0}" y="{by+i*BLH:.1f}" class="{cls}" textLength="{len(l)*BCW}"{extra}>{esc(l)}</text>' for i,l in enumerate(banner))
bstart=t
inner=''
if not static:
    # rgb split copies, glitch periodically
    def glitch(dx,dy,col):
        tv="0 0;%d %d;%d %d;0 0;%d %d;0 0;0 0"%(dx,dy,-dx,dy,dx//2,-dy)
        return (f'<g class="{col}" opacity="0">'
                f'<animate attributeName="opacity" values="0;0.75;0.6;0;0.7;0;0" keyTimes="0;0.02;0.04;0.06;0.08;0.1;1" dur="5s" begin="{bstart:.2f}s" repeatCount="indefinite"/>'
                f'<animateTransform attributeName="transform" type="translate" values="{tv}" keyTimes="0;0.02;0.04;0.06;0.08;0.1;1" calcMode="discrete" dur="5s" begin="{bstart:.2f}s" repeatCount="indefinite"/>'
                f'{blines("bc")}</g>')
    inner+=glitch(4,1,'gr-red')+glitch(-4,-1,'gr-cyan')
# main, revealed line by line
mains=''
for i,l in enumerate(banner):
    mains+=f'<g{op()}>{show(bstart+i*0.08)}<text x="{X0}" y="{by+i*BLH:.1f}" class="b" textLength="{len(l)*BCW}">{esc(l)}</text></g>'
# horizontal tear: duplicate rows 2-3 shifted
tear=''
if not static:
    defs.append(f'<clipPath id="tear"><rect x="0" y="{by+BLH*1-10}" width="{W}" height="{BLH*1.6}"/></clipPath>')
    tear=(f'<g clip-path="url(#tear)"><g opacity="0"><animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.03;0.07;0.08;1" calcMode="discrete" dur="5s" begin="{bstart+0.05:.2f}s" repeatCount="indefinite"/>'
          f'<animateTransform attributeName="transform" type="translate" values="0 0;14 0;-8 0;0 0;0 0" keyTimes="0;0.03;0.05;0.08;1" calcMode="discrete" dur="5s" begin="{bstart+0.05:.2f}s" repeatCount="indefinite"/>'
          f'<rect x="0" y="{by-14}" width="{W}" height="{len(banner)*BLH+6}" fill="#0d1117"/>{blines("b")}</g></g>')
out.append(f'<g filter="url(#glow)">{inner}{mains}{tear}</g>')
bend=bstart+len(banner)*0.08
if not static:
    out.append(f'<rect x="{X0-6}" y="{by-14}" width="8" height="{len(banner)*BLH+6}" class="scan" opacity="0"><set attributeName="opacity" to="0.6" begin="{bend:.2f}s"/><animate attributeName="x" from="{X0-6}" to="{X0+len(banner[0])*BCW}" begin="{bend:.2f}s" dur="0.8s" fill="freeze"/><set attributeName="opacity" to="0" begin="{bend+0.8:.2f}s"/></rect>')
t=bend+1.0
y=by+len(banner)*BLH+30
t=typed(y,'whoami',t)+0.2
line(y+24,[('Petar ','w'),('(','d'),('@APIGranter','h'),(')','d'),(' // ','d'),('security-minded dev','g'),(' // ','d'),('Burgos, ES','w')],t)
t+=0.6; y+=56
t=typed(y,'cat interests.txt',t)+0.2
parts=[]
for k,tg in enumerate(['ethical-hacking','red-teaming','forensics','compliance']):
    parts+=[('[','d'),(tg,'r' if k%2==0 else 'g'),('] ','d')]
line(y+24,parts,t)
t+=0.6; y+=56
t=typed(y,'ls ~/projects',t)+0.2
line(y+24,[('SNItch/','h'),('  -> network traffic analysis tool','d')],t)
t+=0.7; y+=56
cur='' if static else '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite"/>'
out.append(f'<g{op()}>{show(t)}{PR(y)}<rect x="{X0+len(PROMPT)*CW+1}" y="{y-13}" width="{CW}" height="16" class="cur">{cur}</rect></g>')
TY=y+30  # ticker bar top
H=TY+34
# ---------- live threat feed ticker ----------
TCW=7.2
def short(v):
    n=v["vulnerabilityName"].replace(" Vulnerability","")
    return n if len(n)<=70 else n[:67]+"..."
items=[f'{v["cveID"]} :: {short(v)} :: added {v["dateAdded"]}' for v in latest]
feed='   ///   '.join(items)+'   ///   '
L=len(feed)*TCW
LBL=' LIVE THREAT FEED '
lx=X0; lw=len(LBL)*TCW+18
tx0=lx+lw+10
defs.append(f'<clipPath id="tk"><rect x="{tx0}" y="{TY}" width="{W-tx0-12}" height="30"/></clipPath>')
scroll='' if static else f'<animateTransform attributeName="transform" type="translate" from="0 0" to="{-L:.1f} 0" dur="{L/65:.1f}s" repeatCount="indefinite"/>'
ft=''.join(f'<text x="{tx0+k*L:.1f}" y="{TY+20}" class="tk" textLength="{L:.1f}">{esc(feed)}</text>' for k in range(2))
pulse='' if static else '<animate attributeName="opacity" values="1;0.2;1" dur="1.2s" repeatCount="indefinite"/>'
ticker=(f'<line x1="12" y1="{TY}" x2="{W-12}" y2="{TY}" class="sep"/>'
        f'<rect x="{lx}" y="{TY+6}" width="{lw:.1f}" height="20" rx="3" class="lbl"/>'
        f'<circle cx="{lx+10}" cy="{TY+16}" r="3.5" class="dot">{pulse}</circle>'
        f'<text x="{lx+16}" y="{TY+20}" class="lt" textLength="{len(LBL)*TCW:.1f}">{LBL}</text>'
        f'<g clip-path="url(#tk)"><g>{scroll}{ft}</g></g>')
out.append(ticker)

# ---------- matrix rain on the right ----------
rain=''
for k in range(10):
    x=652+k*20
    col=latest[k%len(latest)]['cveID']; n=len(col)
    ts=''.join(f'<tspan x="{x}" dy="16" class="{"rh" if i==n-1 else "rc"}" opacity="{0.15+0.85*i/n:.2f}">{esc(ch)}</tspan>' for i,ch in enumerate(col))
    dur=random.uniform(4,8); delay=random.uniform(0,6)
    anim='' if static else f'<animateTransform attributeName="transform" type="translate" from="0 {-n*16-20}" to="0 {H}" dur="{dur:.1f}s" begin="{-delay:.1f}s" repeatCount="indefinite"/>'
    rain+=f'<g>{anim}<text y="0" style="font-size:13px">{ts}</text></g>'
defs.append(f'<clipPath id="body"><rect x="0" y="33" width="{W}" height="{TY-34}"/></clipPath>')
defs.append('<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#000"/><stop offset="0.35" stop-color="#fff"/></linearGradient>'
            f'<mask id="rm"><rect x="630" y="0" width="230" height="{H}" fill="url(#fade)"/></mask>')
rain_g=f'<g clip-path="url(#body)" mask="url(#rm)" opacity="0.35">{rain}</g>'

shimmer='' if static else f'<animateTransform attributeName="gradientTransform" type="translate" values="-1 0;1 0" dur="6s" repeatCount="indefinite"/>'
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="@APIGranter terminal banner">
<style>
text{{font-family:{FONT};font-size:{FS}px;white-space:pre}}
.b{{font-size:{BFS}px;fill:url(#gr)}} .bc{{font-size:{BFS}px}}
.gr-red text{{fill:#ff2a6d}} .gr-cyan text{{fill:#05d9e8}}
.u{{fill:#ff5f56;font-weight:bold}} .h{{fill:#58a6ff;font-weight:bold}} .d{{fill:#8b949e}} .y{{fill:#e3b341;font-weight:bold}}
.w{{fill:#e6edf3}} .g{{fill:#39d353}} .r{{fill:#ff7b72}}
.ag{{fill:#0d1117;font-weight:bold}} .agbg{{fill:#39d353}}
.cur,.scan{{fill:#39d353}} .rc{{fill:#39d353}} .tk{{font-size:12px;fill:#ff7b72}} .lt{{font-size:12px;font-weight:bold;fill:#0d1117}} .lbl{{fill:#ff5f56}} .dot{{fill:#0d1117}} .sep{{stroke:#30363d}} .rh{{fill:#d2ffd8}}
</style>
<defs>
<linearGradient id="gr" x1="0" x2="1" spreadMethod="reflect"><stop offset="0" stop-color="#39d353"/><stop offset="0.5" stop-color="#2ea043"/><stop offset="1" stop-color="#58a6ff"/>{shimmer}</linearGradient>
<filter id="glow" x="-5%" y="-30%" width="110%" height="160%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="sl" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" opacity="0.03"/></pattern>
<radialGradient id="vig" cx="0.5" cy="0.5" r="0.75"><stop offset="0.6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.45"/></radialGradient>
{''.join(defs)}
</defs>
<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>
{rain_g}
<rect width="{W}" height="32" rx="10" fill="#161b22"/><rect y="22" width="{W}" height="10" fill="#161b22"/>
<line x1="0" y1="32" x2="{W}" y2="32" stroke="#30363d"/>
<circle cx="20" cy="16" r="6" fill="#ff5f56"/><circle cx="40" cy="16" r="6" fill="#ffbd2e"/><circle cx="60" cy="16" r="6" fill="#27c93f"/>
<text x="{W/2}" y="21" text-anchor="middle" class="d" style="font-size:12px">APIGranter@kali: ~  ::  threat feed synced {synced}</text>
{chr(10).join(out)}
<rect y="32" width="{W}" height="{H-32}" fill="url(#sl)"/>
<rect width="{W}" height="{H}" rx="10" fill="url(#vig)"/>
</svg>'''
print(svg)
