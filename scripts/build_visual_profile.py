#!/usr/bin/env python3
"""Build the compact visual profile. Run manually; no scheduled workflow."""
from __future__ import annotations
import concurrent.futures
from datetime import datetime, timezone
from html import escape
import json
import math
import os
from pathlib import Path
import re
import urllib.request
import xml.etree.ElementTree as ET
import build_profile as core

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'
INK, MUTED, CYAN, VIOLET = '#f0f6fc', '#9baac1', '#59d9ff', '#ab9bff'
ICONS = {
 'python': ('Python','python-original'), 'pytorch': ('PyTorch','pytorch-original'),
 'tensorflow': ('TensorFlow','tensorflow-original'),
 'opencv': ('OpenCV','opencv-original'), 'django': ('Django','django-plain'),
 'git': ('Git','git-original'),
 'amazonwebservices': ('AWS','amazonwebservices-original-wordmark'), 'docker': ('Docker','docker-original'),
 'linux': ('Linux','linux-original'),
 'java': ('Java','java-original'), 'typescript': ('TypeScript','typescript-original'),
 'csharp': ('C#','csharp-original'), 'cplusplus': ('C++','cplusplus-original'),
 'rust': ('Rust','rust-original'), 'cuda': ('CUDA','nvidia'), 'vtk': ('VTK','vtk')}
ICON_URLS = {
 'cuda': 'https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/nvidia.svg',
 'vtk': 'https://upload.wikimedia.org/wikipedia/commons/7/76/Visualization_Toolkit_logo.svg'}

def t(x,y,value,size=14,color=INK,**attrs):
    attrs=' '.join(f'{k.replace("_","-")}="{escape(str(v),quote=True)}"' for k,v in attrs.items())
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-family="Arial,Helvetica,sans-serif" {attrs}>{escape(str(value))}</text>'

def wrap(w,h,title,body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title><defs><linearGradient id="panel" x2="1" y2="1"><stop stop-color="#101b30"/><stop offset="1" stop-color="#121422"/></linearGradient><linearGradient id="glow"><stop stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient></defs><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="18" fill="url(#panel)" stroke="#26344a"/>{body}</svg>\n'

def hero():
    b=f'<path d="M28 35 H64" stroke="{CYAN}" stroke-width="4"/>'
    b+=t(80,40,'AI ENGINEER @ ALLIAGE',14,CYAN,letter_spacing=2)
    b+=t(38,124,'Lucas',79,font_weight=700,letter_spacing=-3)
    b+=t(38,207,'Betioli',79,font_weight=700,letter_spacing=-3)
    b+=t(43,258,'COMPUTER VISION   /   MEDICAL AI   /   ML SYSTEMS',12,MUTED,letter_spacing=.5)
    b+=f'<g stroke="#2c3e59" stroke-width="1" opacity=".65">'
    for i in range(6):
        x=600+i*66
        b+=f'<path d="M{x} 66 V252 M590 {80+i*32} H946"/>'
    b+='</g>'
    # An abstract visual field linking image regions and a model graph.
    for i in range(6):
        r=36+i*12
        pts=[]
        for j in range(81):
            a=j*math.pi/40
            rr=r*(1+.14*math.sin(3*a))
            pts.append(f'{759+rr*math.cos(a):.1f},{157+.83*rr*math.sin(a):.1f}')
        b+=f'<polyline points="{" ".join(pts)}" fill="none" stroke="{CYAN if i%2==0 else VIOLET}" stroke-opacity="{.7-i*.08}" stroke-width="1.5"/>'
    nodes=[(648,105),(753,64),(863,106),(882,208),(772,251),(657,215),(759,157)]
    for i,(x,y) in enumerate(nodes[:-1]):
        nx,ny=nodes[(i+1)%6]
        b+=f'<path d="M{x} {y} L{nx} {ny} M{x} {y} L759 157" stroke="#3d5575" stroke-width="1.5"/>'
    for i,(x,y) in enumerate(nodes):
        b+=f'<circle cx="{x}" cy="{y}" r="{7 if i==6 else 4}" fill="{CYAN if i%2==0 else VIOLET}"/><circle cx="{x}" cy="{y}" r="12" fill="none" stroke="{CYAN}" opacity=".2"/>'
    b+=f'<path d="M626 93 V76 H645 M886 76 H905 V94 M626 221 V240 H645 M886 240 H905 V221" fill="none" stroke="{CYAN}" stroke-width="2"/>'
    return wrap(1000,295,'Lucas Betioli — AI Engineer at Alliage. Computer Vision, Medical AI, ML Systems.',b)

def qualifications():
    b=''
    for i,(headline,a,c,year) in enumerate([
      ('M.Sc. · USP','Applied Physics to','Medicine & Biology','2025'),
      ('B.Sc. · USP','Medical Physics','','2023'),
      ('GSoC Mentor','InVesalius','Open-source medical imaging','')]):
        x=26+i*333
        if i:b+=f'<path d="M{x-13} 24 V124" stroke="#2c3a50"/>'
        col=[CYAN,VIOLET,'#6ee7b7'][i]
        b+=f'<rect x="{x}" y="24" width="35" height="35" rx="9" fill="{col}" fill-opacity=".12"/>'
        if i<2:
            b+=f'<path d="M{x+6} 36 l11-6 11 6-11 6z M{x+11} 40 v6 q6 5 12 0 v-6 M{x+28} 36 v11" fill="none" stroke="{col}" stroke-width="1.5"/>'
        else:
            b+=f'<path d="M{x+13} 33 l-6 8 6 8 M{x+23} 33 l6 8-6 8 M{x+20} 31 l-5 20" fill="none" stroke="{col}" stroke-width="1.7"/>'
        b+=t(x+47,49,headline,23,font_weight=700)
        b+=t(x,88,a,15,MUTED)+t(x,110,c,15,MUTED)
        b+=t(x+283,125,year,11,col,text_anchor='end')
    return wrap(1000,148,'Qualifications: M.Sc. and B.Sc. from USP; Google Summer of Code mentor for InVesalius.',b)

def get_icon(key, cache=None):
    title,filename=ICONS[key]
    cached=Path(cache,key+'.svg') if cache is not None else None
    if cached is not None and cached.exists():src=cached.read_text()
    else:
        url=ICON_URLS.get(key,f'https://raw.githubusercontent.com/devicons/devicon/master/icons/{key}/{filename}.svg')
        req=urllib.request.Request(url,headers={'User-Agent':'LucasBetioli-profile'})
        with urllib.request.urlopen(req,timeout=30) as response:src=response.read().decode()
        if cached is not None:cached.write_text(src)
    root=ET.fromstring(src)
    # Inline only static vector shapes. No external links or script content.
    for element in root.iter():
        if element.tag.split('}')[-1] in {'script','foreignObject','image','use'}:
            raise ValueError('Unexpected non-vector icon content')
        for attr in element.attrib:
            if attr.lower().startswith('on') or 'href' in attr.lower():raise ValueError('Unsafe SVG attribute')
    default_view='0 0 '+re.sub(r'[^0-9.]','',root.attrib.get('width','128'))+' '+re.sub(r'[^0-9.]','',root.attrib.get('height','128'))
    view=[float(v) for v in root.attrib.get('viewBox',default_view).replace(',',' ').split()]
    ids={e.attrib['id']:key+'-'+e.attrib['id'] for e in root.iter() if 'id' in e.attrib}
    for element in root.iter():
        for attr,value in list(element.attrib.items()):
            if attr=='id':element.attrib[attr]=ids[value]
            else:
                for old,new in ids.items():value=value.replace('url(#'+old+')','url(#'+new+')')
                element.attrib[attr]=value
    inner=''.join(ET.tostring(child,encoding='unicode') for child in root)
    inner='<g fill="'+root.attrib.get('fill','#76b900' if key=='cuda' else '#f0f6fc')+'">'+inner+'</g>'
    if key=='django':inner=inner.replace('#092e20','#79cda3').replace('#092E20','#79cda3')
    if key=='amazonwebservices':inner=inner.replace('#252f3e','#e6edf3').replace('#252F3E','#e6edf3')
    if key=='rust':
        inner=inner.replace('fill="#000000"','fill="#e2e8f0"').replace('fill="#000"','fill="#e2e8f0"').replace('fill="black"','fill="#e2e8f0"')
    return key,(inner,view)

def stack(icons):
    b=''
    groups=[('AI, GPU & VISUALIZATION',['tensorflow','pytorch','python','opencv','cuda','vtk']),
            ('LANGUAGES & FRAMEWORKS',['django','typescript','java','csharp','cplusplus','rust']),
            ('CLOUD & DEVELOPMENT',['amazonwebservices','docker','git','linux'])]
    for row,(label,keys) in enumerate(groups):
        y=16+row*158
        b+=f'<rect x="16" y="{y}" width="968" height="142" rx="13" fill="#0c1321" stroke="#253147"/>'
        b+=t(36,y+29,label,12,[CYAN,VIOLET,'#6ee7b7'][row],letter_spacing=1.5,font_weight=700)
        for idx,key in enumerate(keys):
            center=16+(idx+.5)*968/len(keys)
            inner,view=icons[key]
            if key=='vtk':
                b+=f'<rect x="{center-34:.2f}" y="{y+47}" width="68" height="52" rx="7" fill="#f1f5f9"/>'
            scale=min(52/view[2],52/view[3]);xx=center-view[2]*scale/2;yy=y+47+(52-view[3]*scale)/2
            b+=f'<g transform="translate({xx:.2f},{yy:.2f}) scale({scale:.7f}) translate({-view[0]},{-view[1]})">{inner}</g>'
            b+=t(round(center,2),y+121,ICONS[key][0],14,MUTED,text_anchor='middle')
    return wrap(1000,490,'AI, GPU and visualization: TensorFlow, PyTorch, Python, OpenCV, CUDA, VTK. Languages and frameworks: Django, TypeScript, Java, C#, C++, Rust. Cloud and development: AWS, Docker, Git, Linux.',b)

def project(which):
    if which=='poligome':
        label='Poligome';sub='AI-assisted image annotation';col=CYAN
        b=f'<g transform="translate(42,18)"><path d="M35 61 C54 12 132 17 177 47 S289 16 338 66 L309 130 210 153 142 128 53 141Z" fill="{col}" fill-opacity=".07" stroke="{col}" stroke-opacity=".5"/>'
        regions=['M55 60 L120 38 159 69 140 118 67 122Z','M164 68 L220 48 279 70 255 120 198 139 145 120Z','M281 72 L326 68 299 119 259 124Z']
        for i,path in enumerate(regions):b+=f'<path d="{path}" fill="{[CYAN,VIOLET,"#6ee7b7"][i]}" fill-opacity=".22" stroke="{[CYAN,VIOLET,"#6ee7b7"][i]}" stroke-width="1.5"/>'
        for x,y in [(55,60),(120,38),(159,69),(140,118),(220,48),(279,70),(255,120)]:b+=f'<circle cx="{x}" cy="{y}" r="3" fill="{col}"/>'
        b+='</g>'
    else:
        label='InVesalius';sub='GSoC mentoring · Medical imaging';col=VIOLET
        b='<g transform="translate(110,9)">'
        for off in [0,14,28]:
            b+=f'<path d="M40 {74+off} Q52 {27+off} 98 {34+off} Q131 {11+off} 164 {33+off} Q212 {29+off} 223 {76+off} Q208 {115+off} 166 {112+off} Q132 {131+off} 101 {110+off} Q51 {115+off} 40 {74+off}Z" fill="{col}" fill-opacity=".06" stroke="{col}" stroke-opacity="{.3+off/70}"/>'
        b+=f'<path d="M132 34 V130 M89 48 Q116 68 92 88 M172 49 Q149 68 176 91 M63 85 Q89 75 101 104 M200 85 Q174 75 165 107" fill="none" stroke="{col}" stroke-width="2"/><circle cx="132" cy="83" r="5" fill="{CYAN}"/></g>'
    b+=t(25,199,label,27,font_weight=700)+t(25,226,sub,14,MUTED)
    b+=t(463,202,'↗',25,col,text_anchor='end')
    return wrap(490,250,label+' — '+sub,b)

def dashboard(totals,days,repos,prs,today):
    b=t(28,37,'GITHUB / PUBLIC SNAPSHOT',12,CYAN,letter_spacing=1.3)
    b+=t(972,37,today.isoformat(),11,MUTED,text_anchor='end')
    values=[(len(repos),'PUBLIC REPOSITORIES'),(prs,'PUBLIC PULL REQUESTS'),(sum(days.values()),f'CONTRIBUTIONS {today.year-1}–{today.year}')]
    for i,(n,label) in enumerate(values):
        x=28+i*159
        b+=t(x,110,n,40,font_weight=700)+t(x,139,label,9,MUTED,letter_spacing=.4)
    b+=f'<path d="M525 61 V231" stroke="#2c3a50"/>'
    colors=[CYAN,VIOLET,'#6ee7b7','#fbbf24','#fb7185','#818cf8']
    total=sum(totals.values());offset=0
    b+=f'<circle cx="620" cy="143" r="55" fill="none" stroke="#26344a" stroke-width="15"/>'
    groups=totals.most_common(4)
    rest=total-sum(n for _,n in groups)
    if rest:groups.append(('Other',rest))
    for i,(name,n) in enumerate(groups):
        length=n/total*2*math.pi*55
        b+=f'<circle cx="620" cy="143" r="55" fill="none" stroke="{colors[i]}" stroke-width="15" stroke-dasharray="{length:.3f} {2*math.pi*55-length:.3f}" stroke-dashoffset="{-offset:.3f}" transform="rotate(-90 620 143)"/>'
        offset+=length
        yy=120+i*25
        b+=f'<circle cx="711" cy="{yy-5}" r="4" fill="{colors[i]}"/>'
        b+=t(725,yy,name,13,MUTED)+t(969,yy,f'{100*n/total:.1f}%',12,INK,text_anchor='end')
    b+=t(620,149,'CODE',12,MUTED,text_anchor='middle',letter_spacing=2)
    b+=t(711,81,'LANGUAGES',12,VIOLET,letter_spacing=1.6)
    b+=t(28,215,'Public activity only. Private work is not represented.',12,MUTED)
    b+=t(711,215,'By bytes · Forks excluded',11,MUTED)
    return wrap(1000,248,'Public GitHub data: repositories, authored pull requests, contribution totals and original-repository language bytes.',b)

def activity(days,today):
    from collections import defaultdict
    months=defaultdict(int)
    for day,n in sorted(days.items()):months[day[:7]]+=n
    b=t(28,36,'CONTRIBUTIONS',12,CYAN,letter_spacing=1.6)
    b+=t(972,36,f'{today.year-1}–{today.year}',12,MUTED,text_anchor='end')
    maxn=max(1,max(months.values()));step=934/len(months)
    for i,(month,n) in enumerate(months.items()):
        x=34+i*step;h=88*n/maxn
        b+=f'<rect x="{x:.1f}" y="{150-h:.1f}" width="{min(24,step*.6):.1f}" height="{max(h,2):.1f}" rx="3" fill="{CYAN if month[:4]==str(today.year) else VIOLET}" opacity="{1 if n else .14}"/>'
        if n:b+=t(round(x+10,1),round(142-h,1),n,11,MUTED,text_anchor='middle')
        label=month[:4] if month.endswith('-01') else datetime.strptime(month,'%Y-%m').strftime('%b')
        b+=t(round(x+10,1),174,label,10,MUTED,text_anchor='middle')
    return wrap(1000,195,'Monthly public contribution activity; current month is partial.',b)

def main():
    today=datetime.now(timezone.utc).date();user='LucasBetioli123';token=os.getenv('GH_TOKEN','')
    totals,days,_,_=core.collect(user,token,today,None)
    repos=json.loads(core.request(f'https://api.github.com/users/{user}/repos?per_page=100&type=owner',token))
    prs=json.loads(core.request(f'https://api.github.com/search/issues?q=author%3A{user}+type%3Apr+is%3Apublic&per_page=1',token))['total_count']
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:icons=dict(pool.map(get_icon,ICONS))
    rendered={'hero-v2.svg':hero(),'qualifications-v2.svg':qualifications(),'stack-v2.svg':stack(icons),'poligome-v2.svg':project('poligome'),'invesalius-v2.svg':project('invesalius'),'github-v2.svg':dashboard(totals,days,repos,prs,today),'activity-v2.svg':activity(days,today)}
    OUT.mkdir(exist_ok=True)
    for name,content in rendered.items():ET.fromstring(content)
    for name,content in rendered.items():(OUT/name).write_text(content)
    print(json.dumps({'assets':len(rendered),'public_repositories':len(repos),'public_prs':prs,'contributions':sum(days.values()),'language_bytes':dict(totals)}))

if __name__=='__main__':main()
